#!/bin/bash
# Test QuantConnect MCP Server with proper handshake

source .env

# Create test input with proper MCP initialization
cat > /tmp/mcp_test.json << 'EOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
EOF

# Run MCP server
cat /tmp/mcp_test.json | docker run -i --rm \
  -e "QUANTCONNECT_USER_ID=${QUANTCONNECT_USER_ID}" \
  -e "QUANTCONNECT_API_TOKEN=${QUANTCONNECT_API_TOKEN}" \
  --platform linux/arm64 \
  quantconnect/mcp-server

rm /tmp/mcp_test.json
