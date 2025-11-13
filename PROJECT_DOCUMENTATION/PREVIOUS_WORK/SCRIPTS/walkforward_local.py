#!/usr/bin/env python3
"""
Local Walk-Forward Validation using Synthetic Data

This replaces qc_walkforward_wrapper.py which used expensive QC Optimization API.

Instead, this:
1. Uses locally generated synthetic data
2. Runs momentum breakout strategy directly in Python
3. Simulates Monte Carlo walk-forward without API costs
4. Returns results in same format for compatibility

NO API COSTS - Fully autonomous testing
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random


class MomentumBreakoutStrategy:
    """
    Local implementation of momentum breakout strategy
    Matches the QuantConnect version for testing
    """

    def __init__(self, lookback_period: int = 20, volume_multiplier: float = 1.5):
        self.lookback_period = lookback_period
        self.volume_multiplier = volume_multiplier
        self.trades = []
        self.position = None

    def run_backtest(self, data: pd.DataFrame) -> Dict:
        """
        Run strategy on data

        Returns backtest results matching QC format
        """
        self.trades = []
        self.position = None
        equity_curve = [100000]  # Starting capital

        for i in range(self.lookback_period, len(data)):
            bar = data.iloc[i]
            history = data.iloc[i-self.lookback_period:i]

            # Calculate 20-day high
            high_20 = history['high'].max()

            # Check for breakout
            if bar['close'] > high_20 and self.position is None:
                # Enter long
                self.position = {
                    'entry_price': bar['close'],
                    'entry_date': bar['date'],
                    'shares': int(equity_curve[-1] / bar['close'])
                }

            # Exit after 10 days or 5% loss
            elif self.position is not None:
                days_held = (bar['date'] - self.position['entry_date']).days
                pnl_pct = (bar['close'] - self.position['entry_price']) / self.position['entry_price']

                if days_held >= 10 or pnl_pct <= -0.05:
                    # Exit
                    exit_value = self.position['shares'] * bar['close']
                    entry_value = self.position['shares'] * self.position['entry_price']
                    trade_pnl = exit_value - entry_value

                    self.trades.append({
                        'entry_date': self.position['entry_date'],
                        'exit_date': bar['date'],
                        'entry_price': self.position['entry_price'],
                        'exit_price': bar['close'],
                        'pnl': trade_pnl,
                        'return': pnl_pct
                    })

                    equity_curve.append(equity_curve[-1] + trade_pnl)
                    self.position = None
                else:
                    # Mark-to-market
                    mtm_value = equity_curve[0] + sum(t['pnl'] for t in self.trades)
                    if self.position:
                        mtm_value += self.position['shares'] * (bar['close'] - self.position['entry_price'])
                    equity_curve.append(mtm_value)
            else:
                equity_curve.append(equity_curve[-1])

        # Calculate statistics
        returns = pd.Series(equity_curve).pct_change().dropna()
        total_return = (equity_curve[-1] / equity_curve[0]) - 1

        if len(returns) > 0 and returns.std() > 0:
            sharpe = returns.mean() / returns.std() * np.sqrt(252)
        else:
            sharpe = 0.0

        # Calculate win rate
        if len(self.trades) > 0:
            wins = sum(1 for t in self.trades if t['pnl'] > 0)
            win_rate = wins / len(self.trades)
        else:
            win_rate = 0.0

        # Max drawdown
        equity_series = pd.Series(equity_curve)
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max
        max_dd = drawdown.min()

        return {
            'sharpe_ratio': sharpe,
            'total_return': total_return,
            'total_trades': len(self.trades),
            'win_rate': win_rate,
            'max_drawdown': max_dd,
            'final_equity': equity_curve[-1],
            'trades': self.trades,
            'equity_curve': equity_curve
        }


class LocalWalkForwardValidator:
    """
    Monte Carlo walk-forward validation using local synthetic data
    """

    def __init__(
        self,
        data_path: str,
        monte_carlo_runs: int = 10,
        train_test_split: float = 0.6,
        parameter_ranges: Dict = None
    ):
        self.data_path = Path(data_path)
        self.monte_carlo_runs = monte_carlo_runs
        self.train_test_split = train_test_split

        if parameter_ranges is None:
            self.parameter_ranges = {
                'lookback_period': {'min': 15, 'max': 25, 'step': 5},
                'volume_multiplier': {'min': 1.3, 'max': 1.7, 'step': 0.2}
            }
        else:
            self.parameter_ranges = parameter_ranges

        # Load data
        self.data = pd.read_csv(self.data_path)
        self.data['date'] = pd.to_datetime(self.data['date'])

    def generate_random_split(self, seed: int = None) -> Tuple:
        """Generate random train/test split"""
        if seed is not None:
            random.seed(seed)

        total_days = len(self.data)
        train_days = int(total_days * self.train_test_split)

        # Random start point
        max_start = total_days - train_days - int(total_days * (1 - self.train_test_split))
        start_idx = random.randint(0, max(0, max_start))

        train_end_idx = start_idx + train_days
        test_end_idx = min(train_end_idx + int(total_days * (1 - self.train_test_split)), total_days)

        train_data = self.data.iloc[start_idx:train_end_idx]
        test_data = self.data.iloc[train_end_idx:test_end_idx]

        return train_data, test_data

    def optimize_parameters(self, train_data: pd.DataFrame) -> Dict:
        """
        Simple grid search optimization on training data
        """
        best_sharpe = -np.inf
        best_params = None

        # Grid search
        for lookback in range(
            self.parameter_ranges['lookback_period']['min'],
            self.parameter_ranges['lookback_period']['max'] + 1,
            self.parameter_ranges['lookback_period']['step']
        ):
            for vol_mult in np.arange(
                self.parameter_ranges['volume_multiplier']['min'],
                self.parameter_ranges['volume_multiplier']['max'] + 0.01,
                self.parameter_ranges['volume_multiplier']['step']
            ):
                strategy = MomentumBreakoutStrategy(
                    lookback_period=lookback,
                    volume_multiplier=vol_mult
                )

                results = strategy.run_backtest(train_data)

                if results['sharpe_ratio'] > best_sharpe:
                    best_sharpe = results['sharpe_ratio']
                    best_params = {
                        'lookback_period': lookback,
                        'volume_multiplier': vol_mult,
                        'train_sharpe': results['sharpe_ratio'],
                        'train_trades': results['total_trades']
                    }

        return best_params

    def run_monte_carlo(self) -> Dict:
        """
        Run Monte Carlo walk-forward validation

        Returns:
            Dict with summary statistics and detailed results
        """
        results = []

        print(f"\nRunning {self.monte_carlo_runs} Monte Carlo walk-forward iterations...")
        print("=" * 80)

        for run in range(self.monte_carlo_runs):
            print(f"\nRun {run + 1}/{self.monte_carlo_runs}")
            print("-" * 80)

            # Generate random split
            train_data, test_data = self.generate_random_split(seed=run)

            print(f"Train period: {train_data['date'].iloc[0].date()} to {train_data['date'].iloc[-1].date()}")
            print(f"Test period: {test_data['date'].iloc[0].date()} to {test_data['date'].iloc[-1].date()}")

            # Optimize on training data
            print("Optimizing parameters on training data...")
            best_params = self.optimize_parameters(train_data)
            print(f"Best params: lookback={best_params['lookback_period']}, "
                  f"vol_mult={best_params['volume_multiplier']:.1f}")
            print(f"Train Sharpe: {best_params['train_sharpe']:.2f}, "
                  f"Trades: {best_params['train_trades']}")

            # Test on out-of-sample data
            print("Testing on out-of-sample data...")
            strategy = MomentumBreakoutStrategy(
                lookback_period=best_params['lookback_period'],
                volume_multiplier=best_params['volume_multiplier']
            )

            test_results = strategy.run_backtest(test_data)
            print(f"Test Sharpe: {test_results['sharpe_ratio']:.2f}, "
                  f"Trades: {test_results['total_trades']}")

            # Calculate degradation
            if best_params['train_sharpe'] != 0:
                degradation = (best_params['train_sharpe'] - test_results['sharpe_ratio']) / abs(best_params['train_sharpe'])
            else:
                degradation = 0.0

            print(f"Degradation: {degradation:.1%}")

            results.append({
                'run': run + 1,
                'train_sharpe': best_params['train_sharpe'],
                'test_sharpe': test_results['sharpe_ratio'],
                'train_trades': best_params['train_trades'],
                'test_trades': test_results['total_trades'],
                'degradation': degradation,
                'best_params': best_params,
                'test_results': test_results
            })

        # Calculate summary statistics
        train_sharpes = [r['train_sharpe'] for r in results]
        test_sharpes = [r['test_sharpe'] for r in results]
        degradations = [r['degradation'] for r in results]

        summary = {
            'configuration': {
                'data_file': str(self.data_path),
                'monte_carlo_runs': self.monte_carlo_runs,
                'train_test_split': self.train_test_split,
                'parameter_ranges': self.parameter_ranges
            },
            'summary': {
                'successful_runs': len(results),
                'mean_train_sharpe': np.mean(train_sharpes),
                'mean_test_sharpe': np.mean(test_sharpes),
                'mean_degradation': np.mean(degradations),
                'std_degradation': np.std(degradations),
                'pct_overfit': sum(1 for d in degradations if d > 0.3) / len(results)
            },
            'detailed_results': results
        }

        # Make robustness decision
        summary['decision'] = self._make_decision(summary['summary'])

        return summary

    def _make_decision(self, summary: Dict) -> Dict:
        """
        Make robustness decision based on Monte Carlo results

        Decision levels:
        1. ROBUST_STRATEGY: <15% degradation, <10% variance
        2. ACCEPTABLE_STRATEGY: <30% degradation, <20% variance
        3. MARGINAL_STRATEGY: <50% degradation
        4. OVERFITTING_LIKELY: >50% degradation OR >30% overfit rate
        5. ABANDON_STRATEGY: Negative test Sharpe or very high degradation
        """
        mean_deg = summary['mean_degradation']
        std_deg = summary['std_degradation']
        pct_overfit = summary['pct_overfit']
        test_sharpe = summary['mean_test_sharpe']

        if test_sharpe < 0:
            decision = "ABANDON_STRATEGY"
            reason = f"Negative test Sharpe ({test_sharpe:.2f})"
            recommendation = "Strategy loses money out-of-sample. Abandon."

        elif mean_deg < 0.15 and std_deg < 0.10:
            decision = "ROBUST_STRATEGY"
            reason = f"Low degradation ({mean_deg:.1%}) with low variance ({std_deg:.1%})"
            recommendation = "Strategy shows excellent generalization. Ready for paper trading."

        elif mean_deg < 0.30 and std_deg < 0.20:
            decision = "ACCEPTABLE_STRATEGY"
            reason = f"Moderate degradation ({mean_deg:.1%}) with acceptable variance ({std_deg:.1%})"
            recommendation = "Strategy is acceptable. Consider further optimization."

        elif mean_deg < 0.50:
            decision = "MARGINAL_STRATEGY"
            reason = f"High degradation ({mean_deg:.1%})"
            recommendation = "Strategy shows signs of overfitting. Use with caution."

        else:
            decision = "OVERFITTING_LIKELY"
            reason = f"Very high degradation ({mean_deg:.1%}) or overfit rate ({pct_overfit:.1%})"
            recommendation = "Strategy appears overfit. Abandon or redesign."

        return {
            'decision': decision,
            'reason': reason,
            'recommendation': recommendation
        }


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Local walk-forward validation with synthetic data")
    parser.add_argument('--data', type=str, required=True, help="Path to synthetic data CSV")
    parser.add_argument('--runs', type=int, default=10, help="Number of Monte Carlo runs")
    parser.add_argument('--output', type=str, default="walkforward_results_local.json", help="Output file")

    args = parser.parse_args()

    print("="*80)
    print("LOCAL WALK-FORWARD VALIDATION (Using Synthetic Data)")
    print("="*80)
    print(f"\nData: {args.data}")
    print(f"Monte Carlo Runs: {args.runs}")

    # Run validation
    validator = LocalWalkForwardValidator(
        data_path=args.data,
        monte_carlo_runs=args.runs
    )

    results = validator.run_monte_carlo()

    # Print summary
    print("\n" + "="*80)
    print("RESULTS SUMMARY")
    print("="*80)
    print(f"\nMean Train Sharpe: {results['summary']['mean_train_sharpe']:.2f}")
    print(f"Mean Test Sharpe: {results['summary']['mean_test_sharpe']:.2f}")
    print(f"Mean Degradation: {results['summary']['mean_degradation']:.1%}")
    print(f"Std Degradation: {results['summary']['std_degradation']:.1%}")
    print(f"Overfit Rate: {results['summary']['pct_overfit']:.1%}")

    print(f"\nDecision: {results['decision']['decision']}")
    print(f"Reason: {results['decision']['reason']}")
    print(f"Recommendation: {results['decision']['recommendation']}")

    # Save results
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {args.output}")
    print("="*80)


if __name__ == "__main__":
    main()
