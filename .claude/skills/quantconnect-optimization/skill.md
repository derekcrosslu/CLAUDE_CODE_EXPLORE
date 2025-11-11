---
name: QuantConnect Optimization
description: QuantConnect optimization API and Phase 4 parameter tuning (project)
---

# QuantConnect Optimization Skill (Phase 4)

This skill provides focused knowledge for **parameter optimization** via the QuantConnect API and Phase 4 decision integration.

## When to Use This Skill

Load this skill when:
- Running `/qc-optimize` command
- Setting up parameter grids
- Evaluating optimization results
- Making Phase 4 routing decisions
- Deciding between baseline and optimized parameters

**Important**: Always store optimization results and logs in `PROJECT_LOGS/` folder. See `PROJECT_LOGS/README.md` for naming conventions.

---

## ⚠️ CRITICAL CONSTRAINT: Project ID Requirements

**YOU MUST USE THE project_id FROM THE BACKTEST YOU JUST RAN**

### Why This Constraint Exists

1. **QuantConnect API requires a completed backtest**
   - Optimization compares new parameter sets against a baseline backtest
   - The API will ERROR if you try to optimize a project with no backtest
   - You cannot optimize an empty project or arbitrary project_id

2. **We must optimize the strategy we just evaluated**
   - After `/qc-backtest`, the project_id is stored in `iteration_state.json`
   - This is the ONLY valid project_id for optimization
   - DO NOT use a different project_id
   - DO NOT create a new project for optimization

3. **Prevents errors and wrong strategy optimization**
   - Ensures we're optimizing the correct strategy
   - Prevents API errors from missing baseline
   - Maintains audit trail (same project through all phases)

### Correct Workflow

```python
# Step 1: Read project_id from iteration_state.json
with open('iteration_state.json', 'r') as f:
    state = json.load(f)

project_id = state['project']['project_id']
backtest_id = state['phase_results']['backtest']['backtest_id']

# Step 2: Validate backtest exists
if not project_id:
    raise ValueError("No project_id found. Run /qc-backtest first.")

if not backtest_id:
    raise ValueError("No backtest_id found. Cannot optimize without baseline backtest.")

# Step 3: Validate we're in correct phase
current_phase = state['workflow']['current_phase']
if current_phase != "backtest":
    raise ValueError(f"Cannot optimize from phase '{current_phase}'. Must be in 'backtest' phase.")

# Step 4: Now safe to optimize
# optimize_strategy(project_id, param_grid)
```

### Wrong Examples (DO NOT DO THIS)

```python
# ❌ WRONG: Creating new project for optimization
project_id = api.create_project("Optimization_Project")
optimize_strategy(project_id, params)  # ERROR: No baseline backtest!

# ❌ WRONG: Using arbitrary project_id
project_id = 12345  # Random project
optimize_strategy(project_id, params)  # ERROR: Not our strategy!

# ❌ WRONG: Using hardcoded project_id
project_id = 26135853  # From previous session
optimize_strategy(project_id, params)  # ERROR: Wrong hypothesis!
```

### Correct Example (DO THIS)

```python
# ✅ CORRECT: Read from iteration_state.json
with open('iteration_state.json', 'r') as f:
    state = json.load(f)

project_id = state['project']['project_id']  # The project we just backtested
optimize_strategy(project_id, param_grid)    # Optimizes correct strategy
```

---

## Optimization Approaches

There are TWO approaches for optimization:

### Option A: QuantConnect API Optimization (Paid Tier)

**Requirements**:
- Quant Researcher tier ($8/month)
- QCC credits for optimization runs (1 QCC = $0.01 USD)
- Cost depends on parameter combinations

**Advantages**:
- Native QC optimization engine
- Parallel execution (faster)
- Built-in parameter sweeps
- Results directly in QC cloud

**Disadvantages**:
- Requires paid subscription
- Costs QCC credits per optimization
- Need to estimate costs before running

### Option B: Manual Parameter Grid (Free Tier)

**Requirements**:
- Free tier (no subscription needed)
- Time (runs sequentially via backtest API)

**Advantages**:
- No additional cost (beyond backtest API calls)
- Full control over parameter combinations
- No subscription required

**Disadvantages**:
- Slower (sequential backtests)
- More API calls
- Need to implement grid search logic

---

## Manual Parameter Grid Approach (Recommended for MVP)

For Phase 1-3 MVP, use **manual parameter grid** to avoid subscription costs.

### Implementation

```python
import sys
sys.path.insert(0, 'SCRIPTS')
from qc_backtest import QuantConnectAPI
import json
import time

def manual_optimize(project_id, param_grid, strategy_template):
    """
    Manual parameter optimization using sequential backtests.

    Args:
        project_id: QC project ID (from iteration_state.json)
        param_grid: List of parameter combinations
        strategy_template: Strategy code with {param} placeholders

    Returns:
        best_params: Best parameter combination
        best_sharpe: Best Sharpe ratio achieved
        all_results: All parameter results
    """
    api = QuantConnectAPI()

    all_results = []
    best_sharpe = -999
    best_params = None

    for i, params in enumerate(param_grid):
        print(f"Testing combination {i+1}/{len(param_grid)}: {params}")

        # Modify strategy code with current parameters
        strategy_code = strategy_template.format(**params)

        # Upload modified strategy
        api.upload_file(project_id, strategy_code, "Main.py")

        # Run backtest
        backtest = api.create_backtest(project_id, f"Optimize_{i+1}")
        backtest_id = backtest['backtestId']

        # Wait for completion
        result = api.wait_for_backtest(project_id, backtest_id, timeout=600)

        # Parse results
        performance = api.parse_backtest_results(result)
        sharpe = performance['sharpe_ratio']

        all_results.append({
            'params': params,
            'sharpe': sharpe,
            'drawdown': performance['max_drawdown'],
            'trades': performance['total_trades']
        })

        # Track best
        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_params = params

        # Rate limit (avoid API throttling)
        time.sleep(2)

    return best_params, best_sharpe, all_results
```

### Parameter Grid Example

```python
# Define parameter grid
param_grid = [
    {'sma_period': 10, 'stop_loss': 0.03},
    {'sma_period': 14, 'stop_loss': 0.03},
    {'sma_period': 20, 'stop_loss': 0.03},
    {'sma_period': 10, 'stop_loss': 0.05},
    {'sma_period': 14, 'stop_loss': 0.05},
    {'sma_period': 20, 'stop_loss': 0.05},
]

# Strategy template with placeholders
strategy_template = '''
class Strategy(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2023, 12, 31)
        self.SetCash(100000)

        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.sma = self.SMA(self.symbol, {sma_period}, Resolution.Daily)
        self.stop_loss_pct = {stop_loss}

    def OnData(self, data):
        if not self.sma.IsReady:
            return

        if not data.ContainsKey(self.symbol):
            return

        bar = data[self.symbol]
        if bar is None:
            return

        price = bar.Close

        # Entry logic
        if not self.Portfolio.Invested:
            if price > self.sma.Current.Value:
                self.SetHoldings(self.symbol, 1.0)
                self.entry_price = price

        # Exit logic (stop loss)
        if self.Portfolio.Invested:
            if price < self.entry_price * (1 - self.stop_loss_pct):
                self.Liquidate()
'''

# Run optimization
best_params, best_sharpe, all_results = manual_optimize(
    project_id=26135853,
    param_grid=param_grid,
    strategy_template=strategy_template
)

print(f"Best params: {best_params}")
print(f"Best Sharpe: {best_sharpe}")
```

---

## Phase 4 Decision Integration

After optimization completes, evaluate improvement:

```python
import sys
sys.path.insert(0, 'SCRIPTS')
from decision_logic import evaluate_optimization, route_decision

# Load baseline and optimized results
baseline_sharpe = state['phase_results']['backtest']['performance']['sharpe_ratio']
optimized_sharpe = best_sharpe

# Calculate improvement
improvement_pct = (optimized_sharpe - baseline_sharpe) / baseline_sharpe

# Evaluate
decision, reason, details = evaluate_optimization(
    baseline_sharpe=baseline_sharpe,
    optimized_sharpe=optimized_sharpe,
    improvement_pct=improvement_pct,
    thresholds=state['thresholds']
)

print(f"Decision: {decision}")
print(f"Reason: {reason}")

# Route to next phase
routing = route_decision(
    current_phase="optimization",
    decision=decision,
    iteration=state['workflow']['iteration']
)

print(f"Next Action: {routing['next_action']}")
```

**Possible decisions**:
- `USE_BASELINE_PARAMS` → Validation with baseline (optimization didn't help)
- `PROCEED_TO_VALIDATION` → Validation with optimized params (improvement found)
- `ESCALATE_TO_HUMAN` → Excessive improvement (> 30%), possible overfitting

**Decision thresholds** (from iteration_state.json):
- Improvement < 0%: USE_BASELINE_PARAMS (got worse)
- 0% ≤ Improvement < 5%: USE_BASELINE_PARAMS (too small)
- 5% ≤ Improvement ≤ 30%: PROCEED_TO_VALIDATION (good improvement)
- Improvement > 30%: ESCALATE_TO_HUMAN (suspicious, likely overfitting)

---

## Best Practices for Optimization

### 1. Start with Small Grid

Test with 3-6 combinations first:
```python
# Small grid for testing
param_grid = [
    {'sma_period': 10},
    {'sma_period': 20},
    {'sma_period': 30},
]
```

### 2. Limit Parameter Count

- **1-2 parameters**: Good (fast, less overfitting risk)
- **3-4 parameters**: Acceptable (watch for overfitting)
- **5+ parameters**: Risky (high overfitting risk, slow)

### 3. Use Reasonable Ranges

```python
# GOOD: Reasonable ranges
param_grid = [
    {'rsi_period': 10},   # Min reasonable
    {'rsi_period': 14},   # Standard
    {'rsi_period': 20},   # Max reasonable
]

# BAD: Too wide, overfitting risk
param_grid = [
    {'rsi_period': 2},    # Too low
    {'rsi_period': 100},  # Too high
]
```

### 4. Monitor Execution Time

- **3x3 grid (9 combinations)**: ~15-20 minutes
- **5x5 grid (25 combinations)**: ~45-60 minutes
- **10x10 grid (100 combinations)**: ~3-5 hours

Plan accordingly and use small grids for MVP.

### 5. Check for Overfitting

After optimization:
```python
# Check if improvement is suspicious
if improvement_pct > 0.30:
    print("WARNING: >30% improvement may indicate overfitting")
    print("Consider using baseline parameters instead")
```

---

## Integration with /qc-optimize Command

The `/qc-optimize` command should:

1. **Read iteration_state.json**
   - Get project_id (MUST exist from backtest!)
   - Get baseline Sharpe ratio
   - Validate current_phase == "backtest"
   - Validate backtest_id exists

2. **Load QuantConnect-Optimization Skill** (this skill!)
   - Get manual optimization approach
   - Get parameter grid examples
   - Get decision integration logic

3. **Define parameter grid**
   - Based on strategy type (momentum, mean reversion, etc.)
   - Start with small grid (3-6 combinations)
   - Use reasonable parameter ranges

4. **Run optimization**
   - Use manual_optimize() function
   - Track all parameter combinations tested
   - Find best Sharpe ratio

5. **Evaluate improvement (Phase 4)**
   - Calculate improvement percentage
   - Call `decision_logic.evaluate_optimization()`
   - Call `decision_logic.route_decision()`

6. **Update iteration_state.json**
   - Store optimized parameters
   - Store improvement percentage
   - Store decision and routing
   - Update current_phase

7. **Git commit**
   - Include baseline vs optimized metrics
   - Include decision and rationale

---

## Common Optimization Errors

### 1. No Baseline Backtest

**Error**: "Cannot optimize: no backtest found in project"

**Fix**: Run `/qc-backtest` first, then `/qc-optimize`

### 2. Wrong Project ID

**Error**: Optimizing a different strategy or empty project

**Fix**: Always read `project_id` from `iteration_state.json`

### 3. Grid Too Large

**Problem**: Optimization takes hours

**Fix**: Start with small grid (3x3), then expand if needed

### 4. Overfitting to In-Sample

**Problem**: 50%+ improvement, then fails in validation

**Fix**: ESCALATE_TO_HUMAN if improvement > 30%

---

## Example: Complete /qc-optimize Workflow

```bash
# Step 1: Validate prerequisites
PROJECT_ID=$(cat iteration_state.json | jq -r '.project.project_id')
BACKTEST_ID=$(cat iteration_state.json | jq -r '.phase_results.backtest.backtest_id')
BASELINE_SHARPE=$(cat iteration_state.json | jq -r '.phase_results.backtest.performance.sharpe_ratio')

if [ "$PROJECT_ID" == "null" ] || [ "$BACKTEST_ID" == "null" ]; then
    echo "ERROR: Run /qc-backtest first"
    exit 1
fi

# Step 2: Define parameter grid (Claude generates based on strategy)
cat > param_grid.json << 'EOF'
[
    {"sma_period": 10, "stop_loss": 0.03},
    {"sma_period": 14, "stop_loss": 0.03},
    {"sma_period": 20, "stop_loss": 0.03}
]
EOF

# Step 3: Run manual optimization
python3 << 'EOF'
import sys, json
sys.path.insert(0, 'SCRIPTS')
from manual_optimize import manual_optimize

with open('iteration_state.json') as f:
    state = json.load(f)
with open('param_grid.json') as f:
    param_grid = json.load(f)
with open('strategy.py') as f:
    strategy_template = f.read()

best_params, best_sharpe, all_results = manual_optimize(
    state['project']['project_id'],
    param_grid,
    strategy_template
)

output = {
    'best_params': best_params,
    'best_sharpe': best_sharpe,
    'baseline_sharpe': state['phase_results']['backtest']['performance']['sharpe_ratio'],
    'improvement_pct': (best_sharpe - state['phase_results']['backtest']['performance']['sharpe_ratio']) / state['phase_results']['backtest']['performance']['sharpe_ratio'],
    'all_results': all_results
}

with open('PROJECT_LOGS/optimization_result.json', 'w') as f:
    json.dump(output, f, indent=2)

print(json.dumps(output, indent=2))
EOF

# Step 4: Evaluate improvement
python3 << 'EOF'
import sys, json
sys.path.insert(0, 'SCRIPTS')
from decision_logic import evaluate_optimization, route_decision

with open('PROJECT_LOGS/optimization_result.json') as f:
    opt_result = json.load(f)
with open('iteration_state.json') as f:
    state = json.load(f)

decision, reason, details = evaluate_optimization(
    baseline_sharpe=opt_result['baseline_sharpe'],
    optimized_sharpe=opt_result['best_sharpe'],
    improvement_pct=opt_result['improvement_pct'],
    thresholds=state['thresholds']
)

routing = route_decision("optimization", decision, state['workflow']['iteration'])

print(f"DECISION={decision}")
print(f"NEXT_ACTION={routing['next_action']}")
EOF

# Step 5: Update iteration_state.json (Claude updates)

# Step 6: Git commit
git add iteration_state.json PROJECT_LOGS/optimization_result.json
git commit -m "optimization: Complete - PROCEED_TO_VALIDATION

Baseline Sharpe: 0.85
Optimized Sharpe: 0.97
Improvement: 14%

Best Parameters:
- sma_period: 14
- stop_loss: 0.03

Decision: PROCEED_TO_VALIDATION
Reason: Good improvement without overfitting risk"
```

---

## Related Skills

- **quantconnect** - Core strategy development
- **quantconnect-backtest** - Phase 3 backtesting (MUST run before optimization!)
- **quantconnect-validation** - Phase 5 validation (runs after optimization)
- **decision-framework** - Decision thresholds and routing logic

---

## Summary

**This skill covers**:
- ✅ Manual parameter grid optimization
- ✅ Critical project_id constraint (use backtest project!)
- ✅ Phase 4 decision integration
- ✅ Improvement evaluation
- ✅ Overfitting detection
- ✅ Best practices for parameter tuning

**When to load**:
- Before running `/qc-optimize` command
- When setting up parameter grids
- When evaluating optimization results
- When deciding baseline vs optimized parameters

**Key constraint**: MUST use project_id from iteration_state.json (the project you just backtested). Cannot optimize empty projects or arbitrary project IDs.

---

**Version**: 1.0.0
**Last Updated**: November 10, 2025
**Status**: Production Ready
**Purpose**: Phase 4 parameter optimization via QuantConnect API
