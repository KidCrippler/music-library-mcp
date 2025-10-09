# MCP Server Setup Guide

## Virtual Environment Setup ✅

A Python 3.11 virtual environment has been created in `.venv/` with all required dependencies installed.

## Running the Server

### Option 1: Using the Start Script (Recommended)

```bash
cd /Users/alonc/mcp-intro
./start_server.sh
```

### Option 2: Manual Activation

```bash
cd /Users/alonc/mcp-intro
source .venv/bin/activate
python -m music_library_mcp.server
```

### Option 3: Direct Python Call

```bash
/Users/alonc/mcp-intro/.venv/bin/python -m music_library_mcp.server
```

## Configuration for Claude Desktop

Add this to your Claude Desktop config at:  
`~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "music-library": {
      "command": "/Users/alonc/mcp-intro/.venv/bin/python",
      "args": [
        "-m",
        "music_library_mcp.server"
      ],
      "cwd": "/Users/alonc/mcp-intro"
    }
  }
}
```

## Configuration for Cursor

Add this to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "music-library": {
      "command": "/Users/alonc/mcp-intro/.venv/bin/python",
      "args": [
        "-m",
        "music_library_mcp.server"
      ],
      "cwd": "/Users/alonc/mcp-intro"
    }
  }
}
```

## Why This Works

- **Dedicated Environment**: The `.venv/` directory contains Python 3.11.12 with all dependencies isolated from your system Python
- **No Global Installation**: Dependencies are only installed in this virtual environment
- **Portable**: Works on any machine by just creating the venv and installing dependencies
- **Consistent**: Always uses the same Python version and package versions

## Troubleshooting

### Testing the Server

```bash
cd /Users/alonc/mcp-intro
source .venv/bin/activate
python -c "import mcp; print('✓ MCP installed')"
python -c "import httpx; print('✓ httpx installed')"
python -m music_library_mcp.server --help
```

### Reinstalling Dependencies

If something goes wrong:

```bash
cd /Users/alonc/mcp-intro
rm -rf .venv
/opt/homebrew/bin/python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install mcp httpx Flask
```

### Python Version Check

```bash
/Users/alonc/mcp-intro/.venv/bin/python --version
# Should show: Python 3.11.12
```

## What Was Fixed

**Problem**: Your default `python3` is version 3.13.6, but the MCP dependencies may have compatibility issues with Python 3.13.

**Solution**: Created a virtual environment using Python 3.11.12 (which you already had installed) with all dependencies isolated.

**Result**: You can now run the MCP server without worrying about Python version conflicts or system-wide package installations.

