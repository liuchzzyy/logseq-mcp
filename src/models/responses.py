"""Response formatting utilities."""

from typing import Any

from pydantic import BaseModel


class BlockEntity(BaseModel):
    """Block data model."""

    uuid: str
    content: str
    page: dict[str, Any] | int = {}
    parent: dict[str, Any] | int | None = None
    children: list["BlockEntity"] = []
    properties: dict[str, Any] = {}
    marker: str | None = None
    priority: str | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "BlockEntity":
        """Create from API response."""
        raw_children = data.get("children", [])
        children = [
            cls.from_api(c) for c in raw_children if isinstance(c, dict)
        ]
        return cls(
            uuid=data.get("uuid", ""),
            content=data.get("content", ""),
            page=data.get("page", {}),
            parent=data.get("parent"),
            children=children,
            properties=data.get("properties", {}),
            marker=data.get("marker"),
            priority=data.get("priority"),
        )


class PageEntity(BaseModel):
    """Page data model."""

    uuid: str
    name: str
    original_name: str | None = None
    journal_day: int | None = None
    properties: dict[str, Any] = {}
    properties_text_values: dict[str, str] = {}
    updated_at: str | int | None = None
    created_at: str | int | None = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "PageEntity":
        """Create from API response."""
        return cls(
            uuid=data.get("uuid", ""),
            name=data.get("name", ""),
            original_name=data.get("originalName"),
            journal_day=data.get("journalDay"),
            properties=data.get("properties", {}),
            properties_text_values=data.get("propertiesTextValues", {}),
            updated_at=data.get("updatedAt"),
            created_at=data.get("createdAt"),
        )


class GraphEntity(BaseModel):
    """Graph data model."""

    name: str
    path: str
    url: str | None = None
    version: str | None = None


class Formatters:
    """Text formatting utilities for MCP responses."""

    @staticmethod
    def format_block(block: BlockEntity, level: int = 0) -> str:
        """Format single block as text."""
        indent = "  " * level
        lines = [f"{indent}- {block.content}"]

        if block.properties:
            for key, value in block.properties.items():
                lines.append(f"{indent}  {key}:: {value}")

        for child in block.children:
            lines.append(Formatters.format_block(child, level + 1))

        return "\n".join(lines)

    @staticmethod
    def format_blocks(blocks: list[BlockEntity]) -> str:
        """Format list of blocks as text."""
        return "\n".join(Formatters.format_block(b) for b in blocks)

    @staticmethod
    def format_page(page: PageEntity) -> str:
        """Format page info as text."""
        lines = [
            f"Page: {page.name}",
            f"UUID: {page.uuid}",
        ]

        if page.journal_day:
            lines.append(f"Journal Day: {page.journal_day}")

        if page.properties_text_values:
            lines.append("Properties:")
            for key, value in page.properties_text_values.items():
                lines.append(f"  {key}:: {value}")

        return "\n".join(lines)

    @staticmethod
    def format_pages(pages: list[PageEntity]) -> str:
        """Format list of pages as text."""
        sorted_pages = sorted(pages, key=lambda p: p.name)
        return "\n".join(f"- {p.name} (UUID: {p.uuid})" for p in sorted_pages)

    @staticmethod
    def format_graph(graph: GraphEntity) -> str:
        """Format graph info as text."""
        lines = [
            f"Graph: {graph.name}",
            f"Path: {graph.path}",
        ]
        if graph.url:
            lines.append(f"URL: {graph.url}")
        if graph.version:
            lines.append(f"Version: {graph.version}")
        return "\n".join(lines)

    @staticmethod
    def format_query_results(results: list[Any]) -> str:
        """Format query results as text."""
        if not results:
            return "No results found."

        lines = [f"Found {len(results)} results:"]
        for i, result in enumerate(results, 1):
            if isinstance(result, dict) and "content" in result:
                lines.append(f"{i}. {result.get('content', str(result))}")
            else:
                lines.append(f"{i}. {str(result)}")
        return "\n".join(lines)

    @staticmethod
    def format_git_status(status: str) -> str:
        """Format git status as text."""
        return f"Git Status:\n{status}"

    @staticmethod
    def format_success(message: str) -> str:
        """Format success message."""
        return f"✓ {message}"

    @staticmethod
    def format_error(error: str) -> str:
        """Format error message."""
        return f"✗ Error: {error}"
