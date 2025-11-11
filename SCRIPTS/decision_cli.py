#!/usr/bin/env python3
"""
Decision Framework CLI for autonomous strategy development.

Usage:
    decision evaluate-backtest --results backtest.json --state iteration_state.json
    decision evaluate-optimization --results optimization.json --state iteration_state.json
    decision evaluate-validation --results validation.json --state iteration_state.json
    decision route --phase backtest --decision PROCEED_TO_OPTIMIZATION --iteration 1

Progressive Disclosure Pattern (Beyond MCP):
- Load only the evaluation logic you need (backtest vs optimization vs validation)
- CLI works for humans, teams, AND agents (trifecta)
- 87.5% context reduction vs loading all decision skills
"""

import click
import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

# Absolute path resolution (Beyond MCP pattern)
SCRIPT_DIR = Path(__file__).resolve().parent


def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON file with error handling."""
    try:
        with open(file_path) as f:
            return json.load(f)
    except FileNotFoundError:
        click.echo(f"❌ Error: {file_path} not found", err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"❌ Error: Invalid JSON in {file_path}: {e}", err=True)
        sys.exit(1)


@click.group()
def cli():
    """Decision framework CLI for autonomous strategy development.

    Evaluate results and route to next phase with progressive disclosure.
    """
    pass


@cli.command()
@click.option('--results', required=True, help='Path to backtest results JSON')
@click.option('--state', default='iteration_state.json', help='Path to iteration state JSON')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def evaluate_backtest(results: str, state: str, output_json: bool):
    """Evaluate backtest results and make Phase 3 decision.

    Decision outputs:
    - PROCEED_TO_OPTIMIZATION: Good performance, can be improved
    - PROCEED_TO_VALIDATION: Excellent performance, skip optimization
    - ABANDON_HYPOTHESIS: Poor performance or too few trades
    - ESCALATE_TO_HUMAN: Overfitting signals or unclear situation
    - FIX_BUG: Runtime error detected

    Examples:
        decision evaluate-backtest --results PROJECT_LOGS/backtest_result.json --state iteration_state.json
        decision evaluate-backtest --results backtest.json --json
    """
    # Load data
    backtest_results = load_json(results)
    iteration_state = load_json(state)

    # Get thresholds
    thresholds = iteration_state.get('thresholds', {})
    perf_criteria = thresholds.get('performance_criteria', {})
    overfit_signals = thresholds.get('overfitting_signals', {})

    # Check for technical failures
    if backtest_results.get('status') == 'error':
        decision = 'ESCALATE_TO_HUMAN'
        reason = f"Backtest failed: {backtest_results.get('error', 'Unknown error')}"
        details = {'error_type': 'technical_failure'}

        output_decision(decision, reason, details, output_json)
        return

    # Extract metrics
    sharpe = backtest_results.get('sharpe_ratio', 0.0)
    drawdown = abs(backtest_results.get('max_drawdown', 1.0))
    num_trades = backtest_results.get('total_trades', 0)
    win_rate = backtest_results.get('win_rate', 0.0)

    # Check for overfitting signals
    if sharpe > overfit_signals.get('too_perfect_sharpe', 3.0):
        decision = 'ESCALATE_TO_HUMAN'
        reason = f"OVERFITTING ALERT: Sharpe {sharpe:.2f} is suspiciously high (>{overfit_signals.get('too_perfect_sharpe', 3.0)})"
        details = {'overfitting_signal': 'too_perfect_sharpe', 'sharpe': sharpe}
        output_decision(decision, reason, details, output_json)
        return

    if num_trades < overfit_signals.get('too_few_trades', 10):
        decision = 'ABANDON_HYPOTHESIS'
        reason = f"Too few trades ({num_trades} < {overfit_signals.get('too_few_trades', 10)}). Insufficient sample size."
        details = {'overfitting_signal': 'too_few_trades', 'num_trades': num_trades}
        output_decision(decision, reason, details, output_json)
        return

    if win_rate > overfit_signals.get('win_rate_too_high', 0.80):
        decision = 'ESCALATE_TO_HUMAN'
        reason = f"OVERFITTING ALERT: Win rate {win_rate:.1%} is suspiciously high"
        details = {'overfitting_signal': 'win_rate_too_high', 'win_rate': win_rate}
        output_decision(decision, reason, details, output_json)
        return

    # Performance categorization
    min_viable = perf_criteria.get('minimum_viable', {})
    opt_worthy = perf_criteria.get('optimization_worthy', {})
    prod_ready = perf_criteria.get('production_ready', {})

    meets_minimum = (
        sharpe >= min_viable.get('sharpe_ratio', 0.5) and
        drawdown <= min_viable.get('max_drawdown', 0.35) and
        num_trades >= min_viable.get('min_trades', 20)
    )

    meets_optimization = (
        sharpe >= opt_worthy.get('sharpe_ratio', 0.7) and
        drawdown <= opt_worthy.get('max_drawdown', 0.30) and
        num_trades >= opt_worthy.get('min_trades', 30)
    )

    meets_production = (
        sharpe >= prod_ready.get('sharpe_ratio', 1.0) and
        drawdown <= prod_ready.get('max_drawdown', 0.20) and
        num_trades >= prod_ready.get('min_trades', 50)
    )

    # Decision logic
    if meets_production:
        decision = 'PROCEED_TO_VALIDATION'
        reason = f"Excellent performance: Sharpe={sharpe:.2f}, DD={drawdown:.1%}, Trades={num_trades}. Skip optimization."
        details = {
            'performance_tier': 'production_ready',
            'sharpe': sharpe,
            'drawdown': drawdown,
            'num_trades': num_trades
        }

    elif meets_optimization:
        decision = 'PROCEED_TO_OPTIMIZATION'
        reason = f"Good performance (Sharpe={sharpe:.2f}), but can optimize. Parameters need tuning."
        details = {
            'performance_tier': 'optimization_worthy',
            'sharpe': sharpe,
            'drawdown': drawdown,
            'num_trades': num_trades
        }

    elif meets_minimum:
        decision = 'PROCEED_TO_VALIDATION'
        reason = f"Marginal performance (Sharpe={sharpe:.2f}). Skipping optimization, validate as-is."
        details = {
            'performance_tier': 'minimum_viable',
            'sharpe': sharpe,
            'drawdown': drawdown,
            'num_trades': num_trades
        }

    else:
        decision = 'ABANDON_HYPOTHESIS'
        reason = f"Poor performance: Sharpe={sharpe:.2f}, DD={drawdown:.1%}. Below minimum thresholds."
        details = {
            'performance_tier': 'below_minimum',
            'sharpe': sharpe,
            'drawdown': drawdown,
            'num_trades': num_trades,
            'minimum_required': min_viable
        }

    output_decision(decision, reason, details, output_json)


@cli.command()
@click.option('--results', required=True, help='Path to optimization results JSON')
@click.option('--state', default='iteration_state.json', help='Path to iteration state JSON')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def evaluate_optimization(results: str, state: str, output_json: bool):
    """Evaluate optimization results and make Phase 4 decision.

    Decision outputs:
    - PROCEED_TO_VALIDATION: Optimization improved performance reasonably
    - USE_BASELINE_PARAMS: Optimization yielded minimal improvement
    - ESCALATE_TO_HUMAN: Improvement suspiciously large (>30%)
    - PROCEED_WITH_ROBUST_PARAMS: High parameter sensitivity detected

    Examples:
        decision evaluate-optimization --results PROJECT_LOGS/optimization_result.json
        decision evaluate-optimization --results opt.json --json
    """
    # Load data
    opt_results = load_json(results)
    iteration_state = load_json(state)

    # Get baseline results
    baseline_sharpe = iteration_state.get('phase_results', {}).get('backtest', {}).get('sharpe_ratio', 0.0)

    # Get best optimization result
    best_sharpe = opt_results.get('best_sharpe', 0.0)
    best_params = opt_results.get('best_parameters', {})

    # Calculate improvement
    if baseline_sharpe > 0:
        improvement = (best_sharpe - baseline_sharpe) / baseline_sharpe
    else:
        improvement = 0.0

    # Check parameter sensitivity (if available)
    parameter_sensitivity = opt_results.get('parameter_sensitivity', 0.0)

    # Decision logic
    if parameter_sensitivity > 0.5:
        decision = 'PROCEED_WITH_ROBUST_PARAMS'
        reason = f"High parameter sensitivity ({parameter_sensitivity:.2f}). Using robust parameters (median of top 25%)."
        details = {
            'improvement': improvement,
            'baseline_sharpe': baseline_sharpe,
            'best_sharpe': best_sharpe,
            'sensitivity': parameter_sensitivity,
            'warning': 'fragile_parameters'
        }

    elif improvement < 0.05:  # Less than 5% improvement
        decision = 'USE_BASELINE_PARAMS'
        reason = f"Optimization yielded minimal improvement ({improvement*100:.1f}%). Proceeding with baseline parameters."
        details = {
            'improvement': improvement,
            'baseline_sharpe': baseline_sharpe,
            'best_sharpe': best_sharpe
        }

    elif improvement > 0.30:  # More than 30% improvement - suspicious
        decision = 'ESCALATE_TO_HUMAN'
        reason = f"Optimization yielded suspiciously large improvement ({improvement*100:.1f}%). Manual review recommended."
        details = {
            'improvement': improvement,
            'baseline_sharpe': baseline_sharpe,
            'best_sharpe': best_sharpe,
            'warning': 'suspicious_improvement'
        }

    else:  # Reasonable improvement (5-30%)
        decision = 'PROCEED_TO_VALIDATION'
        reason = f"Optimization improved performance by {improvement*100:.1f}%. Using optimized parameters."
        details = {
            'improvement': improvement,
            'baseline_sharpe': baseline_sharpe,
            'best_sharpe': best_sharpe,
            'best_parameters': best_params
        }

    output_decision(decision, reason, details, output_json)


@cli.command()
@click.option('--results', required=True, help='Path to validation results JSON')
@click.option('--state', default='iteration_state.json', help='Path to iteration state JSON')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def evaluate_validation(results: str, state: str, output_json: bool):
    """Evaluate validation results and make Phase 5 decision.

    Decision outputs:
    - DEPLOY_STRATEGY: Minimal degradation, ready for production
    - PROCEED_WITH_CAUTION: Moderate degradation, deploy with monitoring
    - ABANDON_HYPOTHESIS: Severe degradation, strategy overfit
    - ESCALATE_TO_HUMAN: Borderline results, human judgment needed

    Examples:
        decision evaluate-validation --results PROJECT_LOGS/validation_result.json
        decision evaluate-validation --results val.json --json
    """
    # Load data
    val_results = load_json(results)
    iteration_state = load_json(state)

    # Get thresholds
    thresholds = iteration_state.get('thresholds', {})
    perf_criteria = thresholds.get('performance_criteria', {})

    # Extract metrics
    in_sample_sharpe = val_results.get('in_sample', {}).get('sharpe_ratio', 0.0)
    out_of_sample_sharpe = val_results.get('out_of_sample', {}).get('sharpe_ratio', 0.0)
    degradation_pct = val_results.get('degradation_pct', 1.0)  # Precomputed or calculate
    robustness_score = val_results.get('robustness_score', 0.0)  # OOS/IS ratio

    # Calculate degradation if not provided
    if in_sample_sharpe > 0:
        calc_degradation = (in_sample_sharpe - out_of_sample_sharpe) / in_sample_sharpe
        if degradation_pct == 1.0:  # Not provided
            degradation_pct = calc_degradation
        calc_robustness = out_of_sample_sharpe / in_sample_sharpe
        if robustness_score == 0.0:  # Not provided
            robustness_score = calc_robustness

    # Check OOS meets minimum criteria
    min_viable = perf_criteria.get('minimum_viable', {})
    oos_meets_minimum = (
        out_of_sample_sharpe >= min_viable.get('sharpe_ratio', 0.5) and
        abs(val_results.get('out_of_sample', {}).get('max_drawdown', 1.0)) <= min_viable.get('max_drawdown', 0.35)
    )

    # Decision logic
    if degradation_pct > 0.40:  # More than 40% degradation
        decision = 'ABANDON_HYPOTHESIS'
        reason = f"OVERFITTING DETECTED: Out-of-sample Sharpe degraded by {degradation_pct*100:.1f}%. Strategy does not generalize."
        details = {
            'in_sample_sharpe': in_sample_sharpe,
            'out_of_sample_sharpe': out_of_sample_sharpe,
            'degradation_pct': degradation_pct,
            'robustness_score': robustness_score
        }

    elif degradation_pct > 0.30:  # 30-40% degradation
        if oos_meets_minimum:
            decision = 'ESCALATE_TO_HUMAN'
            reason = f"Significant degradation ({degradation_pct*100:.1f}%), but OOS meets minimum. Human review needed."
            details = {
                'in_sample_sharpe': in_sample_sharpe,
                'out_of_sample_sharpe': out_of_sample_sharpe,
                'degradation_pct': degradation_pct,
                'robustness_score': robustness_score,
                'oos_meets_minimum': True
            }
        else:
            decision = 'ABANDON_HYPOTHESIS'
            reason = f"Significant degradation ({degradation_pct*100:.1f}%) and OOS below minimum criteria."
            details = {
                'in_sample_sharpe': in_sample_sharpe,
                'out_of_sample_sharpe': out_of_sample_sharpe,
                'degradation_pct': degradation_pct,
                'robustness_score': robustness_score,
                'oos_meets_minimum': False
            }

    elif degradation_pct > 0.15:  # 15-30% degradation
        decision = 'PROCEED_WITH_CAUTION'
        reason = f"Moderate degradation ({degradation_pct*100:.1f}%). Deploy but monitor closely."
        details = {
            'in_sample_sharpe': in_sample_sharpe,
            'out_of_sample_sharpe': out_of_sample_sharpe,
            'degradation_pct': degradation_pct,
            'robustness_score': robustness_score
        }

    else:  # Less than 15% degradation - excellent generalization
        prod_ready_sharpe = perf_criteria.get('production_ready', {}).get('sharpe_ratio', 1.0)

        if out_of_sample_sharpe >= prod_ready_sharpe:
            decision = 'DEPLOY_STRATEGY'
            reason = f"Excellent validation: {degradation_pct*100:.1f}% degradation, OOS Sharpe={out_of_sample_sharpe:.2f}. Ready for production!"
            details = {
                'in_sample_sharpe': in_sample_sharpe,
                'out_of_sample_sharpe': out_of_sample_sharpe,
                'degradation_pct': degradation_pct,
                'robustness_score': robustness_score,
                'production_ready': True
            }
        else:
            decision = 'PROCEED_WITH_CAUTION'
            reason = f"Good validation ({degradation_pct*100:.1f}% degradation), but OOS Sharpe below production criteria."
            details = {
                'in_sample_sharpe': in_sample_sharpe,
                'out_of_sample_sharpe': out_of_sample_sharpe,
                'degradation_pct': degradation_pct,
                'robustness_score': robustness_score,
                'production_ready': False
            }

    output_decision(decision, reason, details, output_json)


@cli.command()
@click.option('--phase', required=True, type=click.Choice(['backtest', 'optimization', 'validation']), help='Current phase')
@click.option('--decision', required=True, help='Decision from evaluate-* command')
@click.option('--iteration', type=int, default=1, help='Current iteration number')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def route(phase: str, decision: str, iteration: int, output_json: bool):
    """Route to next phase based on current phase and decision.

    Examples:
        decision route --phase backtest --decision PROCEED_TO_OPTIMIZATION --iteration 1
        decision route --phase validation --decision DEPLOY_STRATEGY --iteration 1 --json
    """
    routing = {}

    # Backtest phase routing
    if phase == 'backtest':
        if decision == 'PROCEED_TO_OPTIMIZATION':
            routing = {
                'next_phase': 'optimization',
                'next_action': 'Run parameter optimization',
                'update_state': {'current_phase': 'optimization'}
            }
        elif decision == 'PROCEED_TO_VALIDATION':
            routing = {
                'next_phase': 'validation',
                'next_action': 'Run walk-forward validation',
                'update_state': {'current_phase': 'validation'}
            }
        elif decision == 'ABANDON_HYPOTHESIS':
            routing = {
                'next_phase': 'research',
                'next_action': 'Select next hypothesis or generate new ones',
                'update_state': {
                    'current_phase': 'research',
                    'iteration': iteration + 1,
                    'hypothesis_status': 'abandoned'
                }
            }
        elif decision == 'ESCALATE_TO_HUMAN':
            routing = {
                'next_phase': 'paused',
                'next_action': 'Request human guidance',
                'update_state': {'current_phase': 'awaiting_human'}
            }
        else:
            routing = {
                'error': f'Unknown decision: {decision} for phase: {phase}'
            }

    # Optimization phase routing
    elif phase == 'optimization':
        if decision in ['PROCEED_TO_VALIDATION', 'USE_BASELINE_PARAMS', 'PROCEED_WITH_ROBUST_PARAMS']:
            routing = {
                'next_phase': 'validation',
                'next_action': 'Run walk-forward validation',
                'update_state': {'current_phase': 'validation'},
                'use_optimized_params': decision != 'USE_BASELINE_PARAMS'
            }
        elif decision == 'ESCALATE_TO_HUMAN':
            routing = {
                'next_phase': 'paused',
                'next_action': 'Request human guidance on optimization results',
                'update_state': {'current_phase': 'awaiting_human'}
            }
        else:
            routing = {
                'error': f'Unknown decision: {decision} for phase: {phase}'
            }

    # Validation phase routing
    elif phase == 'validation':
        if decision in ['DEPLOY_STRATEGY', 'PROCEED_WITH_CAUTION']:
            routing = {
                'next_phase': 'deployed',
                'next_action': 'Document strategy and prepare for deployment',
                'update_state': {
                    'current_phase': 'deployed',
                    'deployment_status': 'ready' if decision == 'DEPLOY_STRATEGY' else 'caution'
                }
            }
        elif decision == 'ABANDON_HYPOTHESIS':
            routing = {
                'next_phase': 'research',
                'next_action': 'Select next hypothesis',
                'update_state': {
                    'current_phase': 'research',
                    'iteration': iteration + 1,
                    'hypothesis_status': 'failed_validation'
                }
            }
        elif decision == 'ESCALATE_TO_HUMAN':
            routing = {
                'next_phase': 'paused',
                'next_action': 'Request human guidance on validation results',
                'update_state': {'current_phase': 'awaiting_human'}
            }
        else:
            routing = {
                'error': f'Unknown decision: {decision} for phase: {phase}'
            }

    # Output routing
    if output_json:
        click.echo(json.dumps(routing, indent=2))
    else:
        if 'error' in routing:
            click.echo(f"❌ {routing['error']}", err=True)
            sys.exit(1)
        else:
            click.echo(f"🔀 Routing Decision:")
            click.echo(f"   Current Phase: {phase}")
            click.echo(f"   Decision: {decision}")
            click.echo(f"   Next Phase: {routing['next_phase']}")
            click.echo(f"   Next Action: {routing['next_action']}")


def output_decision(decision: str, reason: str, details: Dict[str, Any], output_json: bool):
    """Output decision in human-readable or JSON format."""
    if output_json:
        result = {
            'decision': decision,
            'reason': reason,
            'details': details
        }
        click.echo(json.dumps(result, indent=2))
    else:
        # Emoji based on decision
        emoji_map = {
            'PROCEED_TO_OPTIMIZATION': '🔧',
            'PROCEED_TO_VALIDATION': '✅',
            'ABANDON_HYPOTHESIS': '❌',
            'ESCALATE_TO_HUMAN': '👤',
            'USE_BASELINE_PARAMS': '📊',
            'PROCEED_WITH_ROBUST_PARAMS': '🛡️',
            'DEPLOY_STRATEGY': '🚀',
            'PROCEED_WITH_CAUTION': '⚠️'
        }
        emoji = emoji_map.get(decision, '🤖')

        click.echo(f"{emoji} Decision: {decision}")
        click.echo(f"   Reason: {reason}")

        # Show key metrics from details
        if 'sharpe' in details:
            click.echo(f"   Sharpe Ratio: {details['sharpe']:.2f}")
        if 'drawdown' in details:
            click.echo(f"   Max Drawdown: {details['drawdown']:.1%}")
        if 'num_trades' in details:
            click.echo(f"   Total Trades: {details['num_trades']}")
        if 'improvement' in details:
            click.echo(f"   Improvement: {details['improvement']*100:.1f}%")
        if 'degradation_pct' in details:
            click.echo(f"   Degradation: {details['degradation_pct']*100:.1f}%")


if __name__ == '__main__':
    cli()
