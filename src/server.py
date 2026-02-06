"""MCP Server entry point with new architecture."""

import asyncio
from collections.abc import Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Prompt, TextContent, Tool

from .client.logseq import LogseqClient
from .config.settings import settings
from .handlers.prompts import PromptHandler
from .handlers.tools import ToolHandler
from .services.blocks import BlockService
from .services.graph import GraphService
from .services.pages import PageService
from .services.queries import QueryService


async def serve() -> None:
    """Run the Logseq MCP server."""
    # Initialize server
    server = Server(settings.server_name)

    # Initialize infrastructure
    client = LogseqClient(
        base_url=settings.api_url,
        api_key=settings.api_token,
        timeout=settings.api_timeout,
        max_retries=settings.api_max_retries,
    )

    # Initialize services
    block_service = BlockService(client)
    page_service = PageService(client)
    query_service = QueryService(client)
    graph_service = GraphService(client)

    # Initialize handlers
    tool_handler = ToolHandler(
        block_service=block_service,
        page_service=page_service,
        query_service=query_service,
        graph_service=graph_service,
    )

    prompt_handler = PromptHandler(block_service=block_service, page_service=page_service)

    # Register tools
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return tool_handler.get_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
        return await tool_handler.handle_tool(name, arguments)

    # Register prompts
    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        return prompt_handler.get_prompts()

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict | None):
        # Preserve precise return type from handler (GetPromptResult)
        return await prompt_handler.handle_prompt(name, arguments)

    # Run server
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)


if __name__ == "__main__":
    asyncio.run(serve())
