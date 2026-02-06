"""Tests for services module."""

from unittest.mock import Mock

import pytest

from src.client.logseq import LogseqClient
from src.models.enums import PageFormat
from src.models.responses import BlockEntity, GraphEntity, PageEntity
from src.models.schemas import (
    AdvancedQueryInput,
    BatchBlockInput,
    CreatePageInput,
    DeleteBlockInput,
    DeletePageInput,
    EmptyInput,
    GetAllPagesInput,
    GetBlockInput,
    GetPageInput,
    GetTasksInput,
    GitCommitInput,
    InsertBlockInput,
    MoveBlockInput,
    RenamePageInput,
    SimpleQueryInput,
    UpdateBlockInput,
)
from src.services.blocks import BlockService
from src.services.graph import GraphService
from src.services.pages import PageService
from src.services.queries import QueryService


class TestBlockService:
    """Test BlockService functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Logseq client."""
        return Mock(spec=LogseqClient)

    @pytest.fixture
    def service(self, mock_client):
        """Create BlockService with mock client."""
        return BlockService(mock_client)

    @pytest.mark.asyncio
    async def test_insert_block(self, service, mock_client):
        """Test insert block operation."""
        mock_client.insert_block.return_value = {
            "uuid": "block-uuid",
            "content": "Test content",
            "page": {"name": "Test Page"},
        }

        input_data = InsertBlockInput(
            parent_block="parent-uuid",
            content="Test content",
            is_page_block=True,
            properties={"tags": ["test"]},
        )

        result = await service.insert(input_data)

        assert isinstance(result, BlockEntity)
        assert result.uuid == "block-uuid"
        assert result.content == "Test content"
        mock_client.insert_block.assert_called_once()
        call_args = mock_client.insert_block.call_args
        assert call_args[0][0] == "parent-uuid"
        assert call_args[0][1] == "Test content"

    @pytest.mark.asyncio
    async def test_insert_block_without_parent(self, service, mock_client):
        """Test insert block without parent."""
        mock_client.insert_block.return_value = {
            "uuid": "block-uuid",
            "content": "Test content",
            "page": {"name": "Test Page"},
        }

        input_data = InsertBlockInput(content="Test content")
        result = await service.insert(input_data)

        assert result.uuid == "block-uuid"
        mock_client.insert_block.assert_called_once_with(
            None, "Test content", isPageBlock=False, before=False
        )

    @pytest.mark.asyncio
    async def test_update_block(self, service, mock_client):
        """Test update block operation."""
        mock_client.update_block.return_value = {
            "uuid": "block-uuid",
            "content": "Updated content",
            "page": {"name": "Test Page"},
        }

        input_data = UpdateBlockInput(uuid="block-uuid", content="Updated content")
        result = await service.update(input_data)

        assert isinstance(result, BlockEntity)
        assert result.content == "Updated content"
        mock_client.update_block.assert_called_once_with("block-uuid", "Updated content")

    @pytest.mark.asyncio
    async def test_update_block_with_properties(self, service, mock_client):
        """Test update block with properties."""
        mock_client.update_block.return_value = {
            "uuid": "block-uuid",
            "content": "Updated content",
            "page": {"name": "Test Page"},
            "properties": {"status": "done"},
        }

        input_data = UpdateBlockInput(
            uuid="block-uuid",
            content="Updated content",
            properties={"status": "done"},
        )
        result = await service.update(input_data)

        assert result.properties == {"status": "done"}

    @pytest.mark.asyncio
    async def test_delete_block(self, service, mock_client):
        """Test delete block operation."""
        input_data = DeleteBlockInput(uuid="block-uuid")
        result = await service.delete(input_data)

        assert result is True
        mock_client.delete_block.assert_called_once_with("block-uuid")

    @pytest.mark.asyncio
    async def test_get_block(self, service, mock_client):
        """Test get block operation."""
        mock_client.get_block.return_value = {
            "uuid": "block-uuid",
            "content": "Block content",
            "page": {"name": "Test Page"},
            "children": [],
        }

        input_data = GetBlockInput(uuid="block-uuid")
        result = await service.get(input_data)

        assert isinstance(result, BlockEntity)
        assert result.uuid == "block-uuid"
        mock_client.get_block.assert_called_once_with("block-uuid")

    @pytest.mark.asyncio
    async def test_move_block(self, service, mock_client):
        """Test move block operation."""
        mock_client.move_block.return_value = {
            "uuid": "source-uuid",
            "content": "Moved block",
            "page": {"name": "Test Page"},
        }

        input_data = MoveBlockInput(uuid="source-uuid", target_uuid="target-uuid", as_child=True)
        result = await service.move(input_data)

        assert isinstance(result, BlockEntity)
        assert result.uuid == "source-uuid"
        mock_client.move_block.assert_called_once_with("source-uuid", "target-uuid", children=True)

    @pytest.mark.asyncio
    async def test_insert_batch(self, service, mock_client):
        """Test batch insert operation."""
        mock_client.insert_batch_blocks.return_value = [
            {"uuid": "block-1", "content": "Block 1", "page": {"name": "Page"}},
            {"uuid": "block-2", "content": "Block 2", "page": {"name": "Page"}},
        ]

        blocks = [{"content": "Block 1"}, {"content": "Block 2"}]
        input_data = BatchBlockInput(parent="parent-uuid", blocks=blocks)
        results = await service.insert_batch(input_data)

        assert len(results) == 2
        assert all(isinstance(r, BlockEntity) for r in results)
        mock_client.insert_batch_blocks.assert_called_once_with("parent-uuid", blocks)

    @pytest.mark.asyncio
    async def test_get_page_blocks(self, service, mock_client):
        """Test get page blocks operation."""
        mock_client.get_page_blocks_tree.return_value = [
            {"uuid": "block-1", "content": "Block 1", "page": {"name": "Page"}},
            {"uuid": "block-2", "content": "Block 2", "page": {"name": "Page"}},
        ]

        results = await service.get_page_blocks("Test Page")

        assert len(results) == 2
        assert all(isinstance(r, BlockEntity) for r in results)
        mock_client.get_page_blocks_tree.assert_called_once_with("Test Page")

    @pytest.mark.asyncio
    async def test_get_current_page_blocks(self, service, mock_client):
        """Test get current page blocks operation."""
        mock_client.get_current_page_blocks_tree.return_value = [
            {"uuid": "block-1", "content": "Current Block", "page": {"name": "Page"}},
        ]

        results = await service.get_current_page_blocks()

        assert len(results) == 1
        mock_client.get_current_page_blocks_tree.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_current_block(self, service, mock_client):
        """Test get current block operation."""
        mock_client.get_current_block.return_value = {
            "uuid": "current-block",
            "content": "Current content",
            "page": {"name": "Page"},
        }

        result = await service.get_current_block()

        assert isinstance(result, BlockEntity)
        assert result.uuid == "current-block"

    @pytest.mark.asyncio
    async def test_get_current_block_none(self, service, mock_client):
        """Test get current block when none is focused."""
        mock_client.get_current_block.return_value = None

        result = await service.get_current_block()

        assert result is None

    def test_format_block_tree(self, service):
        """Test block tree formatting."""
        block = BlockEntity(
            uuid="block-1",
            content="Parent block",
            page={"name": "Test"},
            children=[
                BlockEntity(
                    uuid="block-2",
                    content="Child block",
                    page={"name": "Test"},
                    children=[],
                )
            ],
        )

        formatted = service.format_block_tree([block])

        assert "Parent block" in formatted
        assert "Child block" in formatted


class TestPageService:
    """Test PageService functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Logseq client."""
        return Mock(spec=LogseqClient)

    @pytest.fixture
    def service(self, mock_client):
        """Create PageService with mock client."""
        return PageService(mock_client)

    @pytest.mark.asyncio
    async def test_create_page(self, service, mock_client):
        """Test create page operation."""
        mock_client.create_page.return_value = {
            "uuid": "page-uuid",
            "name": "New Page",
            "originalName": "New Page",
        }

        input_data = CreatePageInput(
            page_name="New Page",
            properties={"tags": ["test"]},
            journal=False,
            format=PageFormat.MARKDOWN,
        )
        result = await service.create(input_data)

        assert isinstance(result, PageEntity)
        assert result.name == "New Page"
        mock_client.create_page.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_page_empty_properties(self, service, mock_client):
        """Test create page with None properties defaults to empty dict."""
        mock_client.create_page.return_value = {
            "uuid": "page-uuid",
            "name": "New Page",
        }

        input_data = CreatePageInput(page_name="New Page")
        await service.create(input_data)

        call_args = mock_client.create_page.call_args
        assert call_args[0][1] == {}  # Empty properties dict

    @pytest.mark.asyncio
    async def test_get_page(self, service, mock_client):
        """Test get page operation."""
        mock_client.get_page.return_value = {
            "uuid": "page-uuid",
            "name": "Test Page",
            "originalName": "Test Page",
        }

        input_data = GetPageInput(src_page="Test Page", include_children=True)
        result = await service.get(input_data)

        assert isinstance(result, PageEntity)
        assert result.name == "Test Page"
        mock_client.get_page.assert_called_once_with("Test Page", include_children=True)

    @pytest.mark.asyncio
    async def test_get_all_pages(self, service, mock_client):
        """Test get all pages operation."""
        mock_client.get_all_pages.return_value = [
            {"uuid": "page-1", "name": "Page 1"},
            {"uuid": "page-2", "name": "Page 2"},
        ]

        input_data = GetAllPagesInput(repo="test-repo")
        results = await service.get_all(input_data)

        assert len(results) == 2
        assert all(isinstance(r, PageEntity) for r in results)
        mock_client.get_all_pages.assert_called_once_with("test-repo")

    @pytest.mark.asyncio
    async def test_get_all_pages_no_repo(self, service, mock_client):
        """Test get all pages without repo."""
        mock_client.get_all_pages.return_value = [
            {"uuid": "page-1", "name": "Page 1"},
        ]

        input_data = GetAllPagesInput()
        await service.get_all(input_data)

        mock_client.get_all_pages.assert_called_once_with(None)

    @pytest.mark.asyncio
    async def test_delete_page(self, service, mock_client):
        """Test delete page operation."""
        input_data = DeletePageInput(page_name="Page to Delete")
        result = await service.delete(input_data)

        assert result is True
        mock_client.delete_page.assert_called_once_with("Page to Delete")

    @pytest.mark.asyncio
    async def test_rename_page(self, service, mock_client):
        """Test rename page operation."""
        input_data = RenamePageInput(old_name="Old Name", new_name="New Name")
        result = await service.rename(input_data)

        assert result is True
        mock_client.rename_page.assert_called_once_with("Old Name", "New Name")

    def test_format_page(self, service):
        """Test page formatting."""
        page = PageEntity(
            uuid="page-uuid",
            name="Test Page",
            journal_day=20240101,
            properties_text_values={"tags": "#test"},
        )

        formatted = service.format_page(page)

        assert "Test Page" in formatted
        assert "20240101" in formatted
        assert "tags::" in formatted

    def test_format_pages(self, service):
        """Test pages list formatting."""
        pages = [
            PageEntity(uuid="page-1", name="Page B"),
            PageEntity(uuid="page-2", name="Page A"),
        ]

        formatted = service.format_pages(pages)

        # Should be sorted alphabetically
        assert formatted.index("Page A") < formatted.index("Page B")


class TestQueryService:
    """Test QueryService functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Logseq client."""
        return Mock(spec=LogseqClient)

    @pytest.fixture
    def service(self, mock_client):
        """Create QueryService with mock client."""
        return QueryService(mock_client)

    @pytest.mark.asyncio
    async def test_simple_query(self, service, mock_client):
        """Test simple query operation."""
        mock_client.q.return_value = [{"name": "Page 1"}, {"name": "Page 2"}]

        input_data = SimpleQueryInput(query="[[Project]]")
        results = await service.simple_query(input_data)

        assert len(results) == 2
        mock_client.q.assert_called_once_with("[[Project]]")

    @pytest.mark.asyncio
    async def test_advanced_query(self, service, mock_client):
        """Test advanced query operation."""
        mock_client.datascript_query.return_value = [
            {"block/uuid": "uuid-1", "block/content": "Task 1"}
        ]

        query = '[:find (pull ?b [*]) :where [?b :block/marker "TODO"]]'
        input_data = AdvancedQueryInput(query=query, inputs=[])
        results = await service.advanced_query(input_data)

        assert len(results) == 1
        mock_client.datascript_query.assert_called_once_with(query)

    @pytest.mark.asyncio
    async def test_advanced_query_with_inputs(self, service, mock_client):
        """Test advanced query with inputs."""
        mock_client.datascript_query.return_value = []

        query = "[:find ?e :where [?e :block/name ?n]]"
        input_data = AdvancedQueryInput(query=query, inputs=["input1", "input2"])
        await service.advanced_query(input_data)

        mock_client.datascript_query.assert_called_once_with(query, "input1", "input2")

    @pytest.mark.asyncio
    async def test_get_tasks(self, service, mock_client):
        """Test get tasks operation."""
        mock_client.datascript_query.return_value = [
            {"marker": "TODO", "priority": "A", "content": "Task 1"},
            {"marker": "DOING", "priority": "B", "content": "Task 2"},
            {"marker": "TODO", "priority": "A", "content": "Task 3"},
        ]

        input_data = GetTasksInput(marker="TODO", priority="A")
        results = await service.get_tasks(input_data)

        assert len(results) == 2
        assert all(r["marker"] == "TODO" for r in results)
        assert all(r["priority"] == "A" for r in results)

    @pytest.mark.asyncio
    async def test_get_tasks_no_filters(self, service, mock_client):
        """Test get tasks without filters."""
        mock_client.datascript_query.return_value = [
            {"marker": "TODO", "content": "Task 1"},
            {"marker": "DONE", "content": "Task 2"},
        ]

        input_data = GetTasksInput()
        results = await service.get_tasks(input_data)

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_get_blocks_with_property(self, service, mock_client):
        """Test get blocks with property."""
        mock_client.datascript_query.return_value = [
            {"uuid": "block-1", "properties": {"status": "active"}}
        ]

        results = await service.get_blocks_with_property("status", "active")

        assert len(results) == 1
        mock_client.datascript_query.assert_called_once()
        call_args = mock_client.datascript_query.call_args[0]
        assert "status" in call_args[0]

    @pytest.mark.asyncio
    async def test_get_blocks_with_property_no_value(self, service, mock_client):
        """Test get blocks with property without specific value."""
        mock_client.datascript_query.return_value = []

        await service.get_blocks_with_property("tags")

        call_args = mock_client.datascript_query.call_args[0]
        # Should not have value comparison in query
        assert "(= ?v" not in call_args[0]

    def test_format_results(self, service):
        """Test query results formatting."""
        results = [
            {"content": "Result 1"},
            {"content": "Result 2"},
        ]

        formatted = service.format_results(results)

        assert "Found 2 results" in formatted
        assert "Result 1" in formatted
        assert "Result 2" in formatted

    def test_format_results_empty(self, service):
        """Test empty query results formatting."""
        formatted = service.format_results([])
        assert "No results found" in formatted


class TestGraphService:
    """Test GraphService functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create mock Logseq client."""
        return Mock(spec=LogseqClient)

    @pytest.fixture
    def service(self, mock_client):
        """Create GraphService with mock client."""
        return GraphService(mock_client)

    @pytest.mark.asyncio
    async def test_get_current_graph(self, service, mock_client):
        """Test get current graph operation."""
        mock_client.get_current_graph.return_value = {
            "name": "test-graph",
            "path": "/path/to/graph",
            "url": "logseq://graph/test",
            "version": "0.10.0",
        }

        input_data = EmptyInput()
        result = await service.get_current_graph(input_data)

        assert isinstance(result, GraphEntity)
        assert result.name == "test-graph"
        assert result.path == "/path/to/graph"
        mock_client.get_current_graph.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_configs(self, service, mock_client):
        """Test get user configs operation."""
        mock_client.get_user_configs.return_value = {
            "preferredLanguage": "en",
            "preferredFormat": "markdown",
        }

        input_data = EmptyInput()
        result = await service.get_user_configs(input_data)

        assert result["preferredLanguage"] == "en"
        assert result["preferredFormat"] == "markdown"

    @pytest.mark.asyncio
    async def test_git_commit(self, service, mock_client):
        """Test git commit operation."""
        input_data = GitCommitInput(message="Test commit")
        result = await service.git_commit(input_data)

        assert result is True
        mock_client.git_commit.assert_called_once_with("Test commit")

    @pytest.mark.asyncio
    async def test_git_status(self, service, mock_client):
        """Test git status operation."""
        mock_client.git_status.return_value = {"modified": ["page1.md"], "untracked": []}

        input_data = EmptyInput()
        result = await service.git_status(input_data)

        assert result == {"modified": ["page1.md"], "untracked": []}

    def test_format_graph(self, service):
        """Test graph formatting."""
        graph = GraphEntity(
            name="test-graph",
            path="/path/to/graph",
            url="logseq://graph/test",
            version="0.10.0",
        )

        formatted = service.format_graph(graph)

        assert "test-graph" in formatted
        assert "/path/to/graph" in formatted
        assert "logseq://graph/test" in formatted
        assert "0.10.0" in formatted

    def test_format_git_status(self, service):
        """Test git status formatting."""
        status = "modified: page1.md\nmodified: page2.md"
        formatted = service.format_git_status(status)

        assert "Git Status:" in formatted
        assert "page1.md" in formatted
