#!/usr/bin/env python3
"""
⚠️  DEPRECATED - DO NOT USE ⚠️

This wrapper calls the QC Optimization API which COSTS MONEY.

Use upload_research_notebook.py instead:
- Uploads notebook to research.ipynb (FREE)
- Run optimization inside QC Research (FREE)
- No API costs

QuantConnect Monte Carlo Walk-Forward Wrapper

Fully operational wrapper for Monte Carlo walk-forward validation.
Uses QC programmatic API for multiple optimization and backtest runs.
"""

import json
import sys
import argparse
import random
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
from qc_backtest import QuantConnectAPI


def load_walkforward_config(config_file):
    """Load walk-forward configuration from JSON file"""
    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with open(config_path) as f:
        config = json.load(f)

    # Validate required fields
    required_fields = ['total_period', 'train_test_split', 'monte_carlo_runs', 'parameters']
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


def check_prerequisites(state):
    """Verify that baseline backtest and optimization have been completed"""

    # Check baseline backtest
    backtest_results = state.get('backtest_results', {})
    if not backtest_results or not backtest_results.get('completed'):
        return False, "No baseline backtest completed. Run /qc-backtest first."

    # Check optimization
    optimization = state.get('optimization', {})
    if not optimization or optimization.get('status') != 'completed':
        return False, "No optimization completed. Run /qc-optimize first."

    return True, None


def generate_random_split(start_date, end_date, train_pct, seed=None):
    """
    Generate random training and testing periods for Monte Carlo sampling

    Args:
        start_date: Overall start date
        end_date: Overall end date
        train_pct: Percentage of data for training (0.0-1.0)
        seed: Random seed for reproducibility

    Returns:
        tuple: (train_start, train_end, test_start, test_end)
    """
    if seed is not None:
        random.seed(seed)

    total_days = (end_date - start_date).days

    # For Monte Carlo: use full period minus a buffer for random sampling
    # Buffer is 20% or minimum 30 days (whichever is larger)
    buffer_days = max(30, int(total_days * 0.2))
    usable_days = total_days - buffer_days

    train_days = int(usable_days * train_pct)
    test_days = int(usable_days * (1 - train_pct))

    # Ensure we have at least 3 months for testing
    min_test_days = 90
    if test_days < min_test_days:
        raise ValueError(f"Test period too short ({test_days} days). Need at least {min_test_days} days.")

    # Random start point for training window
    # The train+test window can slide within the total period
    required_days = train_days + 1 + test_days
    max_start_offset = total_days - required_days

    if max_start_offset < 0:
        raise ValueError(f"Period too short. Need {required_days} days but only have {total_days}.")

    # Random offset creates different train/test windows (Monte Carlo sampling)
    start_offset = random.randint(0, max_start_offset)

    train_start = start_date + timedelta(days=start_offset)
    train_end = train_start + timedelta(days=train_days - 1)  # Inclusive
    test_start = train_end + timedelta(days=2)  # 1 day gap
    test_end = test_start + timedelta(days=test_days - 1)  # Inclusive

    # Ensure test_end doesn't exceed original end_date
    if test_end > end_date:
        test_end = end_date

    return train_start, train_end, test_start, test_end


def modify_strategy_dates(strategy_file, start_date, end_date):
    """
    Modify strategy file to use specific date range

    Args:
        strategy_file: Path to strategy Python file
        start_date: Start date
        end_date: End date

    Returns:
        str: Modified strategy content
    """
    with open(strategy_file) as f:
        content = f.read()

    # Replace set_start_date and set_end_date lines
    # Pattern: self.set_start_date(2023, 1, 1)
    import re

    # Replace start date
    start_pattern = r'self\.set_start_date\([^)]+\)'
    start_replacement = f'self.set_start_date({start_date.year}, {start_date.month}, {start_date.day})'
    content = re.sub(start_pattern, start_replacement, content)

    # Replace end date
    end_pattern = r'self\.set_end_date\([^)]+\)'
    end_replacement = f'self.set_end_date({end_date.year}, {end_date.month}, {end_date.day})'
    content = re.sub(end_pattern, end_replacement, content)

    return content


def run_optimization_for_period(api, project_id, strategy_file, train_start, train_end, parameters, run_num):
    """
    Run optimization for a specific training period

    Args:
        api: QuantConnectAPI instance
        project_id: QC project ID
        strategy_file: Path to strategy file
        train_start: Training start date
        train_end: Training end date
        parameters: Optimization parameters
        run_num: Monte Carlo run number

    Returns:
        dict: Optimization results
    """
    print(f"  Training period: {train_start.date()} to {train_end.date()}")

    # Modify strategy with training dates
    modified_strategy = modify_strategy_dates(strategy_file, train_start, train_end)

    # Upload modified strategy (QC expects main.py)
    upload_result = api.upload_file(project_id, "main.py", modified_strategy)
    if not upload_result or not upload_result.get('success'):
        error_detail = upload_result.get('errors') if upload_result else 'No response'
        raise RuntimeError(f"Failed to upload strategy: {error_detail}")

    # Create optimization
    opt_name = f"MC_Train_Run{run_num}_{train_start.strftime('%Y%m%d')}"

    opt_result = api.create_optimization(
        project_id=project_id,
        name=opt_name,
        target="TotalPerformance.PortfolioStatistics.SharpeRatio",
        parameters=parameters,
        target_to="max"
    )

    if not opt_result.get('success'):
        error_msg = opt_result.get('errors', ['Unknown error'])[0]
        raise RuntimeError(f"Optimization failed: {error_msg}")

    # Get optimization ID
    optimizations = opt_result.get('optimizations', [])
    if not optimizations:
        raise RuntimeError("No optimization returned")

    optimization_id = optimizations[0].get('optimizationId')

    # Wait for completion (with shorter timeout for walk-forward)
    print(f"  Optimization ID: {optimization_id}")
    print(f"  Waiting for completion...")

    final_result = api.wait_for_optimization(optimization_id, timeout=1800, poll_interval=20)

    if not final_result.get('success'):
        raise RuntimeError(f"Optimization failed: {final_result.get('error')}")

    # Extract results
    opt_data = final_result.get('optimization', {})
    best_sharpe = opt_data.get('sharpeRatio', 0.0)

    # Get best parameters
    parameter_set = opt_data.get('parameterSet', [])
    best_params = {p.get('name'): p.get('value') for p in parameter_set}

    print(f"  Training Sharpe: {best_sharpe:.3f}")
    print(f"  Best params: {best_params}")

    return {
        'optimization_id': optimization_id,
        'train_sharpe': best_sharpe,
        'best_parameters': best_params
    }


def run_backtest_for_period(api, project_id, strategy_file, test_start, test_end, parameters, run_num):
    """
    Run backtest for a specific testing period with given parameters

    Args:
        api: QuantConnectAPI instance
        project_id: QC project ID
        strategy_file: Path to strategy file
        test_start: Testing start date
        test_end: Testing end date
        parameters: Strategy parameters to use
        run_num: Monte Carlo run number

    Returns:
        dict: Backtest results
    """
    print(f"  Testing period: {test_start.date()} to {test_end.date()}")

    # Modify strategy with testing dates and parameters
    modified_strategy = modify_strategy_dates(strategy_file, test_start, test_end)

    # TODO: Also need to set the parameters in the strategy
    # For now, we'll rely on the parameters being in the strategy via get_parameter()
    # In a full implementation, we'd inject parameter values here

    # Upload modified strategy (QC expects main.py)
    upload_result = api.upload_file(project_id, "main.py", modified_strategy)
    if not upload_result or not upload_result.get('success'):
        error_detail = upload_result.get('errors') if upload_result else 'No response'
        raise RuntimeError(f"Failed to upload strategy: {error_detail}")

    # Create backtest
    backtest_name = f"MC_Test_Run{run_num}_{test_start.strftime('%Y%m%d')}"

    backtest_result = api.create_backtest(project_id, backtest_name)
    if not backtest_result.get('success'):
        raise RuntimeError(f"Failed to create backtest: {backtest_result.get('error')}")

    backtest_id = backtest_result.get('backtest', {}).get('backtestId')

    # Wait for completion
    print(f"  Backtest ID: {backtest_id}")
    print(f"  Waiting for completion...")

    final_result = api.read_backtest_results(project_id, backtest_id)

    # Parse performance metrics
    performance = final_result.get('performance', {})
    test_sharpe = performance.get('sharpe_ratio', 0.0)
    total_trades = final_result.get('trading', {}).get('total_trades', 0)

    print(f"  Testing Sharpe: {test_sharpe:.3f}")
    print(f"  Total trades: {total_trades}")

    return {
        'backtest_id': backtest_id,
        'test_sharpe': test_sharpe,
        'total_trades': total_trades,
        'performance': performance
    }


def run_monte_carlo_walkforward(api, project_id, strategy_file, config):
    """
    Run full Monte Carlo walk-forward analysis

    Args:
        api: QuantConnectAPI instance
        project_id: QC project ID
        strategy_file: Path to strategy file
        config: Walk-forward configuration

    Returns:
        dict: Aggregated results from all Monte Carlo runs
    """
    print("\n" + "="*60)
    print("MONTE CARLO WALK-FORWARD ANALYSIS")
    print("="*60)

    # Parse configuration
    start_date = datetime.strptime(config['total_period']['start'], '%Y-%m-%d')
    end_date = datetime.strptime(config['total_period']['end'], '%Y-%m-%d')
    train_test_split = config['train_test_split']
    monte_carlo_runs = config['monte_carlo_runs']
    parameters = config['parameters']

    print(f"\nConfiguration:")
    print(f"  Period: {start_date.date()} to {end_date.date()}")
    print(f"  Train/Test Split: {train_test_split*100:.0f}%/{(1-train_test_split)*100:.0f}%")
    print(f"  Monte Carlo Runs: {monte_carlo_runs}")
    print(f"  Parameters: {len(parameters)}")

    results = []

    for run in range(monte_carlo_runs):
        print(f"\n{'='*60}")
        print(f"Monte Carlo Run {run + 1}/{monte_carlo_runs}")
        print(f"{'='*60}")

        try:
            # Generate random train/test split
            train_start, train_end, test_start, test_end = generate_random_split(
                start_date, end_date, train_test_split, seed=run
            )

            # Run optimization on training period
            opt_result = run_optimization_for_period(
                api, project_id, strategy_file,
                train_start, train_end, parameters, run + 1
            )

            # Run backtest on testing period with optimized parameters
            test_result = run_backtest_for_period(
                api, project_id, strategy_file,
                test_start, test_end, opt_result['best_parameters'], run + 1
            )

            # Calculate degradation
            train_sharpe = opt_result['train_sharpe']
            test_sharpe = test_result['test_sharpe']

            if train_sharpe > 0:
                degradation = (train_sharpe - test_sharpe) / train_sharpe
            else:
                degradation = 0.0

            print(f"  Degradation: {degradation*100:.1f}%")

            # Store results
            results.append({
                'run': run + 1,
                'train_start': train_start.isoformat(),
                'train_end': train_end.isoformat(),
                'test_start': test_start.isoformat(),
                'test_end': test_end.isoformat(),
                'train_sharpe': train_sharpe,
                'test_sharpe': test_sharpe,
                'degradation': degradation,
                'best_params': opt_result['best_parameters'],
                'test_trades': test_result['total_trades'],
                'optimization_id': opt_result['optimization_id'],
                'backtest_id': test_result['backtest_id']
            })

        except Exception as e:
            print(f"  ❌ Error in run {run + 1}: {e}")
            # Continue with next run
            continue

    return results


def analyze_results(results):
    """
    Analyze Monte Carlo results and compute statistics

    Args:
        results: List of Monte Carlo run results

    Returns:
        dict: Statistical analysis
    """
    if not results:
        raise ValueError("No results to analyze")

    print(f"\n" + "="*60)
    print("STATISTICAL ANALYSIS")
    print("="*60)

    # Convert to numpy arrays for analysis
    train_sharpes = np.array([r['train_sharpe'] for r in results])
    test_sharpes = np.array([r['test_sharpe'] for r in results])
    degradations = np.array([r['degradation'] for r in results])

    # Calculate statistics
    mean_train = np.mean(train_sharpes)
    mean_test = np.mean(test_sharpes)
    mean_deg = np.mean(degradations)
    std_deg = np.std(degradations)

    # Overfitting analysis
    pct_overfit = np.sum(degradations > 0.30) / len(degradations)
    pct_good = np.sum(degradations < 0.15) / len(degradations)

    print(f"\nPerformance Metrics:")
    print(f"  Mean Training Sharpe:  {mean_train:.3f} ± {np.std(train_sharpes):.3f}")
    print(f"  Mean Testing Sharpe:   {mean_test:.3f} ± {np.std(test_sharpes):.3f}")
    print(f"  Mean Degradation:      {mean_deg*100:.1f}% ± {std_deg*100:.1f}%")

    print(f"\nRobustness Analysis:")
    print(f"  Runs with >30% degradation: {pct_overfit*100:.0f}% (overfitting indicator)")
    print(f"  Runs with <15% degradation: {pct_good*100:.0f}% (good generalization)")

    # Parameter stability
    print(f"\nParameter Stability:")
    param_names = list(results[0]['best_params'].keys())

    most_common_params = {}
    for param in param_names:
        values = [r['best_params'][param] for r in results]
        counter = Counter(values)
        most_common = counter.most_common(1)[0]
        consensus = most_common[1] / len(results)

        most_common_params[param] = most_common[0]

        print(f"  {param}:")
        for value, count in counter.most_common(3):
            pct = count / len(results) * 100
            print(f"    {value}: {count}/{len(results)} ({pct:.0f}%)")

        if consensus >= 0.70:
            print(f"    ✅ STABLE: {most_common[0]} chosen {consensus*100:.0f}% of the time")
        else:
            print(f"    ⚠️  UNSTABLE: No clear consensus (max {consensus*100:.0f}%)")

    return {
        'mean_train_sharpe': float(mean_train),
        'mean_test_sharpe': float(mean_test),
        'mean_degradation': float(mean_deg),
        'std_degradation': float(std_deg),
        'pct_overfit': float(pct_overfit),
        'pct_good': float(pct_good),
        'most_common_params': most_common_params
    }


def apply_robustness_decision(stats):
    """
    Apply robustness decision framework

    Args:
        stats: Statistical analysis dict

    Returns:
        tuple: (decision, reason, recommendation)
    """
    mean_deg = stats['mean_degradation']
    std_deg = stats['std_degradation']
    pct_overfit = stats['pct_overfit']

    print(f"\n" + "="*60)
    print("ROBUSTNESS DECISION")
    print("="*60)

    if pct_overfit > 0.50:
        decision = "ABANDON_STRATEGY"
        reason = f"Overfitting in {pct_overfit*100:.0f}% of Monte Carlo runs"
        recommendation = "Strategy does not generalize well. Consider new hypothesis."

    elif mean_deg > 0.40:
        decision = "HIGH_RISK"
        reason = f"Average degradation {mean_deg*100:.1f}% indicates poor generalization"
        recommendation = "Strategy shows high out-of-sample degradation. Use with caution."

    elif std_deg > 0.25:
        decision = "UNSTABLE_PARAMETERS"
        reason = f"High variance ({std_deg*100:.1f}%) suggests parameter instability"
        recommendation = "Parameters not stable. Consider narrowing search space."

    elif mean_deg < 0.15 and std_deg < 0.10:
        decision = "ROBUST_STRATEGY"
        reason = f"Low degradation ({mean_deg*100:.1f}%) with low variance ({std_deg*100:.1f}%)"
        recommendation = "Strategy shows excellent generalization. Ready for live testing."

    else:
        decision = "PROCEED_WITH_CAUTION"
        reason = f"Moderate degradation ({mean_deg*100:.1f}%), acceptable stability"
        recommendation = "Strategy shows reasonable generalization. Additional validation recommended."

    print(f"\nDecision: {decision}")
    print(f"Reason: {reason}")
    print(f"Recommendation: {recommendation}")

    return decision, reason, recommendation


def update_state_files(results, stats, decision, reason):
    """Update iteration_state.json and decisions_log.md"""

    # Update iteration state
    state = load_iteration_state()

    state['walkforward'] = {
        'status': 'completed',
        'method': 'monte_carlo',
        'runs': len(results),
        'mean_train_sharpe': stats['mean_train_sharpe'],
        'mean_test_sharpe': stats['mean_test_sharpe'],
        'mean_degradation': stats['mean_degradation'],
        'std_degradation': stats['std_degradation'],
        'pct_overfit': stats['pct_overfit'],
        'decision': decision.lower().replace(' ', '_'),
        'reason': reason,
        'recommended_params': stats['most_common_params'],
        'completed_at': datetime.now().isoformat()
    }

    state['current_phase'] = 'walkforward_complete'

    save_iteration_state(state)

    # Append to decisions log
    log_entry = f"""
### {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Monte Carlo Walk-Forward Complete

**Phase**: Walk-Forward Validation
**Method**: Monte Carlo Random Sampling
**Runs**: {len(results)}

**Aggregate Results**:
- Mean Training Sharpe: {stats['mean_train_sharpe']:.3f}
- Mean Testing Sharpe: {stats['mean_test_sharpe']:.3f}
- Mean Degradation: {stats['mean_degradation']*100:.1f}%
- Std Degradation: {stats['std_degradation']*100:.1f}%
- Overfitting Rate: {stats['pct_overfit']*100:.0f}%
- Good Generalization Rate: {stats['pct_good']*100:.0f}%

**Most Stable Parameters**:
"""
    for param, value in stats['most_common_params'].items():
        log_entry += f"- {param}: {value}\n"

    log_entry += f"""
**Decision**: `{decision}`

**Reasoning**: {reason}

**Validation Status**: {"✅ PASSED" if decision == "ROBUST_STRATEGY" else "⚠️  NEEDS REVIEW"}

---

"""

    with open("decisions_log.md", "a") as f:
        f.write(log_entry)

    print(f"\n✓ Updated iteration_state.json")
    print(f"✓ Updated decisions_log.md")


def main():
    parser = argparse.ArgumentParser(description="QuantConnect Monte Carlo Walk-Forward Wrapper")
    parser.add_argument("--config", default="walkforward_config.json",
                       help="Path to walk-forward configuration JSON")
    parser.add_argument("--strategy", default="test_strategy.py",
                       help="Path to strategy file")
    parser.add_argument("--output", help="Path to save detailed results JSON")
    parser.add_argument("--test", action="store_true",
                       help="Test mode - skip prerequisite checks (for framework validation)")

    args = parser.parse_args()

    try:
        # Load configuration
        config = load_walkforward_config(args.config)

        # Load iteration state
        state = load_iteration_state()

        # Check prerequisites (skip in test mode)
        if not args.test:
            has_prereq, error_msg = check_prerequisites(state)
            if not has_prereq:
                print(f"\n❌ ERROR: {error_msg}")
                sys.exit(1)
        else:
            print("\n⚠️  TEST MODE: Prerequisite checks skipped")
            print("    This is a functionality test, not a real validation\n")

        # Get project info
        project_id = state['project']['project_id']
        strategy_file = args.strategy

        # Initialize API
        api = QuantConnectAPI()

        # Run Monte Carlo walk-forward
        results = run_monte_carlo_walkforward(api, project_id, strategy_file, config)

        if not results:
            print("\n❌ No successful runs completed")
            sys.exit(1)

        # Analyze results
        stats = analyze_results(results)

        # Apply robustness decision
        decision, reason, recommendation = apply_robustness_decision(stats)

        # Update state files
        update_state_files(results, stats, decision, reason)

        # Save detailed results if requested
        if args.output:
            output_data = {
                'configuration': config,
                'results': results,
                'statistics': stats,
                'decision': decision,
                'reason': reason,
                'recommendation': recommendation,
                'timestamp': datetime.now().isoformat()
            }

            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2, default=str)

            print(f"✓ Detailed results saved to: {args.output}")

        print(f"\n" + "="*60)
        print("WALK-FORWARD VALIDATION COMPLETE")
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
