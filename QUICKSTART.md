# Memos MCP Server - Quick Reference

## Available Tools

The Memos MCP server provides 4 tools for interacting with your Memos instance:

### 1. search_memos
Search for memos with filters
- **Query**: Text search in content
- **Creator ID**: Filter by user
- **Tag**: Filter by tag name
- **Visibility**: PUBLIC, PROTECTED, or PRIVATE
- **Pagination**: Limit and offset support

### 2. create_memo
Create new memos
- **Content**: Markdown supported
- **Visibility**: PUBLIC, PROTECTED, or PRIVATE (default: PRIVATE)

### 3. update_memo
Update existing memos
- **Memo UID**: Required
- **Content**: Optional update
- **Visibility**: Optional update
- **Pinned**: Optional pin/unpin

### 4. get_memo
Retrieve a specific memo by UID

## Running with uv/uvx

### Quick Start (no installation)
```bash
export MEMOS_BASE_URL="http://localhost:5230"
export MEMOS_API_TOKEN="your-token"
uvx --from /path/to/memos_mcp memos-mcp
```

### After installation
```bash
uv sync
uv run memos-mcp
```

## Claude Desktop Configuration

Using uvx (recommended):
```json
{
  "mcpServers": {
    "memos": {
      "command": "uvx",
      "args": ["--from", "/path/to/memos_mcp", "memos-mcp"],
      "env": {
        "MEMOS_BASE_URL": "http://localhost:5230",
        "MEMOS_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

## Security Note

The delete functionality has been intentionally removed to prevent accidental data loss. This server provides read and write operations only.
