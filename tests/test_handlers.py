"""Tests for handlers module."""

from unittest.mock import AsyncMock, Mock

import pytest
from mcp.types import TextContent

from src.handlers.prompts import PromptHandler
from src.handlers.tools import ToolHandler
from src.models.enums import ToolName
from src.models.responses import BlockEntity, GraphEntity, PageEntity
from src.services.blocks import BlockService
from src.services.graph import GraphService
from src.services.pages import PageService
from src.services.queries import QueryService


class TestToolHandler:
    """Test ToolHandler functionality."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        block_service = Mock(spec=BlockService)
        page_service = Mock(spec=PageService)
        query_service = Mock(spec=QueryService)
        graph_service = Mock(spec=GraphService)

        return {
            "block": block_service,
            "page": page_service,
            "query": query_service,
            "graph": graph_service,
        }

    @pytest.fixture
    def handler(self, mock_services):
        """Create ToolHandler with mock services."""
        return ToolHandler(
            block_service=mock_services["block"],
            page_service=mock_services["page"],
            query_service=mock_services["query"],
            graph_service=mock_services["graph"],
        )

    def test_get_tools_count(self, handler):
        """Test that all tools are defined."""
        tools = handler.get_tools()
        assert len(tools) == 25

    def test_get_tools_have_schemas(self, handler):
        """Test that all tools have input schemas."""
        tools = handler.get_tools()
        for tool in tools:
            assert tool.inputSchema is not None
            assert "type" in tool.inputSchema

    @pytest.mark.asyncio
    async def test_handle_insert_block(self, handler, mock_services):
        """Test insert block tool handler."""
        block = BlockEntity(
            uuid="block-uuid",
            content="Test content",
            page={"name": "Test Page"},
        )
        mock_services["block"].insert = AsyncMock(return_value=block)
        mock_services["block"].format_block_tree = Mock(return_value="- Test content")

        result = await handler.handle_tool(
            ToolName.INSERT_BLOCK,
            {"content": "Test content", "parent_block": "parent-uuid"},
        )

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        mock_services["block"].insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_update_block(self, handler, mock_services):
        """Test update block tool handler."""
        block = BlockEntity(
            uuid="block-uuid",
            content="Updated content",
            page={"name": "Test Page"},
        )
        mock_services["block"].update = AsyncMock(return_value=block)

        result = await handler.handle_tool(
            ToolName.UPDATE_BLOCK,
            {"uuid": "block-uuid", "content": "Updated content"},
        )

        assert len(result) == 1
        assert "Updated" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_delete_block(self, handler, mock_services):
        """Test delete block tool handler."""
        mock_services["block"].delete = AsyncMock(return_value=True)

        result = await handler.handle_tool(ToolName.DELETE_BLOCK, {"uuid": "block-uuid"})

        assert len(result) == 1
        assert "deleted successfully" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_block(self, handler, mock_services):
        """Test get block tool handler."""
        block = BlockEntity(
            uuid="block-uuid",
            content="Block content",
            page={"name": "Test Page"},
        )
        mock_services["block"].get = AsyncMock(return_value=block)
        mock_services["block"].format_block_tree = Mock(return_value="- Block content")

        result = await handler.handle_tool(ToolName.GET_BLOCK, {"uuid": "block-uuid"})

        assert len(result) == 1
        mock_services["block"].get.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_move_block(self, handler, mock_services):
        """Test move block tool handler."""
        block = BlockEntity(
            uuid="source-uuid",
            content="Moved block",
            page={"name": "Test Page"},
            parent={"uuid": "target-uuid"},
        )
        mock_services["block"].move = AsyncMock(return_value=block)

        result = await handler.handle_tool(
            ToolName.MOVE_BLOCK,
            {"uuid": "source-uuid", "target_uuid": "target-uuid"},
        )

        assert len(result) == 1
        assert "Moved" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_insert_batch(self, handler, mock_services):
        """Test insert batch tool handler."""
        blocks = [
            BlockEntity(uuid="block-1", content="Block 1", page={"name": "Page"}),
            BlockEntity(uuid="block-2", content="Block 2", page={"name": "Page"}),
        ]
        mock_services["block"].insert_batch = AsyncMock(return_value=blocks)

        result = await handler.handle_tool(
            ToolName.INSERT_BATCH,
            {"parent": "parent-uuid", "blocks": [{"content": "Block 1"}]},
        )

        assert len(result) == 1
        assert "Inserted 2 blocks" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_blocks(self, handler, mock_services):
        """Test get page blocks tool handler."""
        blocks = [
            BlockEntity(uuid="block-1", content="Block 1", page={"name": "Page"}),
        ]
        mock_services["block"].get_page_blocks = AsyncMock(return_value=blocks)
        mock_services["block"].format_block_tree = Mock(return_value="- Block 1")

        result = await handler.handle_tool(ToolName.GET_PAGE_BLOCKS, {"page_name": "Test Page"})

        assert len(result) == 1
        mock_services["block"].get_page_blocks.assert_called_once_with("Test Page")

    @pytest.mark.asyncio
    async def test_handle_get_page_blocks_no_page(self, handler, mock_services):
        """Test get page blocks without page name raises error."""
        from mcp.shared.exceptions import McpError

        with pytest.raises(McpError, match="page_name is required"):
            await handler.handle_tool(ToolName.GET_PAGE_BLOCKS, {})

    @pytest.mark.asyncio
    async def test_handle_get_current_page_content(self, handler, mock_services):
        """Test get current page content tool handler."""
        blocks = [
            BlockEntity(uuid="block-1", content="Current Block", page={"name": "Page"}),
        ]
        mock_services["block"].get_current_page_blocks = AsyncMock(return_value=blocks)
        mock_services["block"].format_block_tree = Mock(return_value="- Current Block")

        result = await handler.handle_tool(ToolName.GET_CURRENT_PAGE_CONTENT, {})

        assert len(result) == 1
        mock_services["block"].get_current_page_blocks.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_create_page(self, handler, mock_services):
        """Test create page tool handler."""
        page = PageEntity(uuid="page-uuid", name="New Page")
        mock_services["page"].create = AsyncMock(return_value=page)
        mock_services["page"].format_page = Mock(return_value="Page: New Page")

        result = await handler.handle_tool(ToolName.CREATE_PAGE, {"page_name": "New Page"})

        assert len(result) == 1
        mock_services["page"].create.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_get_page(self, handler, mock_services):
        """Test get page tool handler."""
        page = PageEntity(uuid="page-uuid", name="Test Page")
        mock_services["page"].get = AsyncMock(return_value=page)
        mock_services["page"].format_page = Mock(return_value="Page: Test Page")

        result = await handler.handle_tool(ToolName.GET_PAGE, {"page_name": "Test Page"})

        assert len(result) == 1
        mock_services["page"].get.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_delete_page(self, handler, mock_services):
        """Test delete page tool handler."""
        mock_services["page"].delete = AsyncMock(return_value=True)

        result = await handler.handle_tool(ToolName.DELETE_PAGE, {"page_name": "Page to Delete"})

        assert len(result) == 1
        assert "deleted successfully" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_rename_page(self, handler, mock_services):
        """Test rename page tool handler."""
        mock_services["page"].rename = AsyncMock(return_value=True)

        result = await handler.handle_tool(
            ToolName.RENAME_PAGE, {"old_name": "Old", "new_name": "New"}
        )

        assert len(result) == 1
        assert "renamed successfully" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_all_pages(self, handler, mock_services):
        """Test get all pages tool handler."""
        pages = [PageEntity(uuid="page-1", name="Page A")]
        mock_services["page"].get_all = AsyncMock(return_value=pages)
        mock_services["page"].format_pages = Mock(return_value="- Page A")

        result = await handler.handle_tool(ToolName.GET_ALL_PAGES, {})

        assert len(result) == 1
        mock_services["page"].get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_get_current_page(self, handler, mock_services):
        """Test get current page tool handler with page active."""
        page = PageEntity(uuid="page-uuid", name="Current Page")
        mock_services["page"].get_current_page = AsyncMock(return_value=page)
        mock_services["page"].format_page = Mock(return_value="Page: Current Page")

        result = await handler.handle_tool(ToolName.GET_CURRENT_PAGE, {})

        assert len(result) == 1
        mock_services["page"].get_current_page.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_get_current_page_none(self, handler, mock_services):
        """Test get current page tool handler with no active page."""
        mock_services["page"].get_current_page = AsyncMock(return_value=None)

        result = await handler.handle_tool(ToolName.GET_CURRENT_PAGE, {})

        assert len(result) == 1
        assert "No active page" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_current_block(self, handler, mock_services):
        """Test get current block tool handler."""
        block = BlockEntity(
            uuid="block-uuid",
            content="Block content",
            page={"name": "Page"},
        )
        mock_services["block"].get_current_block = AsyncMock(return_value=block)
        mock_services["block"].format_block_tree = Mock(return_value="- Block content")

        result = await handler.handle_tool(ToolName.GET_CURRENT_BLOCK, {})

        assert len(result) == 1
        mock_services["block"].get_current_block.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_edit_block(self, handler, mock_services):
        """Test edit block tool handler."""
        mock_services["block"].edit_block = AsyncMock(return_value=None)

        result = await handler.handle_tool(ToolName.EDIT_BLOCK, {"uuid": "block-uuid"})

        assert len(result) == 1
        assert "edit mode" in result[0].text
        mock_services["block"].edit_block.assert_called_once_with("block-uuid", 0)

    @pytest.mark.asyncio
    async def test_handle_exit_editing_mode(self, handler, mock_services):
        """Test exit editing mode tool handler."""
        mock_services["block"].exit_editing_mode = AsyncMock(return_value=None)

        result = await handler.handle_tool(ToolName.EXIT_EDITING_MODE, {})

        assert len(result) == 1
        assert "Exited editing mode" in result[0].text
        mock_services["block"].exit_editing_mode.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_get_editing_content(self, handler, mock_services):
        """Test get editing content tool handler."""
        mock_services["block"].get_editing_content = AsyncMock(return_value="Some content")

        result = await handler.handle_tool(ToolName.GET_EDITING_CONTENT, {})

        assert len(result) == 1
        assert "Some content" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_simple_query(self, handler, mock_services):
        """Test simple query tool handler."""
        mock_services["query"].simple_query = AsyncMock(return_value=[{"name": "Page"}])
        mock_services["query"].format_results = Mock(return_value="Found 1 results")

        result = await handler.handle_tool(ToolName.SIMPLE_QUERY, {"query": "[[Project]]"})

        assert len(result) == 1
        mock_services["query"].simple_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_advanced_query(self, handler, mock_services):
        """Test advanced query tool handler."""
        mock_services["query"].advanced_query = AsyncMock(return_value=[])
        mock_services["query"].format_results = Mock(return_value="No results")

        query = '[:find (pull ?b [*]) :where [?b :block/marker "TODO"]]'
        result = await handler.handle_tool(ToolName.ADVANCED_QUERY, {"query": query, "inputs": []})

        assert len(result) == 1
        mock_services["query"].advanced_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_get_tasks(self, handler, mock_services):
        """Test get tasks tool handler."""
        mock_services["query"].get_tasks = AsyncMock(return_value=[])
        mock_services["query"].format_results = Mock(return_value="No tasks")

        result = await handler.handle_tool(ToolName.GET_TASKS, {"marker": "TODO", "priority": "A"})

        assert len(result) == 1
        mock_services["query"].get_tasks.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_get_current_graph(self, handler, mock_services):
        """Test get current graph tool handler."""
        graph = GraphEntity(name="test-graph", path="/path/to/graph")
        mock_services["graph"].get_current_graph = AsyncMock(return_value=graph)
        mock_services["graph"].format_graph = Mock(return_value="Graph: test-graph")

        result = await handler.handle_tool(ToolName.GET_CURRENT_GRAPH, {})

        assert len(result) == 1
        mock_services["graph"].get_current_graph.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_get_user_configs(self, handler, mock_services):
        """Test get user configs tool handler."""
        configs = {"preferredLanguage": "en"}
        mock_services["graph"].get_user_configs = AsyncMock(return_value=configs)

        result = await handler.handle_tool(ToolName.GET_USER_CONFIGS, {})

        assert len(result) == 1
        assert "en" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_git_commit(self, handler, mock_services):
        """Test git commit tool handler."""
        mock_services["graph"].git_commit = AsyncMock(return_value=True)

        result = await handler.handle_tool(ToolName.GIT_COMMIT, {"message": "Test commit"})

        assert len(result) == 1
        assert "commit successful" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_git_status(self, handler, mock_services):
        """Test git status tool handler."""
        status = {"modified": ["page.md"], "untracked": []}
        mock_services["graph"].git_status = AsyncMock(return_value=status)
        mock_services["graph"].format_git_status = Mock(return_value="Git Status: modified")

        result = await handler.handle_tool(ToolName.GIT_STATUS, {})

        assert len(result) == 1
        mock_services["graph"].git_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_unknown_tool(self, handler, mock_services):
        """Test unknown tool raises error."""
        from mcp.shared.exceptions import McpError

        with pytest.raises(McpError, match="Unknown tool"):
            await handler.handle_tool("unknown_tool", {})

    @pytest.mark.asyncio
    async def test_handle_tool_exception(self, handler, mock_services):
        """Test that tool exceptions are properly handled."""
        from mcp.shared.exceptions import McpError

        mock_services["block"].insert = AsyncMock(side_effect=Exception("Test error"))

        with pytest.raises(McpError):
            await handler.handle_tool(ToolName.INSERT_BLOCK, {"content": "Test"})


class TestPromptHandler:
    """Test PromptHandler functionality."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services."""
        block_service = Mock(spec=BlockService)
        page_service = Mock(spec=PageService)

        return {"block": block_service, "page": page_service}

    @pytest.fixture
    def handler(self, mock_services):
        """Create PromptHandler with mock services."""
        return PromptHandler(
            block_service=mock_services["block"],
            page_service=mock_services["page"],
        )

    def test_get_prompts_count(self, handler):
        """Test that all prompts are defined."""
        prompts = handler.get_prompts()
        assert len(prompts) == 6

    def test_get_prompts_have_arguments(self, handler):
        """Test that prompts have correct arguments."""
        prompts = handler.get_prompts()

        insert_block = next(p for p in prompts if p.name == "logseq_insert_block")
        assert len(insert_block.arguments) == 2
        assert insert_block.arguments[0].name == "content"
        assert insert_block.arguments[0].required is True

    @pytest.mark.asyncio
    async def test_handle_insert_block_prompt(self, handler, mock_services):
        """Test insert block prompt handler."""
        result = await handler.handle_prompt(
            "logseq_insert_block",
            {"content": "Test block", "parent_block": "parent-uuid"},
        )

        assert result.description is not None
        assert len(result.messages) == 1
        assert "Test block" in result.messages[0].content.text
        assert "parent-uuid" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_handle_insert_block_prompt_no_parent(self, handler, mock_services):
        """Test insert block prompt without parent."""
        result = await handler.handle_prompt("logseq_insert_block", {"content": "Test block"})

        assert "Test block" in result.messages[0].content.text
        # Should not mention parent
        assert "under" not in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_handle_create_page_prompt(self, handler, mock_services):
        """Test create page prompt handler."""
        result = await handler.handle_prompt("logseq_create_page", {"page_name": "New Page"})

        assert "Create page: New Page" in result.description
        assert "New Page" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_handle_get_page_prompt(self, handler, mock_services):
        """Test get page prompt handler."""
        result = await handler.handle_prompt("logseq_get_page", {"page_name": "Test Page"})

        assert "Test Page" in result.description
        assert "Test Page" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_handle_get_current_page_prompt(self, handler, mock_services):
        """Test get current page prompt handler."""
        result = await handler.handle_prompt("logseq_get_current_page", {})

        assert "current page" in result.description.lower()
        assert "current active page" in result.messages[0].content.text.lower()

    @pytest.mark.asyncio
    async def test_handle_get_all_pages_prompt(self, handler, mock_services):
        """Test get all pages prompt handler."""
        result = await handler.handle_prompt("logseq_get_all_pages", {})

        assert "all pages" in result.description.lower()
        assert "all pages" in result.messages[0].content.text.lower()

    @pytest.mark.asyncio
    async def test_handle_simple_query_prompt(self, handler, mock_services):
        """Test simple query prompt handler."""
        result = await handler.handle_prompt("logseq_simple_query", {"query": "[[Project]]"})

        assert "[[Project]]" in result.description
        assert "[[Project]]" in result.messages[0].content.text

    @pytest.mark.asyncio
    async def test_handle_unknown_prompt(self, handler, mock_services):
        """Test unknown prompt raises error."""
        result = await handler.handle_prompt("unknown_prompt", {})

        assert "Error" in result.description

    @pytest.mark.asyncio
    async def test_handle_prompt_exception(self, handler, mock_services):
        """Test that prompt exceptions return error result."""
        # This test verifies error handling works
        # The handler catches exceptions and returns error result
        result = await handler.handle_prompt("logseq_insert_block", None)

        # Should still work with None arguments
        assert result.description is not None
