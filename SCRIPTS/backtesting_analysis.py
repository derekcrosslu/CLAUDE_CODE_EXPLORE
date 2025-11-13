#!/usr/bin/env python3
"""
Backtesting Analysis - Reference Documentation

This tool provides comprehensive reference documentation for interpreting
backtest results and detecting overfitting.

Usage:
    python SCRIPTS/backtesting_analysis.py --help
"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Backtesting Analysis Reference Documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
================================================================================
BACKTESTING ANALYSIS - COMPLETE REFERENCE DOCUMENTATION
================================================================================

This reference provides deep analysis for interpreting backtest results,
understanding performance metrics, and detecting overfitting.

--------------------------------------------------------------------------------
SHARPE RATIO - DEEP DIVE
--------------------------------------------------------------------------------

The Sharpe ratio is the PRIMARY metric for evaluating strategies.

Formula:
    Sharpe Ratio = (Strategy Return - Risk-Free Rate) / Strategy Volatility

Detailed Interpretation:

    < 0         POOR           Strategy loses money or underperforms risk-free
    0 - 0.5     BELOW MINIMUM  Not worth trading; insufficient risk-adjusted returns
    0.5 - 0.7   MARGINAL       Barely acceptable; consider optimization
    0.7 - 1.0   ACCEPTABLE     Decent baseline; worth optimizing
    1.0 - 1.5   GOOD           Strong performance; production-ready
    1.5 - 2.0   VERY GOOD      Excellent strategy; validate thoroughly
    2.0 - 3.0   EXCEPTIONAL    Outstanding but verify no overfitting
    > 3.0       SUSPICIOUS     Too good to be true; likely overfitting or bug

Key Insights:

  • Annual vs Daily Sharpe:
    - Annual Sharpe = Daily Sharpe × √252 (trading days)
    - QuantConnect reports ANNUAL Sharpe ratio

  • Context Matters:
    - Sharpe > 1.0 is production-ready for most strategies
    - High-frequency strategies may have higher Sharpe (but beware transaction costs)
    - Long-term strategies typically have lower Sharpe

  • Warning Signs:
    - Sharpe > 3.0 → Overfitting alert (check other metrics)
    - Sharpe varies wildly across years → Unstable strategy
    - Sharpe driven by 1-2 outlier trades → Not robust

  • Strategy-Type Expectations:
    - Momentum: 0.8 - 1.5
    - Mean Reversion: 0.7 - 1.3
    - Trend Following: 0.5 - 1.0
    - Breakout: 0.6 - 1.2

--------------------------------------------------------------------------------
MAXIMUM DRAWDOWN - ANALYSIS
--------------------------------------------------------------------------------

Maximum drawdown measures the largest peak-to-trough decline in portfolio value.

Formula:
    Max Drawdown = (Trough Value - Peak Value) / Peak Value

Detailed Interpretation:

    < 10%       EXCEPTIONAL    Very low risk; rare in real trading
    10% - 20%   EXCELLENT      Low risk; institutional quality
    20% - 30%   GOOD           Acceptable for live trading
    30% - 40%   CONCERNING     High risk; needs strong Sharpe to justify
    40% - 50%   TOO HIGH       Unacceptable for most traders
    > 50%       REJECT         Strategy too risky for live trading

Key Insights:

  • Psychological Impact:
    - Drawdowns > 30% are hard to tolerate psychologically
    - Most traders abandon strategies after 40% drawdown
    - Consider: "Could I stomach this loss in real money?"

  • Relationship to Sharpe:
    - High Sharpe + Low Drawdown = Excellent strategy
    - High Sharpe + High Drawdown = Aggressive but possibly acceptable
    - Low Sharpe + High Drawdown = Reject immediately

  • Drawdown Duration:
    - Time to recover from drawdown matters too
    - Drawdown > 6 months may cause strategy abandonment
    - QuantConnect doesn't always report duration (check equity curve manually)

  • Recovery Analysis:
    - Fast recovery (< 3 months) = Good risk management
    - Slow recovery (> 6 months) = Concerning; may lose confidence
    - Multiple sequential drawdowns = Very concerning

--------------------------------------------------------------------------------
TRADE COUNT - STATISTICAL SIGNIFICANCE
--------------------------------------------------------------------------------

Trade count is critical for statistical significance. Too few trades = unreliable.

Minimum Trade Thresholds:

    0 - 10      UNRELIABLE     ABANDON (or ESCALATE if perfect metrics)
    10 - 20     VERY LOW       ESCALATE_TO_HUMAN (too few for confidence)
    20 - 30     LOW            Minimum viable (barely acceptable)
    30 - 50     MODERATE       Acceptable for baseline evaluation
    50 - 100    GOOD           Strong statistical confidence
    100+        EXCELLENT      Highly reliable metrics

Why Trade Count Matters:

  • Sharpe ratio based on few trades is unreliable
  • Win rate with 5 trades means nothing (could be luck)
  • Need 30+ trades for basic statistical significance
  • Need 100+ trades for high confidence

Context by Strategy Type:

  • High-frequency: Expect 1000+ trades (if < 100, something's wrong)
  • Daily rebalancing: Expect 250+ trades per year
  • Swing trading: Expect 50-200 trades per year
  • Position trading: Expect 10-50 trades per year (harder to validate)

Warning Signs:

  • Zero trades → Entry conditions never met (too restrictive)
  • 1-5 trades with perfect metrics → Pure luck, not skill
  • Trades clustered in one period → Strategy not generalizable
  • Uneven trade distribution → May indicate regime-specific strategy

--------------------------------------------------------------------------------
WIN RATE - ANALYSIS
--------------------------------------------------------------------------------

Win rate = (Winning Trades / Total Trades)

Detailed Interpretation:

    < 30%       LOW            Needs large winners to compensate (trend following)
    30% - 40%   BELOW AVERAGE  Acceptable if profit factor > 1.5
    40% - 55%   AVERAGE        Typical for most strategies
    55% - 65%   GOOD           Strong edge
    65% - 75%   VERY GOOD      Excellent strategy (verify no overfitting)
    > 75%       SUSPICIOUS     Likely overfitting or look-ahead bias

Win Rate Alone is Misleading:

  • 90% win rate with small winners, huge losers = BAD strategy
  • 30% win rate with small losers, huge winners = GOOD strategy (trend following)
  • Must consider profit factor and average win/loss ratio

Strategy-Type Expectations:

  • Mean reversion: Higher win rate (55-70%), smaller wins
  • Trend following: Lower win rate (30-50%), larger wins
  • Breakout: Moderate win rate (40-55%), variable P&L
  • Momentum: Moderate win rate (40-55%), catch trends

Warning Signs:

  • Win rate > 75% → Check for overfitting
  • Win rate = 100% with < 10 trades → Pure luck
  • Win rate < 30% with small winners → Losing strategy
  • Win rate inconsistent across periods → Unstable edge

--------------------------------------------------------------------------------
PROFIT FACTOR - ANALYSIS
--------------------------------------------------------------------------------

Profit factor = (Gross Profit / Gross Loss)

Detailed Interpretation:

    < 1.0       LOSING         Strategy loses money
    1.0 - 1.3   MARGINAL       Barely profitable (transaction costs may kill it)
    1.3 - 1.5   ACCEPTABLE     Decent after costs
    1.5 - 2.0   GOOD           Strong profitability
    2.0 - 3.0   VERY GOOD      Excellent risk/reward
    > 3.0       EXCEPTIONAL    Outstanding (verify no overfitting)

Key Insights:

  • Profit factor accounts for BOTH win rate and win/loss size
  • Minimum 1.5 for live trading (to cover slippage, commissions)
  • High profit factor + low Sharpe → Large volatility (risky)
  • Profit factor should be stable across time periods

Relationship to Other Metrics:

  • High PF + High Win Rate + High Sharpe = Excellent (check for overfit)
  • High PF + Low Win Rate = Trend following (large winners)
  • Low PF + High Win Rate = Mean reversion (small winners)
  • Low PF + Low Win Rate = Poor strategy (abandon)

--------------------------------------------------------------------------------
OVERFITTING DETECTION - COMPLETE GUIDE
--------------------------------------------------------------------------------

Overfitting means the strategy works on historical data but will fail on live data.

Red Flag #1: Too Perfect Sharpe (> 3.0)
  • Why suspicious: Real markets are noisy; Sharpe > 3.0 is extremely rare
  • What to do: ESCALATE_TO_HUMAN, investigate for bugs or look-ahead bias
  • Exception: Very high-frequency strategies on clean data (rare)

Red Flag #2: Too High Win Rate (> 75%)
  • Why suspicious: Consistent winning is hard; > 75% suggests curve-fitting
  • What to do: Check if strategy uses future information (look-ahead bias)
  • Exception: Very short-term mean reversion on specific instruments

Red Flag #3: Too Few Trades (< 20)
  • Why suspicious: Small sample size; metrics unreliable
  • What to do: ESCALATE_TO_HUMAN or ABANDON if combined with poor Sharpe
  • Fix: Loosen entry conditions or use longer backtest period

Red Flag #4: Too Many Parameters
  • Why suspicious: More parameters = more ways to overfit
  • What to do: Prefer simpler strategies (1-3 parameters)
  • Rule of thumb: Need 10-20 trades per parameter

Red Flag #5: Excessive Optimization Improvement (> 30%)
  • Why suspicious: Optimization found lucky parameters, not robust edge
  • What to do: ESCALATE_TO_HUMAN, use baseline parameters instead
  • Example: Baseline Sharpe 0.8 → Optimized 1.5 = 87% improvement (TOO MUCH)

Red Flag #6: Severe Out-of-Sample Degradation (> 40%)
  • Why suspicious: Strategy doesn't generalize to new data
  • What to do: ABANDON_HYPOTHESIS
  • Example: In-sample Sharpe 1.5 → OOS Sharpe 0.6 = 60% degradation

Red Flag #7: Equity Curve Too Smooth
  • Why suspicious: Real trading has volatility; smooth = overfitting
  • What to do: Check if using unrealistic assumptions (no slippage, perfect fills)
  • Real curves have bumps, drawdowns, volatility

Red Flag #8: Strategy Works Only in One Market Regime
  • Why suspicious: Not robust across different conditions
  • What to do: Test across multiple periods (bull, bear, sideways)
  • Fix: Add regime detection or use defensive strategies

Red Flag #9: Parameters are Too Precise
  • Why suspicious: Optimal param = 14.37? Curve-fitted to noise
  • What to do: Round parameters, test sensitivity
  • Good: Parameter = 10, 15, 20 all work similarly
  • Bad: Only parameter = 14.37 works

Red Flag #10: Strategy Exploits Noise
  • Why suspicious: Pattern exists in backtest but is random noise
  • What to do: Understand WHY the edge exists (economic rationale)
  • Good: "Stocks revert because of overreaction"
  • Bad: "Every 3rd Tuesday works better"

--------------------------------------------------------------------------------
STRATEGY-TYPE PROFILES - DETAILED EXPECTATIONS
--------------------------------------------------------------------------------

Momentum Strategies:

  Expected Metrics:
    • Sharpe: 0.8 - 1.5 (can be higher for short-term)
    • Max Drawdown: 20% - 35%
    • Win Rate: 40% - 55%
    • Trade Frequency: Moderate to high
    • Profit Factor: 1.5 - 2.5

  Characteristics:
    • Ride trends, cut losses quickly
    • Performance concentrated in trending markets
    • Struggles in sideways markets

  Warning Signs:
    • Win rate > 65% → Likely overfitting
    • Drawdown < 15% → Too good to be true
    • Zero trades in sideways periods → Overly restrictive

Mean Reversion Strategies:

  Expected Metrics:
    • Sharpe: 0.7 - 1.3
    • Max Drawdown: 15% - 30%
    • Win Rate: 55% - 70%
    • Trade Frequency: High (many small trades)
    • Profit Factor: 1.3 - 2.0

  Characteristics:
    • Profit from price returning to mean
    • Higher win rate, smaller average wins
    • Struggles in strong trends

  Warning Signs:
    • Win rate > 75% → Overfitting or look-ahead bias
    • Large drawdown during trends → Poor risk management
    • Too few trades → Entry conditions too tight

Trend Following Strategies:

  Expected Metrics:
    • Sharpe: 0.5 - 1.0 (lower is normal)
    • Max Drawdown: 25% - 40% (higher tolerance)
    • Win Rate: 30% - 50% (lower is normal)
    • Trade Frequency: Low to moderate
    • Profit Factor: 1.8 - 3.0 (large winners compensate)

  Characteristics:
    • Catch big moves, many small losses
    • Lower win rate but large winners
    • Drawdowns can be substantial

  Warning Signs:
    • Win rate > 55% → Not true trend following
    • Sharpe > 1.5 with high drawdown → Inconsistent
    • Profit factor < 1.5 → Losers too large

Breakout Strategies:

  Expected Metrics:
    • Sharpe: 0.6 - 1.2
    • Max Drawdown: 20% - 35%
    • Win Rate: 40% - 55%
    • Trade Frequency: Moderate
    • Profit Factor: 1.5 - 2.5

  Characteristics:
    • Enter on price breaking support/resistance
    • Mix of momentum and mean reversion traits
    • Performance varies by timeframe

  Warning Signs:
    • Too many false breakouts → Poor filter
    • Win rate < 35% → Too many fakeouts
    • Drawdown > 40% → Poor risk management

--------------------------------------------------------------------------------
EXAMPLE BACKTESTS - ANNOTATED
--------------------------------------------------------------------------------

Example 1: GOOD Strategy (Optimization Worthy)

  Sharpe Ratio: 0.85
  Max Drawdown: 22%
  Total Return: 45%
  Total Trades: 67
  Win Rate: 42%
  Profit Factor: 1.8

  Analysis:
    ✅ Sharpe 0.85 > 0.7 (optimization worthy)
    ✅ Drawdown 22% < 35% (acceptable)
    ✅ Trades 67 > 50 (statistically significant)
    ✅ Win rate 42% (normal, not suspicious)
    ✅ Profit factor 1.8 (good profitability)

  Decision: PROCEED_TO_OPTIMIZATION
  Reason: Decent baseline, worth improving with parameter tuning

Example 2: EXCELLENT Strategy (Production Ready)

  Sharpe Ratio: 1.35
  Max Drawdown: 18%
  Total Return: 78%
  Total Trades: 142
  Win Rate: 53%
  Profit Factor: 2.1

  Analysis:
    ✅ Sharpe 1.35 > 1.0 (production ready)
    ✅ Drawdown 18% < 30% (low risk)
    ✅ Trades 142 > 100 (very reliable)
    ✅ Win rate 53% (good, not suspicious)
    ✅ Profit factor 2.1 (excellent)

  Decision: PROCEED_TO_VALIDATION
  Reason: Already strong, skip optimization, validate out-of-sample

Example 3: SUSPICIOUS Strategy (Overfitting)

  Sharpe Ratio: 4.2
  Max Drawdown: 5%
  Total Return: 350%
  Total Trades: 25
  Win Rate: 88%
  Profit Factor: 5.8

  Analysis:
    ❌ Sharpe 4.2 > 3.0 (too perfect)
    ❌ Drawdown 5% (unrealistically low)
    ❌ Trades 25 < 30 (low statistical significance)
    ❌ Win rate 88% > 75% (way too high)
    ❌ Profit factor 5.8 (suspiciously high)

  Decision: ESCALATE_TO_HUMAN
  Reason: Multiple overfitting signals; likely look-ahead bias or bug

Example 4: POOR Strategy (Abandon)

  Sharpe Ratio: 0.3
  Max Drawdown: 38%
  Total Return: 12%
  Total Trades: 89
  Win Rate: 35%
  Profit Factor: 1.1

  Analysis:
    ❌ Sharpe 0.3 < 0.5 (below minimum viable)
    ❌ Drawdown 38% > 35% (too risky)
    ✅ Trades 89 (reliable sample)
    ✅ Win rate 35% (not suspicious)
    ❌ Profit factor 1.1 (too low after costs)

  Decision: ABANDON_HYPOTHESIS
  Reason: Poor risk-adjusted returns; not worth optimizing

Example 5: MARGINAL Strategy (Try Optimization)

  Sharpe Ratio: 0.62
  Max Drawdown: 31%
  Total Return: 28%
  Total Trades: 45
  Win Rate: 48%
  Profit Factor: 1.4

  Analysis:
    ⚠️ Sharpe 0.62 (between minimum viable and optimization worthy)
    ⚠️ Drawdown 31% (slightly high but acceptable)
    ⚠️ Trades 45 (moderate reliability)
    ✅ Win rate 48% (normal)
    ⚠️ Profit factor 1.4 (marginal)

  Decision: PROCEED_TO_OPTIMIZATION
  Reason: Marginal baseline; optimization might improve to acceptable levels

Example 6: ZERO TRADES (Abandon)

  Sharpe Ratio: 0.0
  Max Drawdown: 0.0
  Total Return: 0.0
  Total Trades: 0
  Win Rate: 0.0
  Profit Factor: 0.0

  Analysis:
    ❌ Trades = 0 (strategy never executed)
    Strategy conditions never met

  Decision: ABANDON_HYPOTHESIS
  Reason: Entry conditions too restrictive; strategy never traded

--------------------------------------------------------------------------------
COMMON CONFUSION POINTS
--------------------------------------------------------------------------------

Q: "The strategy made 200% returns, but Sharpe is only 0.6 - is this good?"

A: No. We prioritize RISK-ADJUSTED returns (Sharpe), not raw returns.
   • High returns with high volatility = bad Sharpe = risky strategy
   • Sharpe 0.6 is between minimum viable (0.5) and optimization worthy (0.7)
   • Decision depends on other metrics (drawdown, trade count)
   • Raw returns are meaningless without considering risk

Q: "I got Sharpe 2.5 with 15 trades - should I proceed?"

A: ESCALATE_TO_HUMAN
   • 15 trades < 20 (too few for statistical significance)
   • Even though Sharpe is good, sample size too small to trust
   • High Sharpe with few trades often indicates luck, not skill
   • Could be 1-2 lucky trades dominating results

Q: "Optimization improved Sharpe from 0.8 to 1.5 (87% improvement) - is this good?"

A: ESCALATE_TO_HUMAN (possible overfitting)
   • 87% improvement > 30% threshold (excessive)
   • Likely overfitting to in-sample period
   • Use baseline parameters instead, or investigate further
   • Good optimization: 10-30% improvement

Q: "Win rate is 78%, Sharpe is 1.2 - why is this flagged?"

A: Win rate > 75% is an overfitting signal
   • Real strategies rarely achieve such high win rates
   • Suggests curve-fitting or look-ahead bias
   • Even with good Sharpe, investigate for bugs
   • Check: Are you closing winners too early / letting losers run?

Q: "Strategy worked great 2019-2022 but failed in 2023 - what happened?"

A: Possible reasons:
   • Overfitting to 2019-2022 data (most likely)
   • Different market regime in 2023
   • Strategy exploited temporary inefficiency
   • Always validate out-of-sample before deployment

--------------------------------------------------------------------------------
VERSION INFORMATION
--------------------------------------------------------------------------------

Version: 2.0.0 (Progressive Disclosure)
Last Updated: November 13, 2025
Status: Production Ready
Purpose: Complete backtest interpretation and overfitting detection

================================================================================
END OF REFERENCE DOCUMENTATION
================================================================================
"""
    )

    parser.add_argument('--version', action='version', version='2.0.0')

    args = parser.parse_args()

    # This tool exists only for --help documentation
    # No functional commands needed

if __name__ == "__main__":
    main()
