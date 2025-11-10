#!/usr/bin/env python3
"""
Decision Logic Module for Autonomous Workflow

Implements the 4-tier decision framework for evaluating backtest results
and making autonomous routing decisions.

Phase 3: Backtest Evaluation
- ABANDON_HYPOTHESIS: Performance below minimum viable
- PROCEED_TO_OPTIMIZATION: Decent performance, worth optimizing
- PROCEED_TO_VALIDATION: Strong performance, ready for validation
- ESCALATE_TO_HUMAN: Suspicious results (overfitting signals)

Usage:
    from decision_logic import evaluate_backtest

    decision, reason, details = evaluate_backtest(
        performance_metrics,
        thresholds
    )
"""

from typing import Dict, Tuple, Any


def evaluate_backtest(
    performance: Dict[str, float],
    thresholds: Dict[str, Any]
) -> Tuple[str, str, Dict[str, Any]]:
    """
    Evaluate backtest results and make autonomous routing decision.

    Args:
        performance: Dictionary with backtest metrics
            {
                "sharpe_ratio": float,
                "max_drawdown": float,
                "total_return": float,
                "total_trades": int,
                "win_rate": float,
                "loss_rate": float
            }

        thresholds: Dictionary with decision thresholds
            {
                "minimum_viable": {
                    "sharpe_ratio": 0.5,
                    "max_drawdown": 0.40,
                    "min_trades": 30
                },
                "optimization_worthy": {
                    "sharpe_ratio": 0.7,
                    "max_drawdown": 0.35,
                    "min_trades": 50
                },
                "production_ready": {
                    "sharpe_ratio": 1.0,
                    "max_drawdown": 0.30,
                    "min_trades": 100,
                    "win_rate": 0.40
                },
                "overfitting_signals": {
                    "too_perfect_sharpe": 3.0,
                    "too_few_trades": 20,
                    "win_rate_too_high": 0.75
                }
            }

    Returns:
        Tuple of (decision, reason, details):
            decision: str - One of:
                "ABANDON_HYPOTHESIS"
                "PROCEED_TO_OPTIMIZATION"
                "PROCEED_TO_VALIDATION"
                "ESCALATE_TO_HUMAN"
            reason: str - Human-readable explanation
            details: dict - Additional analysis details
    """
    # Extract metrics
    sharpe = performance.get("sharpe_ratio", 0.0)
    max_dd = performance.get("max_drawdown", 0.0)
    total_trades = performance.get("total_trades", 0)
    win_rate = performance.get("win_rate", 0.0)
    total_return = performance.get("total_return", 0.0)

    # Extract thresholds
    min_viable = thresholds.get("minimum_viable", {})
    opt_worthy = thresholds.get("optimization_worthy", {})
    prod_ready = thresholds.get("production_ready", {})
    overfit_signals = thresholds.get("overfitting_signals", {})

    # Initialize details
    details = {
        "sharpe_ratio": sharpe,
        "max_drawdown": max_dd,
        "total_trades": total_trades,
        "win_rate": win_rate,
        "total_return": total_return,
        "checks_performed": []
    }

    # TIER 1: Check overfitting signals (highest priority)
    details["checks_performed"].append("overfitting_signals")

    # Too perfect Sharpe (likely overfitting)
    too_perfect_sharpe = overfit_signals.get("too_perfect_sharpe", 3.0)
    if sharpe > too_perfect_sharpe:
        details["overfitting_detected"] = True
        details["overfitting_reason"] = f"Sharpe ratio too perfect ({sharpe:.2f} > {too_perfect_sharpe})"
        return (
            "ESCALATE_TO_HUMAN",
            f"Sharpe ratio too perfect ({sharpe:.2f} > {too_perfect_sharpe}), possible overfitting",
            details
        )

    # Too few trades (unreliable statistics)
    too_few_trades = overfit_signals.get("too_few_trades", 20)
    if 0 < total_trades < too_few_trades:
        details["overfitting_detected"] = True
        details["overfitting_reason"] = f"Too few trades ({total_trades} < {too_few_trades})"
        return (
            "ESCALATE_TO_HUMAN",
            f"Too few trades ({total_trades} < {too_few_trades}), unreliable statistics",
            details
        )

    # Win rate suspiciously high
    win_rate_too_high = overfit_signals.get("win_rate_too_high", 0.75)
    if win_rate > win_rate_too_high:
        details["overfitting_detected"] = True
        details["overfitting_reason"] = f"Win rate suspiciously high ({win_rate:.2%} > {win_rate_too_high:.0%})"
        return (
            "ESCALATE_TO_HUMAN",
            f"Win rate suspiciously high ({win_rate:.2%} > {win_rate_too_high:.0%}), possible overfitting",
            details
        )

    details["overfitting_detected"] = False

    # TIER 2: Check minimum viable thresholds (abandon if below)
    details["checks_performed"].append("minimum_viable")

    min_sharpe = min_viable.get("sharpe_ratio", 0.5)
    max_dd_threshold = min_viable.get("max_drawdown", 0.40)
    min_trades = min_viable.get("min_trades", 30)

    # Sharpe too low
    if sharpe < min_sharpe:
        details["abandon_reason"] = f"Sharpe below minimum viable ({sharpe:.2f} < {min_sharpe})"
        return (
            "ABANDON_HYPOTHESIS",
            f"Sharpe ratio below minimum viable ({sharpe:.2f} < {min_sharpe})",
            details
        )

    # Drawdown too high
    if max_dd > max_dd_threshold:
        details["abandon_reason"] = f"Max drawdown too high ({max_dd:.2%} > {max_dd_threshold:.0%})"
        return (
            "ABANDON_HYPOTHESIS",
            f"Max drawdown too high ({max_dd:.2%} > {max_dd_threshold:.0%})",
            details
        )

    # Insufficient trades
    if total_trades < min_trades:
        details["abandon_reason"] = f"Insufficient trades ({total_trades} < {min_trades})"
        return (
            "ABANDON_HYPOTHESIS",
            f"Insufficient trades for statistical significance ({total_trades} < {min_trades})",
            details
        )

    # TIER 3: Check production ready (can skip optimization)
    details["checks_performed"].append("production_ready")

    prod_sharpe = prod_ready.get("sharpe_ratio", 1.0)
    prod_dd = prod_ready.get("max_drawdown", 0.30)
    prod_trades = prod_ready.get("min_trades", 100)
    prod_win_rate = prod_ready.get("win_rate", 0.40)

    if (sharpe >= prod_sharpe and
        max_dd <= prod_dd and
        total_trades >= prod_trades and
        win_rate >= prod_win_rate):
        details["tier"] = "production_ready"
        details["skip_optimization"] = True
        return (
            "PROCEED_TO_VALIDATION",
            f"Strong baseline performance (Sharpe {sharpe:.2f}, DD {max_dd:.1%}, {total_trades} trades), ready for validation",
            details
        )

    # TIER 4: Check optimization worthy
    details["checks_performed"].append("optimization_worthy")

    opt_sharpe = opt_worthy.get("sharpe_ratio", 0.7)
    opt_dd = opt_worthy.get("max_drawdown", 0.35)
    opt_trades = opt_worthy.get("min_trades", 50)

    if (sharpe >= opt_sharpe and
        max_dd <= opt_dd and
        total_trades >= opt_trades):
        details["tier"] = "optimization_worthy"
        return (
            "PROCEED_TO_OPTIMIZATION",
            f"Decent performance (Sharpe {sharpe:.2f}, DD {max_dd:.1%}, {total_trades} trades), worth optimizing parameters",
            details
        )

    # TIER 5: Marginal case - between minimum viable and optimization worthy
    # Try optimization to see if we can improve
    if sharpe >= min_sharpe and total_trades >= min_trades:
        details["tier"] = "marginal"
        return (
            "PROCEED_TO_OPTIMIZATION",
            f"Marginal performance (Sharpe {sharpe:.2f}), attempting optimization to improve",
            details
        )

    # Fallback (should not reach here if thresholds are properly configured)
    details["abandon_reason"] = "Performance does not meet any criteria"
    return (
        "ABANDON_HYPOTHESIS",
        "Performance does not meet criteria for proceeding",
        details
    )


def evaluate_optimization(
    baseline_sharpe: float,
    optimized_sharpe: float,
    improvement_pct: float,
    thresholds: Dict[str, Any]
) -> Tuple[str, str, Dict[str, Any]]:
    """
    Evaluate optimization results and make routing decision.

    Args:
        baseline_sharpe: Sharpe ratio before optimization
        optimized_sharpe: Sharpe ratio after optimization
        improvement_pct: Percentage improvement (0.0 to 1.0)
        thresholds: Decision thresholds

    Returns:
        Tuple of (decision, reason, details)
    """
    details = {
        "baseline_sharpe": baseline_sharpe,
        "optimized_sharpe": optimized_sharpe,
        "improvement_pct": improvement_pct
    }

    # Check for performance degradation
    if improvement_pct < 0:
        details["degraded"] = True
        return (
            "USE_BASELINE_PARAMS",
            f"Optimization degraded performance ({improvement_pct:.1%}), use baseline parameters",
            details
        )

    # Check for minimal improvement (not worth it)
    if improvement_pct < 0.05:
        details["minimal_improvement"] = True
        return (
            "USE_BASELINE_PARAMS",
            f"Minimal improvement ({improvement_pct:.1%}), use baseline parameters",
            details
        )

    # Check for excessive improvement (overfitting risk)
    if improvement_pct > 0.30:
        details["overfitting_risk"] = True
        return (
            "ESCALATE_TO_HUMAN",
            f"Excessive improvement ({improvement_pct:.1%}), high overfitting risk - needs manual review",
            details
        )

    # Reasonable improvement - proceed to validation
    details["reasonable_improvement"] = True
    return (
        "PROCEED_TO_VALIDATION",
        f"Reasonable improvement ({improvement_pct:.1%}), proceed to out-of-sample validation",
        details
    )


def evaluate_validation(
    train_sharpe: float,
    test_sharpe: float,
    degradation_pct: float,
    robustness_score: float,
    thresholds: Dict[str, Any]
) -> Tuple[str, str, Dict[str, Any]]:
    """
    Evaluate walk-forward validation results and make deployment decision.

    Args:
        train_sharpe: Sharpe on training period
        test_sharpe: Sharpe on test period
        degradation_pct: Performance degradation (0.0 to 1.0)
        robustness_score: Overall robustness score (0.0 to 1.0)
        thresholds: Decision thresholds

    Returns:
        Tuple of (decision, reason, details)
    """
    details = {
        "train_sharpe": train_sharpe,
        "test_sharpe": test_sharpe,
        "degradation_pct": degradation_pct,
        "robustness_score": robustness_score
    }

    # Check for severe degradation
    if degradation_pct > 0.40:
        details["high_risk"] = True
        return (
            "ABANDON_HYPOTHESIS",
            f"Severe degradation in out-of-sample testing ({degradation_pct:.1%}), strategy not robust",
            details
        )

    # Check for low robustness score
    if robustness_score < 0.5:
        details["unstable"] = True
        return (
            "ABANDON_HYPOTHESIS",
            f"Low robustness score ({robustness_score:.2f}), strategy unstable across different periods",
            details
        )

    # Check for minimal degradation (very robust)
    if degradation_pct < 0.15 and robustness_score > 0.75:
        details["robust"] = True
        return (
            "DEPLOY_STRATEGY",
            f"Minimal degradation ({degradation_pct:.1%}), high robustness ({robustness_score:.2f}), ready for deployment",
            details
        )

    # Moderate degradation (proceed with caution)
    if degradation_pct < 0.30 and robustness_score > 0.60:
        details["moderate_risk"] = True
        return (
            "PROCEED_WITH_CAUTION",
            f"Moderate degradation ({degradation_pct:.1%}), robustness acceptable ({robustness_score:.2f}), monitor closely",
            details
        )

    # Borderline case - escalate for human judgment
    details["borderline"] = True
    return (
        "ESCALATE_TO_HUMAN",
        f"Borderline results (degradation {degradation_pct:.1%}, robustness {robustness_score:.2f}), needs human judgment",
        details
    )


if __name__ == "__main__":
    # Simple self-test
    print("=== Decision Logic Module Self-Test ===\n")

    # Default thresholds
    thresholds = {
        "minimum_viable": {
            "sharpe_ratio": 0.5,
            "max_drawdown": 0.40,
            "min_trades": 30
        },
        "optimization_worthy": {
            "sharpe_ratio": 0.7,
            "max_drawdown": 0.35,
            "min_trades": 50
        },
        "production_ready": {
            "sharpe_ratio": 1.0,
            "max_drawdown": 0.30,
            "min_trades": 100,
            "win_rate": 0.40
        },
        "overfitting_signals": {
            "too_perfect_sharpe": 3.0,
            "too_few_trades": 20,
            "win_rate_too_high": 0.75
        }
    }

    # Test cases
    test_cases = [
        {
            "name": "Zero trades (should ABANDON)",
            "performance": {
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "total_return": 0.0,
                "total_trades": 0,
                "win_rate": 0.0,
                "loss_rate": 0.0
            }
        },
        {
            "name": "Below minimum viable (should ABANDON)",
            "performance": {
                "sharpe_ratio": 0.3,
                "max_drawdown": 0.25,
                "total_return": 0.05,
                "total_trades": 50,
                "win_rate": 0.45,
                "loss_rate": 0.55
            }
        },
        {
            "name": "Optimization worthy (should PROCEED_TO_OPTIMIZATION)",
            "performance": {
                "sharpe_ratio": 0.85,
                "max_drawdown": 0.22,
                "total_return": 0.156,
                "total_trades": 67,
                "win_rate": 0.42,
                "loss_rate": 0.58
            }
        },
        {
            "name": "Production ready (should PROCEED_TO_VALIDATION)",
            "performance": {
                "sharpe_ratio": 1.45,
                "max_drawdown": 0.18,
                "total_return": 0.32,
                "total_trades": 120,
                "win_rate": 0.55,
                "loss_rate": 0.45
            }
        },
        {
            "name": "Overfitting - too perfect (should ESCALATE)",
            "performance": {
                "sharpe_ratio": 4.2,
                "max_drawdown": 0.05,
                "total_return": 0.80,
                "total_trades": 25,
                "win_rate": 0.88,
                "loss_rate": 0.12
            }
        },
        {
            "name": "Overfitting - too few trades (should ESCALATE)",
            "performance": {
                "sharpe_ratio": 1.8,
                "max_drawdown": 0.15,
                "total_return": 0.25,
                "total_trades": 12,
                "win_rate": 0.67,
                "loss_rate": 0.33
            }
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['name']}")
        decision, reason, details = evaluate_backtest(test["performance"], thresholds)
        print(f"  Decision: {decision}")
        print(f"  Reason: {reason}")
        print(f"  Overfitting detected: {details.get('overfitting_detected', False)}")
        print()

    print("✅ Self-test complete")
