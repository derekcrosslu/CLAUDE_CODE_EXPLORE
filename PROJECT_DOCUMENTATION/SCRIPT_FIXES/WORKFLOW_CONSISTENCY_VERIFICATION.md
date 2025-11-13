# Workflow Consistency Verification Report

**Date:** 2025-11-13
**Purpose:** Verify consistency across all QC commands and scripts
**Requested Workflow:** Each phase independent, all read project_id from iteration_state.json

---

## Expected Workflow

```
/qc-init      → Creates iteration_state.json (no QC project yet)
/qc-backtest  → Creates QC project on FIRST run, saves project_id to iteration_state.json
                Uses project_id for ALL subsequent backtests
/qc-optimize  → Reads project_id from iteration_state.json, uploads optimized file, runs optimization
                NO dependency on qc_backtest.py
/qc-validate  → Reads project_id from iteration_state.json, uploads research.ipynb, runs MC validation
                NO dependency on qc_backtest.py
```

---

## Actual Current State

### ✅ CORRECT: `/qc-init`
**Command:** `.claude/commands/qc-init.md`
**Script:** N/A (uses bash commands directly)

**What it does:**
1. Creates git branch
2. Creates `iteration_state.json` from template
3. **Does NOT create QC project** (correct - project created in backtest phase)

**Status:** ✅ CORRECT

---

### ✅ MOSTLY CORRECT: `/qc-backtest`
**Command:** `.claude/commands/qc-backtest.md`
**Script:** `SCRIPTS/qc_backtest.py`

**What it does:**
1. Reads `iteration_state.json` for project_id
2. If project_id is null:
   - Creates NEW QC project via `qc_backtest.py --create`
   - Saves project_id to iteration_state.json
3. If project_id exists:
   - Uses `qc_backtest.py --run --project-id {ID}` to reuse project
   - Uploads strategy file
   - Runs backtest

**Command Says (Line 188):**
```
- `/qc-init` → Creates project, saves PROJECT_ID to iteration_state.json
```

**❌ INCORRECT DOCUMENTATION:**
- `/qc-init` does NOT create QC project
- `/qc-backtest` creates QC project on first run

**Correct Statement:**
```
- `/qc-init` → Creates iteration_state.json (project_id = null)
- `/qc-backtest` (first run) → Creates QC project, saves project_id
- `/qc-backtest` (subsequent) → Reuses project_id
```

**Script Status:** ✅ CORRECT (but we fixed it recently to respect --project-id)

---

### ❌ INCORRECT: `/qc-optimize`
**Command:** `.claude/commands/qc-optimize.md`
**Script:** `SCRIPTS/qc_optimize.py`

**What command says (Line 16):**
```
- Read `iteration_state.json` to get current project_id
```

**What command does (Line 43):**
```
- Use `qc_backtest.py --optimize` with native QC API
```

**❌ PROBLEMS:**

1. **Command depends on qc_backtest.py**
   - Line 43: "Use `qc_backtest.py --optimize`"
   - This violates independence principle

2. **Script depends on qc_backtest.py for API client**
   - `qc_optimize.py` line 28: `from qc_backtest import QuantConnectAPI`
   - Should have its OWN API client

**Expected Behavior:**
```python
# qc_optimize.py should:
1. Read iteration_state.json for project_id
2. Have its OWN QuantConnectAPI class (no import from qc_backtest)
3. Upload optimized strategy file
4. Run optimization via QC API
5. Save results to iteration_state.json
```

**Status:** ❌ NEEDS FIX

---

### ❌ INCORRECT: `/qc-validate`
**Command:** `.claude/commands/qc-validate.md`
**Script:** `SCRIPTS/qc_validate.py`

**What command says (Line 9):**
```
- Do NOT create a new project for validation
- Validation runs on the SAME project created during /qc-init
```

**❌ INCORRECT DOCUMENTATION:**
- Project NOT created in /qc-init
- Project created in /qc-backtest (first run)

**What script does:**
- `qc_validate.py` line 28: `from qc_backtest import QuantConnectAPI`
- Depends on qc_backtest.py for API client

**❌ PROBLEMS:**

1. **Script depends on qc_backtest.py for API client**
   - Should have its OWN API client

2. **Does NOT implement advanced Monte Carlo**
   - Current implementation: Simple train/test split
   - User needs: PSR, DSR, MinTRL, MACHR, bootstrap, permutation testing

3. **Does NOT use QC Research QuantBook**
   - Current: Uses backtest API
   - User needs: research.ipynb executed online

**Expected Behavior:**
```python
# qc_validate.py should:
1. Read iteration_state.json for project_id
2. Have its OWN QuantConnectAPI class (no import from qc_backtest)
3. Generate research.ipynb with advanced MC metrics
4. Upload research.ipynb to project_id
5. Prompt user to run notebook online
6. Collect results
7. Make decision based on PSR/DSR/WFE thresholds
8. Save results to iteration_state.json
```

**Status:** ❌ NEEDS MAJOR OVERHAUL

---

## Dependency Analysis

### Current Dependencies

```
qc_backtest.py (self-contained)
    ↑
    |--- qc_optimize.py imports QuantConnectAPI
    |
    |--- qc_validate.py imports QuantConnectAPI
```

**Problem:** Both qc_optimize.py and qc_validate.py depend on qc_backtest.py

### Desired Independence

```
qc_backtest.py (self-contained, has own API client)

qc_optimize.py (self-contained, has own API client)

qc_validate.py (self-contained, has own API client)
```

**Solution:** Each script has its own QuantConnectAPI class

---

## Fixes Needed

### Fix 1: Correct Documentation in `/qc-backtest`

**File:** `.claude/commands/qc-backtest.md` (Line 188)

**Change FROM:**
```
- `/qc-init` → Creates project, saves PROJECT_ID to iteration_state.json
```

**Change TO:**
```
- `/qc-init` → Creates iteration_state.json (project_id = null)
- `/qc-backtest` (first run) → Creates QC project, saves project_id
```

---

### Fix 2: Remove qc_backtest.py dependency from qc_optimize.py

**File:** `SCRIPTS/qc_optimize.py`

**Change FROM:**
```python
try:
    sys.path.insert(0, str(SCRIPT_DIR))
    from qc_backtest import QuantConnectAPI
except ImportError:
    click.echo("❌ Error: qc_backtest.py not found. Ensure it exists in SCRIPTS/", err=True)
    sys.exit(1)
```

**Change TO:**
```python
# Own QC API client (no dependency on qc_backtest.py)
import requests
from typing import Dict, Any

class QuantConnectAPI:
    """QC API client for optimization operations"""
    def __init__(self, user_id: str, api_token: str):
        self.user_id = user_id
        self.api_token = api_token
        self.base_url = "https://api.quantconnect.com/v2"
        self.auth = (user_id, api_token)

    def upload_file(self, project_id: int, file_name: str, content: str) -> Dict[str, Any]:
        """Upload file to QC project"""
        url = f"{self.base_url}/files/create"
        data = {
            "projectId": project_id,
            "name": file_name,
            "content": content
        }
        response = requests.post(url, json=data, auth=self.auth)
        return response.json()

    def create_optimization(self, project_id: int, compile_id: str, params: Dict) -> Dict[str, Any]:
        """Create optimization job"""
        url = f"{self.base_url}/optimizations/create"
        data = {
            "projectId": project_id,
            "compileId": compile_id,
            "name": params.get("name", "Optimization"),
            "target": params.get("target"),
            "targetTo": params.get("targetTo", "max"),
            "targetValue": params.get("targetValue"),
            "strategy": params.get("strategy", "grid"),
            "constraints": params.get("constraints", []),
            "estimatedCost": params.get("estimatedCost"),
            "nodeType": params.get("nodeType", "O2-8"),
            "parallelNodes": params.get("parallelNodes", 2)
        }
        response = requests.post(url, json=data, auth=self.auth)
        return response.json()

    def get_optimization(self, optimization_id: str) -> Dict[str, Any]:
        """Get optimization status/results"""
        url = f"{self.base_url}/optimizations/read"
        params = {"optimizationId": optimization_id}
        response = requests.get(url, params=params, auth=self.auth)
        return response.json()

    @classmethod
    def from_env(cls):
        """Create API client from environment variables"""
        import os
        user_id = os.getenv("QC_USER_ID")
        api_token = os.getenv("QC_API_TOKEN")
        if not user_id or not api_token:
            raise ValueError("QC_USER_ID and QC_API_TOKEN must be set")
        return cls(user_id, api_token)
```

---

### Fix 3: Update qc-optimize command to NOT use qc_backtest.py

**File:** `.claude/commands/qc-optimize.md` (Line 43)

**Change FROM:**
```
- Use `qc_backtest.py --optimize` with native QC API
```

**Change TO:**
```
- Use `qc_optimize.py run` with native QC API
```

---

### Fix 4: Remove qc_backtest.py dependency from qc_validate.py

**File:** `SCRIPTS/qc_validate.py`

**Same as Fix 2 - add own QuantConnectAPI class**

---

### Fix 5: Implement Advanced Monte Carlo in qc_validate.py

**File:** `SCRIPTS/qc_validate.py`

**Add:**
1. `generate_notebook()` command - creates research.ipynb
2. `upload_notebook()` command - uploads to QC project
3. `collect_results()` command - parses MC results
4. PSR/DSR/MinTRL/MACHR implementation in notebook template

**Details:** See `VALIDATION_FIX_PLAN.md`

---

### Fix 6: Delete `/qc-walkforward` command

**File:** `.claude/commands/qc-walkforward.md`

**Action:** DELETE (redundant with new qc-validate)

---

## Consistent project_id Usage

### ✅ ALL scripts should:

```python
# At the start of EVERY command:
def run_command():
    # Read iteration_state.json
    state_file = Path('iteration_state.json')
    if not state_file.exists():
        print("❌ Error: iteration_state.json not found")
        print("Run /qc-init first to initialize hypothesis")
        sys.exit(1)

    state = json.load(open(state_file))
    project_id = state.get('project', {}).get('project_id')

    if not project_id:
        print("❌ Error: No project_id found in iteration_state.json")
        print("Run /qc-backtest first to create QC project")
        sys.exit(1)

    # Use project_id for all operations
    api = QuantConnectAPI.from_env()
    api.upload_file(project_id, ...)
```

### ❌ NEVER accept project_id as CLI argument

```python
# WRONG:
@cli.command()
@click.option('--project-id', required=True)
def command(project_id):
    ...

# CORRECT:
@cli.command()
def command():
    state = json.load(open('iteration_state.json'))
    project_id = state['project']['project_id']
    ...
```

---

## Summary of Required Changes

| Component | Status | Required Action |
|-----------|--------|-----------------|
| `/qc-init` | ✅ Correct | None |
| `/qc-backtest` command | ⚠️ Minor doc fix | Fix line 188 documentation |
| `/qc-backtest` script | ✅ Correct | None (recently fixed) |
| `/qc-optimize` command | ❌ Needs fix | Remove qc_backtest.py reference (line 43) |
| `/qc-optimize` script | ❌ Needs fix | Add own API client, remove import |
| `/qc-validate` command | ❌ Needs overhaul | Document advanced MC workflow |
| `/qc-validate` script | ❌ Needs overhaul | Add own API client, implement MC |
| `/qc-walkforward` | ❌ Delete | Remove redundant command |

---

## Implementation Priority

1. **HIGH: Fix qc_optimize.py** - Remove qc_backtest.py dependency
2. **HIGH: Fix qc_validate.py** - Remove qc_backtest.py dependency + implement MC
3. **MEDIUM: Update qc-optimize.md** - Fix command references
4. **MEDIUM: Update qc-backtest.md** - Fix documentation line 188
5. **LOW: Delete qc-walkforward.md** - Remove redundant command

---

## User Approval Required

Should I proceed with these fixes in this order?

1. Fix qc_optimize.py (add own API client)
2. Fix qc_validate.py (add own API client + advanced MC)
3. Update command documentation
4. Delete qc-walkforward.md

**Estimated Effort:**
- Fix 1 (qc_optimize.py): 30 minutes
- Fix 2 (qc_validate.py): 2-3 hours (complex MC implementation)
- Fix 3 (docs): 15 minutes
- Fix 4 (delete): 5 minutes

**Total:** ~3-4 hours of implementation

---

**Waiting for user approval to proceed.**
