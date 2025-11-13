# Fix Plan: Unified Validation with Advanced Monte Carlo

**Date:** 2025-11-13
**Issue:** Broken validation workflow - commands don't implement intended advanced Monte Carlo
**Root Cause:** Confusion between simple API backtests and Research QuantBook validation

---

## The Problem (Clear and Simple)

**User Intent:**
```
/qc-validate → Advanced Monte Carlo validation using QC Research notebook (research.ipynb)
                Implements: PSR, DSR, MinTRL, MACHR, bootstrap, permutation testing
                Executes: Online in QC web interface (QuantBook)
```

**Current Reality:**
- `/qc-validate`: Simple single OOS test via API (NOT Monte Carlo)
- `/qc-walkforward`: Basic MC walk-forward via API (NOT advanced metrics)
- **NEITHER** uses QC Research QuantBook
- **NEITHER** implements PSR/DSR/MinTRL/MACHR
- Confusion: Calls `qc_backtest.py` to upload notebooks (wrong dependency)

---

## The Solution (Single Valid Path)

### ONE Command: `/qc-validate`

**Purpose:** Advanced Monte Carlo validation using QC Research QuantBook

**Workflow:**
1. Read iteration_state.json (get project_id, backtest results, parameters)
2. Generate research.ipynb with full advanced Monte Carlo:
   - PSR (Probabilistic Sharpe Ratio ≥0.95)
   - DSR (Deflated Sharpe Ratio)
   - MinTRL (Minimum Track Record Length)
   - WFE (Walk-Forward Efficiency ≥50%)
   - Bootstrap resampling (1,000-10,000 runs)
   - MACHR (Market Condition Historical Randomization)
   - Permutation testing (p < 0.05)
   - Monte Carlo drawdown distribution (99th percentile)
3. **Upload research.ipynb using qc_validate.py's OWN upload method**
4. Prompt user to run notebook online in QC
5. Wait for user to return with results
6. Parse results, make decision, update iteration_state.json
7. Git commit with validation results

**Script:** `SCRIPTS/qc_validate.py`
- Self-contained (NO dependency on qc_backtest.py for uploads)
- Has its own QC API client
- Has its own upload_file() method
- **ALWAYS reads iteration_state.json for project_id** (NEVER passed as argument)
- Generates research.ipynb from template
- Uploads directly to project_id from iteration_state.json

**CRITICAL RULE:**
```python
# qc_validate.py ALWAYS does this:
state = json.load(open('iteration_state.json'))
project_id = state['project']['project_id']

# NEVER accept project_id as CLI argument
# Source of truth: iteration_state.json
```

**Command:** `.claude/commands/qc-validate.md`
- Single purpose: Advanced Monte Carlo
- No flags, no levels, no complexity
- ONE clear workflow

---

## What to Delete

**Delete:** `/qc-walkforward` command
- File: `.claude/commands/qc-walkforward.md`
- Reason: Redundant, confusing, not implementing advanced MC

**Reason:** Walk-forward analysis is PART of Monte Carlo validation, not a separate command

---

## Implementation Plan

### Phase 1: Fix qc_validate.py Script

**Current Status:**
- ✅ Script exists: `SCRIPTS/qc_validate.py`
- ❌ Uses simple train/test split (not Monte Carlo)
- ❌ Depends on `qc_backtest.py` for API (wrong)

**Changes Needed:**

1. **Remove dependency on qc_backtest.py**
   ```python
   # REMOVE THIS:
   from qc_backtest import QuantConnectAPI

   # ADD THIS:
   # Own QC API client implementation
   class QuantConnectAPI:
       def __init__(self, user_id, api_token):
           self.user_id = user_id
           self.api_token = api_token
           self.base_url = "https://api.quantconnect.com/v2"

       def upload_file(self, project_id, file_name, content):
           """Upload file to QC project"""
           # Implementation

       def get_project(self, project_id):
           """Get project details"""
           # Implementation
   ```

2. **Add research.ipynb generation**
   ```python
   def generate_research_notebook(backtest_id, parameters, time_periods):
       """Generate research.ipynb with advanced Monte Carlo"""
       notebook = {
           "cells": [
               # Cell 1: Initialize QuantBook
               {
                   "cell_type": "code",
                   "source": [
                       "from QuantConnect import *\n",
                       "from QuantConnect.Research import *\n",
                       "import numpy as np\n",
                       "import pandas as pd\n",
                       "from scipy import stats\n"
                   ]
               },
               # Cell 2: Load backtest results
               # Cell 3: Implement PSR calculation
               # Cell 4: Implement DSR calculation
               # Cell 5: Bootstrap resampling
               # Cell 6: MACHR regime testing
               # Cell 7: Permutation testing
               # Cell 8: MC drawdown distribution
               # Cell 9: Final decision and export results
           ]
       }
       return json.dumps(notebook)
   ```

3. **Add upload logic**
   ```python
   @cli.command()
   @click.option('--file', required=True, help='Notebook file path')
   def upload_notebook(file):
       """Upload research.ipynb to QC project"""
       # ALWAYS read project_id from iteration_state.json
       state = json.load(open('iteration_state.json'))
       project_id = state['project']['project_id']

       api = QuantConnectAPI.from_env()

       with open(file) as f:
           content = f.read()

       result = api.upload_file(project_id, "research.ipynb", content)

       if result['success']:
           print(f"✅ Uploaded research.ipynb to project {project_id}")
           print(f"🔗 https://www.quantconnect.com/project/{project_id}")
           print("\n📋 Next Steps:")
           print("1. Open QuantConnect web interface")
           print("2. Click 'Research' tab")
           print("3. Open research.ipynb")
           print("4. Run all cells")
           print("5. Return here when complete")
       else:
           print(f"❌ Upload failed: {result.get('error')}")
   ```

4. **Add result collection**
   ```python
   @cli.command()
   def collect_results():
       """Collect Monte Carlo results from research notebook"""
       # ALWAYS read project_id from iteration_state.json
       state = json.load(open('iteration_state.json'))
       project_id = state['project']['project_id']

       print("📥 Collecting Monte Carlo validation results...")
       print("\nPlease paste the results JSON from notebook output:")
       print("(Copy from last cell output in research.ipynb)")

       results_json = input("\nResults JSON: ")
       results = json.loads(results_json)

       # Parse and validate
       psr = results.get('psr')
       dsr = results.get('dsr')
       min_trl = results.get('min_trl')
       wfe = results.get('wfe')

       # Make decision
       decision = make_decision(psr, dsr, wfe)

       # Update iteration_state.json
       update_state(decision, results)

       print(f"\n✅ Validation Complete: {decision}")
   ```

### Phase 2: Update /qc-validate Command

**File:** `.claude/commands/qc-validate.md`

**New Content:**
```markdown
Run advanced Monte Carlo validation using QC Research QuantBook.

## Task

Execute comprehensive Monte Carlo validation with advanced statistical metrics:

1. **Read Current State**
   - Read iteration_state.json
   - Extract project_id, backtest_id, parameters
   - Extract time periods (start_date, end_date)

2. **Generate research.ipynb**
   ```bash
   # NO project-id argument - reads from iteration_state.json
   python SCRIPTS/qc_validate.py generate-notebook \
     --output research.ipynb
   ```

   Notebook implements:
   - Probabilistic Sharpe Ratio (PSR ≥ 0.95)
   - Deflated Sharpe Ratio (DSR)
   - Minimum Track Record Length (MinTRL)
   - Walk-Forward Efficiency (WFE ≥ 50%)
   - Bootstrap resampling (1,000-10,000 runs)
   - MACHR (Market Condition Historical Randomization)
   - Permutation testing (p < 0.05)
   - Monte Carlo drawdown distribution (99th percentile)

3. **Upload to QuantConnect**
   ```bash
   # NO project-id argument - reads from iteration_state.json
   python SCRIPTS/qc_validate.py upload-notebook \
     --file research.ipynb
   ```

   Output:
   ```
   ✅ Uploaded research.ipynb to project 26186305
   🔗 https://www.quantconnect.com/project/26186305

   📋 Next Steps:
   1. Open QuantConnect web interface
   2. Click 'Research' tab
   3. Open research.ipynb
   4. Run all cells (takes 5-30 minutes)
   5. Return here when complete
   ```

4. **User Executes Notebook**
   - User opens QC web interface
   - Runs research.ipynb online
   - Waits for Monte Carlo completion
   - Copies results JSON from last cell

5. **Collect Results**
   ```bash
   # NO project-id argument - reads from iteration_state.json
   python SCRIPTS/qc_validate.py collect-results
   ```

   Prompts for results JSON, parses metrics, makes decision

6. **Decision Framework**
   ```python
   if psr < 0.95:
       decision = "FAILED_PSR"
       reason = f"PSR {psr:.2f} < 0.95 (insufficient statistical significance)"

   elif wfe < 0.50:
       decision = "FAILED_WFE"
       reason = f"WFE {wfe:.2f} < 0.50 (poor generalization)"

   elif permutation_pvalue > 0.05:
       decision = "FAILED_PERMUTATION"
       reason = f"p-value {permutation_pvalue:.3f} > 0.05 (not significant)"

   elif mc_drawdown_99th > tolerance:
       decision = "EXCESSIVE_RISK"
       reason = f"99th percentile drawdown {mc_drawdown_99th:.1%} exceeds tolerance"

   else:
       decision = "ROBUST_STRATEGY"
       reason = f"PSR {psr:.2f}, WFE {wfe:.2f}, all tests passed"
   ```

7. **Update State and Commit**
   ```json
   {
     "validation": {
       "status": "completed",
       "method": "monte_carlo_advanced",
       "monte_carlo_runs": 1000,
       "psr": 0.98,
       "dsr": 0.94,
       "min_trl": 245,
       "wfe": 0.67,
       "machr_consistency": 0.12,
       "permutation_pvalue": 0.018,
       "mc_drawdown_99th": 0.187,
       "decision": "robust_strategy"
     }
   }
   ```

## Requirements

- Completed baseline backtest
- Valid QC API credentials
- QC Research access (free online)
- Patience (Monte Carlo takes 5-30 minutes)

## Important Notes

- **Execution:** Online in QC Research (NOT API backtests)
- **Cost:** FREE (Research notebooks execute online)
- **Time:** 5-30 minutes depending on MC runs
- **Statistical Rigor:** Industry-standard metrics (PSR, DSR, MACHR)
- **This is the FINAL validation** before live trading

## No Flags, No Levels

Single purpose: Advanced Monte Carlo validation
No --quick, no --standard, no complexity
ONE clear workflow
```

### Phase 3: Delete /qc-walkforward

```bash
rm .claude/commands/qc-walkforward.md
```

**Update references:**
- Skills: Remove qc-walkforward references
- Documentation: Update to single /qc-validate command
- Git commit: Document consolidation

### Phase 4: Update Skills

**File:** `.claude/skills/quantconnect-validation/skill.md`

Update to reflect:
- Single /qc-validate command
- Advanced Monte Carlo methodology
- Research QuantBook workflow
- No dependency on qc_backtest.py

---

## Key Principle

**NO CONFUSION:**
- `/qc-validate` = ONE command
- `qc_validate.py` = Self-contained script
- research.ipynb = Generated by qc_validate.py
- Upload = qc_validate.py's OWN method
- NO calls to qc_backtest.py

**Clear Separation:**
- `qc_backtest.py` = Backtesting (Phase 3)
- `qc_optimize.py` = Optimization (Phase 4)
- `qc_validate.py` = Validation (Phase 5)

Each script is independent and self-contained.

---

## Next Steps

1. ✅ User approves this plan
2. Implement qc_validate.py changes
3. Update /qc-validate.md command
4. Delete /qc-walkforward.md
5. Update skills and documentation
6. Test workflow end-to-end
7. Git commit all changes

**Waiting for user approval to proceed.**
