#!/bin/bash
# Test QuantConnect MCP Server - Get Tools List

source .env

# MCP protocol sequence: initialize -> initialized notification -> tools/list
cat > /tmp/mcp_tools.json << 'EOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
EOF

cat /tmp/mcp_tools.json | docker run -i --rm \
  -e "QUANTCONNECT_USER_ID=${QUANTCONNECT_USER_ID}" \
  -e "QUANTCONNECT_API_TOKEN=${QUANTCONNECT_API_TOKEN}" \
  --platform linux/arm64 \
  quantconnect/mcp-server 2>&1

rm /tmp/mcp_tools.json
