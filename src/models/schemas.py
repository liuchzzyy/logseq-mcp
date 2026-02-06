"""Pydantic models for request/response validation."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .enums import PageFormat


class LogseqBaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, populate_by_name=True)


# ==================== Block Models ====================


class InsertBlockInput(LogseqBaseModel):
    """Input for inserting a block."""

    parent_block: str | None = Field(default=None, description="Parent block UUID or page name")
    content: str = Field(..., description="Block content")
    is_page_block: bool = Field(default=False, description="Create as page-level block")
    before: bool = Field(default=False, description="Insert before parent instead of after")
    custom_uuid: str | None = Field(default=None, description="Custom UUID for the block")
    properties: dict[str, Any] | None = Field(default=None, description="Block properties")

    @field_validator("parent_block", "custom_uuid")
    @classmethod
    def clean_block_refs(cls, v: str | None) -> str | None:
        """Clean ((uuid)) format to uuid."""
        if isinstance(v, str) and v.startswith("((") and v.endswith("))"):
            return v[2:-2]
        return v


class UpdateBlockInput(LogseqBaseModel):
    """Input for updating a block."""

    uuid: str = Field(..., description="Block UUID")
    content: str = Field(..., description="New content")
    properties: dict[str, Any] | None = Field(default=None, description="Updated properties")


class MoveBlockInput(LogseqBaseModel):
    """Input for moving a block."""

    uuid: str = Field(..., description="Block UUID to move")
    target_uuid: str = Field(..., description="Target block UUID")
    as_child: bool = Field(default=False, description="Move as child of target")


class DeleteBlockInput(LogseqBaseModel):
    """Input for deleting a block."""

    uuid: str = Field(..., description="Block UUID to delete")


class GetBlockInput(LogseqBaseModel):
    """Input for getting a block."""

    uuid: str = Field(..., description="Block UUID")


class BatchBlockInput(LogseqBaseModel):
    """Input for batch block operations."""

    parent: str = Field(..., description="Parent block or page")
    blocks: list[dict[str, Any]] = Field(..., description="List of block data")


# ==================== Page Models ====================


class CreatePageInput(LogseqBaseModel):
    """Input for creating a page."""

    page_name: str = Field(..., description="Page name")
    properties: dict[str, Any] | None = Field(default=None, description="Page properties")
    journal: bool = Field(default=False, description="Create as journal page")
    format: PageFormat = Field(default=PageFormat.MARKDOWN, description="Page format")
    create_first_block: bool = Field(default=True, description="Create initial empty block")

    @field_validator("properties", mode="before")
    @classmethod
    def parse_properties(cls, v):
        """Parse properties from JSON string if needed."""
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format for properties")
        return v or {}


class GetPageInput(LogseqBaseModel):
    """Input for getting a page."""

    page_name: str = Field(..., description="Page name or UUID")
    include_children: bool = Field(default=False, description="Include child blocks")


class DeletePageInput(LogseqBaseModel):
    """Input for deleting a page."""

    page_name: str = Field(..., description="Page name to delete")


class RenamePageInput(LogseqBaseModel):
    """Input for renaming a page."""

    old_name: str = Field(..., description="Current page name")
    new_name: str = Field(..., description="New page name")


class GetAllPagesInput(LogseqBaseModel):
    """Input for listing all pages."""

    repo: str | None = Field(default=None, description="Repository name (optional)")


# ==================== Editor Models ====================


class EditBlockInput(LogseqBaseModel):
    """Input for entering edit mode."""

    uuid: str = Field(..., description="Block UUID")
    pos: int = Field(default=0, description="Cursor position", ge=0, le=10000)


class ExitEditingInput(LogseqBaseModel):
    """Input for exiting edit mode."""

    select_block: bool = Field(default=False, description="Keep block selected")


# ==================== Query Models ====================


class SimpleQueryInput(LogseqBaseModel):
    """Input for simple query."""

    query: str = Field(
        ...,
        description="Query string (e.g., '[[tag]]')",
        examples=["[[Project]]", "#important"],
    )


class AdvancedQueryInput(LogseqBaseModel):
    """Input for advanced Datascript query."""

    query: str = Field(..., description="Datascript query")
    inputs: list[Any] = Field(default_factory=list, description="Query inputs")


class GetTasksInput(LogseqBaseModel):
    """Input for getting tasks."""

    marker: str | None = Field(
        default=None, description="Filter by marker (TODO, DOING, DONE, etc.)"
    )
    priority: str | None = Field(default=None, description="Filter by priority (A, B, C)")


# ==================== Graph Models ====================


class GitCommitInput(LogseqBaseModel):
    """Input for git commit."""

    message: str = Field(..., description="Commit message")


class EmptyInput(LogseqBaseModel):
    """Empty input for no-argument operations."""

    pass
