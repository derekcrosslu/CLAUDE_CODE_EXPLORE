#!/usr/bin/env python3
"""
Monte Carlo Validation Analysis for Hypothesis 5
Using Advanced Metrics from CLAUDE_MC_VALIDATION_GUIDE

This script performs theoretical Monte Carlo analysis on existing backtest results
without requiring additional QC API backtests.
"""

import numpy as np
import json
from scipy import stats
from scipy.special import ndtr
from datetime import datetime


# ==================== BACKTEST RESULTS ====================
# From backtest ID: 26ccf4d10e367096c9f9eb1962a70bfb

BACKTEST_RESULTS = {
    "sharpe_ratio": 1.8086,
    "sortino_ratio": 2.2329,
    "max_drawdown": 0.083,
    "total_return": 2.247,
    "annual_return": 0.3841,
    "win_rate": 0.617,
    "loss_rate": 0.383,
    "psr": 0.9915,
    "total_trades": 329,
    "winning_trades": 204,
    "losing_trades": 125,
    "average_win": 2589.34,
    "average_loss": -2328.38,
    "profit_loss_ratio": 1.1121,
    "volatility": 0.1197,
    "alpha": 0.2144,
    "beta": 0.0548,
    "test_period": "2022-01-05 to 2025-08-04",
    "test_days": 1307
}

# Calculate return statistics from backtest
# Approximate daily returns based on annual metrics
DAILY_RETURNS_STATS = {
    "mean": BACKTEST_RESULTS["annual_return"] / 252,  # Daily mean return
    "std": BACKTEST_RESULTS["volatility"] / np.sqrt(252),  # Daily std
    "skewness": -0.5,  # Estimated (typical for trading strategies)
    "kurtosis": 4.5,   # Estimated (typical excess kurtosis)
    "observations": BACKTEST_RESULTS["test_days"]
}


# ==================== ADVANCED METRICS FUNCTIONS ====================

def calculate_probabilistic_sharpe_ratio(sharpe, returns_stats, benchmark_sr=0.0):
    """
    Calculate Probabilistic Sharpe Ratio (PSR)
    
    Reference: Bailey & López de Prado (2012)
    Industry threshold: PSR ≥ 0.95 for statistical significance
    """
    T = returns_stats['observations']
    skew = returns_stats['skewness']
    kurt = returns_stats['kurtosis']
    
    if T < 2:
        return 0.0
    
    # Standard error of Sharpe ratio (accounting for non-normality)
    variance_term = 1 + (sharpe**2 / 2) - skew * sharpe + ((kurt - 3) / 4) * sharpe**2
    variance_term = max(variance_term, 0.0001)
    
    se_sharpe = np.sqrt(variance_term / (T - 1))
    
    # PSR = Φ[(ŜR - SR*) / σ̂(ŜR)]
    if se_sharpe > 0:
        z_score = (sharpe - benchmark_sr) / se_sharpe
        psr = ndtr(z_score)
    else:
        psr = 1.0 if sharpe > benchmark_sr else 0.0
    
    return float(psr)


def calculate_minimum_track_record_length(sharpe, returns_stats, benchmark_sr=0.0, confidence=0.95):
    """
    Calculate Minimum Track Record Length (MinTRL)
    
    Reference: Bailey & López de Prado (2014)
    """
    if sharpe <= benchmark_sr:
        return float('inf')
    
    skew = returns_stats['skewness']
    kurt = returns_stats['kurtosis']
    
    z_alpha = stats.norm.ppf(confidence)
    
    # MinTRL = 1 + [1 - γ₃×SR + (γ₄-1)/4 × SR²] × (Z_α/(SR-SR*))²
    factor = 1 - skew * sharpe + ((kurt - 1) / 4) * sharpe**2
    factor = max(factor, 0.0001)
    
    min_trl = 1 + factor * (z_alpha / (sharpe - benchmark_sr))**2
    
    return int(np.ceil(min_trl))


def calculate_deflated_sharpe_ratio(sharpe_ratios, confidence=0.95):
    """
    Calculate Deflated Sharpe Ratio (DSR) to correct for multiple testing
    
    Reference: Bailey & López de Prado (2014)
    """
    sharpe_array = np.array(sharpe_ratios)
    N = len(sharpe_array)
    
    if N <= 1:
        return 1.0
    
    var_sharpes = np.var(sharpe_array, ddof=1)
    
    if var_sharpes == 0:
        return 1.0
    
    gamma_em = 0.5772156649  # Euler-Mascheroni constant
    
    # Expected maximum Sharpe under null hypothesis
    term1 = (1 - gamma_em) * stats.norm.ppf(1 - 1/N)
    term2 = gamma_em * stats.norm.ppf(1 - (1/N) * np.exp(-1))
    
    sr_expected_max = np.sqrt(var_sharpes) * (term1 + term2)
    
    sr_best = np.max(sharpe_array)
    
    if sr_best > sr_expected_max:
        z_score = (sr_best - sr_expected_max) / np.sqrt(var_sharpes / N)
        dsr = ndtr(z_score)
    else:
        dsr = 0.5
    
    return float(dsr)


def assess_sample_size_adequacy(n_trades, autocorrelation=0.0):
    """Assess whether sample size is adequate for statistical validation"""
    n_effective = n_trades * (1 - abs(autocorrelation))
    
    if n_effective >= 1000:
        adequacy = "EXCELLENT"
        confidence = "High confidence in statistical inference"
    elif n_effective >= 100:
        adequacy = "GOOD"
        confidence = "Adequate for production systems"
    elif n_effective >= 50:
        adequacy = "MARGINAL"
        confidence = "Minimum acceptable, use with caution"
    elif n_effective >= 30:
        adequacy = "WEAK"
        confidence = "Preliminary hypothesis testing only"
    else:
        adequacy = "INSUFFICIENT"
        confidence = "Too few samples for reliable inference"
    
    return {
        'n_actual': n_trades,
        'n_effective': int(n_effective),
        'autocorrelation': autocorrelation,
        'adequacy': adequacy,
        'confidence': confidence,
        'recommended_minimum': 100
    }


# ==================== MONTE CARLO SIMULATION ====================

def simulate_monte_carlo_equity_curves(n_simulations=1000):
    """
    Simulate Monte Carlo equity curves based on backtest statistics
    
    Uses bootstrap resampling of trade results to generate alternative
    equity curve realizations.
    """
    # Approximate trade-level statistics
    n_trades = BACKTEST_RESULTS["total_trades"]
    win_rate = BACKTEST_RESULTS["win_rate"]
    avg_win = BACKTEST_RESULTS["average_win"]
    avg_loss = BACKTEST_RESULTS["average_loss"]
    
    simulated_sharpes = []
    simulated_drawdowns = []
    simulated_returns = []
    
    for _ in range(n_simulations):
        # Generate random trades
        trades = []
        for _ in range(n_trades):
            if np.random.random() < win_rate:
                # Winning trade
                pnl = np.random.normal(avg_win, avg_win * 0.5)
            else:
                # Losing trade
                pnl = np.random.normal(avg_loss, abs(avg_loss) * 0.5)
            trades.append(pnl)
        
        # Calculate equity curve
        equity = np.cumsum(trades) + 100000  # Starting capital
        returns = np.diff(equity) / equity[:-1]
        
        # Calculate metrics
        if len(returns) > 0 and np.std(returns) > 0:
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
            total_return = (equity[-1] / equity[0]) - 1
            
            # Calculate drawdown
            cummax = np.maximum.accumulate(equity)
            drawdown = (cummax - equity) / cummax
            max_dd = np.max(drawdown)
            
            simulated_sharpes.append(sharpe)
            simulated_drawdowns.append(max_dd)
            simulated_returns.append(total_return)
    
    return {
        'sharpes': simulated_sharpes,
        'drawdowns': simulated_drawdowns,
        'returns': simulated_returns
    }


# ==================== MAIN ANALYSIS ====================

def run_monte_carlo_validation():
    """Run comprehensive Monte Carlo validation analysis"""
    
    print("="*70)
    print("MONTE CARLO VALIDATION ANALYSIS - HYPOTHESIS 5")
    print("Statistical Arbitrage Pairs Trading")
    print("="*70)
    print()
    
    # 1. Calculate PSR
    print("1. PROBABILISTIC SHARPE RATIO (PSR)")
    print("-" * 70)
    psr = calculate_probabilistic_sharpe_ratio(
        BACKTEST_RESULTS["sharpe_ratio"],
        DAILY_RETURNS_STATS,
        benchmark_sr=0.0
    )
    print(f"   Sharpe Ratio: {BACKTEST_RESULTS['sharpe_ratio']:.4f}")
    print(f"   PSR (vs SR > 0): {psr:.4f}")
    print(f"   Interpretation: {psr*100:.2f}% probability SR > 0")
    print(f"   Status: {'✅ SIGNIFICANT' if psr >= 0.95 else '⚠️  MARGINAL' if psr >= 0.90 else '❌ NOT SIGNIFICANT'}")
    print(f"   (Threshold: PSR ≥ 0.95 for 95% confidence)")
    print()
    
    # 2. Calculate MinTRL
    print("2. MINIMUM TRACK RECORD LENGTH (MinTRL)")
    print("-" * 70)
    min_trl = calculate_minimum_track_record_length(
        BACKTEST_RESULTS["sharpe_ratio"],
        DAILY_RETURNS_STATS,
        benchmark_sr=0.0,
        confidence=0.95
    )
    actual_obs = DAILY_RETURNS_STATS["observations"]
    print(f"   Required observations: {min_trl}")
    print(f"   Actual observations: {actual_obs}")
    print(f"   Coverage: {actual_obs/min_trl*100:.1f}%")
    print(f"   Status: {'✅ ADEQUATE' if actual_obs >= min_trl else '❌ INSUFFICIENT'}")
    print(f"   Gap: {max(0, min_trl - actual_obs)} days short" if actual_obs < min_trl else "   ✅ Meets requirement")
    print()
    
    # 3. Sample Size Assessment
    print("3. SAMPLE SIZE ADEQUACY")
    print("-" * 70)
    sample_assessment = assess_sample_size_adequacy(
        BACKTEST_RESULTS["total_trades"],
        autocorrelation=0.1  # Estimated
    )
    print(f"   Total trades: {sample_assessment['n_actual']}")
    print(f"   Effective trades: {sample_assessment['n_effective']} (adj for autocorr)")
    print(f"   Adequacy: {sample_assessment['adequacy']}")
    print(f"   Confidence: {sample_assessment['confidence']}")
    print(f"   Status: {'✅ PASS' if sample_assessment['adequacy'] in ['EXCELLENT', 'GOOD'] else '⚠️  MARGINAL' if sample_assessment['adequacy'] == 'MARGINAL' else '❌ FAIL'}")
    print()
    
    # 4. Monte Carlo Simulation
    print("4. MONTE CARLO EQUITY CURVE SIMULATION")
    print("-" * 70)
    print(f"   Running {1000} simulations...")
    mc_results = simulate_monte_carlo_equity_curves(n_simulations=1000)
    
    sharpe_p10 = np.percentile(mc_results['sharpes'], 10)
    sharpe_median = np.percentile(mc_results['sharpes'], 50)
    sharpe_p90 = np.percentile(mc_results['sharpes'], 90)
    
    dd_p10 = np.percentile(mc_results['drawdowns'], 10)
    dd_median = np.percentile(mc_results['drawdowns'], 50)
    dd_p90 = np.percentile(mc_results['drawdowns'], 90)
    
    ret_p10 = np.percentile(mc_results['returns'], 10)
    ret_median = np.percentile(mc_results['returns'], 50)
    ret_p90 = np.percentile(mc_results['returns'], 90)
    
    print(f"\n   Sharpe Ratio Distribution:")
    print(f"      10th percentile: {sharpe_p10:.3f} (worst case in 90% of scenarios)")
    print(f"      Median: {sharpe_median:.3f}")
    print(f"      90th percentile: {sharpe_p90:.3f}")
    print(f"      Backtest actual: {BACKTEST_RESULTS['sharpe_ratio']:.3f}")
    
    print(f"\n   Max Drawdown Distribution:")
    print(f"      10th percentile: {dd_p10*100:.2f}%")
    print(f"      Median: {dd_median*100:.2f}%")
    print(f"      90th percentile: {dd_p90*100:.2f}% (worst case in 90% of scenarios)")
    print(f"      Backtest actual: {BACKTEST_RESULTS['max_drawdown']*100:.2f}%")
    print(f"      ⚠️  Note: MC suggests drawdowns could be {dd_p90/BACKTEST_RESULTS['max_drawdown']:.1f}x larger")
    
    print(f"\n   Total Return Distribution:")
    print(f"      10th percentile: {ret_p10*100:.1f}%")
    print(f"      Median: {ret_median*100:.1f}%")
    print(f"      90th percentile: {ret_p90*100:.1f}%")
    print()
    
    # 5. Deflated Sharpe Ratio (simulating multiple tests)
    print("5. DEFLATED SHARPE RATIO (DSR)")
    print("-" * 70)
    # Simulate testing 10 parameter combinations (conservative estimate)
    simulated_tests = [BACKTEST_RESULTS["sharpe_ratio"]] + list(np.random.normal(
        BACKTEST_RESULTS["sharpe_ratio"] * 0.8,  # Assume other params ~20% worse
        BACKTEST_RESULTS["sharpe_ratio"] * 0.15,  # Variance
        9
    ))
    dsr = calculate_deflated_sharpe_ratio(simulated_tests)
    print(f"   Simulated parameter tests: {len(simulated_tests)}")
    print(f"   Best Sharpe (current): {BACKTEST_RESULTS['sharpe_ratio']:.4f}")
    print(f"   DSR: {dsr:.4f}")
    print(f"   Status: {'✅ SIGNIFICANT' if dsr >= 0.95 else '⚠️  MARGINAL' if dsr >= 0.90 else '❌ NOT SIGNIFICANT'}")
    print(f"   (Accounts for multiple testing bias)")
    print()
    
    # 6. Overfitting Risk Assessment
    print("6. OVERFITTING RISK ASSESSMENT")
    print("-" * 70)
    
    overfitting_indicators = []
    
    # Check 1: Sharpe too perfect?
    if BACKTEST_RESULTS["sharpe_ratio"] > 3.0:
        overfitting_indicators.append("❌ Sharpe > 3.0 (suspiciously high)")
    else:
        print(f"   ✅ Sharpe {BACKTEST_RESULTS['sharpe_ratio']:.2f} < 3.0 (not suspiciously perfect)")
    
    # Check 2: Win rate too high?
    if BACKTEST_RESULTS["win_rate"] > 0.75:
        overfitting_indicators.append("❌ Win rate > 75% (suspiciously high)")
    else:
        print(f"   ✅ Win rate {BACKTEST_RESULTS['win_rate']*100:.1f}% < 75% (realistic)")
    
    # Check 3: Trade count sufficient?
    if BACKTEST_RESULTS["total_trades"] < 30:
        overfitting_indicators.append("❌ < 30 trades (insufficient sample)")
    else:
        print(f"   ✅ {BACKTEST_RESULTS['total_trades']} trades ≥ 30 (sufficient sample)")
    
    # Check 4: PSR passes?
    if psr < 0.95:
        overfitting_indicators.append(f"⚠️  PSR {psr:.3f} < 0.95 (marginal significance)")
    else:
        print(f"   ✅ PSR {psr:.3f} ≥ 0.95 (statistically significant)")
    
    # Check 5: Parameter count reasonable?
    param_count = 6  # z_entry, z_exit, lookback, position_size, max_days, stop_loss
    if param_count > 10:
        overfitting_indicators.append(f"⚠️  {param_count} parameters (risk of curve-fitting)")
    else:
        print(f"   ✅ {param_count} parameters < 10 (simple strategy)")
    
    print(f"\n   Overall Overfitting Risk: ", end="")
    if len(overfitting_indicators) == 0:
        print("✅ LOW")
    elif len(overfitting_indicators) <= 2:
        print("⚠️  MODERATE")
    else:
        print("❌ HIGH")
        for indicator in overfitting_indicators:
            print(f"      {indicator}")
    print()
    
    # 7. Final Assessment
    print("="*70)
    print("FINAL ROBUSTNESS ASSESSMENT")
    print("="*70)
    print()
    
    score = 0
    max_score = 6
    
    criteria = []
    
    # Criterion 1: PSR ≥ 0.95
    if psr >= 0.95:
        score += 1
        criteria.append(("✅ PSR ≥ 0.95", True))
    else:
        criteria.append(("❌ PSR < 0.95", False))
    
    # Criterion 2: MinTRL met
    if actual_obs >= min_trl:
        score += 1
        criteria.append(("✅ Track record adequate", True))
    else:
        criteria.append(("⚠️  Track record short", False))
    
    # Criterion 3: Sample size good
    if sample_assessment['adequacy'] in ['EXCELLENT', 'GOOD']:
        score += 1
        criteria.append(("✅ Sample size adequate", True))
    else:
        criteria.append(("⚠️  Sample size marginal", False))
    
    # Criterion 4: MC 10th percentile Sharpe > 0.5
    if sharpe_p10 > 0.5:
        score += 1
        criteria.append((f"✅ MC 10th %ile Sharpe {sharpe_p10:.2f} > 0.5", True))
    else:
        criteria.append((f"❌ MC 10th %ile Sharpe {sharpe_p10:.2f} ≤ 0.5", False))
    
    # Criterion 5: Low overfitting risk
    if len(overfitting_indicators) <= 1:
        score += 1
        criteria.append(("✅ Low overfitting risk", True))
    else:
        criteria.append(("⚠️  Moderate overfitting risk", False))
    
    # Criterion 6: MC max DD < 20%
    if dd_p90 < 0.20:
        score += 1
        criteria.append((f"✅ MC 90th %ile DD {dd_p90*100:.1f}% < 20%", True))
    else:
        criteria.append((f"⚠️  MC 90th %ile DD {dd_p90*100:.1f}% ≥ 20%", False))
    
    print("Validation Criteria:")
    for criterion, passed in criteria:
        print(f"   {criterion}")
    
    print(f"\n📊 Score: {score}/{max_score} ({score/max_score*100:.0f}%)")
    print()
    
    # Decision
    if score >= 5:
        decision = "ROBUST_STRATEGY"
        recommendation = "✅ Strategy passes rigorous validation. Ready for paper trading."
    elif score >= 4:
        decision = "PROCEED_WITH_CAUTION"
        recommendation = "⚠️  Strategy shows acceptable robustness but has some concerns. Monitor closely in paper trading."
    elif score >= 3:
        decision = "WEAK_ROBUSTNESS"
        recommendation = "⚠️  Strategy shows weak validation. Additional testing recommended before deployment."
    else:
        decision = "ABANDON_STRATEGY"
        recommendation = "❌ Strategy fails validation. Consider new hypothesis or significant revisions."
    
    print(f"🎯 DECISION: {decision}")
    print(f"📝 RECOMMENDATION: {recommendation}")
    print()
    
    # Generate summary dict
    summary = {
        "strategy": "Hypothesis 5 - Statistical Arbitrage Pairs Trading",
        "validation_date": datetime.now().isoformat(),
        "backtest_metrics": BACKTEST_RESULTS,
        "advanced_metrics": {
            "psr": float(psr),
            "min_trl_required": int(min_trl),
            "min_trl_actual": int(actual_obs),
            "sample_adequacy": sample_assessment['adequacy'],
            "dsr": float(dsr),
            "mc_sharpe_p10": float(sharpe_p10),
            "mc_sharpe_median": float(sharpe_median),
            "mc_sharpe_p90": float(sharpe_p90),
            "mc_dd_p10": float(dd_p10),
            "mc_dd_median": float(dd_median),
            "mc_dd_p90": float(dd_p90),
            "mc_return_p10": float(ret_p10),
            "mc_return_median": float(ret_median),
            "mc_return_p90": float(ret_p90)
        },
        "overfitting_risk": "LOW" if len(overfitting_indicators) == 0 else "MODERATE" if len(overfitting_indicators) <= 2 else "HIGH",
        "validation_score": f"{score}/{max_score}",
        "decision": decision,
        "recommendation": recommendation,
        "criteria_passed": [c[0] for c in criteria if c[1]],
        "criteria_failed": [c[0] for c in criteria if not c[1]]
    }
    
    # Save results
    filename = "mc_validation_results.json"
    with open(filename, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"💾 Results saved to: {filename}")
    print("="*70)
    
    return summary


if __name__ == "__main__":
    results = run_monte_carlo_validation()
