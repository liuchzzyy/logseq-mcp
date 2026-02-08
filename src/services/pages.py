"""Page operations service."""

from ..client.logseq import LogseqClient
from ..models.responses import Formatters, PageEntity
from ..models.schemas import (
    CreatePageInput,
    DeletePageInput,
    GetAllPagesInput,
    GetPageInput,
    RenamePageInput,
)


class PageService:
    """Service for page operations."""

    def __init__(self, client: LogseqClient):
        """Initialize with Logseq client."""
        self.client = client

    async def create(self, input_data: CreatePageInput) -> PageEntity:
        """Create new page."""
        options = {
            "journal": input_data.journal,
            "format": input_data.format.value,
            "createFirstBlock": input_data.create_first_block,
        }

        result = await self.client.create_page(
            input_data.page_name, input_data.properties or {}, **options
        )
        return PageEntity.from_api(result)

    async def get(self, input_data: GetPageInput) -> PageEntity:
        """Get page by name or UUID."""
        result = await self.client.get_page(
            input_data.page_name, include_children=input_data.include_children
        )
        return PageEntity.from_api(result)

    async def get_all(self, input_data: GetAllPagesInput) -> list[PageEntity]:
        """Get all pages."""
        results = await self.client.get_all_pages(input_data.repo)
        return [PageEntity.from_api(r) for r in results]

    async def get_current_page(self) -> PageEntity | None:
        """Get current active page."""
        result = await self.client.get_current_page()
        if isinstance(result, dict):
            return PageEntity.from_api(result)
        return None

    async def delete(self, input_data: DeletePageInput) -> bool:
        """Delete page."""
        await self.client.delete_page(input_data.page_name)
        return True

    async def rename(self, input_data: RenamePageInput) -> bool:
        """Rename page."""
        await self.client.rename_page(input_data.old_name, input_data.new_name)
        return True

    def format_page(self, page: PageEntity) -> str:
        """Format page as readable text."""
        return Formatters.format_page(page)

    def format_pages(self, pages: list[PageEntity]) -> str:
        """Format pages list as readable text."""
        return Formatters.format_pages(pages)
