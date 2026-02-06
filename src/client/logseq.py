"""Logseq HTTP API client implementation."""

from typing import Any

from .base import BaseAPIClient


class LogseqClient(BaseAPIClient):
    """Client for Logseq HTTP API."""

    def health_check(self) -> bool:
        """Check if Logseq API is accessible."""
        try:
            self.get_current_graph()
            return True
        except Exception:
            return False

    # ==================== Editor API ====================

    def insert_block(self, parent: str | None, content: str, **options) -> dict[str, Any]:
        """Insert a new block."""
        return self._make_request("logseq.Editor.insertBlock", [parent, content, options])

    def update_block(self, uuid: str, content: str, **options) -> dict[str, Any]:
        """Update block content."""
        return self._make_request("logseq.Editor.updateBlock", [uuid, content, options])

    def delete_block(self, uuid: str) -> None:
        """Delete a block."""
        self._make_request("logseq.Editor.removeBlock", [uuid])

    def get_block(self, uuid: str) -> dict[str, Any]:
        """Get block by UUID."""
        return self._make_request("logseq.Editor.getBlock", [uuid])

    def move_block(self, uuid: str, target_uuid: str, **options) -> dict[str, Any]:
        """Move block to new location."""
        return self._make_request("logseq.Editor.moveBlock", [uuid, target_uuid, options])

    def insert_batch_blocks(
        self, parent: str, blocks: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Insert multiple blocks at once."""
        return self._make_request("logseq.Editor.insertBatchBlock", [parent, blocks])

    def get_page_blocks_tree(self, page_name: str) -> list[dict[str, Any]]:
        """Get all blocks in page as tree."""
        return self._make_request("logseq.Editor.getPageBlocksTree", [page_name])

    def get_current_page_blocks_tree(self) -> dict[str, Any]:
        """Get current page's block tree."""
        return self._make_request("logseq.Editor.getCurrentPageBlocksTree", [])

    def get_current_block(self) -> dict[str, Any] | None:
        """Get currently focused block."""
        return self._make_request("logseq.Editor.getCurrentBlock", [])

    def get_current_page(self) -> dict[str, Any]:
        """Get current active page."""
        return self._make_request("logseq.Editor.getCurrentPage", [])

    def edit_block(self, uuid: str, pos: int = 0) -> None:
        """Enter edit mode for block."""
        self._make_request("logseq.Editor.editBlock", [uuid, {"pos": pos}])

    def exit_editing_mode(self, select_block: bool = False) -> None:
        """Exit edit mode."""
        self._make_request("logseq.Editor.exitEditingMode", [select_block])

    def get_editing_block_content(self) -> dict[str, Any]:
        """Get content of block being edited."""
        return self._make_request("logseq.Editor.getEditingBlockContent", [])

    # ==================== Page API ====================

    def create_page(
        self, name: str, properties: dict[str, Any] | None = None, **options
    ) -> dict[str, Any]:
        """Create new page."""
        return self._make_request("logseq.Editor.createPage", [name, properties or {}, options])

    def get_page(self, identifier: str, include_children: bool = False) -> dict[str, Any]:
        """Get page by name or UUID."""
        return self._make_request(
            "logseq.Editor.getPage", [identifier, {"includeChildren": include_children}]
        )

    def get_all_pages(self, repo: str | None = None) -> list[dict[str, Any]]:
        """Get all pages in graph."""
        args = [repo] if repo else []
        return self._make_request("logseq.Editor.getAllPages", args)

    def delete_page(self, name: str) -> None:
        """Delete page by name."""
        self._make_request("logseq.Editor.deletePage", [name])

    def rename_page(self, old_name: str, new_name: str) -> None:
        """Rename page."""
        self._make_request("logseq.Editor.renamePage", [old_name, new_name])

    # ==================== Query API ====================

    def q(self, query: str, *inputs: Any) -> list[Any]:
        """Execute simple query."""
        return self._make_request("logseq.DB.q", [query, *inputs])

    def datascript_query(self, query: str, *inputs: Any) -> list[Any]:
        """Execute advanced Datascript query."""
        return self._make_request("logseq.DB.datascriptQuery", [query, *inputs])

    # ==================== App API ====================

    def get_current_graph(self) -> dict[str, Any]:
        """Get current graph info."""
        return self._make_request("logseq.App.getCurrentGraph", [])

    def get_user_configs(self) -> dict[str, Any]:
        """Get user configurations."""
        return self._make_request("logseq.App.getUserConfigs", [])

    def show_msg(self, content: str, status: str = "success") -> None:
        """Show UI message."""
        self._make_request("logseq.UI.showMsg", [content, status])

    # ==================== Git API ====================

    def git_commit(self, message: str) -> None:
        """Execute git commit."""
        self._make_request("logseq.Git.commit", [message])

    def git_status(self) -> dict[str, Any]:
        """Get git status."""
        return self._make_request("logseq.Git.status", [])
