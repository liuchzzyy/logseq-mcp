# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`logseq-mcp` is an MCP (Model Context Protocol) server providing LLM integration with Logseq's knowledge base. It exposes 25 tools and 6 prompts for block/page/query/graph/git operations via the MCP protocol, plus a standalone CLI.

## Common Commands

```bash
# Run tests
uv run python -m pytest tests/
uv run python -m pytest tests/test_services.py -v          # single file
uv run python -m pytest tests/test_models.py::TestInsertBlockInput -v  # single class
uv run python -m pytest tests/ --cov=src --cov-report=html  # with coverage

# Lint & format
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type check
uv run ty check --extra-search-path src src

# CLI (requires LOGSEQ_API_TOKEN in .env or environment)
uv run logseq-mcp --help
uv run logseq-mcp pages list
uv run logseq-mcp serve                   # start MCP server (stdio)
uv run python -m src serve                # equivalent

# Debug with MCP Inspector
npx @modelcontextprotocol/inspector uv --directory . run logseq-mcp
```

## Architecture

Four-layer clean architecture. Upper layers depend on lower layers only.

```
Presentation   → handlers/tools.py (25 MCP tools, match/case routing)
                 handlers/prompts.py (6 MCP prompts)
Application    → services/{blocks,pages,queries,graph}.py (async business logic)
Domain         → models/schemas.py (Pydantic input validation)
                 models/responses.py (Entity classes + Formatters)
                 models/enums.py (ToolName, PageFormat, BlockMarker, Priority)
Infrastructure → client/base.py (BaseAPIClient: retry, auth, error mapping)
                 client/logseq.py (LogseqClient: 30+ Logseq HTTP API methods)
                 config/settings.py (pydantic-settings, env prefix LOGSEQ_)
```

**Orchestration**: `server.py` wires everything — creates client, 4 services, 2 handlers, registers MCP callbacks via `@server.list_tools()` / `@server.call_tool()` / etc.

**CLI**: `client/cli.py` provides argparse-based CLI that reuses the same services directly (bypassing MCP protocol).

## Key Patterns

- **All Logseq API calls** go through `BaseAPIClient._make_request()` as POST to `/api` with body `{"method": "logseq.Editor.xxx", "args": [...]}`. Tenacity retries 3 times with exponential backoff.
- **Tool routing** in `handlers/tools.py` uses Python 3.10 `match/case` on `ToolName` enum values.
- **Input schemas** are Pydantic models with `extra="forbid"`. `model_json_schema()` auto-generates MCP tool schemas.
- **Entity factory**: `BlockEntity.from_api()` / `PageEntity.from_api()` recursively parse API responses.
- **Formatters**: Static methods on `Formatters` class convert entities to human-readable text for MCP responses.
- **Error flow**: Custom exception hierarchy in `utils/errors.py` → `format_error()` converts to `McpError` with appropriate MCP error codes.
- **Config**: Single `LogseqSettings` singleton loaded at import time. Env vars prefixed with `LOGSEQ_`. Priority: CLI args > env vars > .env file > defaults.
- **Version**: Defined once in `pyproject.toml`, read at runtime via `importlib.metadata` in `config/settings.py`.

## Testing

Tests import modules via absolute paths (e.g., `from client.logseq import LogseqClient`) — this works because `conftest.py` adds `src/` to `sys.path`. Services are tested with `Mock(spec=LogseqClient)` and `@pytest.mark.asyncio`. Handlers use `AsyncMock` for service methods.

## Build

- Build system: hatchling. Package name: `mcp-server-logseq`. CLI entry point: `logseq-mcp`.
- `[tool.hatch.build.targets.wheel] packages = ["src"]`
- Python >=3.10 required (match/case syntax).
