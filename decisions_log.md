# Decisions Log - Hypothesis 4: RSI Mean Reversion Strategy

**Hypothesis**: Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought)

**Created**: 2025-11-10T16:30:00Z

---

## Decision Timeline

### 2025-11-10T16:30:00Z - Initialize Hypothesis

**Phase**: research

**Decision**: initialize_hypothesis

**Reason**: Starting new hypothesis: RSI mean reversion strategy

**Next Action**: implement_strategy

**Metrics**: N/A

---

## Hypothesis Details

**Strategy Type**: Mean reversion using RSI indicator

**Entry Signal**: RSI < 30 (oversold condition)

**Exit Signal**: RSI > 70 (overbought condition)

**Rationale**:
- RSI is a momentum oscillator that measures overbought/oversold conditions
- Mean reversion strategies profit from price returning to average after extremes
- Traditional RSI thresholds (30/70) are widely used in quantitative trading

**Parameters to Test**:
- RSI period (default: 14)
- Oversold threshold (default: 30)
- Overbought threshold (default: 70)
- Position sizing (default: 100%)

---

## Next Steps

1. Implement RSI mean reversion strategy in `rsi_mean_reversion.py`
2. Test strategy locally for syntax errors
3. Upload to QuantConnect project
4. Run backtest with `/qc-backtest`
5. Evaluate results using decision framework

---

## Notes

- This is hypothesis 4 in the autonomous framework development
- Previous hypothesis (3: Simple Momentum) was abandoned due to 0 trades
- RSI mean reversion is a proven strategy pattern worth testing
- Will use 2023-2024 date range for backtest
