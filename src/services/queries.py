"""Query operations service."""

from typing import Any

from ..client.logseq import LogseqClient
from ..models.responses import Formatters
from ..models.schemas import AdvancedQueryInput, GetTasksInput, SimpleQueryInput


class QueryService:
    """Service for advanced queries."""

    def __init__(self, client: LogseqClient):
        """Initialize with Logseq client."""
        self.client = client

    async def simple_query(self, input_data: SimpleQueryInput) -> list[Any]:
        """Execute simple query."""
        return self.client.q(input_data.query)

    async def advanced_query(self, input_data: AdvancedQueryInput) -> list[Any]:
        """Execute advanced Datascript query."""
        return self.client.datascript_query(input_data.query, *input_data.inputs)

    async def get_tasks(self, input_data: GetTasksInput) -> list[dict[str, Any]]:
        """Get tasks with optional filters."""
        # Query for all tasks
        query = """
        [:find (pull ?b [*])
         :where
         [?b :block/marker ?m]]
        """

        results = self.client.datascript_query(query)

        # Apply filters
        filtered = results
        if input_data.marker:
            filtered = [r for r in filtered if r.get("marker") == input_data.marker]
        if input_data.priority:
            filtered = [r for r in filtered if r.get("priority") == input_data.priority]

        return filtered

    async def get_blocks_with_property(
        self, property_name: str, value: Any = None
    ) -> list[dict[str, Any]]:
        """Get blocks with specific property."""
        query = f"""
        [:find (pull ?b [*])
         :where
         [?b :block/properties ?p]
         [(get ?p :{property_name}) ?v]
         {f'[(= ?v "{value}")]' if value else ""}]
        ]
        """
        return self.client.datascript_query(query)

    def format_results(self, results: list[Any]) -> str:
        """Format query results as text."""
        return Formatters.format_query_results(results)
