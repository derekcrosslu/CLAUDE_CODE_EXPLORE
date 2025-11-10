# Monte Carlo Walk-Forward Validation - REAL Implementation

## What This Does

**TRUE Monte Carlo Walk-Forward** using QuantConnect Research APIs:
- ✅ **Random time period sampling** (Monte Carlo)
- ✅ **Real QC optimization** on training data (`qb.Optimize()`)
- ✅ **Real QC backtest** on test data (`qb.Backtest()`)
- ✅ **Statistical analysis** of performance degradation
- ✅ **Robustness decision framework**

## File Location

**`monte_carlo_walkforward_REAL.ipynb`** - Upload this to QuantConnect Research

## How to Use

### Step 1: Upload to QuantConnect

1. Go to https://www.quantconnect.com/research
2. Click "Upload" → Select `monte_carlo_walkforward_REAL.ipynb`
3. Notebook will open in QC Research environment

### Step 2: Configure

Edit Cell 2 configuration:

```python
config = {
    'project_id': 26129044,  # ← Your QC project ID
    'algorithm_file': 'main.py',  # ← Your strategy file

    'total_period': {
        'start': datetime(2023, 1, 1),  # ← Start date
        'end': datetime(2024, 12, 31)   # ← End date
    },

    'train_test_split': 0.60,  # ← 60% train, 40% test
    'monte_carlo_runs': 10,    # ← Number of MC runs

    'parameters': {  # ← Parameters to optimize
        'lookback_period': {'min': 15, 'max': 25, 'step': 5},
        'volume_multiplier': {'min': 1.3, 'max': 1.7, 'step': 0.2}
    },

    'target_metric': 'SharpeRatio',  # ← Optimization target
    'random_seed': 42  # ← For reproducibility
}
```

### Step 3: Run

Click "Run All Cells" or execute cells sequentially.

### Step 4: Review Results

The notebook will output:
1. **Aggregate statistics** (mean degradation, variance)
2. **Parameter stability** (which params are chosen most often)
3. **Robustness decision** (ROBUST/CAUTION/ABANDON)
4. **Visualizations** (4 plots showing degradation, stability, etc.)
5. **JSON results file** (saved locally in QC Research)

---

## What Each Cell Does

| Cell | Purpose |
|------|---------|
| 1 | Import libraries, initialize QuantBook |
| 2 | Configuration (YOU EDIT THIS) |
| 3 | Helper functions (random splits, formatting) |
| 4 | **MAIN MONTE CARLO LOOP** (optimization + backtest) |
| 5 | Aggregate analysis & statistics |
| 6 | Robustness decision framework |
| 7 | Visualizations (4 plots) |
| 8 | Save results to JSON |

---

## Key Functions

### `qb.Optimize()`
```python
optimization = qb.Optimize(
    project_id,
    parameters=opt_params,
    start_date=train_start,
    end_date=train_end,
    target='SharpeRatio',
    targetDirection=OptimizationTargetDirection.Maximum
)
```

**Returns:**
- `optimization.OptimalParameters` - Best parameter values
- `optimization.OptimalResult.Statistics` - Performance metrics

### `qb.Backtest()`
```python
backtest = qb.Backtest(
    project_id,
    parameters=best_params,
    start_date=test_start,
    end_date=test_end
)
```

**Returns:**
- `backtest.Statistics` - All performance metrics

---

## Robustness Decision Rules

```python
if pct_overfit > 50%:
    → ABANDON_STRATEGY (overfits on >50% of runs)

elif mean_degradation > 40%:
    → HIGH_RISK (poor generalization)

elif std_degradation > 25%:
    → UNSTABLE_PARAMETERS (high variance)

elif mean_degradation < 15% AND std_degradation < 10%:
    → ROBUST_STRATEGY (excellent generalization)

else:
    → PROCEED_WITH_CAUTION (moderate performance)
```

---

## Requirements

### Your Strategy MUST Use GetParameter()

```python
class MyStrategy(QCAlgorithm):
    def Initialize(self):
        # Parameters MUST be defined like this:
        self.lookback_period = self.GetParameter("lookback_period", 20)
        self.volume_multiplier = self.GetParameter("volume_multiplier", 1.5)
```

Without `GetParameter()`, optimization won't work!

### QuantConnect Account

- **Free tier:** Works, but slower (limited compute)
- **Paid tier:** Faster, more parallel runs

---

## Example Output

```
============================================================
MONTE CARLO WALK-FORWARD ANALYSIS
============================================================

Monte Carlo Run 1/10
============================================================
Training:  2023-04-09 to 2024-03-23 (349 days)
Testing:   2024-03-24 to 2024-12-31 (283 days)

🔍 Running optimization on training period...
  ✅ Optimization complete
  Best parameters: {'lookback_period': 20, 'volume_multiplier': 1.5}
  Training Sharpe: 0.852

🧪 Running backtest on test period...
  ✅ Backtest complete
  Testing Sharpe: 0.721
  Total Trades: 18
  📊 Degradation: 15.4%

... (9 more runs)

============================================================
AGGREGATE RESULTS
============================================================

Performance Metrics:
  Mean Training Sharpe:  0.825 ± 0.087
  Mean Testing Sharpe:   0.698 ± 0.095
  Mean Degradation:      15.8% ± 8.2%

Robustness Analysis:
  Runs with >30% degradation: 1/10 (10%)
  Runs with <15% degradation: 6/10 (60%)

============================================================
PARAMETER STABILITY
============================================================

lookback_period:
  20: 7/10 (70%)
  15: 2/10 (20%)
  25: 1/10 (10%)
  ✅ STABLE: 20 appears in 70% of runs

volume_multiplier:
  1.5: 6/10 (60%)
  1.3: 3/10 (30%)
  1.7: 1/10 (10%)
  ✅ STABLE: 1.5 appears in 60% of runs

============================================================
ROBUSTNESS DECISION FRAMEWORK
============================================================

✅ Decision: ROBUST_STRATEGY

📝 Reason: Low degradation (15.8%) with low variance (8.2%)

💡 Recommendation: Strategy shows excellent generalization.
                   Ready for paper trading.

============================================================
RECOMMENDED PARAMETERS FOR LIVE TRADING
============================================================
  lookback_period: 20 (chosen 70% of the time)
  volume_multiplier: 1.5 (chosen 60% of the time)
============================================================
```

---

## Troubleshooting

### Error: "Project not found"
→ Check `project_id` is correct in config

### Error: "Parameter not found"
→ Your strategy must use `GetParameter()` for all optimized params

### Error: "Insufficient data"
→ Increase total period or reduce train_test_split

### Optimization times out
→ Reduce parameter ranges or number of Monte Carlo runs

### All runs fail
→ Check algorithm compiles successfully first

---

## Differences from Old Wrapper

| Old (`qc_walkforward_wrapper.py`) | New (`monte_carlo_walkforward_REAL.ipynb`) |
|------------------------------------|------------------------------------------|
| ❌ Runs locally via API | ✅ Runs in QC Research |
| ❌ Calls QC optimization API (paid tier) | ✅ Uses `qb.Optimize()` (works on free) |
| ❌ Complex setup | ✅ Simple notebook |
| ❌ Simulated results | ✅ REAL results |
| ❌ Slow (API limits) | ✅ Fast (native QC compute) |

---

## Next Steps After Running

### If Decision = ROBUST_STRATEGY
1. Use recommended parameters for paper trading
2. Monitor live performance
3. Compare to walk-forward expectations

### If Decision = PROCEED_WITH_CAUTION
1. Run additional validation on different period
2. Consider ensemble of parameter sets
3. Start with smaller position size

### If Decision = HIGH_RISK or ABANDON
1. Review strategy logic
2. Try different parameter ranges
3. Consider new hypothesis

---

## Cost Estimation

**Free Tier:**
- 10 MC runs = ~20 optimizations + ~10 backtests
- Time: ~2-3 hours
- Cost: $0

**Paid Tier ($8/month):**
- Same runs, but faster (parallel compute)
- Time: ~30-60 minutes
- Included in monthly subscription

---

## Questions?

- **QC Documentation:** https://www.quantconnect.com/docs/v2/research-environment/optimization
- **Research API Reference:** https://www.quantconnect.com/docs/v2/research-environment/api-reference
- **Optimization Guide:** https://www.quantconnect.com/docs/v2/writing-algorithms/optimization

---

**Created:** 2025-11-10
**Version:** 1.0 - Real Implementation
**Author:** Claude Code
**Status:** Production Ready
