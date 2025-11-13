# QuantConnect MCP Server Integration

## Overview

The QuantConnect MCP (Model Context Protocol) Server provides **native Claude Code integration** for QuantConnect operations. This is **superior to the Python wrapper approach** because:

- ✅ Native tool integration (no subprocess calls)
- ✅ Automatic error handling
- ✅ Structured responses (no JSON parsing needed)
- ✅ Better context management
- ✅ Asynchronous support
- ✅ Built-in authentication

## Setup Complete

### Configuration File
**Location**: `~/.config/claude_code.json`

```json
{
  "mcpServers": {
    "quantconnect": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "QUANTCONNECT_USER_ID",
        "-e", "QUANTCONNECT_API_TOKEN",
        "-e", "AGENT_NAME",
        "--platform", "linux/arm64",
        "quantconnect/mcp-server"
      ]
    }
  }
}
```

### Docker Image
- **Status**: ✅ Pulled
- **Image**: `quantconnect/mcp-server:latest`
- **Platform**: `linux/arm64` (Apple Silicon)

### Environment Variables
The MCP server uses credentials from `.env`:
- `QUANTCONNECT_USER_ID`
- `QUANTCONNECT_API_TOKEN`
- `AGENT_NAME` (optional)

## Available MCP Tools

Once Claude Code restarts and connects to the MCP server, you'll have access to tools like:

**Expected Tools** (based on typical QuantConnect MCP servers):
- `mcp__quantconnect__list_projects` - List all projects
- `mcp__quantconnect__create_project` - Create new project
- `mcp__quantconnect__read_project` - Get project details
- `mcp__quantconnect__create_file` - Upload code to project
- `mcp__quantconnect__create_backtest` - Submit backtest
- `mcp__quantconnect__read_backtest` - Get backtest results
- `mcp__quantconnect__list_backtests` - List all backtests

**To discover actual tools**:
1. Restart Claude Code
2. Tools will appear with `mcp__quantconnect__` prefix
3. Use autocomplete or list available tools

## Usage in Autonomous Workflow

### Before (Python Wrapper):
```python
# Complex subprocess call
result = subprocess.run([
    "python3", "qc_backtest.py",
    "--run", "--name", "Strategy", "--file", "strategy.py"
], capture_output=True)

# Parse JSON manually
metrics = json.loads(result.stdout)
```

### After (MCP Tools):
```markdown
# Direct tool call from Claude
Use mcp__quantconnect__create_project to create "Strategy" project

Then use mcp__quantconnect__create_file to upload strategy.py

Then use mcp__quantconnect__create_backtest to run backtest

Then use mcp__quantconnect__read_backtest to get results

# Results are automatically structured!
```

## Integration with Autonomous Workflow

### Phase 3: Backtesting (Updated)

**Old Approach**:
```bash
python3 qc_backtest.py --run --name "H1" --file strategy.py
```

**New Approach (MCP)**:
```
1. mcp__quantconnect__create_project(name="H1")
2. mcp__quantconnect__create_file(project_id=X, name="main.py", content=strategy_code)
3. mcp__quantconnect__create_backtest(project_id=X)
4. mcp__quantconnect__read_backtest(project_id=X, backtest_id=Y)
```

**Benefits**:
- No external process management
- Automatic error handling
- Structured responses (no JSON parsing)
- Native Claude Code integration
- Can monitor progress in real-time
- Better context usage

## Testing MCP Server

### Step 1: Restart Claude Code
After configuration, restart Claude Code to load MCP server.

### Step 2: List Available Tools
```
Ask Claude: "What MCP tools are available?"
```

You should see tools prefixed with `mcp__quantconnect__`

### Step 3: Test Connection
```
Use mcp__quantconnect__list_projects to list my QuantConnect projects
```

### Step 4: Run Test Backtest
```
1. Create a project called "TestMCP"
2. Upload test_strategy.py
3. Run backtest
4. Get results
```

## Updated Workflow Architecture

### Minimum Viable System (Week 1-2)
- ✅ QuantConnect Skill
- ✅ MCP Server configured
- ⏳ Test MCP tools
- ⏳ Manual workflow with MCP

### Phase 2: Automation (Week 3-4)
- Plugin commands call MCP tools directly
- `/qc-backtest` → MCP tool wrapper
- Simpler, more reliable

### Phase 3: Full Autonomy (Week 5-8)
- Master loop uses MCP tools
- No subprocess management
- Native error handling
- Cleaner code

## Advantages Over Python Wrapper

| Aspect | Python Wrapper | MCP Server |
|--------|---------------|------------|
| Integration | Subprocess | Native Claude tool |
| Error Handling | Manual parsing | Automatic |
| Response Format | JSON strings | Structured objects |
| Authentication | Manual | Automatic from .env |
| Async Support | No | Yes |
| Context Usage | Higher (tool + results) | Lower (just results) |
| Reliability | External process | Native runtime |
| Development | Custom code | Standard protocol |

## Migration Plan

**Keep Python Wrapper For**:
- Standalone CLI usage
- Non-Claude Code environments
- Debugging and development

**Use MCP Tools For**:
- Claude Code autonomous operation
- Plugin commands
- Agent SDK integration

**Both approaches are valid** - MCP for Claude Code, wrapper for standalone scripts.

## Next Steps

1. **Restart Claude Code** to activate MCP server
2. **Test MCP tools** - list projects, create project
3. **Update autonomous workflow** to use MCP tools
4. **Document actual MCP tool signatures** (names, parameters, responses)
5. **Run manual workflow** using MCP instead of wrapper

## Comparison: Wrapper vs MCP

### Backtest Execution

**Python Wrapper**:
```bash
$ python3 qc_backtest.py --run --name "Test" --file strategy.py --output results.json

=== Creating Project ===
Project ID: 12345

=== Uploading Code ===
File created: main.py

=== Running Backtest ===
Backtest ID: abc123
Status: InProgress... (polling every 5s)
Status: Completed

=== Results ===
{
  "sharpe_ratio": 1.2,
  "max_drawdown": 0.15
}
```

**MCP Tools**:
```
Claude: Create a QuantConnect project called "Test" and run a backtest

[Uses mcp__quantconnect__create_project]
Project created: ID 12345

[Uses mcp__quantconnect__create_file with strategy code]
File uploaded: main.py

[Uses mcp__quantconnect__create_backtest]
Backtest started: ID abc123

[Uses mcp__quantconnect__read_backtest]
Results: Sharpe 1.2, Drawdown 15%
```

**Result**: Same outcome, but MCP is:
- More natural (conversational)
- Automatic (no manual subprocess)
- Integrated (native to Claude Code)
- Reliable (standard protocol)

## Conclusion

**MCP Server integration is a MAJOR upgrade** to the autonomous workflow:

- ✅ Cleaner architecture
- ✅ Better error handling
- ✅ Native Claude Code integration
- ✅ Simpler plugin development
- ✅ More reliable autonomous operation

**Status**: Configuration complete, ready to test after Claude Code restart.
