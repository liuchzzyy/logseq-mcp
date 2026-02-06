"""MCP Tool handlers."""

import json
from collections.abc import Sequence
from typing import Any

from mcp.types import TextContent, Tool

from ..models.enums import ToolName
from ..models.responses import BlockEntity
from ..models.schemas import (
    AdvancedQueryInput,
    BatchBlockInput,
    CreatePageInput,
    DeleteBlockInput,
    DeletePageInput,
    EditBlockInput,
    EmptyInput,
    ExitEditingInput,
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
from ..services.blocks import BlockService
from ..services.graph import GraphService
from ..services.pages import PageService
from ..services.queries import QueryService


class ToolHandler:
    """Handler for MCP tool calls."""

    def __init__(
        self,
        block_service: BlockService,
        page_service: PageService,
        query_service: QueryService,
        graph_service: GraphService,
    ):
        """Initialize with services."""
        self.block_service = block_service
        self.page_service = page_service
        self.query_service = query_service
        self.graph_service = graph_service

    @staticmethod
    def get_tools() -> list[Tool]:
        """Get all tool definitions."""
        return [
            # Block tools
            Tool(
                name=ToolName.INSERT_BLOCK,
                description="Insert a new block in Logseq",
                inputSchema=InsertBlockInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.UPDATE_BLOCK,
                description="Update an existing block",
                inputSchema=UpdateBlockInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.DELETE_BLOCK,
                description="Delete a block",
                inputSchema=DeleteBlockInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.GET_BLOCK,
                description="Get block details by UUID",
                inputSchema=GetBlockInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.MOVE_BLOCK,
                description="Move block to another location",
                inputSchema=MoveBlockInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.INSERT_BATCH,
                description="Insert multiple blocks at once",
                inputSchema=BatchBlockInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.GET_PAGE_BLOCKS,
                description="Get all blocks in a page",
                inputSchema=GetPageInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.GET_CURRENT_PAGE_CONTENT,
                description="Get current page block tree",
                inputSchema=EmptyInput.model_json_schema(),
            ),
            # Page tools
            Tool(
                name=ToolName.CREATE_PAGE,
                description="Create a new page",
                inputSchema=CreatePageInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.GET_PAGE,
                description="Get page details",
                inputSchema=GetPageInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.DELETE_PAGE,
                description="Delete a page",
                inputSchema=DeletePageInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.RENAME_PAGE,
                description="Rename a page",
                inputSchema=RenamePageInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.GET_ALL_PAGES,
                description="List all pages",
                inputSchema=GetAllPagesInput.model_json_schema(),
            ),
            # Editor tools
            Tool(
                name=ToolName.GET_CURRENT_PAGE,
                description="Get current active page",
                inputSchema=EmptyInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.GET_CURRENT_BLOCK,
                description="Get currently focused block",
                inputSchema=EmptyInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.EDIT_BLOCK,
                description="Enter edit mode for block",
                inputSchema=EditBlockInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.EXIT_EDITING_MODE,
                description="Exit edit mode",
                inputSchema=ExitEditingInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.GET_EDITING_CONTENT,
                description="Get content of block being edited",
                inputSchema=EmptyInput.model_json_schema(),
            ),
            # Query tools
            Tool(
                name=ToolName.SIMPLE_QUERY,
                description="Run a simple Logseq query",
                inputSchema=SimpleQueryInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.ADVANCED_QUERY,
                description="Run an advanced Datascript query",
                inputSchema=AdvancedQueryInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.GET_TASKS,
                description="Get all tasks with optional filters",
                inputSchema=GetTasksInput.model_json_schema(),
            ),
            # Graph tools
            Tool(
                name=ToolName.GET_CURRENT_GRAPH,
                description="Get current graph information",
                inputSchema=EmptyInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.GET_USER_CONFIGS,
                description="Get user configurations",
                inputSchema=EmptyInput.model_json_schema(),
            ),
            # Git tools
            Tool(
                name=ToolName.GIT_COMMIT,
                description="Execute git commit",
                inputSchema=GitCommitInput.model_json_schema(),
            ),
            Tool(
                name=ToolName.GIT_STATUS,
                description="Get git status",
                inputSchema=EmptyInput.model_json_schema(),
            ),
        ]

    async def handle_tool(self, name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
        """Handle tool call."""
        try:
            match name:
                # Block operations
                case ToolName.INSERT_BLOCK:
                    result = await self.block_service.insert(InsertBlockInput(**arguments))
                    if isinstance(result, BlockEntity):
                        text = self.block_service.format_block_tree([result])
                    else:
                        text = "Block inserted successfully"

                case ToolName.UPDATE_BLOCK:
                    result = await self.block_service.update(UpdateBlockInput(**arguments))
                    if isinstance(result, BlockEntity):
                        text = f"Updated block: {result.content[:100]}"
                    else:
                        text = "Block updated successfully"

                case ToolName.DELETE_BLOCK:
                    await self.block_service.delete(DeleteBlockInput(**arguments))
                    text = "Block deleted successfully"

                case ToolName.GET_BLOCK:
                    result = await self.block_service.get(GetBlockInput(**arguments))
                    text = self.block_service.format_block_tree([result])

                case ToolName.MOVE_BLOCK:
                    result = await self.block_service.move(MoveBlockInput(**arguments))
                    if isinstance(result, BlockEntity):
                        text = f"Moved block to: {result.parent}"
                    else:
                        text = "Block moved successfully"

                case ToolName.INSERT_BATCH:
                    results = await self.block_service.insert_batch(BatchBlockInput(**arguments))
                    if isinstance(results, list):
                        text = f"Inserted {len(results)} blocks"
                    else:
                        text = "Batch insert completed successfully"

                case ToolName.GET_PAGE_BLOCKS:
                    page_name = arguments.get("page_name")
                    if page_name is None:
                        raise ValueError("page_name is required for GET_PAGE_BLOCKS")
                    results = await self.block_service.get_page_blocks(page_name)
                    text = self.block_service.format_block_tree(results)

                case ToolName.GET_CURRENT_PAGE_CONTENT:
                    results = await self.block_service.get_current_page_blocks()
                    text = self.block_service.format_block_tree(results)

                # Page operations
                case ToolName.CREATE_PAGE:
                    result = await self.page_service.create(CreatePageInput(**arguments))
                    text = self.page_service.format_page(result)

                case ToolName.GET_PAGE:
                    result = await self.page_service.get(GetPageInput(**arguments))
                    text = self.page_service.format_page(result)

                case ToolName.DELETE_PAGE:
                    await self.page_service.delete(DeletePageInput(**arguments))
                    text = "Page deleted successfully"

                case ToolName.RENAME_PAGE:
                    await self.page_service.rename(RenamePageInput(**arguments))
                    text = "Page renamed successfully"

                case ToolName.GET_ALL_PAGES:
                    results = await self.page_service.get_all(GetAllPagesInput(**arguments))
                    text = self.page_service.format_pages(results)

                # Editor operations
                case ToolName.GET_CURRENT_PAGE:
                    result = await self.page_service.get_current_page()
                    if result:
                        text = self.page_service.format_page(result)
                    else:
                        text = "No active page"

                case ToolName.GET_CURRENT_BLOCK:
                    result = await self.block_service.get_current_block()
                    if result:
                        text = self.block_service.format_block_tree([result])
                    else:
                        text = "No block selected"

                case ToolName.EDIT_BLOCK:
                    params = EditBlockInput(**arguments)
                    await self.block_service.edit_block(params.uuid, params.pos)
                    text = f"Entered edit mode for block {params.uuid}"

                case ToolName.EXIT_EDITING_MODE:
                    params = ExitEditingInput(**arguments)
                    await self.block_service.exit_editing_mode(params.select_block)
                    text = "Exited editing mode"

                case ToolName.GET_EDITING_CONTENT:
                    result = await self.block_service.get_editing_content()
                    text = str(result) if result else "No content being edited"

                # Query operations
                case ToolName.SIMPLE_QUERY:
                    results = await self.query_service.simple_query(SimpleQueryInput(**arguments))
                    text = self.query_service.format_results(results)

                case ToolName.ADVANCED_QUERY:
                    results = await self.query_service.advanced_query(
                        AdvancedQueryInput(**arguments)
                    )
                    text = self.query_service.format_results(results)

                case ToolName.GET_TASKS:
                    results = await self.query_service.get_tasks(GetTasksInput(**arguments))
                    text = self.query_service.format_results(results)

                # Graph operations
                case ToolName.GET_CURRENT_GRAPH:
                    result = await self.graph_service.get_current_graph(EmptyInput())
                    text = self.graph_service.format_graph(result)

                case ToolName.GET_USER_CONFIGS:
                    result = await self.graph_service.get_user_configs(EmptyInput())
                    text = json.dumps(result, indent=2)

                # Git operations
                case ToolName.GIT_COMMIT:
                    await self.graph_service.git_commit(GitCommitInput(**arguments))
                    text = "Git commit successful"

                case ToolName.GIT_STATUS:
                    result = await self.graph_service.git_status(EmptyInput())
                    if isinstance(result, dict):
                        text = json.dumps(result, indent=2)
                    else:
                        text = self.graph_service.format_git_status(result)

                case _:
                    raise ValueError(f"Unknown tool: {name}")

            return [TextContent(type="text", text=text)]

        except Exception as e:
            from ..utils.errors import format_error

            raise format_error(e)
