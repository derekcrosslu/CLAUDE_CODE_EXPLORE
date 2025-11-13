#!/bin/bash
# Test QuantConnect MCP Server

# Load credentials
source .env

# Test MCP server
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
docker run -i --rm \
  -e "QUANTCONNECT_USER_ID=${QUANTCONNECT_USER_ID}" \
  -e "QUANTCONNECT_API_TOKEN=${QUANTCONNECT_API_TOKEN}" \
  --platform linux/arm64 \
  quantconnect/mcp-server
