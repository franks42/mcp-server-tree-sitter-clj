#!/bin/bash
# Development server with auto-reload for Clojure tree-sitter MCP

echo "🚀 Starting Clojure Tree-sitter Development Server..."
echo "=================================================="
echo "Port: 3001"
echo "Mode: Development (debug enabled)"
echo "Config: dev-config.yaml"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed. Please install uv first."
    exit 1
fi

# Set development environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export MCP_TREE_SITTER_DEBUG=true
export MCP_TREE_SITTER_PORT=3001

# Run the server
uv run python -m mcp_server_tree_sitter \
    --debug \
    --port 3001 \
    --config dev-config.yaml

echo ""
echo "🛑 Server stopped."