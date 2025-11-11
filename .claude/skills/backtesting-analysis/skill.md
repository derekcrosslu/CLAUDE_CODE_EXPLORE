---
name: Backtesting Analysis
description: Comprehensive guidance for interpreting backtest results and detecting overfitting (project)
---

# Backtesting Analysis Skill

This skill provides deep knowledge for interpreting backtest results, understanding performance metrics, and detecting overfitting or unreliable strategies.

## Purpose

When you (Claude Code) need to evaluate backtest results or make decisions about strategy quality, load this skill to understand what the metrics mean and how to interpret them in context.

## When to Use This Skill

Load this skill when:
- Evaluating backtest results (Phase 3)
- Confused about whether performance is good or concerning
- Detecting potential overfitting
- Understanding strategy-specific performance expectations
- Comparing multiple strategies
- Explaining results to the user

---

## Sharpe Ratio Interpretation

The Sharpe ratio is the **primary metric** for evaluating strategies. It measures risk-adjusted returns.

### Formula

```
Sharpe Ratio = (Strategy Return - Risk-Free Rate) / Strategy Volatility
```

### Interpretation Guidelines

| Sharpe Ratio | Quality | Interpretation |
|--------------|---------|----------------|
| < 0 | Poor | Strategy loses money or underperforms risk-free rate |
| 0 - 0.5 | Below Minimum | Not worth trading; insufficient risk-adjusted returns |
| 0.5 - 0.7 | Marginal | Barely acceptable; consider optimization |
| 0.7 - 1.0 | Acceptable | Decent baseline; worth optimizing |
| 1.0 - 1.5 | Good | Strong performance; production-ready |
| 1.5 - 2.0 | Very Good | Excellent strategy; validate thoroughly |
| 2.0 - 3.0 | Exceptional | Outstanding but verify no overfitting |
| > 3.0 | **SUSPICIOUS** | **Too good to be true; likely overfitting or bug** |

### Key Insights

**Annual Sharpe vs Daily Sharpe:**
- Annual Sharpe = Daily Sharpe × √252 (trading days)
- QuantConnect reports **annual Sharpe ratio**

**Context Matters:**
- Sharpe > 1.0 is production-ready for most strategies
- High-frequency strategies may have higher Sharpe (but beware transaction costs)
- Long-term strategies typically have lower Sharpe

**Warning Signs:**
- Sharpe > 3.0 → Overfitting alert (check other metrics)
- Sharpe varies wildly across years → Unstable strategy
- Sharpe driven by 1-2 outlier trades → Not robust

---

## Maximum Drawdown Interpretation

Maximum drawdown measures the largest peak-to-trough decline in portfolio value.

### Formula

```
Max Drawdown = (Trough Value - Peak Value) / Peak Value
```

### Interpretation Guidelines

| Max Drawdown | Quality | Interpretation |
|--------------|---------|----------------|
| < 10% | Exceptional | Very low risk; rare in real trading |
| 10% - 20% | Excellent | Low risk; institutional quality |
| 20% - 30% | Good | Acceptable for live trading |
| 30% - 40% | Concerning | High risk; needs strong Sharpe to justify |
| 40% - 50% | Too High | Unacceptable for most traders |
| > 50% | Reject | Strategy too risky for live trading |

### Key Insights

**Psychological Impact:**
- Drawdowns > 30% are hard to tolerate psychologically
- Most traders abandon strategies after 40% drawdown
- Consider: "Could I stomach this loss in real money?"

**Relationship to Sharpe:**
- High Sharpe + Low Drawdown = Excellent strategy
- High Sharpe + High Drawdown = Aggressive but possibly acceptable
- Low Sharpe + High Drawdown = Reject immediately

**Drawdown Duration:**
- Time to recover from drawdown matters too
- Drawdown > 6 months may cause strategy abandonment
- QuantConnect doesn't always report duration (check equity curve manually)

---

## Total Trades Analysis

Trade count is critical for **statistical significance**. Too few trades = unreliable metrics.

### Minimum Trade Thresholds

| Trade Count | Reliability | Decision Impact |
|-------------|-------------|-----------------|
| 0 - 10 | Unreliable | ABANDON (or ESCALATE if perfect metrics) |
| 10 - 20 | Very Low | ESCALATE_TO_HUMAN (too few for confidence) |
| 20 - 30 | Low | Minimum viable (barely acceptable) |
| 30 - 50 | Moderate | Acceptable for baseline evaluation |
| 50 - 100 | Good | Strong statistical confidence |
| 100+ | Excellent | Highly reliable metrics |

### Key Insights

**Why Trade Count Matters:**
- Sharpe ratio based on few trades is unreliable
- Win rate with 5 trades means nothing (could be luck)
- Need 30+ trades for basic statistical significance
- Need 100+ trades for high confidence

**Context by Strategy Type:**
- **High-frequency**: Expect 1000+ trades (if < 100, something's wrong)
- **Daily rebalancing**: Expect 250+ trades per year
- **Swing trading**: Expect 50-200 trades per year
- **Position trading**: Expect 10-50 trades per year (harder to validate)

**Warning Signs:**
- Zero trades → Entry conditions never met (too restrictive)
- 1-5 trades with perfect metrics → Pure luck, not skill
- Trades clustered in one period → Strategy not generalizable

---

## Win Rate Interpretation

Win rate = (Winning Trades / Total Trades)

### Interpretation Guidelines

| Win Rate | Quality | Interpretation |
|----------|---------|----------------|
| < 30% | Low | Needs large winners to compensate (trend following) |
| 30% - 40% | Below Average | Acceptable if profit factor > 1.5 |
| 40% - 55% | Average | Typical for most strategies |
| 55% - 65% | Good | Strong edge |
| 65% - 75% | Very Good | Excellent strategy (verify no overfitting) |
| > 75% | **SUSPICIOUS** | **Likely overfitting or look-ahead bias** |

### Key Insights

**Win Rate Alone is Misleading:**
- 90% win rate with small winners, huge losers = bad strategy
- 30% win rate with small losers, huge winners = good strategy (trend following)
- Must consider **profit factor** and **average win/loss ratio**

**Strategy-Type Expectations:**
- **Mean reversion**: Higher win rate (55-70%), smaller wins
- **Trend following**: Lower win rate (30-50%), larger wins
- **Breakout**: Moderate win rate (40-55%), variable P&L

**Warning Signs:**
- Win rate > 75% → Check for overfitting
- Win rate = 100% with < 10 trades → Pure luck
- Win rate < 30% with small winners → Losing strategy

---

## Profit Factor

Profit factor = (Gross Profit / Gross Loss)

### Interpretation Guidelines

| Profit Factor | Quality | Interpretation |
|---------------|---------|----------------|
| < 1.0 | Losing | Strategy loses money |
| 1.0 - 1.3 | Marginal | Barely profitable (transaction costs may kill it) |
| 1.3 - 1.5 | Acceptable | Decent after costs |
| 1.5 - 2.0 | Good | Strong profitability |
| 2.0 - 3.0 | Very Good | Excellent risk/reward |
| > 3.0 | Exceptional | Outstanding (verify no overfitting) |

### Key Insights

- Profit factor accounts for **both** win rate and win/loss size
- Minimum 1.5 for live trading (to cover slippage, commissions)
- High profit factor + low Sharpe → Large volatility (risky)

---

## Overfitting Detection Patterns

Overfitting means the strategy works on historical data but will fail on live/future data.

### Red Flags for Overfitting

#### 1. Too Perfect Sharpe (> 3.0)
- **Why it's suspicious**: Real markets are noisy; Sharpe > 3.0 is extremely rare
- **What to do**: ESCALATE_TO_HUMAN, investigate for bugs or look-ahead bias

#### 2. Too High Win Rate (> 75%)
- **Why it's suspicious**: Consistent winning is hard; > 75% suggests curve-fitting
- **What to do**: Check if strategy uses future information (look-ahead bias)

#### 3. Too Few Trades (< 20)
- **Why it's suspicious**: Small sample size; metrics unreliable
- **What to do**: ESCALATE_TO_HUMAN or ABANDON if combined with poor Sharpe

#### 4. Too Many Parameters
- **Why it's suspicious**: More parameters = more ways to overfit
- **What to do**: Prefer simpler strategies (1-3 parameters)

#### 5. Excessive Optimization Improvement (> 30%)
- **Why it's suspicious**: Optimization found lucky parameters, not robust edge
- **What to do**: ESCALATE_TO_HUMAN, use baseline parameters instead

#### 6. Severe Out-of-Sample Degradation (> 40%)
- **Why it's suspicious**: Strategy doesn't generalize to new data
- **What to do**: ABANDON_HYPOTHESIS

#### 7. Equity Curve Too Smooth
- **Why it's suspicious**: Real trading has volatility; smooth = overfitting
- **What to do**: Check if using unrealistic assumptions (no slippage, perfect fills)

#### 8. Strategy Works Only in One Market Regime
- **Why it's suspicious**: Not robust across different conditions
- **What to do**: Test across multiple periods (bull, bear, sideways)

---

## Strategy-Type Specific Expectations

Different strategy types have different performance profiles.

### Momentum Strategies

**Expected Metrics:**
- Sharpe: 0.8 - 1.5 (can be higher for short-term)
- Max Drawdown: 20% - 35%
- Win Rate: 40% - 55%
- Trade Frequency: Moderate to high
- Profit Factor: 1.5 - 2.5

**Characteristics:**
- Ride trends, cut losses quickly
- Performance concentrated in trending markets
- Struggles in sideways markets

**Warning Signs:**
- Win rate > 65% → Likely overfitting
- Drawdown < 15% → Too good to be true
- Zero trades in sideways periods → Overly restrictive

---

### Mean Reversion Strategies

**Expected Metrics:**
- Sharpe: 0.7 - 1.3
- Max Drawdown: 15% - 30%
- Win Rate: 55% - 70%
- Trade Frequency: High (many small trades)
- Profit Factor: 1.3 - 2.0

**Characteristics:**
- Profit from price returning to mean
- Higher win rate, smaller average wins
- Struggles in strong trends

**Warning Signs:**
- Win rate > 75% → Overfitting or look-ahead bias
- Large drawdown during trends → Poor risk management
- Too few trades → Entry conditions too tight

---

### Trend Following Strategies

**Expected Metrics:**
- Sharpe: 0.5 - 1.0 (lower is normal)
- Max Drawdown: 25% - 40% (higher tolerance)
- Win Rate: 30% - 50% (lower is normal)
- Trade Frequency: Low to moderate
- Profit Factor: 1.8 - 3.0 (large winners compensate)

**Characteristics:**
- Catch big moves, many small losses
- Lower win rate but large winners
- Drawdowns can be substantial

**Warning Signs:**
- Win rate > 55% → Not true trend following
- Sharpe > 1.5 with high drawdown → Inconsistent
- Profit factor < 1.5 → Losers too large

---

### Breakout Strategies

**Expected Metrics:**
- Sharpe: 0.6 - 1.2
- Max Drawdown: 20% - 35%
- Win Rate: 40% - 55%
- Trade Frequency: Moderate
- Profit Factor: 1.5 - 2.5

**Characteristics:**
- Enter on price breaking support/resistance
- Mix of momentum and mean reversion traits
- Performance varies by timeframe

**Warning Signs:**
- Too many false breakouts → Poor filter
- Win rate < 35% → Too many fakeouts
- Drawdown > 40% → Poor risk management

---

## Examples of Good vs Bad Backtests

### Example 1: GOOD Strategy (Optimization Worthy)

```
Sharpe Ratio: 0.85
Max Drawdown: 22%
Total Return: 45%
Total Trades: 67
Win Rate: 42%
Profit Factor: 1.8
```

**Analysis:**
- ✅ Sharpe 0.85 > 0.7 (optimization worthy)
- ✅ Drawdown 22% < 35% (acceptable)
- ✅ Trades 67 > 50 (statistically significant)
- ✅ Win rate 42% (normal, not suspicious)
- ✅ Profit factor 1.8 (good profitability)

**Decision:** PROCEED_TO_OPTIMIZATION
**Reason:** Decent baseline, worth improving with parameter tuning

---

### Example 2: EXCELLENT Strategy (Production Ready)

```
Sharpe Ratio: 1.35
Max Drawdown: 18%
Total Return: 78%
Total Trades: 142
Win Rate: 53%
Profit Factor: 2.1
```

**Analysis:**
- ✅ Sharpe 1.35 > 1.0 (production ready)
- ✅ Drawdown 18% < 30% (low risk)
- ✅ Trades 142 > 100 (very reliable)
- ✅ Win rate 53% (good, not suspicious)
- ✅ Profit factor 2.1 (excellent)

**Decision:** PROCEED_TO_VALIDATION
**Reason:** Already strong, skip optimization, validate out-of-sample

---

### Example 3: SUSPICIOUS Strategy (Overfitting)

```
Sharpe Ratio: 4.2
Max Drawdown: 5%
Total Return: 350%
Total Trades: 25
Win Rate: 88%
Profit Factor: 5.8
```

**Analysis:**
- ❌ Sharpe 4.2 > 3.0 (too perfect)
- ❌ Drawdown 5% (unrealistically low)
- ❌ Trades 25 < 30 (low statistical significance)
- ❌ Win rate 88% > 75% (way too high)
- ❌ Profit factor 5.8 (suspiciously high)

**Decision:** ESCALATE_TO_HUMAN
**Reason:** Multiple overfitting signals; likely look-ahead bias or bug

---

### Example 4: POOR Strategy (Abandon)

```
Sharpe Ratio: 0.3
Max Drawdown: 38%
Total Return: 12%
Total Trades: 89
Win Rate: 35%
Profit Factor: 1.1
```

**Analysis:**
- ❌ Sharpe 0.3 < 0.5 (below minimum viable)
- ❌ Drawdown 38% > 35% (too risky)
- ✅ Trades 89 (reliable sample)
- ✅ Win rate 35% (not suspicious)
- ❌ Profit factor 1.1 (too low after costs)

**Decision:** ABANDON_HYPOTHESIS
**Reason:** Poor risk-adjusted returns; not worth optimizing

---

### Example 5: MARGINAL Strategy (Try Optimization)

```
Sharpe Ratio: 0.62
Max Drawdown: 31%
Total Return: 28%
Total Trades: 45
Win Rate: 48%
Profit Factor: 1.4
```

**Analysis:**
- ⚠️ Sharpe 0.62 (between minimum viable and optimization worthy)
- ⚠️ Drawdown 31% (slightly high but acceptable)
- ⚠️ Trades 45 (moderate reliability)
- ✅ Win rate 48% (normal)
- ⚠️ Profit factor 1.4 (marginal)

**Decision:** PROCEED_TO_OPTIMIZATION
**Reason:** Marginal baseline; optimization might improve to acceptable levels

---

### Example 6: ZERO TRADES (Abandon)

```
Sharpe Ratio: 0.0
Max Drawdown: 0.0
Total Return: 0.0
Total Trades: 0
Win Rate: 0.0
Profit Factor: 0.0
```

**Analysis:**
- ❌ Trades = 0 (strategy never executed)
- Strategy conditions never met

**Decision:** ABANDON_HYPOTHESIS
**Reason:** Entry conditions too restrictive; strategy never traded

---

## Common Confusion Points

### "The strategy made 200% returns, but Sharpe is only 0.6 - is this good?"

**Answer:** No. We prioritize **risk-adjusted returns** (Sharpe), not raw returns.
- High returns with high volatility = bad Sharpe = risky strategy
- Sharpe 0.6 is between minimum viable (0.5) and optimization worthy (0.7)
- Decision depends on other metrics (drawdown, trade count)

### "I got Sharpe 2.5 with 15 trades - should I proceed?"

**Answer:** ESCALATE_TO_HUMAN
- 15 trades < 20 (too few for statistical significance)
- Even though Sharpe is good, sample size too small to trust
- High Sharpe with few trades often indicates luck, not skill

### "Optimization improved Sharpe from 0.8 to 1.5 (87% improvement) - is this good?"

**Answer:** ESCALATE_TO_HUMAN (possible overfitting)
- 87% improvement > 30% threshold (excessive)
- Likely overfitting to in-sample period
- Use baseline parameters instead, or investigate further

### "Win rate is 78%, Sharpe is 1.2 - why is this flagged?"

**Answer:** Win rate > 75% is an overfitting signal
- Real strategies rarely achieve such high win rates
- Suggests curve-fitting or look-ahead bias
- Even with good Sharpe, investigate for bugs

---

## Integration with Decision Framework

This skill **complements** the decision-framework skill:

- **decision-framework**: Provides **thresholds** and **decision logic**
- **backtesting-analysis**: Provides **interpretation** and **context**

**When to use both:**
1. Load decision-framework to apply thresholds
2. Load backtesting-analysis to understand what the metrics mean
3. Combine insights to make informed decisions

**Example workflow:**
```
1. Backtest completes with Sharpe 0.85, drawdown 22%, 67 trades
2. Load decision-framework → Returns: PROCEED_TO_OPTIMIZATION
3. Load backtesting-analysis → Confirms: "Decent baseline, worth optimizing"
4. Apply decision with confidence
```

---

## Summary

**Key Principles:**
1. **Sharpe ratio is king** - Primary metric for risk-adjusted returns
2. **Trade count matters** - Need 30+ for reliability, 100+ for confidence
3. **Beware overfitting** - Too perfect results are suspicious
4. **Context by strategy type** - Different strategies have different expectations
5. **Risk-adjusted, not raw returns** - High returns with high volatility = bad

**When confused:**
1. Load this skill to understand what metrics mean
2. Check strategy-type specific expectations
3. Look for overfitting red flags
4. Trust the decision framework thresholds (they're calibrated)

**Remember:**
- Better to abandon weak strategies than waste time optimizing
- Overfitting is the #1 cause of backtest-to-live performance gap
- Statistical significance (trade count) is non-negotiable
- Real edge is rare; most strategies should be abandoned

---

## Related Files

- `.claude/skills/decision-framework/skill.md` - Decision thresholds and logic
- `SCRIPTS/decision_logic.py` - Implementation of decision functions
- `iteration_state_schema.md` - Threshold configuration schema
- `.claude/commands/qc-backtest.md` - How backtests are executed

---

**Version**: 1.0.0
**Last Updated**: November 10, 2025
**Status**: Production Ready
**Purpose**: Comprehensive backtest interpretation and overfitting detection
