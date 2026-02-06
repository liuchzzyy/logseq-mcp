"""MCP Prompt handlers."""

from typing import Any

from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
)

from ..services.blocks import BlockService
from ..services.pages import PageService


class PromptHandler:
    """Handler for MCP prompts."""

    def __init__(self, block_service: BlockService, page_service: PageService):
        """Initialize with services."""
        self.block_service = block_service
        self.page_service = page_service

    @staticmethod
    def get_prompts() -> list[Prompt]:
        """Get all prompt definitions."""
        return [
            Prompt(
                name="logseq_insert_block",
                description="Create a new block in Logseq",
                arguments=[
                    PromptArgument(name="content", description="Block content", required=True),
                    PromptArgument(
                        name="parent_block",
                        description="Parent block or page name",
                        required=False,
                    ),
                ],
            ),
            Prompt(
                name="logseq_create_page",
                description="Create a new page",
                arguments=[
                    PromptArgument(name="page_name", description="Page name", required=True),
                    PromptArgument(
                        name="properties",
                        description="Page properties as JSON",
                        required=False,
                    ),
                ],
            ),
            Prompt(
                name="logseq_get_page",
                description="Get page details",
                arguments=[
                    PromptArgument(
                        name="page_name", description="Page name or UUID", required=True
                    ),
                ],
            ),
            Prompt(
                name="logseq_get_current_page",
                description="Get current active page",
                arguments=[],
            ),
            Prompt(name="logseq_get_all_pages", description="List all pages", arguments=[]),
            Prompt(
                name="logseq_simple_query",
                description="Run a query",
                arguments=[
                    PromptArgument(name="query", description="Query string", required=True),
                ],
            ),
        ]

    async def handle_prompt(self, name: str, arguments: dict[str, Any] | None) -> GetPromptResult:
        """Handle prompt request."""
        arguments = arguments or {}

        try:
            match name:
                case "logseq_insert_block":
                    content = arguments.get("content", "")
                    parent = arguments.get("parent_block")
                    parent_text = f" under {parent}" if parent else ""
                    prompt_text = f"Please insert block '{content}'{parent_text}"

                    return GetPromptResult(
                        description=f"Create block: {content[:50]}...",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(
                                    type="text",
                                    text=prompt_text,
                                ),
                            )
                        ],
                    )

                case "logseq_create_page":
                    page_name = arguments.get("page_name", "")

                    return GetPromptResult(
                        description=f"Create page: {page_name}",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(
                                    type="text",
                                    text=f"Please create page '{page_name}'",
                                ),
                            )
                        ],
                    )

                case "logseq_get_page":
                    page_name = arguments.get("page_name", "")

                    return GetPromptResult(
                        description=f"Get page: {page_name}",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(
                                    type="text", text=f"Please get page '{page_name}'"
                                ),
                            )
                        ],
                    )

                case "logseq_get_current_page":
                    return GetPromptResult(
                        description="Get current page",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(
                                    type="text",
                                    text="Please get the current active page",
                                ),
                            )
                        ],
                    )

                case "logseq_get_all_pages":
                    return GetPromptResult(
                        description="List all pages",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(
                                    type="text",
                                    text="Please list all pages in the graph",
                                ),
                            )
                        ],
                    )

                case "logseq_simple_query":
                    query = arguments.get("query", "")

                    return GetPromptResult(
                        description=f"Query: {query}",
                        messages=[
                            PromptMessage(
                                role="user",
                                content=TextContent(type="text", text=f"Please run query: {query}"),
                            )
                        ],
                    )

                case _:
                    raise ValueError(f"Unknown prompt: {name}")

        except Exception as e:
            return GetPromptResult(
                description=f"Error: {str(e)}",
                messages=[
                    PromptMessage(role="user", content=TextContent(type="text", text=str(e)))
                ],
            )
