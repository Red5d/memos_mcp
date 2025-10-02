# Memos MCP Server

An MCP (Model Context Protocol) server that provides tools for interacting with a [Memos](https://github.com/usememos/memos) instance. This server allows AI assistants to search, create, and update memos through the Memos API.

## Features

- **Search Memos**: Search for memos with filters like creator, tags, visibility, and content
- **Create Memos**: Create new memos with markdown support
- **Update Memos**: Update existing memos (content, visibility, pinned status)
- **Get Memo**: Retrieve a specific memo by UID

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd memos_mcp
```

2. Install dependencies:

### Using uv (recommended)
```bash
uv sync
```

### Using pip
```bash
pip install -r requirements.txt
```

## Configuration

Set the following environment variables:

- `MEMOS_BASE_URL`: The base URL of your Memos instance (default: `http://localhost:5230`)
- `MEMOS_API_TOKEN`: Your Memos API authentication token (optional for public instances)

### Getting an API Token

1. Log into your Memos instance
2. Go to Settings → Access Tokens
3. Create a new access token
4. Copy the token and set it as the `MEMOS_API_TOKEN` environment variable

Example:
```bash
export MEMOS_BASE_URL="https://memos.example.com"
export MEMOS_API_TOKEN="your-token-here"
```

## Usage

### Running the Server

#### Using uvx (no installation required)
```bash
# Run directly with uvx
uvx --from . memos-mcp
```

#### Using uv after installation
```bash
# After running 'uv sync'
uv run memos-mcp
```

#### Using FastMCP directly
```bash
fastmcp run server.py
```

#### Programmatic usage
```python
from server import mcp

# The server is ready to use
```

### Available Tools

#### 1. search_memos
Search for memos with optional filters.

**Parameters:**
- `query` (optional): Text to search for in memo content
- `creator_id` (optional): Filter by creator user ID
- `tag` (optional): Filter by tag name
- `visibility` (optional): Filter by visibility (PUBLIC, PROTECTED, PRIVATE)
- `limit` (default: 10): Maximum number of results
- `offset` (default: 0): Number of results to skip

**Example:**
```python
result = await search_memos(query="meeting notes", limit=5)
```

#### 2. create_memo
Create a new memo.

**Parameters:**
- `content`: The content of the memo (supports Markdown)
- `visibility` (default: PRIVATE): Visibility level (PUBLIC, PROTECTED, PRIVATE)

**Example:**
```python
result = await create_memo(
    content="# Meeting Notes\n\n- Discuss project timeline\n- Review budget",
    visibility="PRIVATE"
)
```

#### 3. update_memo
Update an existing memo.

**Parameters:**
- `memo_uid`: The UID of the memo to update
- `content` (optional): New content for the memo
- `visibility` (optional): New visibility level
- `pinned` (optional): Whether to pin the memo

**Example:**
```python
result = await update_memo(
    memo_uid="abc123",
    content="Updated content",
    pinned=True
)
```

#### 4. get_memo
Get a specific memo by its UID.

**Parameters:**
- `memo_uid`: The UID of the memo to retrieve

**Example:**
```python
result = await get_memo(memo_uid="abc123")
```

## Integration with MCP Clients

### Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

#### Using uvx (recommended - no installation needed)
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

#### Using uv (after installation)
```json
{
  "mcpServers": {
    "memos": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/memos_mcp", "memos-mcp"],
      "env": {
        "MEMOS_BASE_URL": "http://localhost:5230",
        "MEMOS_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

#### Using Python directly
```json
{
  "mcpServers": {
    "memos": {
      "command": "python",
      "args": ["-m", "fastmcp", "run", "/path/to/memos_mcp/server.py"],
      "env": {
        "MEMOS_BASE_URL": "http://localhost:5230",
        "MEMOS_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

## API Reference

This server is built on the Memos API v1. The API follows Google's API Improvement Proposals (AIPs) design guidelines.

### API Endpoints Used

- `GET /api/v1/memos` - List/search memos
- `POST /api/v1/memos` - Create a memo
- `GET /api/v1/memos/{uid}` - Get a specific memo
- `PATCH /api/v1/memos/{uid}` - Update a memo

### Authentication

The server supports Bearer token authentication. Include your access token in the `Authorization` header:

```
Authorization: Bearer your-token-here
```

## Development

### Running Tests

```bash
pytest
```

### Code Structure

- `server.py`: Main MCP server implementation with all tools
- `requirements.txt`: Python dependencies

## About Memos

Memos is a lightweight, self-hosted memo hub with knowledge management and social networking features. Learn more at:
- Website: https://www.usememos.com/
- GitHub: https://github.com/usememos/memos

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
