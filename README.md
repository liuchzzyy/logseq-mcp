# Logseq MCP Server

A Model Context Protocol server that provides direct integration with Logseq's knowledge base. This server enables LLMs to interact with Logseq graphs, create pages, manage blocks, and organize information programmatically.

<a href="https://glama.ai/mcp/servers/@dailydaniel/logseq-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@dailydaniel/logseq-mcp/badge" alt="Logseq Server MCP server" />
</a>

## Features

- **25 MCP Tools** for complete Logseq automation
- **6 MCP Prompts** for common workflows
- **4-Layer Architecture** for maintainability and extensibility
- **Full Type Safety** with Pydantic models
- **Comprehensive Test Coverage** (158 tests, 87% coverage)
- **Retry Logic** with exponential backoff for API resilience

## Usage with Claude Desktop

Add this to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%/Claude/claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "logseq": {
      "command": "uv",
      "args": ["--directory", "/path/to/logseq-mcp", "run", "logseq-mcp"],
      "env": {
        "LOGSEQ_API_TOKEN": "<YOUR_API_TOKEN>",
        "LOGSEQ_API_URL": "http://127.0.0.1:12315"
      }
    }
  }
}
```

## Available Tools (25 Total)

### Block Operations (8 tools)

#### `logseq_insert_block`
Create a new block in Logseq.

**Parameters:**
- `content` (string, required): Block content
- `parent_block` (string): Parent block UUID or page name
- `is_page_block` (boolean): Create as page-level block
- `before` (boolean): Insert before parent instead of after
- `custom_uuid` (string): Custom UUID for the block
- `properties` (object): Block properties as key-value pairs

**Example:**
```json
{
  "parent_block": "[[Project Roadmap]]",
  "content": "- [ ] Finalize API documentation",
  "properties": {"priority": "high", "due": "2024-03-20"}
}
```

#### `logseq_update_block`
Update existing block content and properties.

**Parameters:**
- `uuid` (string, required): Block UUID
- `content` (string, required): New content
- `properties` (object): Updated properties

#### `logseq_delete_block`
Delete a block by UUID.

**Parameters:**
- `uuid` (string, required): Block UUID to delete

#### `logseq_get_block`
Retrieve block details by UUID.

**Parameters:**
- `uuid` (string, required): Block UUID

#### `logseq_move_block`
Move a block to a new location.

**Parameters:**
- `uuid` (string, required): Block UUID to move
- `target_uuid` (string, required): Target block UUID
- `as_child` (boolean): Move as child of target

#### `logseq_insert_batch`
Insert multiple blocks at once.

**Parameters:**
- `parent` (string, required): Parent block or page
- `blocks` (array, required): List of block data objects

**Example:**
```json
{
  "parent": "[[Meeting Notes]]",
  "blocks": [
    {"content": "- Action item 1"},
    {"content": "- Action item 2"}
  ]
}
```

#### `logseq_get_page_blocks`
Get all blocks in a page as a tree structure.

**Parameters:**
- `page_name` (string, required): Page name or UUID

#### `logseq_get_current_page_content`
Get all blocks from the currently active page.

**Parameters:** None

### Page Operations (5 tools)

#### `logseq_create_page`
Create a new page.

**Parameters:**
- `page_name` (string, required): Page name
- `properties` (object): Page properties
- `journal` (boolean): Create as journal page
- `format` (string): Page format (`markdown` or `org`)
- `create_first_block` (boolean): Create initial empty block

**Example:**
```json
{
  "page_name": "Team Meeting 2024-03-15",
  "properties": {
    "tags": "meeting,engineering",
    "participants": "Alice,Bob,Charlie"
  },
  "format": "markdown"
}
```

#### `logseq_get_page`
Get page details.

**Parameters:**
- `page_name` (string, required): Page name or UUID
- `include_children` (boolean): Include child blocks

#### `logseq_delete_page`
Delete a page.

**Parameters:**
- `page_name` (string, required): Page name to delete

#### `logseq_rename_page`
Rename a page.

**Parameters:**
- `old_name` (string, required): Current page name
- `new_name` (string, required): New page name

#### `logseq_get_all_pages`
List all pages in the graph.

**Parameters:**
- `repo` (string): Repository name (optional, uses current graph if not specified)

### Editor Operations (5 tools)

#### `logseq_get_current_page`
Get the currently active page.

**Parameters:** None

#### `logseq_get_current_block`
Get the currently focused block.

**Parameters:** None

#### `logseq_edit_block`
Enter edit mode for a block.

**Parameters:**
- `uuid` (string, required): Block UUID
- `pos` (number): Cursor position (0-10000)

#### `logseq_exit_editing_mode`
Exit editing mode.

**Parameters:**
- `select_block` (boolean): Keep block selected after exiting

#### `logseq_get_editing_content`
Get the content of the block currently being edited.

**Parameters:** None

### Query Operations (3 tools)

#### `logseq_simple_query`
Execute a simple Logseq query.

**Parameters:**
- `query` (string, required): Query string (e.g., `[[tag]]`, `#important`)

**Examples:**
- `[[Project]]` - Find all blocks referencing Project
- `#important` - Find all blocks with #important tag
- `{{query [[TODO]]}}` - Advanced query syntax

#### `logseq_advanced_query`
Execute an advanced Datascript query.

**Parameters:**
- `query` (string, required): Datascript query
- `inputs` (array): Query input parameters

**Example:**
```json
{
  "query": "[:find (pull ?b [*]) :where [?b :block/marker ?m] [(= ?m \"TODO\")]]",
  "inputs": []
}
```

#### `logseq_get_tasks`
Get all tasks with optional filters.

**Parameters:**
- `marker` (string): Filter by marker (`TODO`, `DOING`, `DONE`, `NOW`, `LATER`, `WAITING`, `CANCELLED`)
- `priority` (string): Filter by priority (`A`, `B`, `C`)

### Graph Operations (2 tools)

#### `logseq_get_current_graph`
Get information about the current graph.

**Parameters:** None

#### `logseq_get_user_configs`
Get user configurations.

**Parameters:** None

### Git Operations (2 tools)

#### `logseq_git_commit`
Execute a git commit.

**Parameters:**
- `message` (string, required): Commit message

#### `logseq_git_status`
Get git status.

**Parameters:** None

## Available Prompts (6 Total)

### `logseq_insert_block`
Create a new block in Logseq.

**Arguments:**
- `content` (required): Block content
- `parent_block`: Parent block reference (page name or UUID)

### `logseq_create_page`
Create a new Logseq page.

**Arguments:**
- `page_name` (required): Name of the page
- `properties`: Page properties as JSON

### `logseq_get_page`
Get page details.

**Arguments:**
- `page_name` (required): Page name or UUID

### `logseq_get_current_page`
Get the currently active page.

**Arguments:** None

### `logseq_get_all_pages`
List all pages in the graph.

**Arguments:** None

### `logseq_simple_query`
Run a query.

**Arguments:**
- `query` (required): Query string

## Installation from Source

```bash
git clone https://github.com/dailydaniel/logseq-mcp.git
cd logseq-mcp
uv sync
```

Run the server:
```bash
uv run logseq-mcp
```

Or with explicit environment:
```bash
LOGSEQ_API_TOKEN=<token> LOGSEQ_API_URL=http://localhost:12315 uv run logseq-mcp
```

## Configuration

### Getting an API Token

1. Open Logseq
2. Go to Settings → HTTP API Server
3. Enable the HTTP API Server
4. Click "Authorization tokens"
5. Generate a new token
6. Copy the token for use in your MCP configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOGSEQ_API_TOKEN` | Yes | - | Logseq API authorization token |
| `LOGSEQ_API_URL` | No | `http://localhost:12315` | Logseq HTTP API endpoint |

## Architecture

This MCP server uses a 4-layer architecture:

```
┌─────────────────────────────────────────┐
│  Layer 4: Infrastructure                │
│  ├── client/logseq.py    - API client   │
│  ├── client/base.py      - HTTP base    │
│  └── config/settings.py  - Settings     │
├─────────────────────────────────────────┤
│  Layer 3: Domain                        │
│  ├── models/schemas.py   - Data models  │
│  ├── models/enums.py     - Enums        │
│  └── models/responses.py - Formatters   │
├─────────────────────────────────────────┤
│  Layer 2: Application                   │
│  ├── services/blocks.py  - Block ops    │
│  ├── services/pages.py   - Page ops     │
│  ├── services/queries.py - Queries      │
│  └── services/graph.py   - Graph ops    │
├─────────────────────────────────────────┤
│  Layer 1: Presentation                  │
│  ├── handlers/tools.py   - MCP tools    │
│  └── handlers/prompts.py - MCP prompts  │
└─────────────────────────────────────────┘
```

## Examples

### Create meeting notes

```
Create a new page "Team Meeting 2024-03-15" with properties:
- Tags: meeting, engineering
- Participants: Alice, Bob, Charlie
- Status: pending
```

### Add a task

```
Add a TODO block to [[Project Roadmap]]:
- [ ] Finalize API documentation
- Due: 2024-03-20
- Priority: high
```

### Query tasks

```
Show me all TODO tasks with high priority
```

### Get current page content

```
What blocks are on the current page?
```

## Development

### Running Tests

```bash
# Run all tests
uv run python -m pytest tests/

# With coverage report
uv run python -m pytest tests/ --cov=src --cov-report=html

# Specific test file
uv run python -m pytest tests/test_services.py -v
```

### Linting and Type Checking

```bash
# Run ruff linter
uv run ruff check src/ tests/

# Run ruff formatter
uv run ruff format src/ tests/

# Run type checker
uv run ty check --extra-search-path src src
```

### CLI Usage

Serve (default):
```bash
uv run logseq-mcp serve
```

Pages:
```bash
uv run logseq-mcp pages list
uv run logseq-mcp pages get --name "Page Name" --children
uv run logseq-mcp pages create --name "New Page" --properties '{"tags":"demo"}'
uv run logseq-mcp pages delete --name "Old Page"
uv run logseq-mcp pages rename --old "Old" --new "New"
```

Journals:
```bash
uv run logseq-mcp journals create --name "2026-02-06"
uv run logseq-mcp journals list
```

Blocks:
```bash
uv run logseq-mcp blocks get --uuid <uuid>
uv run logseq-mcp blocks insert --parent "Page Name" --content "- item" --as-page-block
uv run logseq-mcp blocks update --uuid <uuid> --content "updated"
uv run logseq-mcp blocks delete --uuid <uuid>
uv run logseq-mcp blocks move --uuid <uuid> --target <uuid> --as-child
uv run logseq-mcp blocks batch-insert --parent "Page" --file blocks.json
uv run logseq-mcp blocks page-blocks --page "Page Name"
uv run logseq-mcp blocks current-page-blocks
uv run logseq-mcp blocks current-block
```

Queries:
```bash
uv run logseq-mcp queries simple --query "[[tag]]"
uv run logseq-mcp queries advanced --query "[:find ...]" --inputs '["arg1", 2]'
uv run logseq-mcp queries tasks --marker TODO --priority A
uv run logseq-mcp queries blocks-with-prop --property status --value done
```

Graph:
```bash
uv run logseq-mcp graph info
uv run logseq-mcp graph user-configs
uv run logseq-mcp graph git-status
```

## Debugging

Use the MCP Inspector for debugging:

```bash
npx @modelcontextprotocol/inspector uv --directory . run logseq-mcp
```

## Troubleshooting

### Connection refused error

Ensure Logseq HTTP API is enabled:
1. Open Logseq
2. Go to Settings → HTTP API Server
3. Enable it and set the port (default: 12315)

### Authentication failed

Check that your `LOGSEQ_API_TOKEN` is correct and hasn't expired. Generate a new token in Logseq if needed.

### Module not found errors

If running from source, ensure you're using `uv run` or have activated the virtual environment.

## Contributing

Contributions are welcome! Areas for enhancement:

- Additional API endpoints
- Template support for common workflows
- Enhanced error handling
- Performance optimizations
- Additional test coverage

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

### v1.1.0 (2026-02-07)
- Standardized field naming across all models and handlers
- Wired editor tool handlers (edit_block, exit_editing, get_editing_content)
- Fixed BlockEntity/PageEntity type annotations for Logseq API compatibility
- Cleaned up unused code and intermediate files
- Updated documentation (CLAUDE.md, README.md, Chinese guide)
- Full integration test: 26/26 CLI commands passed

### v1.0.0 (2026-02-06)
- Complete refactor to 4-layer architecture
- Added 25 MCP tools (up from 9)
- Added 6 MCP prompts
- Comprehensive test suite (158 tests, 87% coverage)
- Full Pydantic v2 type safety
- Retry logic with exponential backoff
- Response formatting utilities
