---
name: Decision Framework
description: Autonomous decision-making framework for strategy evaluation and routing (project)
---

# Autonomous Decision Framework

This skill provides the complete decision-making framework for evaluating trading strategies and making autonomous routing decisions through the 5-phase workflow.

## Purpose

When you (Claude Code) need to decide what to do next after completing a phase (backtest, optimization, or validation), load this skill to understand the decision criteria and make the correct routing decision.

## Core Philosophy

**Decision-making is deterministic and threshold-based**, not subjective:

1. **Safety First**: Prioritize identifying dangerous patterns (overfitting) before evaluating performance
2. **Statistical Significance**: Require minimum trade count for reliable metrics
3. **Risk-Adjusted**: Use Sharpe ratio (not raw returns) as primary metric
4. **Conservative**: Err on side of abandoning rather than proceeding with weak strategies

## When to Use This Skill

Load this skill when:
- Evaluating backtest results (Phase 3)
- Deciding whether to optimize parameters (after Phase 3)
- Evaluating optimization results (Phase 4)
- Deciding whether to validate (after Phase 4)
- Evaluating validation results (Phase 5)
- Making deployment decisions (after Phase 5)
- **Confused about what decision to make**
- **Unsure if results are good or concerning**

---

## Phase 3: Backtest Evaluation

### Decision Framework (4-Tier System)

After a backtest completes, apply this decision framework **in order**:

#### Tier 1: Overfitting Detection (HIGHEST PRIORITY)

**Check for red flags that indicate unreliable results:**

1. **Too Perfect Sharpe**
   - Threshold: Sharpe > 3.0
   - Decision: **ESCALATE_TO_HUMAN**
   - Reason: Extremely high Sharpe ratios are suspicious and often indicate overfitting or data snooping

2. **Too Few Trades**
   - Threshold: 0 < trades < 20
   - Decision: **ESCALATE_TO_HUMAN**
   - Reason: Insufficient sample size for statistical significance; any metrics are unreliable

3. **Suspiciously High Win Rate**
   - Threshold: Win rate > 75%
   - Decision: **ESCALATE_TO_HUMAN**
   - Reason: Real strategies rarely achieve such high win rates; suggests overfitting or look-ahead bias

**If ANY overfitting signal triggers → ESCALATE_TO_HUMAN (do not proceed)**

#### Tier 2: Minimum Viable Threshold (ABANDON LINE)

**Check if strategy meets basic requirements:**

1. **Sharpe Ratio**
   - Threshold: Sharpe < 0.5
   - Decision: **ABANDON_HYPOTHESIS**
   - Reason: Strategy doesn't beat risk-free rate sufficiently

2. **Maximum Drawdown**
   - Threshold: Max drawdown > 40%
   - Decision: **ABANDON_HYPOTHESIS**
   - Reason: Excessive risk, not acceptable for live trading

3. **Trade Count**
   - Threshold: Total trades < 30
   - Decision: **ABANDON_HYPOTHESIS**
   - Reason: Insufficient trades for statistical significance

**If ANY minimum viable check fails → ABANDON_HYPOTHESIS**

#### Tier 3: Production Ready (SKIP OPTIMIZATION)

**Check if strategy is already strong enough for validation:**

Must meet ALL criteria:
- Sharpe ratio >= 1.0
- Max drawdown <= 30%
- Total trades >= 100
- Win rate >= 40%

**If all criteria met → PROCEED_TO_VALIDATION** (skip optimization, already strong)

#### Tier 4: Optimization Worthy

**Check if strategy is worth optimizing:**

Must meet ALL criteria:
- Sharpe ratio >= 0.7
- Max drawdown <= 35%
- Total trades >= 50

**If all criteria met → PROCEED_TO_OPTIMIZATION** (decent baseline, try to improve)

#### Tier 5: Marginal Case

**Between minimum viable and optimization worthy:**

If:
- Sharpe >= 0.5 (meets minimum)
- Total trades >= 30 (meets minimum)
- But doesn't qualify for optimization worthy

**Decision: PROCEED_TO_OPTIMIZATION** (marginal, but worth trying to improve)

---

## Using the Decision Logic Module

The decision framework is implemented in `SCRIPTS/decision_logic.py` for consistency and testing.

### In Python (Preferred)

```python
import json
import sys
sys.path.insert(0, 'SCRIPTS')
from decision_logic import evaluate_backtest

# Load backtest results
with open('PROJECT_LOGS/backtest_result.json', 'r') as f:
    results = json.load(f)

# Load thresholds from iteration_state.json
with open('iteration_state.json', 'r') as f:
    state = json.load(f)

# Evaluate
decision, reason, details = evaluate_backtest(
    results['performance'],
    state['thresholds']
)

print(f"Decision: {decision}")
print(f"Reason: {reason}")
print(f"Details: {details}")
```

### In Bash (For /qc-backtest command)

```bash
# Call Python module from bash
python3 << 'EOF'
import json, sys
sys.path.insert(0, 'SCRIPTS')
from decision_logic import evaluate_backtest

with open('PROJECT_LOGS/backtest_result.json') as f:
    results = json.load(f)
with open('iteration_state.json') as f:
    state = json.load(f)

decision, reason, details = evaluate_backtest(
    results['performance'],
    state['thresholds']
)

# Output for bash to parse
print(f"DECISION={decision}")
print(f"REASON={reason}")
EOF
```

---

## Phase 4: Optimization Evaluation

After optimization completes, evaluate the improvement:

### Decision Criteria

1. **Performance Degraded** (improvement_pct < 0)
   - Decision: **USE_BASELINE_PARAMS**
   - Reason: Optimization made things worse, use original parameters

2. **Minimal Improvement** (0% <= improvement < 5%)
   - Decision: **USE_BASELINE_PARAMS**
   - Reason: Not worth the risk, use baseline

3. **Excessive Improvement** (improvement > 30%)
   - Decision: **ESCALATE_TO_HUMAN**
   - Reason: Too much improvement suggests overfitting to training period

4. **Reasonable Improvement** (5% <= improvement <= 30%)
   - Decision: **PROCEED_TO_VALIDATION**
   - Reason: Good improvement without overfitting risk

### Example

```python
from decision_logic import evaluate_optimization

decision, reason, details = evaluate_optimization(
    baseline_sharpe=0.85,
    optimized_sharpe=1.15,
    improvement_pct=0.35,  # 35% improvement
    thresholds=thresholds
)
# Returns: ESCALATE_TO_HUMAN (improvement too high)
```

---

## Phase 5: Validation Evaluation

After walk-forward validation, evaluate robustness:

### Decision Criteria

1. **Severe Degradation** (degradation > 40%)
   - Decision: **ABANDON_HYPOTHESIS**
   - Reason: Strategy performance collapses out-of-sample

2. **Low Robustness** (robustness_score < 0.5)
   - Decision: **ABANDON_HYPOTHESIS**
   - Reason: Strategy unstable across different periods

3. **Minimal Degradation** (degradation < 15% AND robustness > 0.75)
   - Decision: **DEPLOY_STRATEGY**
   - Reason: Strategy is robust and ready for live trading

4. **Moderate Degradation** (degradation < 30% AND robustness > 0.60)
   - Decision: **PROCEED_WITH_CAUTION**
   - Reason: Acceptable but requires close monitoring

5. **Borderline**
   - Decision: **ESCALATE_TO_HUMAN**
   - Reason: Results unclear, needs human judgment

---

## Decision Examples

### Example 1: Zero Trades Strategy

**Input**:
```json
{
  "sharpe_ratio": 0.0,
  "max_drawdown": 0.0,
  "total_trades": 0,
  "win_rate": 0.0
}
```

**Analysis**:
1. Check overfitting: trades = 0, so skip (not between 0 and 20)
2. Check minimum viable: trades < 30 → **FAIL**

**Decision**: ABANDON_HYPOTHESIS

**Reason**: "Insufficient trades for statistical significance (0 < 30)"

**Lesson**: Strategy never traded, entry conditions too restrictive

---

### Example 2: Optimization Worthy Strategy

**Input**:
```json
{
  "sharpe_ratio": 0.85,
  "max_drawdown": 0.22,
  "total_trades": 67,
  "win_rate": 0.42
}
```

**Analysis**:
1. Check overfitting: All pass (Sharpe < 3.0, trades > 20, win_rate < 0.75)
2. Check minimum viable: All pass (Sharpe > 0.5, DD < 0.40, trades > 30)
3. Check production ready: Fail (Sharpe 0.85 < 1.0)
4. Check optimization worthy: Pass (Sharpe > 0.7, DD < 0.35, trades > 50)

**Decision**: PROCEED_TO_OPTIMIZATION

**Reason**: "Decent performance (Sharpe 0.85, DD 22.0%, 67 trades), worth optimizing parameters"

---

### Example 3: Suspiciously Good Strategy

**Input**:
```json
{
  "sharpe_ratio": 4.2,
  "max_drawdown": 0.05,
  "total_trades": 25,
  "win_rate": 0.88
}
```

**Analysis**:
1. Check overfitting: **MULTIPLE FAILURES**
   - Sharpe 4.2 > 3.0 → Too perfect
   - Trades 25 > 20 but win rate 0.88 > 0.75 → Too high

**Decision**: ESCALATE_TO_HUMAN

**Reason**: "Sharpe ratio too perfect (4.20 > 3.0), possible overfitting"

**Lesson**: Don't trust results that are "too good to be true"

---

## Common Confusion Points

### "The Sharpe ratio is 0.9, should I proceed?"

**Load this skill and check**:
1. Is Sharpe > 3.0? No → Not overfitting
2. Is Sharpe < 0.5? No → Meets minimum viable
3. Are trades >= 30? Check the actual count
4. Is Sharpe >= 1.0? No (0.9 < 1.0) → Not production ready
5. Is Sharpe >= 0.7? Yes → Optimization worthy

**Decision: PROCEED_TO_OPTIMIZATION**

### "The strategy made 200% returns, but Sharpe is only 0.6"

**Load this skill and remember**:
- We use **Sharpe ratio** (risk-adjusted), not raw returns
- High returns with high volatility = bad Sharpe
- Sharpe 0.6 > 0.5 (minimum viable) but < 0.7 (optimization worthy)
- Check drawdown and trade count to make final decision

### "I got 5 trades with 100% win rate"

**This is an overfitting signal**:
- 5 trades < 20 → ESCALATE_TO_HUMAN (too few)
- Even if it were 25 trades, win rate 100% > 75% → ESCALATE_TO_HUMAN

**Never trust extremely high win rates**

---

## Threshold Customization

The default thresholds are in `iteration_state.json`:

```json
{
  "thresholds": {
    "minimum_viable": {
      "sharpe_ratio": 0.5,
      "max_drawdown": 0.40,
      "min_trades": 30
    },
    "optimization_worthy": {
      "sharpe_ratio": 0.7,
      "max_drawdown": 0.35,
      "min_trades": 50
    },
    "production_ready": {
      "sharpe_ratio": 1.0,
      "max_drawdown": 0.30,
      "min_trades": 100,
      "win_rate": 0.40
    },
    "overfitting_signals": {
      "too_perfect_sharpe": 3.0,
      "too_few_trades": 20,
      "win_rate_too_high": 0.75
    }
  }
}
```

**These thresholds are conservative by design.**

If you're unsure whether to adjust them, **don't**. The defaults are based on industry best practices.

---

## Integration with Commands

### In /qc-backtest

After backtest completes:
1. Load decision-framework skill (you're reading it now!)
2. Call `decision_logic.evaluate_backtest()`
3. Apply the decision returned
4. Update iteration_state.json
5. Make git commit with decision and metrics

### In /qc-optimize

After optimization completes:
1. Load decision-framework skill
2. Call `decision_logic.evaluate_optimization()`
3. Apply the decision returned
4. Update iteration_state.json

### In /qc-validate

After validation completes:
1. Load decision-framework skill
2. Call `decision_logic.evaluate_validation()`
3. Apply the decision returned
4. Update iteration_state.json

---

## Testing the Decision Framework

The decision_logic.py module includes self-tests:

```bash
python3 SCRIPTS/decision_logic.py
```

This runs 6 test cases covering all decision paths:
1. Zero trades → ABANDON
2. Below minimum → ABANDON
3. Optimization worthy → PROCEED_TO_OPTIMIZATION
4. Production ready → PROCEED_TO_VALIDATION
5. Overfitting (too perfect) → ESCALATE
6. Overfitting (too few trades) → ESCALATE

All tests should pass ✅

---

## Summary

**When confused about a decision**:

1. Load this skill (`quantconnect` skill already loaded during backtest)
2. Extract performance metrics from backtest results
3. Call `decision_logic.evaluate_backtest()` with metrics and thresholds
4. Trust the decision returned (it's tested and consistent)
5. Update iteration_state.json with decision and reason
6. Make structured git commit

**Key Principle**: The decision framework is deterministic. Given the same inputs, it always produces the same output. This ensures consistency across all hypotheses.

**When in doubt**: ESCALATE_TO_HUMAN is always a safe choice. Better to ask for human review than make a wrong autonomous decision.

---

## Related Files

- `SCRIPTS/decision_logic.py` - Implementation of decision functions
- `iteration_state_schema.md` - Schema for thresholds configuration
- `.claude/commands/qc-backtest.md` - How to use in backtest command
- `PROJECT_DOCUMENTATION/autonomous_decision_framework.md` - Complete architecture

---

**Version**: 1.0.0
**Last Updated**: November 10, 2025
**Status**: Production Ready
