# Monte Carlo Walk-Forward Analysis - Usage Guide

## Overview

This framework implements Monte Carlo walk-forward optimization to validate strategy robustness without relying on third-party data providers. Everything runs within QuantConnect's ecosystem using their Research Notebooks.

## Why Monte Carlo Walk-Forward?

**Traditional Walk-Forward Issues:**
- Sequential windows may miss important market regimes
- Results depend heavily on chosen window size
- Limited testing of parameter stability

**Monte Carlo Advantages:**
- Tests strategy across randomly sampled periods
- More robust to period selection bias
- Provides distribution of expected degradation
- Identifies truly stable parameters

## How to Use in QuantConnect

### Step 1: Upload Notebook to QC Research

1. Log into QuantConnect
2. Navigate to Research → Notebooks
3. Upload `monte_carlo_walkforward.ipynb`
4. The notebook will have access to QC's data and API automatically

### Step 2: Configure Parameters

Edit the configuration cell:

```python
config = {
    'project_id': YOUR_PROJECT_ID,  # Get from QC project
    'total_period': {
        'start': datetime(2020, 1, 1),
        'end': datetime(2023, 12, 31)
    },
    'train_test_split': 0.60,  # 60/40 split
    'monte_carlo_runs': 10,    # More runs = more reliable
    'parameters': {
        # Define your optimizable parameters
        'rsi_oversold': {'min': 30, 'max': 45, 'step': 5},
        'bb_distance_pct': {'min': 1.02, 'max': 1.10, 'step': 0.04},
        'use_trend_filter': {'min': 0, 'max': 1, 'step': 1}
    },
    'validation_metric': 'sharpe_ratio'
}
```

### Step 3: Run Analysis

Execute all cells in sequence. The notebook will:

1. ✅ Generate random train/test splits
2. ✅ Run optimization on each training period
3. ✅ Validate on corresponding test period
4. ✅ Calculate performance degradation
5. ✅ Analyze parameter stability
6. ✅ Produce visualizations
7. ✅ Make robustness decision

### Step 4: Interpret Results

The notebook outputs:

**Performance Metrics:**
```
Mean Training Sharpe:  0.850 ± 0.120
Mean Testing Sharpe:   0.720 ± 0.095
Mean Degradation:      15.3% ± 8.7%
```

**Robustness Analysis:**
```
Runs with >30% degradation: 10% (overfitting indicator)
Runs with <15% degradation: 60% (good generalization)
```

**Parameter Stability:**
```
rsi_oversold:
  35: 7/10 (70%) ✅ STABLE
  40: 2/10 (20%)
  30: 1/10 (10%)
```

**Final Decision:**
```
Decision: ROBUST_STRATEGY
Reason: Low degradation (15.3%) with low variance (8.7%)
Recommendation: Strategy shows excellent generalization. Ready for live testing.
```

## Decision Framework

| Decision | Condition | Meaning |
|----------|-----------|---------|
| **ROBUST_STRATEGY** | Degradation < 15% AND Variance < 10% | Excellent generalization, ready for live |
| **PROCEED_WITH_CAUTION** | Degradation 15-40% | Acceptable, additional validation recommended |
| **UNSTABLE_PARAMETERS** | Variance > 25% | Parameters not stable across periods |
| **HIGH_RISK** | Degradation > 40% | Poor generalization, use with caution |
| **ABANDON_STRATEGY** | >50% runs show >30% degradation | Does not generalize, try new hypothesis |

## Integration with Autonomous Framework

After completing walk-forward analysis:

1. **If ROBUST_STRATEGY:**
   ```bash
   # Use recommended parameters for live trading
   # Update test_strategy.py with most stable parameters
   ```

2. **If PROCEED_WITH_CAUTION:**
   ```bash
   # Run additional out-of-sample validation
   /qc-validate
   ```

3. **If UNSTABLE/HIGH_RISK:**
   ```bash
   # Narrow parameter search space
   # Rerun optimization with tighter ranges
   /qc-optimize
   ```

4. **If ABANDON_STRATEGY:**
   ```bash
   # Start fresh with new hypothesis
   /qc-init
   ```

## Cost Considerations

**Monte Carlo Runs:** Each run requires 1 optimization + 1 backtest

- 10 runs = ~20 backtests
- 20 runs = ~40 backtests (more reliable, higher cost)
- 50 runs = ~100 backtests (very robust, expensive)

**Recommendation:** Start with 10 runs, increase to 20-30 for production strategies.

## Advantages vs External Walk-Forward Tools

**Using QC Research Notebooks:**
- ✅ Direct access to QC's high-quality data
- ✅ No data provider subscription fees
- ✅ Integrated with QC backtesting infrastructure
- ✅ Cloud compute (no local hardware needed)
- ✅ Results directly comparable to live trading
- ✅ No data synchronization issues

**External Tools:**
- ❌ Requires data subscription (Polygon, Alpha Vantage, etc.)
- ❌ Data quality/alignment issues
- ❌ Results may differ from QC live trading
- ❌ Additional complexity

## Visualizations

The notebook produces 4 key visualizations:

1. **Degradation Distribution** - Shows spread of OOS performance loss
2. **Training vs Testing Scatter** - Visual overfitting check
3. **Performance Over Runs** - Consistency across Monte Carlo samples
4. **Parameter Stability Heatmap** - Shows which parameters are chosen

All saved to `monte_carlo_walkforward_results.png`

## Output Files

- `walkforward_results_YYYYMMDD_HHMMSS.json` - Complete results with all metrics
- `monte_carlo_walkforward_results.png` - Visualization dashboard
- Can be downloaded from QC Research and committed to git

## Next Steps

After successful walk-forward validation:

1. Document results in `decisions_log.md`
2. Update `iteration_state.json` with walkforward status
3. Commit recommended parameters to git
4. Proceed to paper trading or live deployment

## Support

For issues or questions:
- Check QC Research API docs: https://www.quantconnect.com/docs/research/overview
- Review example notebooks in QC library
- Consult decisions_log.md for past analysis patterns
