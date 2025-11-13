# H6 Statistical Arbitrage Pair Analysis (2015-2022 Period)

**Date:** 2025-11-11
**Objective:** Identify best performing pairs for 2015-2022 to complement H5 (which performs poorly in this period)
**Analysis Period:** 2015-2022 (weak period for H5)
**Screening Criteria:** Pairs with strong cointegration, high Sharpe, and robust statistics

---

## Executive Summary

**Top 3 Recommended Pairs:**

### 1. MPLX vs V (Marathon Petroleum vs Visa) ⭐ BEST CANDIDATE
- **Sharpe Ratio:** 3.13
- **Correlation:** 0.73 (strong cointegration)
- **Half-life:** 19.0 days
- **Sectors:** Energy (MPLX) vs Financial (V)
- **Cross-sector:** Yes (lower systemic risk)
- **Quality Score:** Excellent cointegration (p-val: 0.008, β: 6.675)

### 2. ENB vs WEC (Enbridge vs Wisconsin Electric)
- **Sharpe Ratio:** 3.07
- **Correlation:** 0.77 (very strong cointegration)
- **Half-life:** 14.4 days
- **Sectors:** Energy (ENB) vs Utilities (WEC)
- **Cross-sector:** Yes
- **Quality Score:** Excellent cointegration (p-val: 0.003, β: 2.113)

### 3. COO vs GPK (Cooper Companies vs Graphic Packaging)
- **Sharpe Ratio:** 3.10
- **Correlation:** 0.57 (moderate cointegration)
- **Half-life:** 18.6 days
- **Sectors:** Healthcare (COO) vs Consumer Cyclical (GPK)
- **Cross-sector:** Yes
- **Quality Score:** Strong cointegration (p-val: 0.012, β: 3.135)

---

## Screening Methodology

### Filters Applied (from screenshots)

**Quality Filters:**
- ✓ Cointegrated @ 95% significance
- ✓ Half-life (C) >= 10 days (mean reversion timeframe)
- ✓ Half-life (C) <= 40 days (not too slow)
- ✓ Sharpe ratio >= 1.5
- ✓ Market capitalization >= $1000M (liquidity requirement)
- ✓ Backtests performed >= 19
- ✓ Average volume >= 1,000,000 (execution feasibility)

**Sorting Criteria:**
1. Median Sharpe ratio (primary)
2. Half-life cointegration (secondary)
3. Cointegration p-value (quality check)

---

## Detailed Pair Analysis

### 1. MPLX vs V (Energy/Financial Cross-Sector) ⭐

**Statistical Quality:**
- Cointegration Strength: 95% (strict), 99% (relaxed)
- Cointegration p-value: 0.008 (highly significant)
- β coefficient: 6.675 (OLS)
- Half-life: 19.0 days (optimal for pairs trading)
- Skew: 0.150, Kurt: -0.55 (near-normal returns)

**Performance Metrics:**
- **Sharpe Ratio:** 3.13 (Train), 2.81 (Resd)
- **RSI:** 3.98 (Train), 3.27 (Resd)
- **K-Grind:** 0.30 (low grinding)
- **Profit(19):** CAGR 12.1%, Lnrty 0.937, Sharpe 3.15, Score 10.5 (>0.01)
- **SDir(19):** CAGR 6.09, Lnrty 0.891, Sharpe 2.68, Score 4.53 (>0.00)

**Risk Assessment:**
- ADF: 0.00 (stationary residuals)
- β: 7.18 (Hilfe: 17.4)
- PACF: -10 (mean-reverting autocorrelation)
- Normality: Pass (DH, SW tests)

**Liquidity:**
- MPLX: Vol 1749k, Price $50.41, Cap $6.66B (CFD available)
- V: Vol 5858k, Price $342.43, Cap $168.16B (CFD available)

**Why It's Best:**
- Highest Sharpe (3.13) among top candidates
- Cross-sector diversification (Energy/Financial)
- Strong cointegration with fast mean reversion (19 days)
- Excellent liquidity on both legs
- Near-normal return distribution (low tail risk)
- Robust out-of-sample performance (Resd Sharpe: 2.81)

---

### 2. ENB vs WEC (Energy/Utilities Cross-Sector)

**Statistical Quality:**
- Cointegration Strength: 95%, 99% (very strong)
- Cointegration p-value: 0.003 (extremely significant)
- β coefficient: 2.113 (OLS)
- Half-life: 14.4 days (fast mean reversion)
- Skew: -0.136, Kurt: -0.53 (near-normal)

**Performance Metrics:**
- **Sharpe Ratio:** 3.07 (Train), 2.51 (Resd)
- **RSI:** 2.91 (Train), 2.59 (Resd)
- **K-Grind:** 2.38 (moderate grinding)
- **Profit(19):** CAGR 11.6%, Lnrty 0.846, Sharpe 3.07, Score 9.49 (>3.76)
- **SDir(19):** CAGR 6.20, Lnrty 0.944, Sharpe 2.19, Score 5.15 (>0.67)

**Risk Assessment:**
- ADF: 0.00 (stationary)
- β: 2.37 (Hilfe: 14.3)
- PACF: -5 (mean-reverting)
- Normality: Pass (DH, SW tests)

**Liquidity:**
- ENB: Vol 3940k, Price $47.12, Cap $39.39B
- WEC: Vol 2394k, Price $114.56, Cap $11.25B (CFD available)

**Why It's Strong:**
- Fastest half-life (14.4 days = more trading opportunities)
- Strongest cointegration (p-val: 0.003)
- Cross-sector (Energy/Utilities - correlated but not identical)
- Very high liquidity
- Lowest K-Grind degradation

---

### 3. COO vs GPK (Healthcare/Consumer Cross-Sector)

**Statistical Quality:**
- Cointegration Strength: 95%, 99%
- Cointegration p-value: 0.012 (significant)
- β coefficient: 3.135 (OLS)
- Half-life: 18.6 days
- Skew: 0.198, Kurt: -0.54 (acceptable)

**Performance Metrics:**
- **Sharpe Ratio:** 3.10 (Train), 3.32 (Resd - IMPROVED!)
- **RSI:** 2.91 (Train), 2.42 (Resd)
- **K-Grind:** 2.93 (higher grinding)
- **Profit(19):** CAGR 18.8%, Lnrty 0.931, Sharpe 3.02, Score 15.0 (>4.24)
- **SDir(19):** CAGR 11.6, Lnrty 0.902, Sharpe 2.38, Score 7.03 (>0.07)

**Risk Assessment:**
- ADF: 0.00 (stationary)
- β: 4.92 (Hilfe: 18.1)
- PACF: -6 (mean-reverting)
- Normality: Pass (DH, SW tests)

**Liquidity:**
- COO: Vol 2424k, Price $71.39, Cap $16.41B (CFD available)
- GPK: Vol 5880k, Price $16.93, Cap $4.84B

**Why It's Strong:**
- **Resd Sharpe > Train Sharpe** (3.32 vs 3.10 = robust!)
- Highest CAGR (18.8%)
- True cross-sector diversification (Healthcare/Consumer)
- Good liquidity
- Lower correlation (0.57) = more independent price action

---

## Additional Strong Candidates

### 4. ECL vs EWJ (Ecolab vs Japan ETF)
- Sharpe: 3.30 (Train), 3.07 (Resd)
- Correlation: 0.74
- Half-life: 86.9 days (slower - longer holding periods)
- Cross-asset: US Stock vs Japan ETF (international diversification)
- Profit(19): CAGR 12.8%, Sharpe 2.99
- **Note:** Slower mean reversion (86 days), but extremely robust

### 5. PNC vs KBE (PNC Financial vs Bank ETF)
- Sharpe: 2.40 (Train), 3.53 (Resd - HUGE IMPROVEMENT!)
- Correlation: 0.96 (very high - same sector)
- Half-life: 14.2 days (fast)
- Profit(19): CAGR 7.28%, Sharpe 2.92, Score 5.63 (>=0.00)
- **Warning:** Both in financials sector (higher systemic risk)
- **Note:** Resd Sharpe 1.5x Train Sharpe (exceptional robustness)

---

## Extended Period Analysis (2015-2025 vs 2015-2023)

From the "SEARCH_UPTO_2025_EXTENDED.png" and "SEARCH_UPTO_2023_EXTENDED.png" screenshots, I can see additional pairs tested over longer periods:

### Top Performers 2015-2025 (10-Year Test):

1. **GRVO vs EWY** (Grocery Outlet vs South Korea ETF)
   - Sharpe: 2.5 range
   - Cross-asset: US retail vs Korea ETF

2. **BEN vs SUM** (Franklin Resources vs Summit Materials)
   - Sharpe: 2.6+ range
   - Cross-sector: Financial vs Basic Materials

3. **LBRDA vs THU** (Liberty Broadband vs Tianhe Environmental)
   - Sharpe: 2.8+ range
   - Cross-sector: Communications vs Utilities

4. **FOXA vs AXP** (Fox Corp vs American Express)
   - Sharpe: 2.8+ range
   - Cross-sector: Communications vs Financial

5. **PSEC vs KAI** (Prospect Capital vs Kadant Inc)
   - Sharpe: 2.8+ range
   - Cross-sector: Financial vs Industrials

6. **KRC vs VNO** (Kilroy Realty vs Vornado Realty)
   - Sharpe: 2.8+ range
   - Same sector: REITs (high correlation expected)

7. **VRSN vs CRI** (Verisign vs Carter's)
   - Sharpe: 2.9+ range
   - Cross-sector: Technology vs Consumer

8. **ARE vs CRI** (Alexandria Real Estate vs Carter's)
   - Sharpe: 3.0+ range
   - Cross-sector: REIT vs Consumer

---

## Comparison to H5 Strategy

### H5 (Financial/REIT/Energy Pairs - 2022-2024 Focus)
- **Best Period:** 2022-2024 (Sharpe ~1.8-3.7)
- **Weak Period:** 2015-2021 (flat/choppy performance)
- **Regime Preference:** High volatility, mean-reverting markets
- **Sectors:** Financials, REITs, Energy (often same-sector pairs)

### H6 Candidates (This Analysis - 2015-2022 Focus)
- **Target Period:** 2015-2022 (complement H5's weakness)
- **Regime Preference:** Should work in trending/low-vol markets
- **Sectors:** Cross-sector pairs (Energy/Financial, Energy/Utilities, Healthcare/Consumer)
- **Expected Sharpe:** 2.5-3.3 (comparable to H5 but different periods)

### Correlation Expectations:
- **MPLX/V:** Different sectors, likely **LOW correlation to H5** (0.2-0.4)
- **ENB/WEC:** Different sectors, likely **LOW correlation to H5** (0.1-0.3)
- **COO/GPK:** Very different sectors, likely **VERY LOW correlation to H5** (0.0-0.2)

---

## Risk Assessment

### Strengths:
✓ All pairs pass strict cointegration tests (p < 0.05)
✓ Strong Sharpe ratios (2.4-3.3 range)
✓ Fast mean reversion (14-19 days for top 3)
✓ High liquidity (all > 1M volume)
✓ Cross-sector diversification
✓ Robust out-of-sample performance (Resd Sharpe ≈ Train Sharpe)
✓ Near-normal return distributions (low tail risk)

### Weaknesses:
⚠ **PNC/KBE:** Same sector (financials) - higher systemic risk
⚠ **ECL/EWJ:** Slow half-life (86 days) - fewer opportunities
⚠ **All pairs:** Past performance in 2015-2022 doesn't guarantee future performance
⚠ **Regime dependency:** May underperform in different market conditions

### Unknown Risks:
❓ **H5 correlation:** Need to calculate actual correlation between H6 candidate and H5
❓ **2022-2024 performance:** How do these pairs perform in H5's strong period?
❓ **Transaction costs:** Need to model slippage and commissions
❓ **Execution degradation:** K-Grind values suggest some degradation (0.3-2.9)

---

## Recommendation

### Primary Choice: MPLX vs V ⭐

**Rationale:**
1. **Highest Sharpe:** 3.13 (best risk-adjusted returns)
2. **Optimal half-life:** 19 days (not too fast, not too slow)
3. **Cross-sector:** Energy/Financial (diversification benefit)
4. **Robust:** Resd Sharpe 2.81 (90% of Train Sharpe)
5. **Liquid:** Both legs highly tradable
6. **Low grinding:** K-Grind 0.30 (minimal execution degradation)
7. **Statistical quality:** Excellent cointegration (p=0.008)

### Backup Choice: ENB vs WEC

**If MPLX/V fails validation, use ENB/WEC:**
- Strongest cointegration (p=0.003)
- Fastest mean reversion (14.4 days)
- Slightly lower Sharpe (3.07) but more trading opportunities

### Alternative: COO vs GPK

**For maximum diversification from H5:**
- Healthcare/Consumer sectors (very different from H5)
- Improving out-of-sample (Resd > Train Sharpe!)
- Lower correlation (0.57) to each other

---

## Next Steps

### Immediate (Today):
1. ✅ Document findings in this report
2. ⏭ Choose final H6 pair (recommendation: MPLX/V)
3. ⏭ Verify data availability on QuantConnect
4. ⏭ Begin H6 hypothesis document

### This Week:
1. ⏭ Code MPLX/V pair strategy in QC
2. ⏭ Run 10-year backtest (2015-2025)
3. ⏭ Compare performance to H5 by period:
   - 2015-2021: H6 should outperform H5
   - 2022-2024: H5 should outperform H6
4. ⏭ Calculate H5-H6 correlation
5. ⏭ Decision: Proceed if correlation < 0.4 AND 10-year Sharpe > 0.5

### Decision Criteria for H6:
- ✓ **10-Year Sharpe:** > 0.5 minimum (target > 1.0)
- ✓ **Correlation to H5:** < 0.4 (ideally < 0.3)
- ✓ **2015-2021 Sharpe:** > 0.5 (performs when H5 doesn't)
- ✓ **Data availability:** Both legs on QC with sufficient history
- ✓ **Execution feasibility:** Volume > 500k, spread < 0.5%

---

## Appendix: Research Tool Observations

### Screening Platform:
The screenshots show a sophisticated pairs trading screening platform with:
- Statistical tests: Cointegration (ADF, p-values), correlation, half-life
- Performance metrics: Sharpe, CAGR, linearity, system score
- Risk metrics: Skew, kurtosis, normality tests (DH, SW)
- Execution metrics: K-Grind (execution degradation)
- Orthogonal tests: β coefficient (TLS vs OLS)

### Filter Settings Used:
- **Quality:** Cointegration @ 95%, Half-life 10-40 days, Sharpe ≥ 1.5
- **Liquidity:** Market cap ≥ $1B, Volume ≥ 1M
- **Robustness:** Backtests ≥ 19 (walk-forward testing)
- **Sorting:** Median Sharpe → Half-life → p-value

### Data Period Coverage:
- Primary analysis: 2015-2022 (H5's weak period)
- Extended validation: 2015-2023, 2015-2025 (10-year tests)
- Multiple backtests: 19+ walks (robust validation)

---

## File Metadata

**Created:** 2025-11-11
**Author:** Claude (Statistical Analysis)
**Source Data:** /Users/donaldcross/ALGOS/Experimentos/Sanboxes/CLAUDE_CODE_EXPLORE/RESEARCH_STAT_ARB/H6/*.png
**Next Update:** After H6 prototype backtest complete
**Status:** Analysis complete, awaiting pair selection decision

---

## References

- H5 Strategy: `/STRATEGIES/hypothesis_5_statistical_arbitrage/`
- H5 Session Handoff: `/PROJECT_DOCUMENTATION/H5/SESSION_HANDOFF_REPORT_20251111.md`
- Strategy Complement Research: `/PROJECT_DOCUMENTATION/STRATEGY_COMPLEMENT_RESEARCH.md`
- Pairs Screening Screenshots: `/RESEARCH_STAT_ARB/H6/*.png`

---

**RECOMMENDATION: Proceed with MPLX vs V as H6 primary candidate**

**Next Action:** Create H6 hypothesis document and verify QC data availability
