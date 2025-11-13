# QuantConnect Optimization Strategies Guide

## Problem: Grid Search is Inefficient

**Grid Search** tests ALL combinations exhaustively:
- 5 position sizes × 7 stop losses × 4 holding periods = **140 backtests**
- Tests all variations of bad parameters before moving on
- **Wastes resources on clearly inferior regions**

Example waste:
```
Testing position_size=0.20 (too conservative):
  ❌ 28 backtests testing all stop_loss + holding_day combos
  Result: All negative Sharpe (worse than baseline)

Before testing position_size=0.30, 0.35, 0.40 (likely better)
```

---

## Better Strategies

### 1. **Euler Search** (Random Sampling) ✅ Recommended

**Strategy**: `QuantConnect.Optimizer.Strategies.EulerSearchOptimizationStrategy`

Tests random combinations across full parameter space:
```python
{
  "strategy": "QuantConnect.Optimizer.Strategies.EulerSearchOptimizationStrategy",
  "maximumConcurrentBacktests": 40  # Instead of 140
}
```

**Benefits**:
- ✅ Tests full parameter spectrum immediately
- ✅ 30-40 samples often enough to find optimum
- ✅ 70% fewer backtests than grid search
- ✅ No bias toward parameter order

**When to use**:
- 3+ parameters
- Don't know which parameters matter most
- Want fast, broad coverage

---

### 2. **Grid Search** (Exhaustive)

**Strategy**: `QuantConnect.Optimizer.Strategies.GridSearchOptimizationStrategy` (default)

Tests every combination:
```python
{
  "strategy": "QuantConnect.Optimizer.Strategies.GridSearchOptimizationStrategy"
}
```

**Benefits**:
- ✅ Guaranteed to find global optimum
- ✅ See full parameter surface
- ✅ Good for 1-2 parameters

**Drawbacks**:
- ❌ Exponential growth: n^p backtests (n values, p parameters)
- ❌ Tests bad regions exhaustively
- ❌ Expensive for 3+ parameters

**When to use**:
- 1-2 parameters only
- Small parameter grids (< 50 combinations)
- Need complete coverage for research

---

### 3. **Custom Optimization** (Advanced)

Create custom parameter sets:
```json
{
  "parameterSets": [
    {"position_size": 0.30, "stop_z": 5.5, "days": 20},
    {"position_size": 0.35, "stop_z": 6.0, "days": 25},
    {"position_size": 0.40, "stop_z": 5.0, "days": 30}
  ]
}
```

**When to use**:
- Have strong hypotheses about good regions
- Want targeted testing
- Combining insights from previous runs

---

## Recommendation Matrix

| Parameters | Grid Size | Recommended Strategy | Backtests |
|-----------|-----------|---------------------|-----------|
| 1-2 params | < 20 combos | Grid Search | All |
| 1-2 params | 20-50 combos | Grid Search or Euler | All or 30 |
| 3+ params | 50-200 combos | **Euler Search** | 30-50 |
| 3+ params | 200+ combos | Euler or Custom | 40-60 |

---

## Example: This Project

**Current (Inefficient)**:
```json
{
  "strategy": "GridSearchOptimizationStrategy",
  "parameters": [
    {"name": "position_size_per_pair", "min": 0.20, "max": 0.40, "step": 0.05},
    {"name": "stop_loss_z", "min": 4.0, "max": 7.0, "step": 0.5},
    {"name": "max_holding_days", "min": 15, "max": 30, "step": 5}
  ]
}
```
**Result**: 5 × 7 × 4 = **140 backtests** 💸

**Better Approach**:
```json
{
  "strategy": "EulerSearchOptimizationStrategy",
  "maximumConcurrentBacktests": 40,
  "parameters": [
    {"name": "position_size_per_pair", "min": 0.20, "max": 0.40, "step": 0.05},
    {"name": "stop_loss_z", "min": 4.0, "max": 7.0, "step": 0.5},
    {"name": "max_holding_days", "min": 15, "max": 30, "step": 5}
  ]
}
```
**Result**: **40 random samples** across full space ✅
**Savings**: 100 backtests (71% reduction)

---

## Implementation

Update `qc_optimize.py` to support strategy selection:

```python
@cli.command()
@click.option('--strategy',
              default='EulerSearchOptimizationStrategy',
              help='Optimization strategy (GridSearchOptimizationStrategy, EulerSearchOptimizationStrategy)')
@click.option('--max-backtests',
              default=40,
              help='Maximum backtests for Euler search')
def run(config, state, output, strategy, max_backtests):
    # Use provided strategy instead of hardcoded GridSearch
    ...
```

---

## Lessons Learned

1. **Grid search explodes** with number of parameters (exponential)
2. **Random sampling** often finds optimum in 30-40% of tests
3. **Parameter order matters** in grid search (tested sequentially)
4. **Always estimate total backtests** before running
5. **Cost vs benefit**: Is exhaustive search worth 3x the cost?

---

## References

- [QuantConnect Optimization Docs](https://www.quantconnect.com/docs/v2/cloud-platform/optimization/overview)
- [Grid Search vs Random Search (Bergstra & Bengio 2012)](http://www.jmlr.org/papers/volume13/bergstra12a/bergstra12a.pdf)
- Euler Search approximates random search with better coverage
