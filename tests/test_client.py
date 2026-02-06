"""Tests for client module."""

from unittest.mock import Mock, patch

import pytest
import requests

from client.logseq import LogseqClient


class TestBaseAPIClient:
    """Test BaseAPIClient functionality."""

    def test_initialization(self):
        """Test client initialization."""
        client = LogseqClient(
            base_url="http://localhost:12315",
            api_key="test-token",
            timeout=30,
            max_retries=5,
        )

        assert client.base_url == "http://localhost:12315"
        assert client.api_key == "test-token"
        assert client.timeout == 30
        assert client.max_retries == 5
        assert client.session.headers["Authorization"] == "Bearer test-token"
        assert client.session.headers["Content-Type"] == "application/json"

    def test_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from URL."""
        client = LogseqClient(
            base_url="http://localhost:12315/",
            api_key="test-token",
        )
        assert client.base_url == "http://localhost:12315"

    def test_default_values(self):
        """Test default initialization values."""
        client = LogseqClient(
            base_url="http://localhost:12315",
            api_key="test-token",
        )
        assert client.timeout == 10
        assert client.max_retries == 3

    @patch("requests.Session.post")
    def test_make_request_success(self, mock_post):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = LogseqClient("http://localhost:12315", "test-token")
        result = client._make_request("logseq.test.method", ["arg1", "arg2"])

        assert result == {"result": "success"}
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:12315/api"
        assert call_args[1]["json"] == {
            "method": "logseq.test.method",
            "args": ["arg1", "arg2"],
        }

    @patch("requests.Session.post")
    def test_make_request_timeout(self, mock_post):
        """Test request timeout handling."""
        mock_post.side_effect = requests.exceptions.Timeout()

        client = LogseqClient("http://localhost:12315", "test-token", timeout=5)

        with pytest.raises(ConnectionError, match="Request timeout after 5s"):
            client._make_request("logseq.test.method", [])

    @patch("requests.Session.post")
    def test_make_request_connection_error(self, mock_post):
        """Test connection error handling."""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        client = LogseqClient("http://localhost:12315", "test-token")

        with pytest.raises(ConnectionError, match="Failed to connect to http://localhost:12315"):
            client._make_request("logseq.test.method", [])

    @patch("requests.Session.post")
    def test_make_request_http_error(self, mock_post):
        """Test HTTP error handling."""
        mock_post.side_effect = requests.exceptions.HTTPError("404 Not Found")

        client = LogseqClient("http://localhost:12315", "test-token")

        with pytest.raises(Exception, match="Request failed"):
            client._make_request("logseq.test.method", [])

    @patch("requests.Session.post")
    def test_custom_timeout_override(self, mock_post):
        """Test custom timeout can override default."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        client = LogseqClient("http://localhost:12315", "test-token", timeout=10)
        client._make_request("logseq.test.method", [], timeout=30)

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["timeout"] == 30


class TestLogseqClientEditorAPI:
    """Test LogseqClient Editor API methods."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return LogseqClient("http://localhost:12315", "test-token")

    @patch.object(LogseqClient, "_make_request")
    def test_insert_block(self, mock_request, client):
        """Test insert_block method."""
        mock_request.return_value = {"uuid": "new-block-uuid"}

        result = client.insert_block("parent-uuid", "Block content", properties={"key": "value"})

        assert result == {"uuid": "new-block-uuid"}
        mock_request.assert_called_once_with(
            "logseq.Editor.insertBlock",
            ["parent-uuid", "Block content", {"properties": {"key": "value"}}],
        )

    @patch.object(LogseqClient, "_make_request")
    def test_update_block(self, mock_request, client):
        """Test update_block method."""
        mock_request.return_value = {"uuid": "block-uuid"}

        result = client.update_block("block-uuid", "Updated content")

        assert result == {"uuid": "block-uuid"}
        mock_request.assert_called_once_with(
            "logseq.Editor.updateBlock", ["block-uuid", "Updated content", {}]
        )

    @patch.object(LogseqClient, "_make_request")
    def test_delete_block(self, mock_request, client):
        """Test delete_block method."""
        client.delete_block("block-uuid")

        mock_request.assert_called_once_with("logseq.Editor.removeBlock", ["block-uuid"])

    @patch.object(LogseqClient, "_make_request")
    def test_get_block(self, mock_request, client):
        """Test get_block method."""
        mock_request.return_value = {"uuid": "block-uuid", "content": "Block content"}

        result = client.get_block("block-uuid")

        assert result == {"uuid": "block-uuid", "content": "Block content"}
        mock_request.assert_called_once_with("logseq.Editor.getBlock", ["block-uuid"])

    @patch.object(LogseqClient, "_make_request")
    def test_move_block(self, mock_request, client):
        """Test move_block method."""
        mock_request.return_value = {"success": True}

        result = client.move_block("source-uuid", "target-uuid", as_child=True)

        assert result == {"success": True}
        mock_request.assert_called_once_with(
            "logseq.Editor.moveBlock",
            ["source-uuid", "target-uuid", {"as_child": True}],
        )

    @patch.object(LogseqClient, "_make_request")
    def test_insert_batch_blocks(self, mock_request, client):
        """Test insert_batch_blocks method."""
        blocks = [{"content": "Block 1"}, {"content": "Block 2"}]
        mock_request.return_value = {"inserted": 2}

        result = client.insert_batch_blocks("parent-uuid", blocks)

        assert result == {"inserted": 2}
        mock_request.assert_called_once_with(
            "logseq.Editor.insertBatchBlock", ["parent-uuid", blocks]
        )

    @patch.object(LogseqClient, "_make_request")
    def test_get_page_blocks_tree(self, mock_request, client):
        """Test get_page_blocks_tree method."""
        mock_request.return_value = [{"content": "Block 1"}, {"content": "Block 2"}]

        result = client.get_page_blocks_tree("Test Page")

        assert result == [{"content": "Block 1"}, {"content": "Block 2"}]
        mock_request.assert_called_once_with("logseq.Editor.getPageBlocksTree", ["Test Page"])

    @patch.object(LogseqClient, "_make_request")
    def test_get_current_page_blocks_tree(self, mock_request, client):
        """Test get_current_page_blocks_tree method."""
        mock_request.return_value = [{"content": "Current Block"}]

        result = client.get_current_page_blocks_tree()

        assert result == [{"content": "Current Block"}]
        mock_request.assert_called_once_with("logseq.Editor.getCurrentPageBlocksTree", [])

    @patch.object(LogseqClient, "_make_request")
    def test_get_current_block(self, mock_request, client):
        """Test get_current_block method."""
        mock_request.return_value = {"uuid": "current-block", "content": "Current content"}

        result = client.get_current_block()

        assert result == {"uuid": "current-block", "content": "Current content"}
        mock_request.assert_called_once_with("logseq.Editor.getCurrentBlock", [])

    @patch.object(LogseqClient, "_make_request")
    def test_get_current_page(self, mock_request, client):
        """Test get_current_page method."""
        mock_request.return_value = {"name": "Current Page"}

        result = client.get_current_page()

        assert result == {"name": "Current Page"}
        mock_request.assert_called_once_with("logseq.Editor.getCurrentPage", [])

    @patch.object(LogseqClient, "_make_request")
    def test_edit_block(self, mock_request, client):
        """Test edit_block method."""
        client.edit_block("block-uuid", pos=5)

        mock_request.assert_called_once_with("logseq.Editor.editBlock", ["block-uuid", {"pos": 5}])

    @patch.object(LogseqClient, "_make_request")
    def test_exit_editing_mode(self, mock_request, client):
        """Test exit_editing_mode method."""
        client.exit_editing_mode(select_block=True)

        mock_request.assert_called_once_with("logseq.Editor.exitEditingMode", [True])

    @patch.object(LogseqClient, "_make_request")
    def test_get_editing_block_content(self, mock_request, client):
        """Test get_editing_block_content method."""
        mock_request.return_value = "Editing block content"

        result = client.get_editing_block_content()

        assert result == "Editing block content"
        mock_request.assert_called_once_with("logseq.Editor.getEditingBlockContent", [])


class TestLogseqClientPageAPI:
    """Test LogseqClient Page API methods."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return LogseqClient("http://localhost:12315", "test-token")

    @patch.object(LogseqClient, "_make_request")
    def test_create_page(self, mock_request, client):
        """Test create_page method."""
        mock_request.return_value = {"name": "New Page"}

        result = client.create_page("New Page", properties={"tags": ["test"]}, journal=True)

        assert result == {"name": "New Page"}
        mock_request.assert_called_once_with(
            "logseq.Editor.createPage",
            ["New Page", {"tags": ["test"]}, {"journal": True}],
        )

    @patch.object(LogseqClient, "_make_request")
    def test_create_page_empty_properties(self, mock_request, client):
        """Test create_page with None properties defaults to empty dict."""
        mock_request.return_value = {"name": "New Page"}

        client.create_page("New Page")

        mock_request.assert_called_once_with("logseq.Editor.createPage", ["New Page", {}, {}])

    @patch.object(LogseqClient, "_make_request")
    def test_get_page(self, mock_request, client):
        """Test get_page method."""
        mock_request.return_value = {"name": "Test Page", "blocks": []}

        result = client.get_page("Test Page", include_children=True)

        assert result == {"name": "Test Page", "blocks": []}
        mock_request.assert_called_once_with(
            "logseq.Editor.getPage",
            ["Test Page", {"includeChildren": True}],
        )

    @patch.object(LogseqClient, "_make_request")
    def test_get_all_pages_with_repo(self, mock_request, client):
        """Test get_all_pages with repository."""
        mock_request.return_value = [{"name": "Page 1"}, {"name": "Page 2"}]

        result = client.get_all_pages(repo="my-repo")

        assert len(result) == 2
        mock_request.assert_called_once_with("logseq.Editor.getAllPages", ["my-repo"])

    @patch.object(LogseqClient, "_make_request")
    def test_get_all_pages_without_repo(self, mock_request, client):
        """Test get_all_pages without repository."""
        mock_request.return_value = [{"name": "Page 1"}]

        result = client.get_all_pages()

        assert len(result) == 1
        mock_request.assert_called_once_with("logseq.Editor.getAllPages", [])

    @patch.object(LogseqClient, "_make_request")
    def test_delete_page(self, mock_request, client):
        """Test delete_page method."""
        client.delete_page("Page to Delete")

        mock_request.assert_called_once_with("logseq.Editor.deletePage", ["Page to Delete"])

    @patch.object(LogseqClient, "_make_request")
    def test_rename_page(self, mock_request, client):
        """Test rename_page method."""
        client.rename_page("Old Name", "New Name")

        mock_request.assert_called_once_with("logseq.Editor.renamePage", ["Old Name", "New Name"])


class TestLogseqClientQueryAPI:
    """Test LogseqClient Query API methods."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return LogseqClient("http://localhost:12315", "test-token")

    @patch.object(LogseqClient, "_make_request")
    def test_q_simple_query(self, mock_request, client):
        """Test q method for simple queries."""
        mock_request.return_value = [{"name": "Page 1"}]

        result = client.q("[[Project]]")

        assert len(result) == 1
        mock_request.assert_called_once_with("logseq.DB.q", ["[[Project]]"])

    @patch.object(LogseqClient, "_make_request")
    def test_q_with_inputs(self, mock_request, client):
        """Test q method with additional inputs."""
        mock_request.return_value = []

        client.q("?p :block/name ?n", "input1", "input2")

        mock_request.assert_called_once_with(
            "logseq.DB.q", ["?p :block/name ?n", "input1", "input2"]
        )

    @patch.object(LogseqClient, "_make_request")
    def test_datascript_query(self, mock_request, client):
        """Test datascript_query method."""
        mock_request.return_value = [{"block/uuid": "uuid-123"}]

        query = '[:find (pull ?b [*]) :where [?b :block/marker "TODO"]]'
        result = client.datascript_query(query)

        assert len(result) == 1
        mock_request.assert_called_once_with("logseq.DB.datascriptQuery", [query])


class TestLogseqClientAppAPI:
    """Test LogseqClient App API methods."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return LogseqClient("http://localhost:12315", "test-token")

    @patch.object(LogseqClient, "_make_request")
    def test_get_current_graph(self, mock_request, client):
        """Test get_current_graph method."""
        mock_request.return_value = {"name": "test-graph", "path": "/path/to/graph"}

        result = client.get_current_graph()

        assert result["name"] == "test-graph"
        mock_request.assert_called_once_with("logseq.App.getCurrentGraph", [])

    @patch.object(LogseqClient, "_make_request")
    def test_get_user_configs(self, mock_request, client):
        """Test get_user_configs method."""
        mock_request.return_value = {"preferredLanguage": "en"}

        result = client.get_user_configs()

        assert result["preferredLanguage"] == "en"
        mock_request.assert_called_once_with("logseq.App.getUserConfigs", [])

    @patch.object(LogseqClient, "_make_request")
    def test_show_msg(self, mock_request, client):
        """Test show_msg method."""
        client.show_msg("Hello World", status="info")

        mock_request.assert_called_once_with("logseq.UI.showMsg", ["Hello World", "info"])


class TestLogseqClientGitAPI:
    """Test LogseqClient Git API methods."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return LogseqClient("http://localhost:12315", "test-token")

    @patch.object(LogseqClient, "_make_request")
    def test_git_commit(self, mock_request, client):
        """Test git_commit method."""
        client.git_commit("Initial commit")

        mock_request.assert_called_once_with("logseq.Git.commit", ["Initial commit"])

    @patch.object(LogseqClient, "_make_request")
    def test_git_status(self, mock_request, client):
        """Test git_status method."""
        mock_request.return_value = {"modified": ["page1.md"], "untracked": []}

        result = client.git_status()

        assert "modified" in result
        mock_request.assert_called_once_with("logseq.Git.status", [])


class TestLogseqClientHealthCheck:
    """Test LogseqClient health check."""

    @patch.object(LogseqClient, "get_current_graph")
    def test_health_check_success(self, mock_get_graph):
        """Test health check when API is accessible."""
        mock_get_graph.return_value = {"name": "test-graph"}

        client = LogseqClient("http://localhost:12315", "test-token")
        result = client.health_check()

        assert result is True
        mock_get_graph.assert_called_once()

    @patch.object(LogseqClient, "get_current_graph")
    def test_health_check_failure(self, mock_get_graph):
        """Test health check when API is not accessible."""
        mock_get_graph.side_effect = Exception("Connection refused")

        client = LogseqClient("http://localhost:12315", "test-token")
        result = client.health_check()

        assert result is False
