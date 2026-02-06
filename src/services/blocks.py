"""Block operations service."""

from typing import Any, cast

from ..client.logseq import LogseqClient
from ..models.responses import BlockEntity, Formatters
from ..models.schemas import (
    BatchBlockInput,
    DeleteBlockInput,
    GetBlockInput,
    InsertBlockInput,
    MoveBlockInput,
    UpdateBlockInput,
)


class BlockService:
    """Service for block operations."""

    def __init__(self, client: LogseqClient):
        """Initialize with Logseq client."""
        self.client = client

    async def insert(self, input_data: InsertBlockInput) -> BlockEntity:
        """Insert a new block."""
        options = {
            "isPageBlock": input_data.is_page_block,
            "before": input_data.before,
            "customUUID": input_data.custom_uuid,
            "properties": input_data.properties,
        }

        result = self.client.insert_block(
            input_data.parent_block,
            input_data.content,
            **{k: v for k, v in options.items() if v is not None},
        )

        return BlockEntity.from_api(result)

    async def update(self, input_data: UpdateBlockInput) -> BlockEntity | bool:
        """Update block content."""
        options = {}
        if input_data.properties:
            options["properties"] = input_data.properties

        result = self.client.update_block(input_data.uuid, input_data.content, **options)
        if not isinstance(result, dict):
            return True
        return BlockEntity.from_api(result)

    async def delete(self, input_data: DeleteBlockInput) -> bool:
        """Delete a block."""
        self.client.delete_block(input_data.uuid)
        return True

    async def get(self, input_data: GetBlockInput) -> BlockEntity:
        """Get block by UUID."""
        result = self.client.get_block(input_data.uuid)
        return BlockEntity.from_api(result)

    async def move(self, input_data: MoveBlockInput) -> BlockEntity | bool:
        """Move block to new location."""
        result = self.client.move_block(
            input_data.uuid, input_data.target_uuid, children=input_data.as_child
        )
        if not isinstance(result, dict):
            return True
        return BlockEntity.from_api(result)

    async def insert_batch(self, input_data: BatchBlockInput) -> list[BlockEntity] | bool:
        """Insert multiple blocks."""
        raw_results: Any = self.client.insert_batch_blocks(input_data.parent, input_data.blocks)
        if not isinstance(raw_results, list):
            return True
        dict_results = [r for r in raw_results if isinstance(r, dict)]
        typed_results = cast(list[dict[str, Any]], dict_results)
        return [BlockEntity.from_api(r) for r in typed_results]

    async def get_page_blocks(self, page_name: str) -> list[BlockEntity]:
        """Get all blocks in page."""
        raw_results: Any = self.client.get_page_blocks_tree(page_name)
        if not isinstance(raw_results, list):
            return []
        dict_results = [r for r in raw_results if isinstance(r, dict)]
        if len(dict_results) != len(raw_results):
            return []
        typed_results = cast(list[dict[str, Any]], dict_results)
        return [BlockEntity.from_api(r) for r in typed_results]

    async def get_current_page_blocks(self) -> list[BlockEntity]:
        """Get current page blocks."""
        raw_results: Any = self.client.get_current_page_blocks_tree()
        if not isinstance(raw_results, list):
            return []
        dict_results = [r for r in raw_results if isinstance(r, dict)]
        if len(dict_results) != len(raw_results):
            return []
        typed_results = cast(list[dict[str, Any]], dict_results)
        return [BlockEntity.from_api(r) for r in typed_results]

    async def get_current_block(self) -> BlockEntity | None:
        """Get current focused block."""
        result = self.client.get_current_block()
        if isinstance(result, dict):
            return BlockEntity.from_api(result)
        return None

    def format_block_tree(self, blocks: list[BlockEntity]) -> str:
        """Format blocks as readable text."""
        return Formatters.format_blocks(blocks)
