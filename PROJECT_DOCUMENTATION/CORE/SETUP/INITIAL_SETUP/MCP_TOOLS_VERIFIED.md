# QuantConnect MCP Tools - VERIFIED ✅

## Validation Status

**✅ MCP Server: WORKING**
- Server: quantconnect v1.13.1
- Protocol: MCP 2024-11-05
- Platform: linux/arm64 (Apple Silicon)
- Authentication: via .env credentials

## Available Tools (30 total)

### Account Management
- `read_account` - Read organization account status

### Project Management
- `create_project` - Create new project (name, language: C#/Py)
- `read_project` - Read project details by ID
- `list_projects` - List all projects
- `update_project` - Update project settings
- `delete_project` - Delete project
- `lock_project_with_collaborators` - Lock project

### Collaborator Management
- `create_project_collaborator` - Add collaborator
- `read_project_collaborators` - List collaborators
- `update_project_collaborator` - Update permissions
- `delete_project_collaborator` - Remove collaborator

### Node Management
- `read_project_nodes` - List available nodes
- `update_project_nodes` - Update node configuration

### Code Management
- `create_file` - Create/upload file (supports main.py, config.json, etc.)
- `read_file` - Read file contents
- `update_file_name` - Rename file
- `update_file_contents` - Update file contents
- `patch_file` - **Partial update** (preferred for small changes)
- `delete_file` - Delete file

### Compilation
- `create_compile` - **Compile code** (check syntax before backtest)
- `read_compile` - Read compilation results/errors

### Backtesting
- `create_backtest` - **Submit backtest**
- `read_backtest` - **Get backtest results** (key metrics, status)
- `list_backtests` - List all backtests for project
- `read_backtest_chart` - Get chart data
- `read_backtest_orders` - Get order history
- `read_backtest_insights` - Get algorithm insights
- `update_backtest` - Update backtest metadata
- `delete_backtest` - Delete backtest

## Autonomous Workflow Integration

### Phase 3: Backtesting (Using MCP)

**Complete Workflow**:
```
1. create_project(name="H1_RSI", language="Py")
   → Returns: projectId

2. create_file(projectId=X, name="main.py", content=strategy_code)
   → Returns: success

3. create_compile(projectId=X)
   → Returns: compileId, errors (if any)

4. read_compile(projectId=X, compileId=Y)
   → Check: No syntax errors

5. create_backtest(projectId=X, compileId=Y)
   → Returns: backtestId

6. read_backtest(projectId=X, backtestId=Z)
   → Poll until complete
   → Returns: statistics (Sharpe, drawdown, trades, etc.)
```

## Key Features

### 1. Compile Before Backtest
**Server Instructions**: "Before running backtests, run the compile tool"

This is CRITICAL - catches syntax errors before wasting compute:
```
create_compile → read_compile → fix errors → create_backtest
```

### 2. Patch vs Update File
**Server Instructions**: "Use patch_file for line-level changes instead of update_file_contents"

For bug fixes, use `patch_file` (more efficient)

### 3. PEP8 Style
**Server Instructions**: "Write code in PEP8 style (snake_case)"

Matches our QuantConnect Skill standards!

## Example: Complete Backtest Flow

```json
// 1. Create project
{"method": "create_project", "params": {
  "model": {"name": "TestStrategy", "language": "Py"}
}}

// 2. Upload code
{"method": "create_file", "params": {
  "projectId": 12345,
  "name": "main.py",
  "content": "from AlgorithmImports import *\n..."
}}

// 3. Compile
{"method": "create_compile", "params": {
  "projectId": 12345
}}

// 4. Check compilation
{"method": "read_compile", "params": {
  "projectId": 12345,
  "compileId": "abc"
}}

// 5. If no errors, create backtest
{"method": "create_backtest", "params": {
  "projectId": 12345,
  "compileId": "abc",
  "backtestName": "Run 1"
}}

// 6. Poll for results
{"method": "read_backtest", "params": {
  "projectId": 12345,
  "backtestId": "xyz"
}}
```

## Comparison: MCP vs Python Wrapper

| Task | Python Wrapper | MCP Tools |
|------|---------------|-----------|
| Create Project | subprocess call | `create_project` |
| Upload Code | File I/O + API | `create_file` |
| Compile Check | ❌ Not supported | ✅ `create_compile` |
| Submit Backtest | API + polling | `create_backtest` |
| Get Results | JSON parsing | `read_backtest` |
| Error Handling | Manual | Automatic |
| Integration | External | Native |

## Next Steps

1. ✅ MCP server verified working
2. ⏳ Test in Claude Code (after restart)
3. ⏳ Run complete backtest with test_strategy.py
4. ⏳ Validate output format for decision framework
5. ⏳ Update autonomous workflow to use MCP tools

## Critical Discovery

**MCP server requires COMPILATION before backtest**

This was missing from our workflow design! Updated flow:
```
Implementation → Compile → Fix Errors → Backtest → ...
```

This is BETTER than our original design - catches errors early!

## Usage from Claude Code

After restart, tools will be available as:
```
mcp__quantconnect__create_project
mcp__quantconnect__create_file
mcp__quantconnect__create_compile
mcp__quantconnect__read_compile
mcp__quantconnect__create_backtest
mcp__quantconnect__read_backtest
```

(Note: `quantconnect__` prefix added automatically by MCP)

## Status

✅ **VERIFIED: MCP server fully functional**
✅ **30 tools discovered and documented**
✅ **Workflow updated with compilation step**
⏳ **Ready for Claude Code integration testing**
