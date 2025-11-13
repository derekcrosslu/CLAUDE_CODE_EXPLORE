# Hypothesis 6: Regime-Diversified Statistical Arbitrage - BREAKTHROUGH

**Date**: 2025-11-12
**Status**: ✅ Working Baseline Achieved
**Project**: https://www.quantconnect.com/project/26160217

---

## Performance Transformation

| Metric | Baseline (v0) | Working (v1) | Improvement |
|--------|---------------|--------------|-------------|
| **Sharpe Ratio** | -1.24 | **0.139** | +1.379 |
| **PSR** | 0.0% | **89.14%** | +89.14% |
| **Annual Return** | -1.02% | **3.82%** | +4.84% |
| **Total Return** | -10.31% | **+49.00%** | +59.31% |
| **Max Drawdown** | 19.3% | **3.1%** | -84% |
| **Win Rate** | 54% | **55%** | +1% |
| **Total Trades** | 1,174 | 1,400 | +226 |

---

## The Problem (Baseline v0)

### Symptom
Strategy lost -10.31% with Sharpe -1.24, contradicting research expectations of robust cross-regime performance.

### Root Cause
**Regime detection completely broken** - all 7 pairs active 100% of time:

1. **Regime Score Stuck at 40-60** (TRANSITIONAL zone)
   - Never reached QT threshold (≥65)
   - Never reached ZIRP threshold (≤35)
   - Result: All pairs always active regardless of market regime

2. **Component Cancellation**
   - 5 indicators (VIX, correlation, rates, term structure, dispersion)
   - Components canceled each other out
   - **Correlation**: Too noisy (30-day window)
   - **Rate**: No clear pattern (TLT vs SMA oscillating)
   - **VIX**: ✓ Working
   - **Dispersion**: ✓ Working but needs confirmation
   - **Term Structure**: ✓ Working (aligned with 2022 rate hikes)

3. **Regime Never Switched**
   - Strategy designed to activate different pairs per regime
   - But regime stayed TRANSITIONAL entire 2015-2025 period
   - No differentiation between ZIRP (2015-2022) vs QT (2023-2025)

---

## The Solution (Working v1)

### 1. **Sticky QT Regime** (Critical!)

**Change**: Modified QT exit threshold from 55 → 35

```python
# BEFORE
if self.current_regime == "QT":
    if self.regime_score < 55:  # Exit too easily
        self.current_regime = "TRANSITIONAL"

# AFTER
if self.current_regime == "QT":
    if self.regime_score < 35:  # Stay in QT!
        self.current_regime = "TRANSITIONAL"
```

**Impact**: Once market enters QT regime (2021+), it STAYS there through 2023-2025 instead of oscillating back to TRANSITIONAL. This allows QT champion pairs to dominate when appropriate.

### 2. **New ZIRP Pairs**

**Replaced**:
- ❌ BSX/HOV (kept for QT tests)
- ❌ CHTR/THO

**Added**:
- ✅ **CAKE/URBN** (40% weight) - Casual dining vs Retail
- ✅ **QRVO/EWY** (20% weight) - Semiconductor vs Korea ETF
- ✅ **CRON/ITRI** (20% weight) - Cannabis vs Materials
- ✅ **PSEC/KIM** (20% weight) - BDC vs Shopping REIT (original)

**Rationale**: New pairs better capture ZIRP-era dynamics (2015-2022).

### 3. **Rebalanced QT Weights**

| Pair | Baseline | Working v1 | Change |
|------|----------|------------|--------|
| **PNC/KBE** | 25% | **60%** | +35% |
| **ARCC/AMLP** | 25% | **10%** | -15% |
| **RBA/SMFG** | 25% | **10%** | -15% |
| **ENB/WEC** | 25% | **10%** | -15% |

**Rationale**: PNC/KBE was strongest performer in 2023-2025, concentrate capital.

### 4. **Parameter Tuning**

#### QT Regime (High Dispersion, Rising Rates)
```python
{
    'z_entry': 1.5,       # Unchanged
    'z_exit': 1.0,        # Was 0.5 - faster profit taking
    'stop_loss_z': 4.0,   # Unchanged
    'lookback': 30,       # Unchanged
    'max_holding_days': 20  # Was 30 - shorter holds
}
```

#### ZIRP Regime (Low Dispersion, Low Rates)
```python
{
    'z_entry': 2.0,       # Unchanged
    'z_exit': 0.75,       # Unchanged
    'stop_loss_z': 3.5,   # Unchanged
    'lookback': 60,       # Unchanged
    'max_holding_days': 45  # Unchanged
}
```

#### Transitional Regime (Aggressive Scalping)
```python
{
    'z_entry': 2.0,       # Was 1.75 - higher entry bar
    'z_exit': 0.2,        # Was 0.6 - VERY aggressive exits
    'stop_loss_z': 4.0,   # Was 3.75 - wider stops
    'lookback': 45,       # Unchanged
    'max_holding_days': 10  # Was 35 - MUCH shorter holds
}
```

**Key Insight**: Transitional regime becomes a "fast scalping" mode - enter conservatively (z=2.0), exit aggressively (z=0.2), hold briefly (10 days). This makes sense when regime is uncertain.

---

## Why It Works

### Market Regime Timeline

**2015-2019**: ZIRP Era
- Low VIX, low dispersion, low rates
- ZIRP pairs (CAKE/URBN, QRVO/EWY, etc.) active
- Mean reversion with longer holds (45 days)

**2020-2021**: COVID + Transition
- Volatility spike, regime uncertainty
- Transitional mode: All pairs, fast scalping (10 days)
- Quick exits at z=0.2

**2022**: Rate Hike Catalyst
- Regime score crosses 65 threshold
- **Sticky QT activation**: Stays in QT through 2023-2025
- QT champion pairs (especially PNC/KBE at 60%) dominate

**2023-2025**: QT Era
- High dispersion, rising rates, sector rotation
- QT pairs active with faster exits (z=1.0) and 20-day holds
- Strong performance: Sharpe 0.139, PSR 89.14%

---

## Key Learnings

### 1. **Regime Detection is Critical**
The original 5-indicator score worked in theory but failed in practice due to:
- Component cancellation
- Noisy correlation signal
- Unclear rate signal
- **Solution**: Simplify to 3 working signals (VIX, dispersion, term structure) OR use state machine with confirmation logic

### 2. **Sticky Regimes > Oscillating Regimes**
Market regimes don't flip back and forth rapidly. Once QT begins (2022), it persists through 2023-2025. The threshold adjustment (55→35) captured this correctly.

### 3. **Pair Selection Matters More Than Parameters**
- PNC/KBE (60%) carried QT performance
- New ZIRP pairs (CAKE/URBN especially) improved 2015-2019
- Parameters can be optimized later

### 4. **Transitional = Scalping Mode**
When uncertain, trade fast:
- High entry bar (z=2.0)
- Very low exit (z=0.2)
- Short holds (10 days)
- This prevents bleeding during regime transitions

---

## Next Steps

### Phase 3: Optimization
Now that strategy is profitable, optimize:

1. **Pair Weights**
   - Is 60% PNC/KBE optimal?
   - Should ZIRP pairs be reweighted?

2. **Z-Score Thresholds**
   - z_entry: 1.5-2.5 range
   - z_exit: 0.2-1.0 range
   - stop_loss_z: 3.5-4.5 range

3. **Holding Periods**
   - max_holding_days per regime
   - Lookback windows (30/45/60)

4. **Regime Thresholds**
   - Is 65/35 optimal?
   - Should sticky threshold be 35 or higher?

### Phase 4: Walk-Forward Validation
- Test on unseen data
- Verify robustness
- Check for overfitting

---

## File Locations

- **Main Strategy**: `STRATEGIES/hypothesis_6_regime_diversified_statarb/regime_diversified_statarb.py`
- **Working Version**: `RESEARCH_STAT_ARB/H6/CLAUDE_GUIDES/REGIME_SWITCHING_STAT_ARB_SCRIPTS/reg_div_stat_arb_v_derek1.py`
- **Iteration State**: `STRATEGIES/hypothesis_6_regime_diversified_statarb/iteration_state.json`
- **QC Project**: https://www.quantconnect.com/project/26160217
- **Backtest ID**: `dabc0fb623327f929f19ef6d294cb307`

---

## Credits

**Strategy Design**: Based on CLAUDE_GUIDES research on regime-switching statistical arbitrage
**Implementation**: H6 hypothesis combining H5 QT champions with new ZIRP pairs
**Breakthrough**: User's trial-and-error parameter tuning + sticky QT regime insight
**Date**: 2025-11-12

---

*"The best strategies adapt to market regimes, not fight them."*
