# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Model Context Protocol (MCP) server** that exposes a music library database (1,569 songs, 618 artists) to AI assistants like Claude Desktop and Cursor. The server implements all three MCP primitives: Resources, Tools, and Prompts.

## Development Commands

### Install dependencies
```bash
pip install mcp httpx
```

### Test the database layer
```bash
python test_server.py
```

### Run the MCP server
```bash
python -m music_library_mcp.server
```

The server communicates via stdio and will block waiting for MCP protocol messages from a client.

## Architecture

### Two-Layer Design

**Layer 1: Database (`database.py`)**
- `SongsDatabase` class loads `songs/songs.json` and builds in-memory indexes
- Three indexes created on initialization:
  - `songs_by_id`: Direct song lookup by ID
  - `songs_by_artist`: Artist names normalized to lowercase for case-insensitive matching
  - `songs_by_category`: Category ID to songs mapping
- All search/query methods delegate to these pre-built indexes for O(1) or O(n) performance

**Layer 2: MCP Server (`server.py`)**
- Single global `db` instance initialized at module load time from `songs/songs.json`
- Three types of MCP handlers, each using decorator pattern:

**Resources** (`@app.list_resources()`, `@app.read_resource()`):
- URI-based data access using `songs://` scheme
- Dynamic resource generation: First 50 artists get individual `songs://artist/{name}` URIs
- Resources are read-only snapshots of the data

**Tools** (`@app.list_tools()`, `@app.call_tool()`):
- `search_songs`: Multi-criteria filtering (combines artist, category, and text query)
- `get_lyrics`: Async HTTP fetch from song's `markupUrl` field
- `get_youtube_metadata`: Constructs YouTube URLs from `youTubeVideoId` field

**Prompts** (`@app.list_prompts()`, `@app.get_prompt()`):
- Return `GetPromptResult` with pre-filled context and instructions
- Designed for AI to execute complex workflows (e.g., playlist generation, similarity analysis)

### Data Flow for Queries

1. MCP client (Claude/Cursor) sends request via stdio
2. `server.py` receives and routes to appropriate handler
3. Handler calls `db.method()` to query indexes
4. Results serialized to JSON with `ensure_ascii=False` (preserves Hebrew characters)
5. Response sent back via stdio to client

### Key Architectural Decisions

**Artist matching is case-insensitive**: Artists indexed by `artist.lower()` but original casing preserved in song objects. When adding new features, use `get_songs_by_artist()` which handles normalization.

**Category IDs are strings**: The JSON schema uses string IDs ("1", "2", etc.) not integers. Always treat `categoryIds` as `list[str]`.

**Global database instance**: The `db` object is created once at module import time. If you modify data, indexes must be manually rebuilt or the server restarted.

**Hebrew text handling**: All JSON serialization uses `ensure_ascii=False` to preserve UTF-8 characters. File reads use `encoding='utf-8'`.

## Database Schema

Songs JSON structure:
```python
{
  "version": str,
  "title": str,
  "categories": [{"id": str, "name": str}],
  "songs": [{
    "id": int,
    "name": str,
    "singer": str,
    "playback": {"youTubeVideoId": str},
    "categoryIds": [str],  # Not int[]!
    "lyrics": {"markupUrl": str},
    "dateCreated": int,  # Unix timestamp in milliseconds
    "dateModified": int
  }]
}
```

## Adding New Features

**New Resource**: Add URI pattern handling in `read_resource()` function. URI parsing uses `urlparse()` then path matching.

**New Tool**: Add tool definition to `list_tools()` and implementation to `call_tool()`. Tools return `list[TextContent]`.

**New Prompt**: Add prompt definition to `list_prompts()` and implementation to `get_prompt()`. Prompts return `GetPromptResult` with messages.

**New Index**: If adding indexes to `database.py`, build them in `_build_indexes()` called from `__init__`.

## Python Version Compatibility

Requires Python 3.10+. Type hints use `Union[X, Y]` and `Optional[X]` syntax (not `X | Y`) for compatibility with Python 3.11 runtime environment.

## Testing

`test_server.py` validates:
- Database loads successfully from `songs/songs.json`
- Indexes are built correctly
- Basic queries work (artist lookup, category filtering, text search)

Run before adding to MCP client to verify data layer integrity.

## Client Configuration

MCP clients (Claude Desktop, Cursor) connect via:
```json
{
  "command": "python",
  "args": ["-m", "music_library_mcp.server"],
  "cwd": "/path/to/mcp-intro"
}
```

The `cwd` must point to the repository root where `songs/songs.json` exists.
