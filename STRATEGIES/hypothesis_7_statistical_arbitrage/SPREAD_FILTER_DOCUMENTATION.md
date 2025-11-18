# Spread Deviation Filter - Documentation

## Overview

The Spread Deviation Filter is a risk management layer that monitors abnormal spread behavior and exits positions when the spread deviates beyond acceptable bounds. This filter is **DISABLED by default** and can be enabled for testing and optimization.

## Configuration Parameters

All parameters are configurable via `GetParameter()` for optimization:

### Enable/Disable
- **`enable_spread_filter`** (default: `False`)
  - Set to `True` to activate the spread filter
  - When disabled, the filter has no effect on trading

### Spread Deviation Thresholds
- **`spread_warning_threshold`** (default: `3.0`)
  - Warning level in standard deviations from historical mean
  - Currently for monitoring only (logged but no action taken)

- **`spread_critical_threshold`** (default: `4.0`)
  - Critical level in standard deviations from historical mean
  - **ACTION: Exit position immediately** when exceeded

### Lookback Period
- **`spread_lookback_days`** (default: `60`)
  - Historical window for calculating spread statistics
  - Not currently used (uses `lookback_period` from main strategy)
  - Reserved for future enhancement

## How It Works

### 1. Spread Calculation
For each pair, the filter monitors:
- **Current spread**: `log(long_price) - log(short_price)`
- **Historical mean**: Rolling average over lookback period
- **Historical std**: Standard deviation over lookback period

### 2. Deviation Calculation
```python
spread_deviation = abs(current_spread - spread_mean) / spread_std
```

### 3. Exit Trigger
When a position is open and `enable_spread_filter = True`:
- If `spread_deviation > spread_critical_threshold`:
  - Exit position immediately
  - Exit reason: `SPREAD_CRITICAL`
  - Log: "SPREAD FILTER TRIGGERED"

## Integration with Main Strategy

### Filter Priority
The spread filter is checked **4th** in the exit logic:
1. Mean reversion (`Z < z_exit_threshold`)
2. Timeout (`holding_days >= max_holding_days`)
3. Stop loss (`|Z| > stop_loss_z`)
4. **Spread filter** (`spread_deviation > critical_threshold`)

### Exit Logging
When the spread filter triggers an exit, the log includes:
```
EXIT - PAIR_NAME | SPREAD_CRITICAL | Entry Z=X.XX → Exit Z=Y.YY | Spread Δ=Z.ZZZZ | ...
```

The `Spread Δ` shows the change from entry to exit spread value.

## Usage Examples

### Example 1: Enable for Testing
```python
# In QuantConnect parameters or GetParameter defaults
enable_spread_filter = True
spread_critical_threshold = 4.0  # Exit if spread > 4 std devs
```

### Example 2: Optimization Range
```xml
<Parameter name="spread_critical_threshold" type="double" min="3.0" max="5.0" step="0.5">
  <Value>4.0</Value>
</Parameter>
```

### Example 3: Disable (Default)
```python
# Filter is off by default
enable_spread_filter = False  # No spread monitoring
```

## When to Use This Filter

### Enable When:
- **Regime changes**: Market structure shifts could cause spread distributions to change
- **Structural breaks**: Corporate actions, M&A, index rebalancing
- **Extreme volatility**: Spread behavior becomes erratic and unpredictable
- **Testing robustness**: Evaluate if spread limits improve risk-adjusted returns

### Disable When:
- **Normal operations**: Baseline strategy already uses Z-score entry/exit
- **High correlation**: Spread filter may be redundant with stop-loss Z
- **Testing baseline**: Want to isolate performance without additional filters

## Risk Considerations

### Overlap with Existing Filters
- **Stop Loss Z**: Already exits when Z-score > threshold
- **Spread filter**: Exits based on raw spread deviation
- These are **correlated but not identical**:
  - Z-score = (spread - mean) / std (normalized)
  - Spread deviation = |spread - mean| / std (same calculation!)

**Note**: Spread filter is essentially checking the same condition as Z-score, just phrased differently. Main utility is as a **secondary safety net** with different threshold.

### Potential Issues
1. **Redundancy**: May trigger at similar times as stop-loss Z
2. **Overfitting**: Adding more exit conditions can reduce sample size
3. **Look-ahead bias**: Uses same spread data for both Z-score and deviation check

## Comparison to Other Filters

| Filter | Purpose | Entry Effect | Exit Effect | Default State |
|--------|---------|--------------|-------------|---------------|
| VIX | Volatility regime | Reduce size or skip | Exit if crisis | ENABLED |
| ADF | Cointegration health | Skip if broken | Exit if broken | ENABLED |
| Half-Life | Mean reversion speed | Reduce size if slow | Exit if too slow | ENABLED |
| **Spread** | **Abnormal behavior** | **None** | **Exit if extreme** | **DISABLED** |

## Future Enhancements

Potential improvements (not currently implemented):

1. **Warning state**: Reduce position size when `spread_deviation > warning_threshold`
2. **Separate lookback**: Use `spread_lookback_days` instead of main `lookback_period`
3. **Adaptive thresholds**: Adjust critical threshold based on VIX regime
4. **Direction-aware**: Different thresholds for long vs short spread positions

## Complete Parameter List

Summary of all spread filter parameters:

```python
# Enable/Disable
self.enable_spread_filter = self.get_parameter("enable_spread_filter", False)

# Thresholds (standard deviations)
self.spread_warning_threshold = float(self.get_parameter("spread_warning_threshold", 3.0))
self.spread_critical_threshold = float(self.get_parameter("spread_critical_threshold", 4.0))

# Lookback (days) - reserved for future use
self.spread_lookback_days = int(self.get_parameter("spread_lookback_days", 60))
```

## Initialization Log

When `enable_spread_filter = True`, you'll see:
```
======================================================================
Spread Deviation Filter initialized
Warning threshold: 3.0 std deviations
Critical threshold: 4.0 std deviations
Lookback period: 60 days
======================================================================
```

## Testing Recommendations

### Phase 1: Baseline
- `enable_spread_filter = False`
- Establish baseline performance without filter

### Phase 2: Conservative
- `enable_spread_filter = True`
- `spread_critical_threshold = 5.0` (very permissive)
- Observe how often it triggers

### Phase 3: Moderate
- `spread_critical_threshold = 4.0` (default)
- Compare to baseline

### Phase 4: Aggressive
- `spread_critical_threshold = 3.0` (tight control)
- Evaluate if tighter risk control improves metrics

### Phase 5: Optimization
- Optimize `spread_critical_threshold` in range [3.0, 5.0]
- Compare Sharpe, drawdown, and trade count to baseline

---

**Status**: Implemented and ready for testing
**Default**: DISABLED (safe for existing backtests)
**Impact**: None when disabled, exit-only when enabled
