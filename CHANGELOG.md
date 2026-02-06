# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-06

### Added
- Complete 4-layer architecture refactoring
- **25 MCP Tools** (expanded from 9):
  - Block operations (8): insert, update, delete, get, move, batch insert, get page blocks, get current page content
  - Page operations (5): create, get, delete, rename, get all
  - Editor operations (5): get current page/block, edit block, exit editing, get editing content
  - Query operations (3): simple query, advanced query, get tasks
  - Graph operations (2): get current graph, get user configs
  - Git operations (2): git commit, git status
- **6 MCP Prompts**: insert_block, create_page, get_page, get_current_page, get_all_pages, simple_query
- Comprehensive test suite with 158 tests and 87% coverage
- Pydantic v2 models for all inputs with validation
- Response formatting utilities for readable output
- Tenacity retry logic with exponential backoff
- Proper error handling with McpError conversion
- Type-safe architecture with mypy (52 non-blocking strict-mode warnings)

### Changed
- Migrated from single-file architecture to modular 4-layer design
- Moved from `src/mcp_server_logseq/` to flat `src/` structure with absolute imports
- Updated all imports to use absolute paths (e.g., `from client.logseq import ...`)
- Enhanced configuration management with Pydantic Settings
- Improved error messages and response formatting

### Fixed
- Import path issues for flat module structure
- Type annotations for better IDE support
- Response type handling for list vs dict API returns

### Technical Details
- **Architecture**: Infrastructure → Domain → Application → Presentation layers
- **Test Coverage**: 158 tests, 87% overall coverage
  - client/: 97-100%
  - handlers/: 99-100%
  - models/: 94-100%
  - services/: 100%
  - utils/: 81%
- **Linting**: 100% pass with ruff
- **Type Checking**: MyPy configured for strict mode with flat module support

## [0.0.1] - 2025-XX-XX

### Added
- Initial release with basic Logseq MCP integration
- 9 core MCP tools for block and page operations
- Basic HTTP API client
- Simple README documentation
- PyPI package setup
