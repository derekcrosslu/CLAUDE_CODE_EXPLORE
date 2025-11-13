#!/usr/bin/env python3
"""
QuantConnect Optimization Wrapper

Fully operational wrapper for parameter optimization using QC's native optimization API.
Integrates with the autonomous framework and applies decision framework.
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from qc_backtest import QuantConnectAPI


def load_optimization_config(config_file):
    """Load optimization configuration from JSON file"""
    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with open(config_path) as f:
        config = json.load(f)

    # Validate required fields
    required_fields = ['parameters', 'target', 'targetTo']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field '{field}' in config")

    return config


def load_iteration_state():
    """Load current iteration state"""
    state_file = Path("iteration_state.json")
    if not state_file.exists():
        raise FileNotFoundError("iteration_state.json not found. Run /qc-init first.")

    with open(state_file) as f:
        state = json.load(f)

    return state


def save_iteration_state(state):
    """Save updated iteration state"""
    with open("iteration_state.json", "w") as f:
        json.dump(state, f, indent=2)


def check_baseline_backtest(state):
    """Verify that a baseline backtest has been completed"""
    backtest_results = state.get('backtest_results', {})

    if not backtest_results:
        return False, "No baseline backtest found in iteration_state.json"

    if not backtest_results.get('completed'):
        return False, "Baseline backtest not completed"

    if not backtest_results.get('backtest_id'):
        return False, "No backtest_id in baseline results"

    return True, backtest_results


def run_optimization(api, project_id, config, baseline_sharpe=0.0):
    """
    Run parameter optimization using QC native API

    Args:
        api: QuantConnectAPI instance
        project_id: QC project ID
        config: Optimization configuration dict
        baseline_sharpe: Baseline Sharpe ratio for comparison

    Returns:
        dict: Optimization results with decision
    """
    print("\n" + "="*60)
    print("STARTING PARAMETER OPTIMIZATION")
    print("="*60)

    # Extract configuration
    parameters = config['parameters']
    target = config.get('target', 'TotalPerformance.PortfolioStatistics.SharpeRatio')
    target_to = config.get('targetTo', 'max')
    node_type = config.get('nodeType', 'O2-8')
    parallel_nodes = config.get('parallelNodes', 2)

    # Calculate number of combinations
    total_combinations = 1
    for param in parameters:
        param_min = float(param['min'])
        param_max = float(param['max'])
        param_step = float(param['step'])
        n_values = int((param_max - param_min) / param_step) + 1
        total_combinations *= n_values

    print(f"\nOptimization Configuration:")
    print(f"  Project ID: {project_id}")
    print(f"  Target: {target} ({target_to})")
    print(f"  Parameters: {len(parameters)}")
    print(f"  Total combinations: {total_combinations}")
    print(f"  Compute: {parallel_nodes} x {node_type}")

    # Estimate cost and time
    print(f"\n  Estimating optimization cost...")
    estimate = api.estimate_optimization(
        project_id=project_id,
        parameters=parameters,
        node_type=node_type,
        parallel_nodes=parallel_nodes
    )

    if estimate.get('success'):
        estimated_cost = estimate.get('estimatedCost', 'Unknown')
        print(f"  Estimated cost: ${estimated_cost}")
    else:
        print(f"  Warning: Could not estimate cost: {estimate.get('errors', 'Unknown error')}")

    # Create optimization
    opt_name = f"Optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\nCreating optimization: {opt_name}...")

    opt_result = api.create_optimization(
        project_id=project_id,
        name=opt_name,
        target=target,
        parameters=parameters,
        target_to=target_to,
        node_type=node_type,
        parallel_nodes=parallel_nodes
    )

    if not opt_result.get('success'):
        error_msg = opt_result.get('errors', ['Unknown error'])[0]
        raise RuntimeError(f"Failed to create optimization: {error_msg}")

    # Extract optimization ID
    optimizations = opt_result.get('optimizations', [])
    if not optimizations:
        raise RuntimeError("No optimization returned in response")

    optimization_id = optimizations[0].get('optimizationId')
    print(f"✓ Optimization created: {optimization_id}")
    print(f"\nWaiting for completion (this may take 10-30 minutes)...")

    # Wait for completion
    final_result = api.wait_for_optimization(optimization_id, timeout=1800, poll_interval=15)

    if not final_result.get('success'):
        raise RuntimeError(f"Optimization failed: {final_result.get('error', 'Unknown error')}")

    # Parse results
    optimization_data = final_result.get('optimization', {})

    # Extract best backtest results
    best_backtest_id = optimization_data.get('backtestId')
    best_sharpe = optimization_data.get('sharpeRatio', 0.0)

    # Get parameter set
    parameter_set = optimization_data.get('parameterSet', [])
    best_params = {}
    for param in parameter_set:
        best_params[param.get('name')] = param.get('value')

    print(f"\n" + "="*60)
    print("OPTIMIZATION COMPLETE")
    print("="*60)
    print(f"\n✓ Best Backtest ID: {best_backtest_id}")
    print(f"✓ Best Sharpe Ratio: {best_sharpe:.3f}")
    print(f"✓ Baseline Sharpe: {baseline_sharpe:.3f}")

    # Calculate improvement
    if baseline_sharpe > 0:
        improvement = (best_sharpe - baseline_sharpe) / baseline_sharpe
        print(f"✓ Improvement: {improvement*100:+.1f}%")
    else:
        improvement = 0.0
        print(f"✓ Improvement: N/A (baseline was 0)")

    print(f"\nBest Parameters:")
    for param_name, param_value in best_params.items():
        print(f"  {param_name}: {param_value}")

    return {
        'optimization_id': optimization_id,
        'best_backtest_id': best_backtest_id,
        'best_sharpe': best_sharpe,
        'baseline_sharpe': baseline_sharpe,
        'improvement': improvement,
        'best_parameters': best_params,
        'total_combinations': total_combinations,
        'raw_data': optimization_data
    }


def apply_decision_framework(results):
    """
    Apply autonomous decision framework to optimization results

    Args:
        results: Optimization results dict

    Returns:
        tuple: (decision, reason, recommendation)
    """
    improvement = results['improvement']
    best_sharpe = results['best_sharpe']

    print(f"\n" + "="*60)
    print("APPLYING DECISION FRAMEWORK")
    print("="*60)

    # Check for overfitting indicators
    if improvement > 0.30:
        decision = "ESCALATE"
        reason = f"Suspicious improvement ({improvement*100:.1f}%), possible overfitting"
        recommendation = "Review parameter sensitivity and consider out-of-sample validation"

    # Check if optimization found good parameters
    elif best_sharpe >= 1.0 and improvement > 0.05:
        decision = "PROCEED_TO_VALIDATION"
        reason = f"Good performance (Sharpe {best_sharpe:.2f}) with {improvement*100:.1f}% improvement"
        recommendation = "Run out-of-sample validation with /qc-validate"

    # Marginal improvement
    elif improvement > 0.05:
        decision = "PROCEED_TO_VALIDATION"
        reason = f"Moderate improvement ({improvement*100:.1f}%), validate OOS"
        recommendation = "Run out-of-sample validation with /qc-validate"

    # No improvement
    elif improvement <= 0.05 and improvement >= -0.05:
        decision = "USE_BASELINE_PARAMS"
        reason = f"Minimal change ({improvement*100:.1f}%), optimization didn't help"
        recommendation = "Use baseline parameters or try different parameter ranges"

    # Performance degraded
    else:
        decision = "REVIEW_PARAMETERS"
        reason = f"Performance degraded ({improvement*100:.1f}%)"
        recommendation = "Review parameter ranges and strategy logic"

    print(f"\nDecision: {decision}")
    print(f"Reason: {reason}")
    print(f"Recommendation: {recommendation}")

    return decision, reason, recommendation


def update_state_files(results, decision, reason):
    """Update iteration_state.json and decisions_log.md"""

    # Update iteration state
    state = load_iteration_state()

    state['optimization'] = {
        'status': 'completed',
        'optimization_id': results['optimization_id'],
        'best_backtest_id': results['best_backtest_id'],
        'best_parameters': results['best_parameters'],
        'best_sharpe': results['best_sharpe'],
        'baseline_sharpe': results['baseline_sharpe'],
        'improvement': results['improvement'],
        'decision': decision.lower().replace(' ', '_'),
        'reason': reason,
        'completed_at': datetime.now().isoformat()
    }

    state['current_phase'] = 'optimization_complete'

    save_iteration_state(state)

    # Append to decisions log
    log_entry = f"""
### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Optimization Complete

**Phase**: Optimization
**Optimization ID**: {results['optimization_id']}

**Results**:
- Best Backtest ID: {results['best_backtest_id']}
- Best Sharpe Ratio: {results['best_sharpe']:.3f}
- Baseline Sharpe: {results['baseline_sharpe']:.3f}
- Improvement: {results['improvement']*100:+.1f}%
- Combinations Tested: {results['total_combinations']}

**Best Parameters**:
"""
    for param_name, param_value in results['best_parameters'].items():
        log_entry += f"- {param_name}: {param_value}\n"

    log_entry += f"""
**Decision**: `{decision}`

**Reasoning**: {reason}

**Next Actions**: Run /qc-validate for out-of-sample validation

---

"""

    with open("decisions_log.md", "a") as f:
        f.write(log_entry)

    print(f"\n✓ Updated iteration_state.json")
    print(f"✓ Updated decisions_log.md")


def main():
    parser = argparse.ArgumentParser(description="QuantConnect Optimization Wrapper")
    parser.add_argument("--config", default="optimization_params.json",
                       help="Path to optimization configuration JSON")
    parser.add_argument("--output", help="Path to save detailed results JSON")

    args = parser.parse_args()

    try:
        # Load configuration
        config = load_optimization_config(args.config)

        # Load iteration state
        state = load_iteration_state()

        # Check for baseline backtest
        has_baseline, baseline_result = check_baseline_backtest(state)
        if not has_baseline:
            print(f"\n❌ ERROR: {baseline_result}")
            print("\nRun /qc-backtest first to establish baseline performance.")
            sys.exit(1)

        # Get project info
        project_id = state['project']['project_id']
        baseline_sharpe = baseline_result.get('performance', {}).get('sharpe_ratio', 0.0)

        # Initialize API
        api = QuantConnectAPI()

        # Run optimization
        results = run_optimization(api, project_id, config, baseline_sharpe)

        # Apply decision framework
        decision, reason, recommendation = apply_decision_framework(results)

        # Update state files
        update_state_files(results, decision, reason)

        # Save detailed results if requested
        if args.output:
            output_data = {
                **results,
                'decision': decision,
                'reason': reason,
                'recommendation': recommendation,
                'timestamp': datetime.now().isoformat()
            }

            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)

            print(f"✓ Detailed results saved to: {args.output}")

        print(f"\n" + "="*60)
        print("OPTIMIZATION WORKFLOW COMPLETE")
        print("="*60)
        print(f"\n✅ {decision}")
        print(f"📝 {recommendation}")

        sys.exit(0)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
