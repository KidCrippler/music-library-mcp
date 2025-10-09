#!/usr/bin/env bash
# Music Library MCP Server Launcher
# This script activates the virtual environment and starts the server

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."

# Display startup information
echo "🎵 Music Library MCP Server"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Working Directory: $PROJECT_ROOT"

# Activate the virtual environment
source "$PROJECT_ROOT/.venv/bin/activate"

# Show Python version
PYTHON_VERSION=$(python --version 2>&1)
echo "🐍 Python: $PYTHON_VERSION"

# Check if database exists
if [ -f "$PROJECT_ROOT/songs/songs.json" ]; then
    SONG_COUNT=$(python -c "import json; data=json.load(open('$PROJECT_ROOT/songs/songs.json')); print(len(data['songs']))" 2>/dev/null || echo "unknown")
    echo "📚 Database: songs.json ($SONG_COUNT songs)"
else
    echo "⚠️  Warning: songs/songs.json not found!"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Starting server (stdio mode)..."
echo "   Press Ctrl+C to stop"
echo ""

# Change to project root and run the MCP server
cd "$PROJECT_ROOT"
exec python -m music_library_mcp.server "$@"

