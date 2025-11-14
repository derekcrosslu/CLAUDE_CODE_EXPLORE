# Complete Command Hierarchy Mapping

**Date Created**: 2025-11-13
**Purpose**: Map all CLI commands to underlying API methods for complete workflow understanding

---

## qc_optimize.py (Phase 4 - Parameter Optimization)

### CLI Commands

**help** - Show reference documentation from JSON
```bash
qc_optimize help                      # Full help
qc_optimize help --section <id>       # Specific section
qc_optimize help --search <query>     # Search help
qc_optimize help --list-sections      # List all sections
```

**run** - Execute parameter optimization
```bash
qc_optimize run --config params.json [options]

Options:
  --config PATH           Optimization parameters JSON (required)
  --state PATH           iteration_state.json path (default: iteration_state.json)
  --output PATH          Output file (default: PROJECT_LOGS/optimization_result.json)
  --estimate-only        Only estimate cost, don't run
  --strategy TEXT        Grid search strategy (default: grid)
  --max-backtests INT    Maximum backtests for random strategies
```

**status** - Check optimization status
```bash
qc_optimize status --optimization-id <id>
```

**results** - Download optimization results
```bash
qc_optimize results --optimization-id <id> [--output PATH]
```

### API Methods Used

**run command uses**:
1. `api.estimate_optimization()` - Estimate cost (if --estimate-only or before run)
2. `api.create_optimization()` - Submit optimization job
3. `api.wait_for_optimization()` - Poll until complete
4. `api.get_optimization_results()` - Retrieve final results

**status command uses**:
1. `api.get_optimization_status()` - Get current status

**results command uses**:
1. `api.get_optimization_results()` - Download complete results

### Workflow Mapping

```
qc_optimize run --config params.json
├─ Read iteration_state.json → Extract project_id
├─ Load params.json → Parse parameters
├─ api.estimate_optimization(project_id, params, ...)
│  └─ POST /optimize/estimate
├─ api.create_optimization(project_id, name, target, params, ...)
│  └─ POST /optimize/create
├─ api.wait_for_optimization(optimization_id, timeout=1800)
│  ├─ Loop every 15 seconds:
│  │  └─ api.get_optimization_status(optimization_id)
│  │     └─ GET /optimize/read
│  └─ Until status == 'completed' or timeout
└─ api.get_optimization_results(optimization_id)
   └─ GET /optimize/read (full results)
```

---

## qc_validate.py (Phase 5 - Walk-Forward Validation)

### CLI Commands

**help** - Show reference documentation from JSON
```bash
qc_validate help                      # Full help
qc_validate help --section <id>       # Specific section
qc_validate help --search <query>     # Search help
qc_validate help --list-sections      # List all sections
```

**run** - Execute walk-forward validation
```bash
qc_validate run --strategy strategy.py [options]

Options:
  --strategy PATH        Strategy file to validate (required)
  --state PATH          iteration_state.json path (default: iteration_state.json)
  --split FLOAT         IS/OOS split ratio (default: 0.80 for 80/20)
  --output PATH         Output file (default: PROJECT_LOGS/validation_result.json)
```

**analyze** - Analyze validation results
```bash
qc_validate analyze --results PATH

Options:
  --results PATH        validation_result.json file (required)
```

### API Methods Used

**run command uses**:
1. `api.read_files()` - Read strategy from project
2. `api.upload_file()` - Upload modified IS strategy
3. `api.create_backtest()` - Run IS backtest
4. `api.wait_for_backtest()` - Wait for IS completion
5. `api.upload_file()` - Upload modified OOS strategy
6. `api.create_backtest()` - Run OOS backtest
7. `api.wait_for_backtest()` - Wait for OOS completion
8. `api.read_backtest()` - Read both backtest results

**analyze command uses**:
- No API calls (analyzes local JSON file)

### Workflow Mapping

```
qc_validate run --strategy strategy.py
├─ Read iteration_state.json → Extract project_id
├─ api.read_files(project_id, "main.py")
│  └─ GET /files/read
├─ Modify code for IS period (2019-2022)
├─ api.upload_file(project_id, "main.py", is_code)
│  ├─ Check if file exists: api.read_files(project_id)
│  ├─ If exists: POST /files/update
│  └─ If not: POST /files/create
├─ api.create_backtest(project_id, name="Validation_IS")
│  └─ POST /backtests/create
├─ api.wait_for_backtest(project_id, backtest_id_is, timeout=600)
│  ├─ Loop every 5 seconds:
│  │  └─ api.read_backtest(project_id, backtest_id_is)
│  │     └─ GET /backtests/read
│  └─ Until status == 'Completed'
├─ Modify code for OOS period (2023)
├─ api.upload_file(project_id, "main.py", oos_code)
│  └─ POST /files/update
├─ api.create_backtest(project_id, name="Validation_OOS")
│  └─ POST /backtests/create
├─ api.wait_for_backtest(project_id, backtest_id_oos, timeout=600)
│  └─ (same polling as IS)
├─ api.read_backtest(project_id, backtest_id_is)
├─ api.read_backtest(project_id, backtest_id_oos)
└─ Calculate degradation, robustness, decision
```

---

## qc_backtest.py (Phase 3 - Baseline Backtest)

### CLI Commands

**help** - Show reference documentation from JSON
```bash
qc_backtest help                      # Full help
qc_backtest help --section <id>       # Specific section
qc_backtest help --search <query>     # Search help
qc_backtest help --list-sections      # List all sections
```

**run** - Execute backtest
```bash
qc_backtest run --file strategy.py [options]

Options:
  --file PATH           Strategy file to backtest (required)
  --name TEXT          Project name (default: auto-generated)
  --state PATH         iteration_state.json path (default: iteration_state.json)
  --output PATH        Output file (default: PROJECT_LOGS/backtest_result.json)
  --create-project     Create new project (default: use existing from state)
```

**status** - Check backtest status
```bash
qc_backtest status --backtest-id <id> --project-id <id>
```

**results** - Download backtest results
```bash
qc_backtest results --backtest-id <id> --project-id <id> [--output PATH]
```

### API Methods Used

**run command uses**:
1. `api.create_project()` - Create project (ONLY if none exists in iteration_state.json)
2. `api.upload_file()` - Upload strategy
3. `api.compile_project()` - Compile strategy
4. `api.read_compile()` - Check compilation status
5. `api.create_backtest()` - Submit backtest
6. `api.wait_for_backtest()` - Poll until complete
7. `api.parse_backtest_results()` - Extract metrics

**status command uses**:
1. `api.read_backtest()` - Get backtest status

**results command uses**:
1. `api.read_backtest()` - Download complete results

### Workflow Mapping

```
qc_backtest run --file strategy.py
├─ Read iteration_state.json
│  ├─ If project_id exists: Use existing project
│  └─ If no project_id: Create new project
├─ If creating new project:
│  └─ api.create_project(name, language="Py")
│     └─ POST /projects/create
├─ api.upload_file(project_id, "main.py", code)
│  ├─ api.read_files(project_id) to check if exists
│  ├─ If exists: POST /files/update
│  └─ If not: POST /files/create
├─ api.compile_project(project_id)
│  └─ POST /compile/create
├─ api.read_compile(project_id, compile_id)
│  └─ GET /compile/read
├─ api.create_backtest(project_id, compile_id, name)
│  └─ POST /backtests/create
├─ api.wait_for_backtest(project_id, backtest_id, timeout=600)
│  ├─ Loop every 5 seconds:
│  │  └─ api.read_backtest(project_id, backtest_id)
│  │     └─ GET /backtests/read
│  └─ Until status == 'Completed'
├─ api.parse_backtest_results(backtest_data)
│  └─ Extract: sharpe, drawdown, trades, win_rate, etc.
└─ Save to PROJECT_LOGS/backtest_result.json
```

---

## qc_api.py - Complete API Reference

### Authentication

**QuantConnectAPI(user_id=None, api_token=None)**
```python
api = QuantConnectAPI()  # Reads from .env
# or
api = QuantConnectAPI(user_id="123", api_token="abc")
```

### Project Management

**list_projects()**
```python
result = api.list_projects()
# Returns: {'success': True, 'projects': [...]}
```

**create_project(name, language="Py")**
```python
result = api.create_project("My Strategy", language="Py")
# Returns: {'success': True, 'projects': {'projectId': 12345, ...}}
```

**read_project(project_id)**
```python
result = api.read_project(12345)
# Returns: {'success': True, 'projects': {'projectId': 12345, ...}}
```

**delete_project(project_id)**
```python
result = api.delete_project(12345)
# Returns: {'success': True}
```

### File Operations

**read_files(project_id, filename=None)**
```python
# Read all files
result = api.read_files(12345)
# Returns: {'success': True, 'files': [{'name': 'main.py', 'content': '...'}]}

# Read specific file
result = api.read_files(12345, "main.py")
# Returns: {'success': True, 'files': [{'name': 'main.py', 'content': '...'}]}
```

**create_file(project_id, name, content)**
```python
result = api.create_file(12345, "main.py", "# Strategy code")
# Returns: {'success': True, 'files': [{'name': 'main.py', ...}]}
```

**upload_file(project_id, name, content)**
```python
# Handles create OR update automatically
result = api.upload_file(12345, "main.py", "# Updated code")
# Returns: {'success': True, 'files': [{'name': 'main.py', ...}]}
```

**delete_file(project_id, name)**
```python
result = api.delete_file(12345, "main.py")
# Returns: {'success': True}
```

### Compilation

**compile_project(project_id)**
```python
result = api.compile_project(12345)
# Returns: {'success': True, 'compileId': 'abc123', 'state': 'InQueue'}
```

**read_compile(project_id, compile_id)**
```python
result = api.read_compile(12345, "abc123")
# Returns: {'success': True, 'state': 'BuildSuccess', 'logs': [...]}
```

### Backtesting

**create_backtest(project_id, compile_id=None, name=None)**
```python
result = api.create_backtest(12345, compile_id="abc", name="Backtest_v1")
# Returns: {'success': True, 'backtests': [{'backtestId': 'xyz', ...}]}
```

**read_backtest(project_id, backtest_id)**
```python
result = api.read_backtest(12345, "xyz")
# Returns: {'success': True, 'backtest': {'backtestId': 'xyz', 'status': 'Completed', ...}}
```

**delete_backtest(project_id, backtest_id)**
```python
result = api.delete_backtest(12345, "xyz")
# Returns: {'success': True}
```

**wait_for_backtest(project_id, backtest_id, timeout=300, poll_interval=5)**
```python
result = api.wait_for_backtest(12345, "xyz", timeout=600)
# Polls every 5 seconds until complete or timeout
# Returns: {'success': True, 'backtest': {'status': 'Completed', ...}}
```

**parse_backtest_results(backtest_data)**
```python
metrics = api.parse_backtest_results(backtest_data)
# Returns: {
#   'sharpe_ratio': 0.85,
#   'max_drawdown': 0.22,
#   'total_return': 0.45,
#   'total_trades': 67,
#   'win_rate': 0.42,
#   ...
# }
```

**read_backtest_results(project_id, backtest_id)**
```python
# Convenience method: read + parse in one call
metrics = api.read_backtest_results(12345, "xyz")
# Returns: Same as parse_backtest_results()
```

### Optimization

**estimate_optimization(project_id, parameters, node_type="O2-8", parallel_nodes=2)**
```python
params = [
    {"name": "rsi_period", "min": 10, "max": 20, "step": 5}
]
result = api.estimate_optimization(12345, params, node_type="O2-8", parallel_nodes=2)
# Returns: {'success': True, 'estimatedCost': 3.50, ...}
```

**create_optimization(project_id, name, target, parameters, target_to="max", strategy="...", node_type="O2-8", parallel_nodes=2)**
```python
result = api.create_optimization(
    project_id=12345,
    name="Optimization_20251113",
    target="TotalPerformance.PortfolioStatistics.SharpeRatio",
    parameters=params,
    target_to="max",
    strategy="QuantConnect.Optimizer.Strategies.GridSearchOptimizationStrategy",
    node_type="O2-8",
    parallel_nodes=2
)
# Returns: {'success': True, 'optimizations': [{'optimizationId': 'opt123', ...}]}
```

**read_optimization(optimization_id)**
```python
result = api.read_optimization("opt123")
# Returns: {'success': True, 'optimization': {'optimizationId': 'opt123', ...}}
```

**delete_optimization(optimization_id)**
```python
result = api.delete_optimization("opt123")
# Returns: {'success': True}
```

**wait_for_optimization(optimization_id, timeout=1800, poll_interval=15)**
```python
result = api.wait_for_optimization("opt123", timeout=1800)
# Polls every 15 seconds until complete or timeout
# Returns: {'success': True, 'optimization': {'status': 'completed', ...}}
```

**get_optimization_status(optimization_id)**
```python
result = api.get_optimization_status("opt123")
# Returns: {'success': True, 'optimization': {'status': 'running', 'progress': 0.45, ...}}
```

**get_optimization_results(optimization_id)**
```python
result = api.get_optimization_results("opt123")
# Returns: {'success': True, 'optimization': {'sharpeRatio': 1.2, 'parameterSet': [...], ...}}
```

---

## Workflow Integration

### Phase 3: Backtest (qc_backtest.py)
```
/qc-backtest
  ↓
qc_backtest run --file strategy.py
  ↓
API: create_project() → upload_file() → compile_project() → create_backtest() → wait_for_backtest()
  ↓
Updates: iteration_state.json (project_id, backtest_id, performance metrics)
```

### Phase 4: Optimize (qc_optimize.py)
```
/qc-optimize
  ↓
qc_optimize run --config params.json
  ↓
Reads: iteration_state.json (project_id from Phase 3)
  ↓
API: estimate_optimization() → create_optimization() → wait_for_optimization() → get_optimization_results()
  ↓
Updates: iteration_state.json (optimization results, decision)
```

### Phase 5: Validate (qc_validate.py)
```
/qc-validate
  ↓
qc_validate run --strategy strategy.py
  ↓
Reads: iteration_state.json (project_id, final parameters)
  ↓
API: read_files() → upload_file() (IS) → create_backtest() (IS) → wait_for_backtest() (IS)
     → upload_file() (OOS) → create_backtest() (OOS) → wait_for_backtest() (OOS)
  ↓
Updates: iteration_state.json (validation results, decision)
```

---

## Critical Rules

1. **NEVER create new project in Phase 4 or Phase 5** - Always use project_id from iteration_state.json
2. **upload_file() handles create/update** - No need to check if file exists first
3. **wait_for_X() methods block** - They poll automatically until completion or timeout
4. **All methods return dict with 'success' key** - Always check `if result['success']:`
5. **Timestamps in UTC ISO format** - Use `datetime.utcnow().isoformat() + 'Z'`

---

**Version**: 1.0.0
**Last Updated**: 2025-11-13
**Status**: Complete command hierarchy mapping
