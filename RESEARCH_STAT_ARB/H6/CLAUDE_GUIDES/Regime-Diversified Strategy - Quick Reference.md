# Regime-Diversified Strategy - Quick Reference

## Configuration Summary

### Regime Classification

| Regime Score | Regime Name | Active Pairs | Allocation | Expected Sharpe |
|--------------|-------------|--------------|------------|-----------------|
| 0-35 | **ZIRP** | BSX/HOV, PSEC/KIM, CHTR/THO | 40% | 1.0-1.5 |
| 35-65 | **TRANSITIONAL** | All 7 pairs | 50% | 1.0-1.3 |
| 65-100 | **QT** | PNC/KBE, ARCC/AMLP, RBA/SMFG, ENB/WEC | 70% | 1.5-2.0 |

## Parameters by Regime

| Parameter | QT Regime | Transitional | ZIRP Regime |
|-----------|-----------|--------------|-------------|
| **Z-Score Entry** | 1.5 | 1.75 | 2.0 |
| **Z-Score Exit** | 0.5 | 0.6 | 0.75 |
| **Stop Loss Z** | 4.0 | 3.75 | 3.5 |
| **Lookback Period** | 30 days | 45 days | 60 days |
| **Max Holding Days** | 30 | 35 | 45 |
| **Position Size/Pair** | 17.5% | 7.1% | 13.3% |

## Pairs Configuration

### QT Champion Pairs (Your Current Winners)

| Pair | Long | Short | Description | When Active |
|------|------|-------|-------------|-------------|
| **PNC_KBE** | PNC | KBE | Regional bank vs Banking ETF | Score ≥ 55 |
| **ARCC_AMLP** | ARCC | AMLP | BDC vs MLP ETF | Score ≥ 55 |
| **RBA_SMFG** | RBA | SMFG | International banking | Score ≥ 55 |
| **ENB_WEC** | ENB | WEC | Energy infra vs Utility | Score ≥ 55 |

**Total Allocation:** 70% (4 pairs × 17.5% each)

### ZIRP Pairs (Low-Rate Environment)

| Pair | Long | Short | Description | Weight | When Active |
|------|------|-------|-------------|--------|-------------|
| **BSX_HOV** | BSX | HOV | Medical devices vs Homebuilder | 35% | Score ≤ 45 |
| **PSEC_KIM** | PSEC | KIM | BDC vs Shopping REIT | 30% | Score ≤ 45 |
| **CHTR_THO** | CHTR | THO | Cable vs RV manufacturer | 35% | Score ≤ 45 |

**Total Allocation:** 40% (distributed by weight: 14%, 12%, 14%)

## Performance Comparison

### Your Current Setup (2023-2025 QT Period Only)

```
Period: 2023-2025 (2.9 years)
Pairs: PNC/KBE, ARCC/AMLP, RBA/SMFG, ENB/WEC
Parameters: z_entry=1.5, lookback=30, max_hold=30

Results:
├─ Sharpe Ratio: 1.829
├─ CAGR: 20.73%
├─ Max Drawdown: 4.40%
├─ Win Rate: 61%
├─ Total Trades: 936
├─ Avg Win: 0.57%
└─ Avg Loss: -0.51%
```

### Regime-Diversified Setup (2015-2025 Full Cycle)

**Expected Results:**

```
Period: 2015-2025 (10.9 years)
Pairs: 7 pairs (regime-switching)
Parameters: Regime-adaptive

Expected Results:
├─ Sharpe Ratio: 1.5-2.0
├─ CAGR: 15-20%
├─ Max Drawdown: 8-12%
├─ Win Rate: 65-70%
├─ Total Trades: 2,000-2,500
├─ Avg Win: 0.5-0.7%
└─ Avg Loss: -0.4-0.6%

By Period:
├─ 2015-2019 (ZIRP): Sharpe 1.0-1.5
├─ 2020-2022 (Transition): Sharpe 1.0-1.3
└─ 2023-2025 (QT): Sharpe 1.6-2.0
```

## Expected Regime Timeline (Historical)

```
┌─────────────────────────────────────────────────────────┐
│ 2015-2016: ZIRP (Score: 20-35)                         │
│ ├─ Active: BSX/HOV, PSEC/KIM, CHTR/THO                 │
│ ├─ Environment: Post-QE3, near-zero rates              │
│ └─ Expected Sharpe: 1.2-1.4                            │
├─────────────────────────────────────────────────────────┤
│ 2017-2018: ZIRP → Transition (Score: 35-50)            │
│ ├─ Active: Gradual shift to all pairs                  │
│ ├─ Environment: Fed normalization begins               │
│ └─ Expected Sharpe: 1.0-1.3                            │
├─────────────────────────────────────────────────────────┤
│ 2019: Transition (Score: 50-60)                        │
│ ├─ Active: All 7 pairs                                 │
│ ├─ Environment: Trade war volatility                   │
│ └─ Expected Sharpe: 0.8-1.2                            │
├─────────────────────────────────────────────────────────┤
│ 2020: QT → ZIRP (Score: 70 → 25)                       │
│ ├─ Active: Quick shift QT → ZIRP pairs                 │
│ ├─ Environment: COVID crash, Fed cuts to zero          │
│ └─ Expected Sharpe: 1.5-2.0 (high volatility profits) │
├─────────────────────────────────────────────────────────┤
│ 2021-2022: ZIRP → Transition (Score: 30-50)            │
│ ├─ Active: ZIRP pairs then gradual transition          │
│ ├─ Environment: Recovery, then Fed hiking begins       │
│ └─ Expected Sharpe: 0.8-1.2                            │
├─────────────────────────────────────────────────────────┤
│ 2023-2025: QT (Score: 70-85)                           │
│ ├─ Active: PNC/KBE, ARCC/AMLP, RBA/SMFG, ENB/WEC       │
│ ├─ Environment: High rates, high dispersion            │
│ └─ Expected Sharpe: 1.6-2.0 (MATCHES YOUR RESULTS!)    │
└─────────────────────────────────────────────────────────┘
```

## Regime Indicator Quick Reference

### What Drives Regime Score Up (Toward QT)

✅ **Higher VIX** (>20) → Stress signals
✅ **Lower sector correlation** (<0.45) → High dispersion
✅ **Rising rates** (TLT falling) → Tighter monetary policy
✅ **Volatility backwardation** (VXX/VIX >1.1) → Near-term stress
✅ **High sector dispersion** (>0.08 std) → Individual stock selection matters

### What Drives Regime Score Down (Toward ZIRP)

✅ **Lower VIX** (<15) → Calm markets
✅ **Higher sector correlation** (>0.60) → Low dispersion, "rising tide"
✅ **Falling rates** (TLT rising) → Accommodative policy
✅ **Volatility contango** (VXX/VIX <0.9) → Complacency
✅ **Low sector dispersion** (<0.04 std) → Macro drives everything

## Optimization Priority Order

1. **Run baseline first** (no changes) → Establish benchmark
2. **Adjust regime thresholds** if switching too frequently
3. **Optimize parameters by regime** (QT params, then ZIRP params)
4. **Fine-tune position sizing** per regime
5. **Consider adding pairs** only after above steps

## Key Monitoring Metrics

### Daily Checks
- [ ] Current regime score
- [ ] Active pairs count
- [ ] Open positions
- [ ] Daily P&L

### Weekly Review
- [ ] Regime stability (days in current regime)
- [ ] Win rate by regime
- [ ] Upcoming earnings for held pairs
- [ ] VIX level and trend

### Monthly Analysis
- [ ] Sharpe ratio by regime
- [ ] Max drawdown by regime
- [ ] Parameter effectiveness
- [ ] Correlation between QT and ZIRP pairs (should be low)

## Critical Success Factors

### ✅ DO

- Trust the regime detection system
- Allow full parameter changes when regime switches
- Close positions when pairs leave active regime
- Monitor regime score weekly
- Keep position sizes per configuration
- Paper trade for 1-2 months first

### ❌ DON'T

- Manually override regime classification
- Mix parameters across regimes
- Keep positions in inactive regime pairs
- Ignore regime score degradation
- Over-optimize on single regime period
- Force pairs to trade outside their regime

## Live Trading Checklist

### Before Going Live

- [ ] Backtest results meet minimum targets (Sharpe >1.5)
- [ ] Regime transitions occur at logical times (2020 crash, 2022 hikes)
- [ ] Current regime matches market expectations (QT in Nov 2025)
- [ ] Paper traded for 1-2 months successfully
- [ ] Monitoring dashboard configured
- [ ] Understand all 7 pairs fundamentally

### First Week Live

- [ ] Verify regime score calculating correctly
- [ ] Confirm only expected pairs are trading
- [ ] Check position sizes match configuration
- [ ] Monitor for any execution issues
- [ ] Compare live vs paper results

### Ongoing

- [ ] Weekly regime status review
- [ ] Monthly performance attribution by regime
- [ ] Quarterly strategy review and optimization consideration
- [ ] Annual full backtest with latest data

## Troubleshooting Quick Guide

| Problem | Likely Cause | Solution |
|---------|--------------|----------|
| **Score stuck at 50** | Data not updating | Check sector ETF data, increase warmup |
| **Too many switches** | Low hysteresis | Increase buffer from 5 to 7-10 points |
| **ZIRP pairs never active** | Threshold too low | Raise ZIRP threshold from 35 to 40 |
| **Poor transition performance** | Too many pairs | Increase allocation or reduce to Tier 1 only |
| **QT underperformance** | Champions degrading | Check if your 4 pairs still cointegrated |
| **ZIRP underperformance** | Wrong pairs for 2015-2019 | Consider pair substitutions from report |

## Expected Path Forward (2025-2027)

### Current State (November 2025)
```
Regime: QT (Score: ~75)
Active Pairs: Your 4 champions
Fed Funds: 4.50%
```

### Likely Path (2026)
```
Q1-Q2: Fed cuts begin → Score drops to 60-70 (Transition starts)
Q3-Q4: Fed at 3.50-4.00% → Score 50-60 (Full Transition)
        All 7 pairs active, 50% allocation
```

### Potential 2027
```
If Fed reaches 2.50-3.00%:
→ Score drops to 35-45 (ZIRP regime)
→ ZIRP pairs activate (BSX/HOV, PSEC/KIM, CHTR/THO)
→ QT champions close positions
→ 40% allocation in ZIRP pairs
```

---

## Bottom Line

**Your current setup:** Optimized for 2023-2025 QT regime (Sharpe 1.829)

**This setup:** Adapts across full 2015-2025 cycle (Expected Sharpe 1.5-2.0)

**When to use each:**
- **Current:** If you believe high dispersion persists indefinitely
- **Regime-Diversified:** If you expect rates to normalize (likely 2026-2027)

**Best approach:** Run both in parallel
- 70% in current champion (immediate performance)
- 30% in regime-diversified (future-proofing)

When regime score drops below 65, shift more capital to regime-diversified system.