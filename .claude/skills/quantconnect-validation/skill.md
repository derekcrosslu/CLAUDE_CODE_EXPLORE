---
name: QuantConnect Validation
description: QuantConnect walk-forward validation and Phase 5 robustness testing (project)
---

# QuantConnect Validation Skill (Phase 5)

This skill provides focused knowledge for **walk-forward validation** and Phase 5 robustness testing.

## When to Use This Skill

Load this skill when:
- Running `/qc-validate` command
- Implementing walk-forward validation
- Testing out-of-sample performance
- Evaluating strategy robustness
- Making deployment decisions

---

## Walk-Forward Validation Approach

Walk-forward validation tests strategy robustness by:
1. Training on in-sample period
2. Testing on out-of-sample period
3. Comparing performance degradation

**Purpose**: Detect overfitting and ensure strategy generalizes to new data.

### Time Period Split

For a 5-year backtest (2019-2023):
- **In-sample (training)**: 2019-2022 (80%)
- **Out-of-sample (testing)**: 2023 (20%)

```python
# In-sample backtest
self.SetStartDate(2019, 1, 1)
self.SetEndDate(2022, 12, 31)

# Out-of-sample backtest
self.SetStartDate(2023, 1, 1)
self.SetEndDate(2023, 12, 31)
```

### Validation Metrics

1. **Performance Degradation**
   - Measures: (In-sample Sharpe - OOS Sharpe) / In-sample Sharpe
   - < 15%: Excellent robustness
   - 15-30%: Acceptable degradation
   - 30-40%: Concerning degradation
   - > 40%: Severe degradation (likely overfit)

2. **Robustness Score**
   - Measures: OOS Sharpe / In-sample Sharpe
   - > 0.75: High robustness
   - 0.60-0.75: Moderate robustness
   - < 0.60: Low robustness

---

## Implementation: Walk-Forward Validation

```python
import sys
sys.path.insert(0, 'SCRIPTS')
from qc_backtest import QuantConnectAPI
import json

def walk_forward_validation(project_id, strategy_code, use_optimized_params=True):
    """
    Run walk-forward validation on strategy.

    Args:
        project_id: QC project ID
        strategy_code: Strategy code (with parameters)
        use_optimized_params: Use optimized or baseline parameters

    Returns:
        in_sample_performance: Performance on training period
        out_of_sample_performance: Performance on testing period
        degradation_pct: Performance degradation percentage
        robustness_score: OOS/In-sample Sharpe ratio
    """
    api = QuantConnectAPI()

    # Step 1: Run in-sample backtest (2019-2022)
    strategy_in_sample = strategy_code.replace(
        "self.SetStartDate(2019, 1, 1)",
        "self.SetStartDate(2019, 1, 1)"
    ).replace(
        "self.SetEndDate(2023, 12, 31)",
        "self.SetEndDate(2022, 12, 31)"
    )

    api.upload_file(project_id, strategy_in_sample, "Main.py")
    backtest_is = api.create_backtest(project_id, "InSample_Validation")
    result_is = api.wait_for_backtest(project_id, backtest_is['backtestId'], timeout=600)
    perf_is = api.parse_backtest_results(result_is)

    # Step 2: Run out-of-sample backtest (2023)
    strategy_oos = strategy_code.replace(
        "self.SetStartDate(2019, 1, 1)",
        "self.SetStartDate(2023, 1, 1)"
    ).replace(
        "self.SetEndDate(2023, 12, 31)",
        "self.SetEndDate(2023, 12, 31)"
    )

    api.upload_file(project_id, strategy_oos, "Main.py")
    backtest_oos = api.create_backtest(project_id, "OutOfSample_Validation")
    result_oos = api.wait_for_backtest(project_id, backtest_oos['backtestId'], timeout=600)
    perf_oos = api.parse_backtest_results(result_oos)

    # Step 3: Calculate metrics
    sharpe_is = perf_is['sharpe_ratio']
    sharpe_oos = perf_oos['sharpe_ratio']

    degradation_pct = (sharpe_is - sharpe_oos) / sharpe_is if sharpe_is != 0 else 1.0
    robustness_score = sharpe_oos / sharpe_is if sharpe_is != 0 else 0.0

    return {
        'in_sample': perf_is,
        'out_of_sample': perf_oos,
        'degradation_pct': degradation_pct,
        'robustness_score': robustness_score
    }
```

---

## Phase 5 Decision Integration

After validation completes, evaluate robustness:

```python
import sys
sys.path.insert(0, 'SCRIPTS')
from decision_logic import evaluate_validation, route_decision

# Load validation results
with open('PROJECT_LOGS/validation_result.json') as f:
    validation = json.load(f)

# Evaluate
decision, reason, details = evaluate_validation(
    in_sample_sharpe=validation['in_sample']['sharpe_ratio'],
    out_of_sample_sharpe=validation['out_of_sample']['sharpe_ratio'],
    degradation_pct=validation['degradation_pct'],
    robustness_score=validation['robustness_score'],
    thresholds=state['thresholds']
)

print(f"Decision: {decision}")
print(f"Reason: {reason}")

# Route to next phase
routing = route_decision(
    current_phase="validation",
    decision=decision,
    iteration=state['workflow']['iteration']
)

print(f"Next Action: {routing['next_action']}")
```

**Possible decisions**:
- `ABANDON_HYPOTHESIS` → Severe degradation (> 40%), start new hypothesis
- `DEPLOY_STRATEGY` → Minimal degradation (< 15%), deploy with confidence
- `PROCEED_WITH_CAUTION` → Moderate degradation (15-30%), deploy but monitor
- `ESCALATE_TO_HUMAN` → Borderline results, needs human judgment

**Decision thresholds** (from iteration_state.json):
- Degradation > 40%: ABANDON (collapses out-of-sample)
- Robustness < 0.5: ABANDON (too unstable)
- Degradation < 15% AND Robustness > 0.75: DEPLOY (excellent)
- Degradation < 30% AND Robustness > 0.60: PROCEED_WITH_CAUTION (acceptable)
- Otherwise: ESCALATE_TO_HUMAN (borderline)

---

## Best Practices for Validation

### 1. Use Realistic Time Splits

- **80/20 split**: Standard (4 years training, 1 year testing)
- **70/30 split**: Conservative (more out-of-sample testing)
- **60/40 split**: Very conservative (extensive testing)

```python
# 5-year backtest (2019-2023)
# 80/20 split:
in_sample = (2019, 1, 1) to (2022, 12, 31)  # 4 years
out_of_sample = (2023, 1, 1) to (2023, 12, 31)  # 1 year
```

### 2. Ensure Sufficient Out-of-Sample Data

- **Minimum**: 6 months
- **Good**: 1 year
- **Excellent**: 2+ years

Too short out-of-sample periods give unreliable results.

### 3. Don't Peek at Out-of-Sample

**Critical**: Never optimize or adjust strategy based on out-of-sample results.
- Out-of-sample is for **testing only**
- If you adjust based on OOS, it becomes in-sample
- This defeats the purpose of validation

### 4. Check Trade Count in Both Periods

```python
trades_is = validation['in_sample']['total_trades']
trades_oos = validation['out_of_sample']['total_trades']

# Both should have sufficient trades
if trades_is < 30 or trades_oos < 10:
    print("WARNING: Insufficient trades for validation")
```

### 5. Compare Multiple Metrics

Don't just look at Sharpe ratio:
```python
# Compare multiple metrics
metrics_to_compare = [
    'sharpe_ratio',
    'max_drawdown',
    'win_rate',
    'profit_factor',
    'total_trades'
]

for metric in metrics_to_compare:
    is_val = validation['in_sample'][metric]
    oos_val = validation['out_of_sample'][metric]
    degradation = (is_val - oos_val) / is_val if is_val != 0 else 0
    print(f"{metric}: {is_val:.2f} → {oos_val:.2f} ({degradation:.1%} degradation)")
```

---

## Common Validation Issues

### 1. Severe Degradation (> 40%)

**Problem**: Strategy overfit to in-sample period

**Example**:
- In-sample Sharpe: 1.5
- Out-of-sample Sharpe: 0.6
- Degradation: 60%

**Decision**: ABANDON_HYPOTHESIS

**Fix for next hypothesis**:
- Simplify strategy (fewer parameters)
- Use longer training period
- Avoid curve-fitting

### 2. Different Market Regimes

**Problem**: In-sample was bull market, out-of-sample was bear market

**Example**:
- 2019-2022: Bull market → Sharpe 1.2
- 2023: Bear market → Sharpe -0.3

**Decision**: Not necessarily overfit, but strategy not robust across regimes

**Fix**:
- Test across multiple regimes
- Add regime detection
- Use defensive strategies

### 3. Low Trade Count in Out-of-Sample

**Problem**: Strategy stops trading in OOS period

**Example**:
- In-sample: 120 trades
- Out-of-sample: 3 trades

**Decision**: ESCALATE_TO_HUMAN

**Reason**: Insufficient OOS data for reliable validation

### 4. Opposite Results

**Problem**: OOS Sharpe is negative while in-sample was positive

**Example**:
- In-sample Sharpe: 0.8
- Out-of-sample Sharpe: -0.5

**Decision**: ABANDON_HYPOTHESIS

**Reason**: Strategy completely fails out-of-sample

---

## Integration with /qc-validate Command

The `/qc-validate` command should:

1. **Read iteration_state.json**
   - Get project_id (from backtest/optimization)
   - Get parameters (baseline or optimized)
   - Validate current_phase is "optimization" or "backtest"

2. **Load QuantConnect-Validation Skill** (this skill!)
   - Get walk-forward validation approach
   - Get time period splits
   - Get decision integration logic

3. **Modify strategy for time splits**
   - Extract current date range
   - Calculate 80/20 split
   - Generate in-sample and OOS versions

4. **Run validation**
   - Run in-sample backtest
   - Run out-of-sample backtest
   - Calculate degradation and robustness

5. **Evaluate robustness (Phase 5)**
   - Calculate degradation percentage
   - Calculate robustness score
   - Call `decision_logic.evaluate_validation()`
   - Call `decision_logic.route_decision()`

6. **Update iteration_state.json**
   - Store validation results
   - Store decision
   - Update current_phase to "deployed" or "abandoned"

7. **Git commit**
   - Include in-sample vs OOS metrics
   - Include decision and rationale

---

## Example: Complete /qc-validate Workflow

```bash
# Step 1: Read prerequisites
PROJECT_ID=$(cat iteration_state.json | jq -r '.project.project_id')
USE_OPTIMIZED=$(cat iteration_state.json | jq -r '.phase_results.optimization.decision == "PROCEED_TO_VALIDATION"')

# Step 2: Run walk-forward validation
python3 << 'EOF'
import sys, json
sys.path.insert(0, 'SCRIPTS')
from walk_forward_validation import walk_forward_validation

with open('iteration_state.json') as f:
    state = json.load(f)
with open('strategy.py') as f:
    strategy_code = f.read()

# Use optimized params if available, otherwise baseline
use_optimized = state.get('phase_results', {}).get('optimization', {}).get('decision') == 'PROCEED_TO_VALIDATION'

validation = walk_forward_validation(
    state['project']['project_id'],
    strategy_code,
    use_optimized_params=use_optimized
)

with open('PROJECT_LOGS/validation_result.json', 'w') as f:
    json.dump(validation, f, indent=2)

print(json.dumps(validation, indent=2))
EOF

# Step 3: Evaluate robustness
python3 << 'EOF'
import sys, json
sys.path.insert(0, 'SCRIPTS')
from decision_logic import evaluate_validation, route_decision

with open('PROJECT_LOGS/validation_result.json') as f:
    validation = json.load(f)
with open('iteration_state.json') as f:
    state = json.load(f)

decision, reason, details = evaluate_validation(
    in_sample_sharpe=validation['in_sample']['sharpe_ratio'],
    out_of_sample_sharpe=validation['out_of_sample']['sharpe_ratio'],
    degradation_pct=validation['degradation_pct'],
    robustness_score=validation['robustness_score'],
    thresholds=state['thresholds']
)

routing = route_decision("validation", decision, state['workflow']['iteration'])

print(f"DECISION={decision}")
print(f"NEXT_ACTION={routing['next_action']}")
EOF

# Step 4: Update iteration_state.json (Claude updates)

# Step 5: Git commit
git add iteration_state.json PROJECT_LOGS/validation_result.json
git commit -m "validation: Complete - DEPLOY_STRATEGY

In-Sample (2019-2022):
- Sharpe: 0.97
- Drawdown: 18%
- Trades: 142

Out-of-Sample (2023):
- Sharpe: 0.89
- Drawdown: 22%
- Trades: 38

Degradation: 8.2%
Robustness: 0.92

Decision: DEPLOY_STRATEGY
Reason: Minimal degradation, high robustness, ready for deployment"
```

---

## Related Skills

- **quantconnect** - Core strategy development
- **quantconnect-backtest** - Phase 3 backtesting
- **quantconnect-optimization** - Phase 4 optimization
- **decision-framework** - Decision thresholds and routing logic

---

## Summary

**This skill covers**:
- ✅ Walk-forward validation approach
- ✅ Time period splits (80/20)
- ✅ Performance degradation calculation
- ✅ Robustness score evaluation
- ✅ Phase 5 decision integration
- ✅ Deployment readiness assessment

**When to load**:
- Before running `/qc-validate` command
- When implementing walk-forward validation
- When evaluating out-of-sample performance
- When making deployment decisions

**Key principle**: Out-of-sample testing is the final check before deployment. Never adjust strategy based on OOS results - that defeats the validation purpose.

---

**Version**: 1.0.0
**Last Updated**: November 10, 2025
**Status**: Production Ready
**Purpose**: Phase 5 walk-forward validation and robustness testing
