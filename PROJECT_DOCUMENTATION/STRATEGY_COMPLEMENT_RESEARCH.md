# Strategy Complement Research Framework
## Goal: Find strategies to complement H5 Statistical Arbitrage

**Date:** 2025-11-11
**Current Strategy:** H5 - Statistical Arbitrage (Mean Reversion Pairs)
**Objective:** Build regime-switching portfolio with 3-5 complementary strategies

---

## H5 Characteristics (Baseline)

### Performance Profile
- **Best Period:** 2022-2024 (high volatility, mean-reverting markets)
- **Weak Period:** 2015-2021 (trending/low volatility)
- **10-Year Sharpe:** [PENDING - optimization in progress]
- **3-Year Sharpe:** 1.829 (2022-2024)

### Strategy DNA
- **Type:** Market-neutral pairs trading
- **Signal:** Z-score mean reversion
- **Timeframe:** 30-day lookback, ~7-30 day holding period
- **Assets:** Equity pairs (financials, REITs, energy)
- **Exposure:** Delta-neutral (long/short pairs)
- **Regime Preference:** High volatility, mean-reverting, choppy markets

### Risk Factors
- **Primary:** Mean reversion risk (trends continue instead of reverting)
- **Secondary:** Correlation breakdown (pairs diverge permanently)
- **Tail Risk:** Market structure changes (2015-2021 underperformance)

---

## Strategy Complement Criteria

### Must Have (Critical)
1. **Low Correlation to H5:** Target < 0.3 (ideally negative)
2. **Opposite Regime Preference:** Profits when H5 struggles
3. **Different Signal Type:** Not mean reversion based
4. **10-Year Track Record:** Works across full cycle (2015-2025)
5. **Positive Sharpe:** Target > 0.5 minimum, > 1.0 preferred

### Nice to Have (Preferred)
1. **Different Asset Class:** Not just equity pairs
2. **Different Timeframe:** Longer or shorter holding periods
3. **Uncorrelated Drawdowns:** Doesn't fail at same time as H5
4. **Simple Implementation:** Proven, well-researched patterns
5. **Scalable:** Can handle significant capital

---

## Research Methodology

### Step 1: Identify Regime Gaps
**When does H5 fail?**
- ✗ Strong trending markets (up or down)
- ✗ Low volatility environments
- ✗ Persistent correlation patterns
- ✗ 2015-2017 conditions (need to investigate why)
- ✗ 2018-2021 conditions (need to investigate why)

**What works in those periods?**
- ✓ Trend following (rides trends instead of fighting them)
- ✓ Momentum strategies (continuation patterns)
- ✓ Volatility strategies (benefits from vol changes)
- ✓ Cross-asset strategies (diversification)

### Step 2: Search Strategy Universe

#### A. Trend Following Strategies
**Candidates:**
1. **Moving Average Crossover**
   - Signal: SMA 50/200 cross, price position
   - Assets: SPY, QQQ, IWM, sector ETFs
   - Expected Sharpe: 0.8-1.5
   - Correlation to H5: -0.2 to 0.0 (low/negative)
   - **Search terms:** "trend following equity ETF", "moving average strategy backtest", "SMA crossover system"

2. **Breakout/Channel**
   - Signal: Donchian channels, ATR breakouts
   - Assets: Equity indices, commodities
   - Expected Sharpe: 0.6-1.2
   - Correlation to H5: -0.1 to +0.1
   - **Search terms:** "breakout trading system", "donchian channel strategy", "volatility breakout"

3. **Dual Momentum (Relative + Absolute)**
   - Signal: 3-12 month momentum, ranking
   - Assets: Equity sectors, international markets
   - Expected Sharpe: 0.8-1.6
   - Expected correlation: 0.0 to +0.2
   - **Search terms:** "dual momentum strategy", "relative strength rotation", "Gary Antonacci momentum"

#### B. Volatility Strategies
**Candidates:**
1. **VIX Mean Reversion**
   - Signal: VIX spikes above threshold, mean revert
   - Assets: VXX, UVXY (short), SPY options
   - Expected Sharpe: 1.0-2.5 (but higher tail risk)
   - Correlation to H5: +0.3 to +0.5 (moderate positive)
   - **Search terms:** "VIX mean reversion strategy", "volatility premium capture", "VXX short strategy"

2. **Volatility Risk Premium**
   - Signal: Sell implied vol (options), collect premium
   - Assets: SPY/SPX options (short strangles/iron condors)
   - Expected Sharpe: 1.5-3.0 (with blow-up risk)
   - Correlation to H5: +0.2 to +0.4
   - **Search terms:** "options premium selling", "volatility risk premium", "short strangle backtest"

3. **Vol Arbitrage (Term Structure)**
   - Signal: VIX futures contango/backwardation
   - Assets: VIX futures calendar spreads
   - Expected Sharpe: 0.8-1.8
   - Correlation to H5: +0.1 to +0.3
   - **Search terms:** "VIX term structure trading", "contango strategy", "VIX futures spread"

#### C. Cross-Asset Strategies
**Candidates:**
1. **Risk Parity / All Weather**
   - Signal: Risk-balanced allocation across assets
   - Assets: Stocks (SPY), Bonds (TLT), Gold (GLD), Commodities (DBC)
   - Expected Sharpe: 0.6-1.0
   - Correlation to H5: +0.1 to +0.3
   - **Search terms:** "risk parity strategy", "all weather portfolio", "permanent portfolio backtest"

2. **Tactical Asset Allocation**
   - Signal: Momentum + valuation across asset classes
   - Assets: Equities, bonds, commodities, currencies
   - Expected Sharpe: 0.7-1.3
   - Correlation to H5: 0.0 to +0.2
   - **Search terms:** "tactical asset allocation", "multi-asset momentum", "global macro strategy"

3. **Carry Trade**
   - Signal: Interest rate differentials, yield curve
   - Assets: Currency pairs, bond markets
   - Expected Sharpe: 0.5-1.2
   - Correlation to H5: -0.1 to +0.1
   - **Search terms:** "currency carry trade strategy", "yield curve trading", "bond arbitrage"

#### D. Alternative Approaches
**Candidates:**
1. **Market Neutral Long/Short Equity**
   - Signal: Factor models (value, quality, momentum)
   - Assets: Equity universe (long best, short worst)
   - Expected Sharpe: 0.8-1.5
   - Correlation to H5: +0.2 to +0.4 (moderate - both equity focused)
   - **Search terms:** "market neutral long short", "factor investing strategy", "quantitative equity strategy"

2. **Statistical Arbitrage (Different Pairs)**
   - Signal: Same as H5 but different sector pairs
   - Assets: Tech pairs, healthcare pairs, consumer pairs
   - Expected Sharpe: 0.8-1.5
   - Correlation to H5: +0.5 to +0.7 (high - similar strategy)
   - **Search terms:** "sector pairs trading", "statistical arbitrage tech stocks"
   - **Note:** May not be complementary enough (too similar to H5)

3. **Machine Learning Prediction**
   - Signal: ML models (random forest, neural nets)
   - Assets: Various (depends on features)
   - Expected Sharpe: Unknown (high variance)
   - Correlation to H5: Unknown
   - **Search terms:** "machine learning trading strategy", "quantitative ML trading"
   - **Note:** Complex, requires more research/validation

---

## Recommended Search Plan

### Phase 1: Quick Literature Review (2-3 hours)

**Search these resources:**

1. **QuantConnect Community**
   - Search: "trend following", "momentum", "volatility strategies"
   - Look for: Shared algorithms with backtests on QC platform
   - URL: https://www.quantconnect.com/forum/

2. **Academic Papers (SSRN/ArXiv)**
   - Search: "trend following Sharpe ratio", "momentum strategies backtest"
   - Focus on: Papers with 10+ year backtests, correlation analysis
   - URL: https://papers.ssrn.com

3. **Quantitative Blogs/Books**
   - **"Following the Trend" by Andreas Clenow** (trend following)
   - **"Dual Momentum Investing" by Gary Antonacci** (momentum)
   - **Alpha Architect blog** (factor investing, momentum)
   - **Quantpedia** (strategy database)

4. **GitHub Repositories**
   - Search: "quantitative trading strategies", "algorithmic trading python"
   - Look for: Well-documented strategies with backtests
   - Validate: Check if code is production-quality

### Phase 2: Strategy Shortlist (1 hour)

**Evaluate top 3-5 candidates on:**
1. Theoretical correlation to H5 (opposite regime preference?)
2. Implementation complexity (can we build in 1-2 weeks?)
3. Data requirements (do we have access on QC?)
4. Historical performance (Sharpe > 0.5 on 10 years?)
5. Research quality (peer-reviewed or well-tested?)

**Create shortlist:** Top 3 strategies to prototype

### Phase 3: Rapid Prototyping (1 week per strategy)

**For each shortlisted strategy:**
1. **Day 1-2:** Code basic version in QC
2. **Day 3-4:** Run 10-year backtest (2015-2025)
3. **Day 5:** Calculate correlation to H5
4. **Day 6-7:** Basic optimization (if Sharpe > 0.5)

**Decision criteria:**
- Keep if: Sharpe > 0.5 AND correlation to H5 < 0.4
- Drop if: Sharpe < 0.3 OR correlation to H5 > 0.6

---

## Strategy Evaluation Matrix

Once you find candidates, score them:

| Strategy | Sharpe (10yr) | Correlation to H5 | Regime Fit | Complexity | SCORE |
|----------|---------------|-------------------|------------|------------|-------|
| Trend Following MA | ? | ? | Opposite | Low | ? |
| Dual Momentum | ? | ? | Different | Low | ? |
| VIX Mean Reversion | ? | ? | Complementary | Medium | ? |
| Risk Parity | ? | ? | Diversifying | Low | ? |
| Vol Risk Premium | ? | ? | Complementary | High | ? |

**Scoring:**
- Sharpe: >1.5 = 5pts, 1.0-1.5 = 4pts, 0.5-1.0 = 3pts, <0.5 = 1pt
- Correlation: <0.0 = 5pts, 0.0-0.2 = 4pts, 0.2-0.4 = 3pts, >0.4 = 1pt
- Regime: Opposite = 5pts, Different = 4pts, Complementary = 3pts, Same = 1pt
- Complexity: Low = 5pts, Medium = 3pts, High = 1pt

**Target Score:** 15+ points = proceed to full validation

---

## Portfolio Construction Framework

Once you have 2-3 validated strategies:

### Equal Weight (Simple Start)
```python
portfolio = {
    'H5_stat_arb': 0.33,
    'H6_trend': 0.33,
    'H7_momentum': 0.34
}
```

### Risk Parity (Better)
```python
# Weight inversely to volatility
for strategy in portfolio:
    weight = (1 / strategy.volatility) / sum(1/s.volatility for s in portfolio)
```

### Regime-Based (Best)
```python
# Detect regime, adjust weights
if regime == 'high_vol_mean_reverting':
    weights = {'H5': 0.60, 'H6': 0.20, 'H7': 0.20}
elif regime == 'low_vol_trending':
    weights = {'H5': 0.20, 'H6': 0.60, 'H7': 0.20}
elif regime == 'crisis':
    weights = {'H5': 0.10, 'H6': 0.30, 'H7': 0.60}  # Defensive
```

---

## Expected Outcome

**Goal:** Portfolio of 3 strategies by end of Q1 2025

**Target Metrics:**
- Portfolio Sharpe: > 1.5 (vs H5 alone: ~1.0-1.8)
- Portfolio Max Drawdown: < 15% (vs H5 alone: ~20%+)
- Correlation between strategies: < 0.4 (low)
- Positive returns in ≥ 2 regimes (bull/bear/sideways)

**Timeline:**
- Week 1: Research & shortlist (THIS WEEK)
- Week 2-3: Prototype top 3 candidates
- Week 4-5: Validate H6 (best candidate)
- Week 6-8: Validate H7 (second best)
- Week 9-10: Build regime detection & portfolio logic
- Week 11-12: Paper trade portfolio

---

## Next Steps

**Immediate (Today):**
1. Search QuantConnect forums for trend following strategies
2. Read Antonacci "Dual Momentum" summary or blog posts
3. Search SSRN for "trend following" + "Sharpe ratio" papers
4. Create shortlist of 3 specific strategies to prototype

**Tomorrow:**
1. Share shortlist for review
2. Pick #1 strategy to start prototyping
3. Begin H6 hypothesis document

**This Week:**
1. Code basic version of H6
2. Run 10-year backtest
3. Calculate correlation to H5
4. Decide: proceed with H6 or try different strategy

---

## Resources to Search

### Online Databases
- **Quantpedia:** https://quantpedia.com (strategy screener - $)
- **AlphaArchitect:** https://alphaarchitect.com/blog/ (free research)
- **Portfolio Charts:** https://portfoliocharts.com (backtests)

### Academic
- **SSRN:** https://papers.ssrn.com
- **ArXiv:** https://arxiv.org (search: "quantitative finance")

### Communities
- **QuantConnect Forum:** https://www.quantconnect.com/forum/
- **Reddit r/algotrading:** https://reddit.com/r/algotrading
- **Quantitative Finance Stack Exchange:** https://quant.stackexchange.com

### Books (Quick Reference)
- "Following the Trend" - Andreas Clenow (trend following)
- "Dual Momentum Investing" - Gary Antonacci (momentum)
- "Quantitative Momentum" - Wesley Gray (momentum factors)
- "Quantitative Trading" - Ernest Chan (mean reversion vs momentum)

---

**CURRENT STATUS:** Awaiting H5 10-year optimization results, beginning complement research

**NEXT ACTION:** Search for trend following strategies that work in 2015-2021 period (when H5 was weak)
