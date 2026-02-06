"""Enumeration definitions for Logseq MCP Server."""

from enum import Enum


class ToolName(str, Enum):
    """All MCP tool names."""

    # Block operations
    INSERT_BLOCK = "logseq_insert_block"
    UPDATE_BLOCK = "logseq_update_block"
    DELETE_BLOCK = "logseq_delete_block"
    GET_BLOCK = "logseq_get_block"
    MOVE_BLOCK = "logseq_move_block"
    INSERT_BATCH = "logseq_insert_batch"
    GET_PAGE_BLOCKS = "logseq_get_page_blocks"
    GET_CURRENT_PAGE_CONTENT = "logseq_get_current_page_content"

    # Page operations
    CREATE_PAGE = "logseq_create_page"
    GET_PAGE = "logseq_get_page"
    DELETE_PAGE = "logseq_delete_page"
    RENAME_PAGE = "logseq_rename_page"
    GET_ALL_PAGES = "logseq_get_all_pages"

    # Editor operations
    GET_CURRENT_PAGE = "logseq_get_current_page"
    GET_CURRENT_BLOCK = "logseq_get_current_block"
    EDIT_BLOCK = "logseq_edit_block"
    EXIT_EDITING_MODE = "logseq_exit_editing_mode"
    GET_EDITING_CONTENT = "logseq_get_editing_content"

    # Query operations
    SIMPLE_QUERY = "logseq_simple_query"
    ADVANCED_QUERY = "logseq_advanced_query"
    GET_TASKS = "logseq_get_tasks"

    # Graph operations
    GET_CURRENT_GRAPH = "logseq_get_current_graph"
    GET_USER_CONFIGS = "logseq_get_user_configs"

    # Git operations
    GIT_COMMIT = "logseq_git_commit"
    GIT_STATUS = "logseq_git_status"


class PageFormat(str, Enum):
    """Page format options."""

    MARKDOWN = "markdown"
    ORG = "org"


class BlockMarker(str, Enum):
    """Task marker types."""

    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"
    NOW = "NOW"
    LATER = "LATER"
    WAITING = "WAITING"
    CANCELLED = "CANCELLED"


class Priority(str, Enum):
    """Task priority levels."""

    HIGH = "A"
    MEDIUM = "B"
    LOW = "C"
