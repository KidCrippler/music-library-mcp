#!/usr/bin/env bash
# Test script to verify the MCP server setup

echo "🔍 Testing MCP Server Setup..."
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."
cd "$PROJECT_ROOT"

# Test 1: Check venv exists
echo "1. Checking virtual environment..."
if [ -d ".venv" ]; then
    echo "   ✓ Virtual environment exists"
else
    echo "   ✗ Virtual environment not found!"
    exit 1
fi

# Test 2: Check Python version
echo ""
echo "2. Checking Python version..."
PYTHON_VERSION=$(.venv/bin/python --version)
echo "   ✓ $PYTHON_VERSION"

# Test 3: Check MCP package
echo ""
echo "3. Checking MCP package..."
if .venv/bin/python -c "import mcp" 2>/dev/null; then
    echo "   ✓ MCP package installed"
else
    echo "   ✗ MCP package not found!"
    exit 1
fi

# Test 4: Check httpx package
echo ""
echo "4. Checking httpx package..."
if .venv/bin/python -c "import httpx" 2>/dev/null; then
    echo "   ✓ httpx package installed"
else
    echo "   ✗ httpx package not found!"
    exit 1
fi

# Test 5: Check server module
echo ""
echo "5. Checking server module..."
if .venv/bin/python -c "import music_library_mcp.server" 2>/dev/null; then
    echo "   ✓ Server module loads correctly"
else
    echo "   ✗ Server module failed to load!"
    exit 1
fi

# Test 6: Check songs database
echo ""
echo "6. Checking songs database..."
if [ -f "songs/songs.json" ]; then
    echo "   ✓ Songs database exists"
else
    echo "   ✗ Songs database not found!"
    exit 1
fi

echo ""
echo "🎉 All tests passed! Your MCP server is ready to use."
echo ""
echo "To start the server:"
echo "  ./scripts/start_server.sh"
echo ""
echo "Or manually:"
echo "  source .venv/bin/activate"
echo "  python -m music_library_mcp.server"

