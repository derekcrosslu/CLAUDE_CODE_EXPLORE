---
name: QuantConnect Backtest
description: QuantConnect backtesting API usage and Phase 3 decision integration (project)
---

# QuantConnect Backtest Skill (Phase 3)

This skill provides focused knowledge for **running backtests via the QuantConnect API** and integrating with the Phase 3 decision framework.

## When to Use This Skill

Load this skill when:
- Running `/qc-backtest` command
- Uploading strategy files to QuantConnect
- Executing backtests via API
- Parsing backtest results
- Making Phase 3 routing decisions
- Debugging backtest API errors

**Important**: Always store backtest results and logs in `PROJECT_LOGS/` folder. See `PROJECT_LOGS/README.md` for naming conventions.

---

## QuantConnect API Integration

### Using qc_backtest.py Wrapper

The project includes `SCRIPTS/qc_backtest.py` which provides complete API wrapper functionality.

**Complete Workflow - Upload Strategy and Run Backtest**:

```bash
# Create project, upload code, run backtest
python SCRIPTS/qc_backtest.py --run \
    --name "MomentumStrategy_20241110" \
    --file strategy.py \
    --output PROJECT_LOGS/backtest_result.json
```

**What this does**:
1. Creates new QC project (or reuses existing if name matches)
2. Uploads strategy file to project
3. Compiles the strategy
4. Runs backtest
5. Waits for completion (polls every 5 seconds)
6. Downloads results
7. Saves to JSON file

**Output format** (`backtest_result.json`):

```json
{
  "project_id": 26135853,
  "project_name": "MomentumStrategy_20241110",
  "backtest_id": "abc123def456",
  "performance": {
    "sharpe_ratio": 0.85,
    "max_drawdown": 0.22,
    "total_return": 0.45,
    "total_trades": 67,
    "win_rate": 0.42,
    "loss_rate": 0.58,
    "profit_factor": 1.8
  },
  "qc_url": "https://www.quantconnect.com/project/26135853"
}
```

---

## Python API Integration

You can also use the API directly in Python:

```python
import sys
sys.path.insert(0, 'SCRIPTS')
from qc_backtest import QuantConnectAPI

# Initialize API (reads credentials from .env)
api = QuantConnectAPI()

# Create project
project_id = api.create_project("TestStrategy_20241110")

# Upload strategy file
api.upload_file(project_id, "strategy.py", "Main.py")

# Run backtest
backtest = api.create_backtest(project_id, "Backtest_v1")
backtest_id = backtest['backtestId']

# Wait for completion
result = api.wait_for_backtest(project_id, backtest_id, timeout=600)

# Parse results
performance = api.parse_backtest_results(result)
print(f"Sharpe: {performance['sharpe_ratio']}")
print(f"Drawdown: {performance['max_drawdown']}")
```

---

## Backtest Results Structure

The API returns structured results optimized for decision-making:

```python
{
    "sharpe_ratio": float,        # Risk-adjusted return metric
    "max_drawdown": float,        # Maximum peak-to-trough decline (0.0-1.0)
    "total_return": float,        # Total return (0.0-1.0)
    "total_trades": int,          # Number of trades executed
    "win_rate": float,            # Winning trades / total trades
    "loss_rate": float,           # Losing trades / total trades
    "profit_factor": float,       # Gross profit / gross loss
    "alpha": float,               # Excess return vs benchmark
    "beta": float,                # Correlation to benchmark
    "annual_variance": float,     # Annual volatility
    "annual_standard_deviation": float,
    "information_ratio": float,   # Risk-adjusted excess return
    "tracking_error": float,      # Deviation from benchmark
    "treynor_ratio": float,       # Return per unit of systematic risk
    "total_fees": float,          # Transaction costs
    "estimated_capacity": float,  # Max capital strategy can handle
}
```

**Most important metrics for Phase 3 decision**:
1. `sharpe_ratio` - Primary decision metric
2. `max_drawdown` - Risk tolerance check
3. `total_trades` - Statistical significance
4. `win_rate` - Overfitting signal (> 0.75 suspicious)

---

## Phase 3 Decision Integration

After backtest completes, integrate with decision framework:

```python
import json
import sys
sys.path.insert(0, 'SCRIPTS')
from decision_logic import evaluate_backtest, route_decision

# Load backtest results
with open('PROJECT_LOGS/backtest_result.json', 'r') as f:
    results = json.load(f)

# Load thresholds from iteration_state.json
with open('iteration_state.json', 'r') as f:
    state = json.load(f)

# Evaluate backtest
decision, reason, details = evaluate_backtest(
    results['performance'],
    state['thresholds']
)

print(f"Decision: {decision}")
print(f"Reason: {reason}")

# Route to next phase
routing = route_decision(
    current_phase="backtest",
    decision=decision,
    iteration=state['workflow']['iteration']
)

print(f"Next Phase: {routing['next_phase']}")
print(f"Next Action: {routing['next_action']}")
```

**Possible decisions**:
- `ABANDON_HYPOTHESIS` → Start new hypothesis
- `PROCEED_TO_OPTIMIZATION` → Run /qc-optimize
- `PROCEED_TO_VALIDATION` → Run /qc-validate (skip optimization)
- `ESCALATE_TO_HUMAN` → Manual review required

---

## Credentials Configuration

**Required environment variables** (`.env` file):

```bash
QC_USER_ID=your_user_id
QC_API_TOKEN=your_api_token
```

**Get credentials from**:
- Login to https://www.quantconnect.com
- Navigate to Account → API Access
- Copy User ID and API Token

**Security**:
- Never commit `.env` to git
- `.env` is already in `.gitignore`
- API uses HMAC authentication with timestamp

---

## Common Backtest Errors

### 1. Strategy Never Trades (0 trades)

**Problem**: Entry conditions too restrictive

**Example**:
```python
# BAD: Too restrictive
if self.sma.IsReady and self.sma.Current.Value > price and volume > 2.0 * avg_volume:
    self.SetHoldings(self.symbol, 1.0)
```

**Fix**: Simplify entry conditions
```python
# GOOD: Simpler conditions
if self.sma.IsReady and self.sma.Current.Value > price:
    self.SetHoldings(self.symbol, 1.0)
```

### 2. Runtime Error: Object Reference Not Set

**Problem**: Accessing data before it's ready

**Example**:
```python
# BAD: No None check
def OnData(self, data):
    bar = data[self.symbol]
    price = bar.Close  # Can fail if bar is None
```

**Fix**: Add None checks
```python
# GOOD: Check for None
def OnData(self, data):
    if not data.ContainsKey(self.symbol):
        return

    bar = data[self.symbol]
    if bar is None:
        return

    price = bar.Close
```

### 3. Indicator Not Ready

**Problem**: Using indicator before warmup period

**Example**:
```python
# BAD: No ready check
def OnData(self, data):
    if self.sma.Current.Value > price:  # Can fail if not ready
        self.SetHoldings(self.symbol, 1.0)
```

**Fix**: Check IsReady property
```python
# GOOD: Check ready state
def OnData(self, data):
    if not self.sma.IsReady:
        return

    if self.sma.Current.Value > price:
        self.SetHoldings(self.symbol, 1.0)
```

### 4. Project Creation Fails

**Problem**: Invalid project name or API credentials

**Check**:
- Project name must be unique (or use existing)
- Credentials in `.env` are correct
- API token hasn't expired

### 5. Backtest Timeout

**Problem**: Backtest runs too long (> 10 minutes)

**Fix**:
- Increase timeout parameter in `wait_for_backtest()`
- Reduce backtest date range
- Use lower resolution data (daily instead of minute)

---

## Best Practices for Backtesting

### 1. Start with Simple Strategies

Test system completeness with minimal logic:
```python
# Simple momentum strategy for system validation
if self.sma.IsReady and price > self.sma.Current.Value:
    self.SetHoldings(self.symbol, 1.0)
elif self.sma.IsReady and price < self.sma.Current.Value:
    self.Liquidate()
```

### 2. Use Appropriate Date Ranges

- **Initial testing**: 1-2 years (fast feedback)
- **Full backtest**: 3-5 years (statistical significance)
- **Too short** (< 1 year): Unreliable results
- **Too long** (> 10 years): Slow, regime changes

### 3. Monitor Trade Count

- **0 trades**: Entry conditions too restrictive
- **1-20 trades**: Insufficient for statistical significance
- **30-100 trades**: Acceptable for baseline
- **100+ trades**: Good statistical confidence
- **1000+ trades**: Excellent (but check transaction costs)

### 4. Always Check for Errors

```python
# After backtest completion
if 'error' in result:
    print(f"Backtest failed: {result['error']}")
    # ESCALATE_TO_HUMAN or fix and retry
else:
    # Parse and evaluate results
    performance = api.parse_backtest_results(result)
```

---

## Integration with /qc-backtest Command

The `/qc-backtest` command should:

1. **Read iteration_state.json**
   - Get hypothesis details
   - Get project_id (if exists) or create new
   - Get current phase (should be "research" or "implementation")

2. **Load QuantConnect Skill** (this skill!)
   - Get strategy templates
   - Get error handling patterns
   - Get API usage examples

3. **Generate strategy code**
   - Use hypothesis description to create entry/exit logic
   - Add risk management (stop loss, position sizing)
   - Add error handling (NoneType checks, indicator ready)

4. **Upload and run backtest**
   - Call `qc_backtest.py --run`
   - Wait for completion
   - Save results to PROJECT_LOGS/

5. **Evaluate results (Phase 3)**
   - Call `decision_logic.evaluate_backtest()`
   - Call `decision_logic.route_decision()`
   - Update iteration_state.json with decision

6. **Git commit**
   - Structured commit with metrics
   - Include decision and rationale

---

## Example: Complete /qc-backtest Workflow

```bash
# Step 1: Read state
HYPOTHESIS=$(cat iteration_state.json | jq -r '.hypothesis.description')
PROJECT_ID=$(cat iteration_state.json | jq -r '.project.project_id')

# Step 2: Generate strategy (Claude generates code based on hypothesis)
# Creates: strategy.py

# Step 3: Run backtest
python SCRIPTS/qc_backtest.py --run \
    --name "Hypothesis_3_Momentum" \
    --file strategy.py \
    --output PROJECT_LOGS/backtest_result.json

# Step 4: Evaluate
python3 << 'EOF'
import json, sys
sys.path.insert(0, 'SCRIPTS')
from decision_logic import evaluate_backtest, route_decision

with open('PROJECT_LOGS/backtest_result.json') as f:
    results = json.load(f)
with open('iteration_state.json') as f:
    state = json.load(f)

decision, reason, details = evaluate_backtest(
    results['performance'],
    state['thresholds']
)

routing = route_decision("backtest", decision, state['workflow']['iteration'])

print(f"DECISION={decision}")
print(f"NEXT_ACTION={routing['next_action']}")
EOF

# Step 5: Update iteration_state.json (Claude updates)

# Step 6: Git commit
git add iteration_state.json strategy.py PROJECT_LOGS/
git commit -m "backtest: Complete iteration 1 - PROCEED_TO_OPTIMIZATION

Results:
- Sharpe: 0.85
- Drawdown: 22%
- Trades: 67

Decision: PROCEED_TO_OPTIMIZATION
Reason: Decent performance, worth optimizing parameters"
```

---

## Related Skills

- **quantconnect** - Core strategy development (indicators, orders, risk management)
- **quantconnect-optimization** - Phase 4 optimization (requires backtest first!)
- **quantconnect-validation** - Phase 5 validation (walk-forward testing)
- **decision-framework** - Decision thresholds and routing logic
- **backtesting-analysis** - Interpreting backtest metrics

---

## Summary

**This skill covers**:
- ✅ Running backtests via QuantConnect API
- ✅ Uploading strategy files
- ✅ Parsing backtest results
- ✅ Phase 3 decision integration
- ✅ Common backtest errors and fixes
- ✅ Best practices for backtesting

**When to load**:
- Before running `/qc-backtest` command
- When debugging backtest API errors
- When interpreting backtest results
- When making Phase 3 routing decisions

**Key principle**: This skill focuses ONLY on backtesting. For optimization, load `quantconnect-optimization` skill instead.

---

**Version**: 1.0.0
**Last Updated**: November 10, 2025
**Status**: Production Ready
**Purpose**: Phase 3 backtesting via QuantConnect API
