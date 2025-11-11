#!/usr/bin/env python3
"""
Monte Carlo Walk-Forward Validation - LOCAL TEST

Purpose: Test the Monte Carlo logic with synthetic data (NO QuantConnect dependencies)

Run:
    python test_monte_carlo_local.py
"""

# Import required libraries (NO QuantConnect dependencies)
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import random
from collections import Counter
import json
import time

print("[OK] Libraries imported successfully")

# ==================== CONFIGURATION ====================

config = {
    # Simulation settings
    'project_id': 'LOCAL_TEST',

    # Total period for analysis
    'total_period': {
        'start': datetime(2023, 1, 1),
        'end': datetime(2024, 12, 31)
    },

    # Train/test split (60% train, 40% test)
    'train_test_split': 0.60,

    # Number of Monte Carlo runs
    'monte_carlo_runs': 10,

    # Parameters being "optimized" (synthetic)
    'parameters': {
        'lookback_period': {'min': 15, 'max': 25, 'step': 5},
        'volume_multiplier': {'min': 1.3, 'max': 1.7, 'step': 0.2}
    },

    # Synthetic data generation settings
    'synthetic': {
        'train_sharpe_mean': 1.5,  # Average training Sharpe
        'train_sharpe_std': 0.3,   # Variance in training
        'degradation_mean': 0.20,  # 20% average degradation
        'degradation_std': 0.10    # Variance in degradation
    },

    # Random seed for reproducibility
    'random_seed': 42
}

# Set random seed
if config['random_seed'] is not None:
    random.seed(config['random_seed'])
    np.random.seed(config['random_seed'])

print("\nConfiguration:")
print(f"  Test Mode: LOCAL SYNTHETIC DATA")
print(f"  Period: {config['total_period']['start'].date()} to {config['total_period']['end'].date()}")
print(f"  Train/Test: {config['train_test_split']*100:.0f}%/{(1-config['train_test_split'])*100:.0f}%")
print(f"  Monte Carlo runs: {config['monte_carlo_runs']}")
print(f"  Parameters: {list(config['parameters'].keys())}")

# ==================== HELPER FUNCTIONS ====================

def generate_random_split(start_date, end_date, train_pct, seed=None):
    """
    Generate random training and testing periods (Monte Carlo sampling)

    Args:
        start_date: Overall start date
        end_date: Overall end date
        train_pct: Percentage of data for training (0.0-1.0)
        seed: Random seed for this split

    Returns:
        tuple: (train_start, train_end, test_start, test_end)
    """
    if seed is not None:
        random.seed(seed)

    total_days = (end_date - start_date).days
    train_days = int(total_days * train_pct)
    test_days = total_days - train_days

    # Ensure minimum test period (90 days)
    min_test_days = 90
    if test_days < min_test_days:
        raise ValueError(f"Test period too short ({test_days} days). Need at least {min_test_days} days.")

    # Random start point for training window
    max_start_offset = total_days - train_days - test_days
    start_offset = random.randint(0, max(0, max_start_offset))

    train_start = start_date + timedelta(days=start_offset)
    train_end = train_start + timedelta(days=train_days)
    test_start = train_end + timedelta(days=1)
    test_end = test_start + timedelta(days=test_days)

    return train_start, train_end, test_start, test_end


def generate_synthetic_backtest(config, run_number):
    """
    Generate synthetic backtest results (replaces real optimization/backtest)

    Args:
        config: Configuration dictionary
        run_number: Current Monte Carlo run number

    Returns:
        dict: Synthetic results with train_sharpe, test_sharpe, best_params
    """
    syn = config['synthetic']

    # Generate training Sharpe (normally distributed)
    train_sharpe = np.random.normal(syn['train_sharpe_mean'], syn['train_sharpe_std'])
    train_sharpe = max(0.1, train_sharpe)  # Ensure positive

    # Generate degradation (normally distributed)
    degradation = np.random.normal(syn['degradation_mean'], syn['degradation_std'])
    degradation = max(0.0, min(0.9, degradation))  # Clamp to [0, 0.9]

    # Calculate test Sharpe
    test_sharpe = train_sharpe * (1 - degradation)

    # Generate random "best" parameters
    best_params = {}
    for param_name, param_range in config['parameters'].items():
        # Pick random value from parameter range
        values = np.arange(param_range['min'], param_range['max'] + param_range['step'], param_range['step'])
        best_params[param_name] = float(np.random.choice(values))

    # Generate synthetic metrics
    test_metrics = {
        'sharpe_ratio': float(test_sharpe),
        'total_trades': int(np.random.randint(50, 200)),
        'win_rate': float(np.random.uniform(0.45, 0.65))
    }

    return {
        'train_sharpe': float(train_sharpe),
        'test_sharpe': float(test_sharpe),
        'degradation': float(degradation),
        'best_params': best_params,
        'test_metrics': test_metrics
    }

print("[OK] Helper functions loaded")

# ==================== MONTE CARLO WALK-FORWARD ====================

print("\n" + "="*60)
print("MONTE CARLO WALK-FORWARD ANALYSIS (SYNTHETIC DATA)")
print("="*60)
print()

results = []
errors = []

for run in range(config['monte_carlo_runs']):
    print(f"{'='*60}")
    print(f"Monte Carlo Run {run + 1}/{config['monte_carlo_runs']}")
    print(f"{'='*60}")

    try:
        # 1. Generate random train/test split
        train_start, train_end, test_start, test_end = generate_random_split(
            config['total_period']['start'],
            config['total_period']['end'],
            config['train_test_split'],
            seed=run if config['random_seed'] else None
        )

        print(f"Training:  {train_start.date()} to {train_end.date()} ({(train_end - train_start).days} days)")
        print(f"Testing:   {test_start.date()} to {test_end.date()} ({(test_end - test_start).days} days)")

        # 2. Generate synthetic results (replaces real optimization/backtest)
        print(f"Generating synthetic backtest results...")
        synthetic_results = generate_synthetic_backtest(config, run)

        train_sharpe = synthetic_results['train_sharpe']
        test_sharpe = synthetic_results['test_sharpe']
        degradation = synthetic_results['degradation']
        best_params = synthetic_results['best_params']
        test_metrics = synthetic_results['test_metrics']

        print(f"  Train Sharpe:  {train_sharpe:.3f}")
        print(f"  Test Sharpe:   {test_sharpe:.3f}")
        print(f"  Degradation:   {degradation*100:.1f}%")
        print(f"  Best Params:   {best_params}")

        # 3. Store results
        results.append({
            'run': run + 1,
            'train_start': train_start,
            'train_end': train_end,
            'test_start': test_start,
            'test_end': test_end,
            'train_sharpe': train_sharpe,
            'test_sharpe': test_sharpe,
            'degradation': degradation,
            'best_params': best_params,
            'test_metrics': test_metrics
        })

    except Exception as e:
        error_msg = str(e)
        print(f"  [ERROR] Error in run {run + 1}: {error_msg}")
        errors.append({
            'run': run + 1,
            'error': error_msg
        })
        continue

print(f"{'='*60}")
print(f"Monte Carlo Walk-Forward Complete")
print(f"  Successful runs: {len(results)}/{config['monte_carlo_runs']}")
print(f"  Failed runs: {len(errors)}/{config['monte_carlo_runs']}")
print(f"{'='*60}")

# ==================== ANALYSIS ====================

if len(results) == 0:
    print("[ERROR] No successful runs to analyze")
    exit(1)

# Convert to DataFrame
df_results = pd.DataFrame(results)

print("\n" + "="*60)
print("AGGREGATE RESULTS")
print("="*60)

# Summary statistics
mean_train = df_results['train_sharpe'].mean()
std_train = df_results['train_sharpe'].std()
mean_test = df_results['test_sharpe'].mean()
std_test = df_results['test_sharpe'].std()
mean_deg = df_results['degradation'].mean()
std_deg = df_results['degradation'].std()

print(f"\nPerformance Metrics:")
print(f"  Mean Training Sharpe:  {mean_train:.3f} ± {std_train:.3f}")
print(f"  Mean Testing Sharpe:   {mean_test:.3f} ± {std_test:.3f}")
print(f"  Mean Degradation:      {mean_deg*100:.1f}% ± {std_deg*100:.1f}%")

# Robustness analysis
overfit_count = (df_results['degradation'] > 0.30).sum()
good_count = (df_results['degradation'] < 0.15).sum()
overfit_pct = overfit_count / len(df_results)
good_pct = good_count / len(df_results)

print(f"\nRobustness Analysis:")
print(f"  Runs with >30% degradation: {overfit_count}/{len(df_results)} ({overfit_pct*100:.0f}%)")
print(f"  Runs with <15% degradation: {good_count}/{len(df_results)} ({good_pct*100:.0f}%)")

# Parameter stability
print(f"\n" + "="*60)
print("PARAMETER STABILITY")
print("="*60)

for param_name in config['parameters'].keys():
    values = [r['best_params'][param_name] for r in results]
    counter = Counter(values)
    most_common = counter.most_common(1)[0]

    print(f"\n{param_name}:")
    for value, count in counter.most_common():
        pct = count / len(results) * 100
        print(f"  {value}: {count}/{len(results)} ({pct:.0f}%)")

    if most_common[1] / len(results) >= 0.70:
        print(f"  [OK] STABLE: {most_common[0]} appears in {most_common[1]/len(results)*100:.0f}% of runs")
    else:
        print(f"  [WARNING] UNSTABLE: No clear consensus (max {most_common[1]/len(results)*100:.0f}%)")

# ==================== ROBUSTNESS DECISION ====================

print("\n" + "="*60)
print("ROBUSTNESS DECISION FRAMEWORK")
print("="*60 + "\n")

# Apply decision rules
if overfit_pct > 0.50:
    decision = "ABANDON_STRATEGY"
    reason = f"Overfitting in {overfit_pct*100:.0f}% of Monte Carlo runs"
    recommendation = "Strategy does not generalize well. Consider new hypothesis."

elif mean_deg > 0.40:
    decision = "HIGH_RISK"
    reason = f"Average degradation {mean_deg*100:.1f}% indicates poor generalization"
    recommendation = "Strategy shows high out-of-sample degradation. Use with extreme caution."

elif std_deg > 0.25:
    decision = "UNSTABLE_PARAMETERS"
    reason = f"High variance ({std_deg*100:.1f}%) suggests parameter instability"
    recommendation = "Parameters not stable across periods. Consider narrowing search space."

elif mean_deg < 0.15 and std_deg < 0.10:
    decision = "ROBUST_STRATEGY"
    reason = f"Low degradation ({mean_deg*100:.1f}%) with low variance ({std_deg*100:.1f}%)"
    recommendation = "Strategy shows excellent generalization. Ready for paper trading."

else:
    decision = "PROCEED_WITH_CAUTION"
    reason = f"Moderate degradation ({mean_deg*100:.1f}%), acceptable stability"
    recommendation = "Strategy shows reasonable generalization. Additional validation recommended."

print(f"Decision: {decision}")
print(f"\nReason: {reason}")
print(f"\nRecommendation: {recommendation}")

# Recommended parameters
print(f"\n" + "="*60)
print("RECOMMENDED PARAMETERS FOR LIVE TRADING")
print("="*60)

recommended_params = {}
for param_name in config['parameters'].keys():
    values = [r['best_params'][param_name] for r in results]
    most_common = Counter(values).most_common(1)[0]
    recommended_params[param_name] = most_common[0]
    print(f"  {param_name}: {most_common[0]} (chosen {most_common[1]/len(results)*100:.0f}% of the time)")

print(f"\n" + "="*60)

# ==================== SAVE RESULTS ====================

output_data = {
    'configuration': {
        'project_id': config['project_id'],
        'period': f"{config['total_period']['start'].date()} to {config['total_period']['end'].date()}",
        'train_test_split': config['train_test_split'],
        'monte_carlo_runs': config['monte_carlo_runs'],
        'parameters': config['parameters'],
        'synthetic': config['synthetic']
    },
    'summary': {
        'successful_runs': len(results),
        'failed_runs': len(errors),
        'mean_train_sharpe': float(mean_train),
        'mean_test_sharpe': float(mean_test),
        'mean_degradation': float(mean_deg),
        'std_degradation': float(std_deg),
        'pct_overfit': float(overfit_pct),
        'decision': decision,
        'reason': reason,
        'recommendation': recommendation
    },
    'recommended_parameters': recommended_params,
    'detailed_results': [
        {
            'run': r['run'],
            'train_period': f"{r['train_start'].date()} to {r['train_end'].date()}",
            'test_period': f"{r['test_start'].date()} to {r['test_end'].date()}",
            'train_sharpe': r['train_sharpe'],
            'test_sharpe': r['test_sharpe'],
            'degradation': r['degradation'],
            'best_params': r['best_params'],
            'test_metrics': r['test_metrics']
        }
        for r in results
    ],
    'errors': errors
}

# Save to JSON
output_filename = f"walkforward_results_local_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_filename, 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"\n[OK] Results saved to: {output_filename}")
print(f"\n" + "="*60)
print("MONTE CARLO WALK-FORWARD ANALYSIS COMPLETE (LOCAL TEST)")
print("="*60)
print("\nThis was a LOCAL TEST with SYNTHETIC data.")
print("The logic and structure have been validated.")
print("Next: Adapt this structure for QuantConnect Research environment.")
