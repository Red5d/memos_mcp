"""
Memos MCP Server

An MCP server that provides tools for interacting with a Memos instance.
Supports searching, creating, and updating memos.
"""

import os
from typing import Optional
import httpx
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("memos")

# Get Memos configuration from environment variables
MEMOS_BASE_URL = os.getenv("MEMOS_BASE_URL", "http://localhost:5230")
MEMOS_API_TOKEN = os.getenv("MEMOS_API_TOKEN", "")


def get_headers() -> dict:
    """Get headers for API requests including authentication"""
    headers = {
        "Content-Type": "application/json",
    }
    if MEMOS_API_TOKEN:
        headers["Authorization"] = f"Bearer {MEMOS_API_TOKEN}"
    return headers


@mcp.tool()
async def search_memos(
    query: Optional[str] = None,
    creator_id: Optional[int] = None,
    tag: Optional[str] = None,
    visibility: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> str:
    """
    Search for memos with optional filters.
    
    Args:
        query: Text to search for in memo content
        creator_id: Filter by creator user ID
        tag: Filter by tag name
        visibility: Filter by visibility (PUBLIC, PROTECTED, PRIVATE)
        limit: Maximum number of results to return (default: 10)
        offset: Number of results to skip (default: 0)
    
    Returns:
        JSON string containing the list of matching memos
    """
    # Build filter expression
    filters = []
    
    if creator_id is not None:
        filters.append(f"creator_id == {creator_id}")
    
    if query:
        # Escape quotes in query
        escaped_query = query.replace('"', '\\"')
        filters.append(f'content.contains("{escaped_query}")')
    
    if tag:
        escaped_tag = tag.replace('"', '\\"')
        filters.append(f'tag in ["{escaped_tag}"]')
    
    if visibility:
        filters.append(f'visibility == "{visibility.upper()}"')
    
    # Combine filters with AND operator
    filter_str = " && ".join(filters) if filters else ""
    
    # Build request parameters
    params = {
        "pageSize": limit,
    }
    
    if filter_str:
        params["filter"] = filter_str
    
    # Calculate page token for pagination
    if offset > 0:
        # For simplicity, we'll use offset/limit approach
        # In production, you'd want to use proper page tokens
        page = offset // limit
        if page > 0:
            params["pageToken"] = f"offset={offset}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MEMOS_BASE_URL}/api/v1/memos",
                params=params,
                headers=get_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Format the response nicely
            memos = data.get("memos", [])
            result = {
                "count": len(memos),
                "memos": [
                    {
                        "name": memo.get("name"),
                        "uid": memo.get("uid"),
                        "creator": memo.get("creator"),
                        "content": memo.get("content"),
                        "visibility": memo.get("visibility"),
                        "pinned": memo.get("pinned", False),
                        "createTime": memo.get("createTime"),
                        "updateTime": memo.get("updateTime"),
                        "displayTime": memo.get("displayTime"),
                    }
                    for memo in memos
                ],
                "nextPageToken": data.get("nextPageToken", "")
            }
            
            return str(result)
            
    except httpx.HTTPError as e:
        return f"Error searching memos: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
async def create_memo(
    content: str,
    visibility: str = "PRIVATE"
) -> str:
    """
    Create a new memo.
    
    Args:
        content: The content of the memo (supports Markdown)
        visibility: Visibility level - PUBLIC, PROTECTED, or PRIVATE (default: PRIVATE)
    
    Returns:
        JSON string containing the created memo details
    """
    # Validate visibility
    valid_visibilities = ["PUBLIC", "PROTECTED", "PRIVATE"]
    visibility = visibility.upper()
    if visibility not in valid_visibilities:
        return f"Error: visibility must be one of {', '.join(valid_visibilities)}"
    
    # Build request payload
    payload = {
        "content": content,
        "visibility": visibility
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MEMOS_BASE_URL}/api/v1/memos",
                json=payload,
                headers=get_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            memo = response.json()
            
            # Format the response
            result = {
                "success": True,
                "memo": {
                    "name": memo.get("name"),
                    "uid": memo.get("uid"),
                    "creator": memo.get("creator"),
                    "content": memo.get("content"),
                    "visibility": memo.get("visibility"),
                    "pinned": memo.get("pinned", False),
                    "createTime": memo.get("createTime"),
                    "updateTime": memo.get("updateTime"),
                    "displayTime": memo.get("displayTime"),
                }
            }
            
            return str(result)
            
    except httpx.HTTPError as e:
        return f"Error creating memo: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
async def update_memo(
    memo_uid: str,
    content: Optional[str] = None,
    visibility: Optional[str] = None,
    pinned: Optional[bool] = None
) -> str:
    """
    Update an existing memo.
    
    Args:
        memo_uid: The UID of the memo to update (e.g., "abc123")
        content: New content for the memo (optional)
        visibility: New visibility level - PUBLIC, PROTECTED, or PRIVATE (optional)
        pinned: Whether to pin the memo (optional)
    
    Returns:
        JSON string containing the updated memo details
    """
    # Validate visibility if provided
    if visibility is not None:
        valid_visibilities = ["PUBLIC", "PROTECTED", "PRIVATE"]
        visibility = visibility.upper()
        if visibility not in valid_visibilities:
            return f"Error: visibility must be one of {', '.join(valid_visibilities)}"
    
    # Build update payload and update mask
    memo_data = {"state": "STATE_UNSPECIFIED"}
    update_paths = []
    
    if content is not None:
        memo_data["content"] = content
        update_paths.append("content")
    
    if visibility is not None:
        memo_data["visibility"] = visibility
        update_paths.append("visibility")
    
    if pinned is not None:
        memo_data["pinned"] = pinned
        update_paths.append("pinned")
    
    if not update_paths:
        return "Error: At least one field (content, visibility, or pinned) must be provided for update"
    
    # Build the full payload
    memo_name = f"memos/{memo_uid}"
    payload = {
        **memo_data
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{MEMOS_BASE_URL}/api/v1/{memo_name}",
                json=payload,
                headers=get_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            memo = response.json()
            
            # Format the response
            result = {
                "success": True,
                "memo": {
                    "name": memo.get("name"),
                    "uid": memo.get("uid"),
                    "creator": memo.get("creator"),
                    "content": memo.get("content"),
                    "visibility": memo.get("visibility"),
                    "pinned": memo.get("pinned", False),
                    "createTime": memo.get("createTime"),
                    "updateTime": memo.get("updateTime"),
                    "displayTime": memo.get("displayTime"),
                }
            }
            
            return str(result)
            
    except httpx.HTTPError as e:
        return f"Error updating memo: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
async def get_memo(memo_uid: str) -> str:
    """
    Get a specific memo by its UID.
    
    Args:
        memo_uid: The UID of the memo to retrieve (e.g., "abc123")
    
    Returns:
        JSON string containing the memo details
    """
    memo_name = f"memos/{memo_uid}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{MEMOS_BASE_URL}/api/v1/{memo_name}",
                headers=get_headers(),
                timeout=30.0
            )
            response.raise_for_status()
            memo = response.json()
            
            # Format the response
            result = {
                "name": memo.get("name"),
                "uid": memo.get("uid"),
                "creator": memo.get("creator"),
                "content": memo.get("content"),
                "visibility": memo.get("visibility"),
                "pinned": memo.get("pinned", False),
                "createTime": memo.get("createTime"),
                "updateTime": memo.get("updateTime"),
                "displayTime": memo.get("displayTime"),
                "snippet": memo.get("snippet", ""),
            }
            
            return str(result)
            
    except httpx.HTTPError as e:
        return f"Error getting memo: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"



