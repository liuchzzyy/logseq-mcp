"""Graph operations service."""

from typing import Any

from ..client.logseq import LogseqClient
from ..models.responses import Formatters, GraphEntity
from ..models.schemas import EmptyInput, GitCommitInput


class GraphService:
    """Service for graph operations."""

    def __init__(self, client: LogseqClient):
        """Initialize with Logseq client."""
        self.client = client

    async def get_current_graph(self, _: EmptyInput) -> GraphEntity:
        """Get current graph info."""
        result = self.client.get_current_graph()
        return GraphEntity(**result)

    async def get_user_configs(self, _: EmptyInput) -> dict[str, Any]:
        """Get user configurations."""
        return self.client.get_user_configs()

    async def git_commit(self, input_data: GitCommitInput) -> bool:
        """Execute git commit."""
        self.client.git_commit(input_data.message)
        return True

    async def git_status(self, _: EmptyInput) -> str | dict[str, Any]:
        """Get git status."""
        result = self.client.git_status()
        if isinstance(result, dict) and "error" in result:
            return result
        if isinstance(result, str):
            return result
        return dict(result) if result else {"status": "ok"}

    def format_graph(self, graph: GraphEntity) -> str:
        """Format graph info as text."""
        return Formatters.format_graph(graph)

    def format_git_status(self, status: str) -> str:
        """Format git status as text."""
        return Formatters.format_git_status(status)
