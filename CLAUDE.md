# CLAUDE.md

Guidance for working in this repo.

## Overview

`logseq-mcp` is an MCP server + CLI for Logseq. It exposes tools/prompts over MCP and reuses the same services for CLI.

## Common Commands

```bash
# Tests
uv run python -m pytest tests/
uv run python -m pytest tests/test_services.py -v
uv run python -m pytest tests/ --cov=src --cov-report=html

# Lint/format
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Type check
uv run ty check --extra-search-path . src

# CLI (requires LOGSEQ_API_TOKEN)
uv run logseq-mcp --help
uv run logseq-mcp pages list
uv run logseq-mcp graph git-support

# MCP server (stdio)
uv run logseq-mcp serve
```

## Architecture (Short)

- Presentation: `src/handlers/*` (tools/prompts)
- Application: `src/services/*`
- Domain: `src/models/*`
- Infrastructure: `src/client/*`, `src/config/settings.py`

`src/server.py` wires everything and registers MCP callbacks.

## Key Notes

- HTTP client is **async** (`httpx.AsyncClient`). `BaseAPIClient._make_request()` is async.
- Feature flags (env prefix `LOGSEQ_`):
  - `LOGSEQ_ENABLE_ADVANCED_QUERIES`
  - `LOGSEQ_ENABLE_GIT_OPERATIONS`
- CLI and MCP share the same service layer.
