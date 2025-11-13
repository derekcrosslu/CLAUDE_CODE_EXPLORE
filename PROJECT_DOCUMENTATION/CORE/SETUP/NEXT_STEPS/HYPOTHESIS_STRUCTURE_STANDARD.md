# Hypothesis Directory Structure Standard

**Date Created**: 2025-11-13
**Purpose**: Define required structure for all hypothesis directories
**Status**: Active Standard - MUST FOLLOW

---

## Standard Directory Structure

Every hypothesis MUST follow this structure:

```
STRATEGIES/hypothesis_N_brief_description/
├── README.md                      # REQUIRED - Hypothesis description
├── iteration_state.json           # REQUIRED - Phase state tracking
├── config.json                    # REQUIRED - QuantConnect configuration
├── strategy_name.py               # REQUIRED - Main strategy implementation
│
├── optimization_params.json       # Created in Phase 4
├── optimization_params_*.json     # Optional variations
├── optimization_results_*.json    # Results from optimization runs
├── optimization_summary.json      # Best parameters summary
│
├── research.ipynb                 # Created in Phase 5 (validation)
├── mc_validation_results.json     # Monte Carlo validation results
├── walkforward_config.json        # Walk-forward configuration
├── VALIDATION_ANALYSIS.md         # Detailed validation analysis
│
├── *.csv                          # Strategy-specific data files
├── *.json                         # Additional config/results
│
├── validation_reports/            # Directory for HTML/PDF reports
│   ├── validation_report.html
│   └── charts/
│
└── __pycache__/                   # Python cache (gitignored)
```

---

## Required Files (Always)

### 1. README.md
**Purpose**: Human-readable hypothesis description

**Template**:
```markdown
# Hypothesis N: [Brief Description]

**Created**: YYYY-MM-DD
**Status**: [in_progress|validated|abandoned]
**Strategy Type**: [mean_reversion|momentum|statistical_arbitrage|other]

## Hypothesis
[1-2 paragraph description of the core hypothesis]

## Edge Thesis
[Why should this work? What market inefficiency does it exploit?]

## Strategy Logic
- Entry conditions
- Exit conditions
- Risk management

## Expected Performance
- Target Sharpe Ratio: X.X
- Expected drawdown: XX%
- Trade frequency: X per month

## Phase Progress
- [x] Phase 1: Initialization
- [x] Phase 2: Implementation
- [x] Phase 3: Backtest (Sharpe: X.X)
- [ ] Phase 4: Optimization
- [ ] Phase 5: Validation

## Notes
[Any important observations, decisions, or learnings]
```

---

### 2. iteration_state.json
**Purpose**: Machine-readable state tracking for autonomous workflow

**Source**: Copied from `PROJECT_SCHEMAS/iteration_state_template.json`

**Key Sections**:
```json
{
  "schema_version": "1.0.0",
  "hypothesis": {
    "id": 7,
    "name": "momentum-regime-filter",
    "description": "Momentum strategy with volatility regime filter",
    "status": "in_progress",
    "current_phase": 3,
    "created_date": "2025-11-14",
    "last_updated": "2025-11-14T15:30:00Z"
  },
  "project": {
    "project_id": 26186305,
    "project_name": "H7-momentum-regime",
    "created_date": "2025-11-14"
  },
  "phases": {
    "phase_1_init": {
      "status": "completed",
      "completed_date": "2025-11-14"
    },
    "phase_3_backtest": {
      "status": "completed",
      "backtest_id": "abc123",
      "decision": "proceed_to_optimization",
      "metrics": {...}
    }
  }
}
```

**CRITICAL RULES**:
- NEVER modify manually (updated by workflow commands only)
- Source of truth for project_id (never pass as CLI argument)
- Tracks complete workflow history

---

### 3. config.json
**Purpose**: QuantConnect-specific configuration

**Template**:
```json
{
  "environment": "cloud",
  "data-folder": "./",
  "debugging": true,
  "debugging-method": "LocalCmdLine",
  "log-handler": "ConsoleLogHandler",
  "messaging-handler": "QuantConnect.Messaging.Messaging",
  "job-queue-handler": "QuantConnect.Queues.JobQueue",
  "api-handler": "QuantConnect.Api.Api",
  "map-file-provider": "QuantConnect.Data.Auxiliary.LocalDiskMapFileProvider",
  "factor-file-provider": "QuantConnect.Data.Auxiliary.LocalDiskFactorFileProvider",
  "data-provider": "QuantConnect.Lean.Engine.DataFeeds.DefaultDataProvider",
  "algorithm-type-name": "StrategyName",
  "algorithm-language": "Python",
  "algorithm-location": "strategy_name.py"
}
```

**Notes**:
- Used by QuantConnect API for project setup
- `algorithm-type-name` should match Python class name
- `algorithm-location` should match strategy filename

---

### 4. strategy_name.py
**Purpose**: Main strategy implementation

**Requirements**:
- Must inherit from `QCAlgorithm`
- Must implement `Initialize()` and `OnData()`
- Class name must match `config.json` algorithm-type-name
- Should include docstring with hypothesis description

**Minimal Template**:
```python
from AlgorithmImports import *

class StrategyName(QCAlgorithm):
    """
    Hypothesis N: Brief Description

    Strategy logic:
    - Entry: [conditions]
    - Exit: [conditions]
    - Risk: [parameters]
    """

    def Initialize(self):
        self.SetStartDate(2023, 1, 1)
        self.SetEndDate(2024, 12, 31)
        self.SetCash(100000)

        # Add universe/symbols
        self.AddEquity("SPY", Resolution.Daily)

        # Parameters (will be optimized in Phase 4)
        self.rsi_period = 14
        self.entry_threshold = 30

    def OnData(self, data):
        # Strategy logic here
        pass
```

---

## Phase-Dependent Files

### Phase 4: Optimization

**optimization_params.json** - Parameter grid definition:
```json
{
  "parameters": [
    {"name": "rsi_period", "min": 10, "max": 20, "step": 2},
    {"name": "entry_threshold", "min": 20, "max": 40, "step": 5}
  ],
  "target": "SharpeRatio",
  "constraints": []
}
```

**optimization_results_YYYYMMDD_HHMMSS.json** - Results from each run

**optimization_summary.json** - Best parameters found:
```json
{
  "best_sharpe": 1.85,
  "best_params": {
    "rsi_period": 14,
    "entry_threshold": 30
  },
  "improvement_vs_baseline": "42%",
  "decision": "proceed_to_validation"
}
```

---

### Phase 5: Validation

**research.ipynb** - Monte Carlo validation notebook:
- Generated by `qc_validate.py generate-notebook`
- Implements PSR, DSR, MinTRL, WFE metrics
- Uploaded to QC and run online
- Results copied back to mc_validation_results.json

**mc_validation_results.json** - Validation metrics:
```json
{
  "psr": 0.98,
  "dsr": 0.94,
  "min_trl": 245,
  "wfe": 0.67,
  "permutation_pvalue": 0.018,
  "mc_drawdown_99th": 0.187,
  "decision": "robust_strategy"
}
```

**walkforward_config.json** - Walk-forward parameters:
```json
{
  "train_period_months": 12,
  "test_period_months": 3,
  "step_months": 1,
  "min_train_samples": 100
}
```

**VALIDATION_ANALYSIS.md** - Detailed analysis report

**validation_reports/** - HTML/PDF reports with charts

---

## Initialization Checklist

When running `/qc-init` for a new hypothesis:

### Step 1: Create Directory
```bash
mkdir -p STRATEGIES/hypothesis_7_momentum_regime_filter
cd STRATEGIES/hypothesis_7_momentum_regime_filter
```

### Step 2: Copy Template Files
```bash
# Copy iteration state template
cp ../../PROJECT_SCHEMAS/iteration_state_template.json iteration_state.json

# Copy config template
cp ../../PROJECT_SCHEMAS/config_template.json config.json

# Copy README template
cp ../../PROJECT_SCHEMAS/hypothesis_README_template.md README.md
```

### Step 3: Customize Files
- Update README.md with hypothesis description
- Update config.json algorithm-type-name and algorithm-location
- Update iteration_state.json hypothesis section

### Step 4: Create Strategy File
- Create strategy_name.py
- Implement basic Initialize() and OnData()
- Match class name to config.json

### Step 5: Initialize Git
```bash
git add .
git commit -m "init: Initialize hypothesis 7 - momentum regime filter

Created directory structure with:
- README.md (hypothesis description)
- iteration_state.json (phase tracking)
- config.json (QC configuration)
- momentum_regime_filter.py (initial implementation)

Phase 1 (Initialization): COMPLETE
Next: Phase 2 (Implementation)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 6: Update iteration_state.json
Mark phase_1_init as completed

---

## Phase Progression Markers

### Phase 1: Initialization
**Status**: `phase_1_init.status = "completed"`
**Files Created**:
- README.md
- iteration_state.json
- config.json
- strategy_name.py (skeleton)

---

### Phase 2: Implementation
**Status**: `phase_2_implementation.status = "completed"`
**Files Updated**:
- strategy_name.py (full implementation)

---

### Phase 3: Backtest
**Status**: `phase_3_backtest.status = "completed"`
**Files Created/Updated**:
- iteration_state.json (backtest_id, metrics, decision)
- Project created on QC (project_id saved)

**Decision Routes**:
- `proceed_to_optimization` → Phase 4
- `proceed_to_validation` → Phase 5 (skip Phase 4)
- `abandon_hypothesis` → STOP
- `escalate` → Human review

---

### Phase 4: Optimization
**Status**: `phase_4_optimization.status = "completed"`
**Files Created**:
- optimization_params.json
- optimization_results_*.json
- optimization_summary.json

**Decision**: Always → Phase 5 (validation)

---

### Phase 5: Validation
**Status**: `phase_5_validation.status = "completed"`
**Files Created**:
- research.ipynb
- mc_validation_results.json
- walkforward_config.json
- VALIDATION_ANALYSIS.md
- validation_reports/

**Decision Routes**:
- `robust_strategy` → Move to validated-strategies branch
- `failed_validation` → Abandon or iterate
- `insufficient_data` → Collect more data
- `overfitting_detected` → Return to Phase 2

---

## Validation Rules

### Required Files Check
Before any phase transition, verify:
```python
required_files = [
    "README.md",
    "iteration_state.json",
    "config.json",
    f"{strategy_name}.py"
]

for file in required_files:
    if not os.path.exists(file):
        raise FileNotFoundError(f"Required file missing: {file}")
```

### Phase Consistency Check
```python
state = json.load(open('iteration_state.json'))
current_phase = state['hypothesis']['current_phase']

# Ensure files exist for completed phases
if current_phase >= 3:
    assert state['project']['project_id'] is not None
if current_phase >= 4:
    assert os.path.exists('optimization_summary.json')
if current_phase >= 5:
    assert os.path.exists('mc_validation_results.json')
```

---

## Git Workflow Integration

### Branch Naming
```
hypotheses/hypothesis-7-momentum-regime-filter
```

### Commit Messages Format
```
<phase>: <action>

<details>

Metrics:
- Sharpe: X.X
- Win Rate: XX%
- Trades: XXX

Phase N (Name): [COMPLETE|IN_PROGRESS]
Next: Phase N+1 (Name)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Common Violations & Fixes

### ❌ Wrong: Files in Wrong Location
```
# DON'T put these in hypothesis directory:
STRATEGIES/hypothesis_7/.env
STRATEGIES/hypothesis_7/requirements.txt
STRATEGIES/hypothesis_7/qc_backtest.py
```

**Fix**: Use project root for shared files

---

### ❌ Wrong: iteration_state.json Modified Manually
```json
// DON'T edit by hand
{
  "project": {
    "project_id": 123456  // Manually typed
  }
}
```

**Fix**: Let workflow commands update automatically

---

### ❌ Wrong: Missing README.md
```
STRATEGIES/hypothesis_7/
└── strategy.py  // Where's the README?
```

**Fix**: Always create README.md first

---

## Examples

### Example 1: Minimal H4 (Backtest Only)
```
STRATEGIES/hypothesis_4_rsi_mean_reversion/
├── README.md
├── iteration_state.json
├── config.json
└── rsi_mean_reversion.py
```
**Phase**: 3 (Backtest complete, decided to abandon)

---

### Example 2: Complete H5 (All Phases)
```
STRATEGIES/hypothesis_5_statistical_arbitrage/
├── README.md
├── iteration_state.json
├── config.json
├── statistical_arbitrage.py
├── optimization_params.json
├── optimization_results_20251111_031810.json
├── optimization_summary.json
├── research.ipynb
├── mc_validation_results.json
├── walkforward_config.json
├── VALIDATION_ANALYSIS.md
├── validation_reports/
│   └── validation_report.html
└── *.csv (data files)
```
**Phase**: 5 (Validation complete - ROBUST)

---

## Quick Reference Commands

```bash
# Check structure compliance
ls -la STRATEGIES/hypothesis_7_*/{README.md,iteration_state.json,config.json,*.py}

# Verify phase consistency
jq '.hypothesis.current_phase, .phases | keys' iteration_state.json

# List all hypothesis directories
ls -d STRATEGIES/hypothesis_*

# Find hypotheses in specific phase
grep -r "\"current_phase\": 5" STRATEGIES/hypothesis_*/iteration_state.json
```

---

**Created By**: Claude (2025-11-13 session)
**Status**: Active Standard
**Enforcement**: MANDATORY for all new hypotheses
**Review**: After each hypothesis completion
