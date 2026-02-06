"""Custom exceptions and error handling."""

from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS, ErrorData


class LogseqError(Exception):
    """Base exception for Logseq operations."""

    pass


class AuthenticationError(LogseqError):
    """API authentication failed."""

    pass


class ConnectionError(LogseqError):
    """Failed to connect to Logseq API."""

    pass


class NotFoundError(LogseqError):
    """Resource not found."""

    pass


class APIError(LogseqError):
    """API request failed."""

    pass


class ValidationError(LogseqError):
    """Input validation failed."""

    pass


def format_error(e: Exception) -> McpError:
    """Convert exception to MCP error."""
    if isinstance(e, AuthenticationError):
        return McpError(ErrorData(code=INTERNAL_ERROR, message=f"Authentication failed: {e!s}"))
    elif isinstance(e, ConnectionError):
        return McpError(ErrorData(code=INTERNAL_ERROR, message=f"Connection failed: {e!s}"))
    elif isinstance(e, NotFoundError):
        return McpError(ErrorData(code=INVALID_PARAMS, message=f"Not found: {e!s}"))
    elif isinstance(e, ValidationError):
        return McpError(ErrorData(code=INVALID_PARAMS, message=f"Validation error: {e!s}"))
    elif isinstance(e, APIError):
        return McpError(ErrorData(code=INTERNAL_ERROR, message=f"API error: {e!s}"))
    else:
        return McpError(ErrorData(code=INTERNAL_ERROR, message=f"Unexpected error: {e!s}"))
