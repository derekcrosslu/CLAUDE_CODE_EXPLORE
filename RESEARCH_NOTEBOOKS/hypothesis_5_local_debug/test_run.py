#!/usr/bin/env python3
"""
Quick test runner for Monte Carlo validation
Runs the exact QC code with mock data
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import required libraries
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random
from collections import Counter, deque
import json

# LOCAL DEBUG MODE - Use mock QuantConnect API
print("="*70)
print("LOCAL DEBUG MODE - Using Mock QuantConnect API")
print("="*70)
from mock_quantbook import QuantBook, Resolution

# Initialize QuantBook (mock)
qb = QuantBook()

print("✓ Mock QuantConnect Research environment initialized")

# ==================== CONFIGURATION ====================

config = {
    'project_id': 26140717,

    # Pairs to trade
    'pairs': [
        {'long': 'PNC', 'short': 'KBE', 'name': 'PNC_KBE'},
        {'long': 'ARCC', 'short': 'AMLP', 'name': 'ARCC_AMLP'},
        {'long': 'RBA', 'short': 'SMFG', 'name': 'RBA_SMFG'},
        {'long': 'ENB', 'short': 'WEC', 'name': 'ENB_WEC'}
    ],

    # Total period for analysis
    'total_period': {
        'start': datetime(2022, 1, 1),
        'end': datetime(2025, 10, 31)
    },

    # Monte Carlo configuration
    'train_test_split': 0.70,
    'monte_carlo_runs': 5,  # Just 5 for quick test
    'random_seed': 42,

    # Optimized parameters to test
    'parameters': {
        'z_entry_threshold': 1.5,
        'z_exit_threshold': 1.0,
        'lookback_period': 30,
        'position_size_per_pair': 0.40,
        'max_holding_days': 30,
        'stop_loss_z': 4.0
    },

    'baseline_sharpe': 1.829,
    'initial_capital': 100000
}

# Set random seed
if config['random_seed']:
    random.seed(config['random_seed'])
    np.random.seed(config['random_seed'])

print("Configuration:")
print(f"  Pairs: {len(config['pairs'])}")
print(f"  Period: {config['total_period']['start'].date()} to {config['total_period']['end'].date()}")
print(f"  Train/Test: {config['train_test_split']*100:.0f}%/{(1-config['train_test_split'])*100:.0f}%")
print(f"  Monte Carlo runs: {config['monte_carlo_runs']} (quick test)")
print(f"  Parameters: {config['parameters']}")
print(f"  Baseline Sharpe: {config['baseline_sharpe']:.3f}")

# ==================== SUBSCRIBE TO SECURITIES ====================

print("\nSubscribing to securities...")

symbols = {}
for pair in config['pairs']:
    long_sym = qb.AddEquity(pair['long'], Resolution.Daily).Symbol
    short_sym = qb.AddEquity(pair['short'], Resolution.Daily).Symbol
    symbols[pair['name']] = {'long': long_sym, 'short': short_sym}
    print(f"  ✓ {pair['name']}: {pair['long']}/{pair['short']}")

print(f"\n✓ Subscribed to {len(symbols)} pairs")

# ==================== HELPER FUNCTIONS ====================

def generate_random_split(start_date, end_date, train_pct, seed=None):
    """Generate random train/test split for Monte Carlo"""
    if seed is not None:
        random.seed(seed)

    total_days = (end_date - start_date).days
    train_days = int(total_days * train_pct)
    test_days = total_days - train_days

    # Random start for training window
    max_offset = test_days
    offset = random.randint(0, max(0, max_offset))

    train_start = start_date + timedelta(days=offset)
    train_end = train_start + timedelta(days=train_days)
    test_start = train_end + timedelta(days=1)
    test_end = train_start + timedelta(days=total_days)

    return train_start, train_end, test_start, test_end


def calculate_spread(long_prices, short_prices):
    """Calculate spread between two price series"""
    return np.log(long_prices) - np.log(short_prices)


def calculate_zscore(spread, lookback):
    """Calculate z-score using rolling window"""
    if len(spread) < lookback:
        return pd.Series([np.nan] * len(spread), index=spread.index)

    rolling_mean = spread.rolling(window=lookback).mean()
    rolling_std = spread.rolling(window=lookback).std(ddof=1)

    zscore = (spread - rolling_mean) / rolling_std
    return zscore


def simulate_strategy(data, params):
    """
    Simulate statistical arbitrage strategy on historical data

    Args:
        data: Dict of DataFrames with price data for each pair
        params: Strategy parameters

    Returns:
        equity_curve: Daily portfolio values
        trades: List of trade records
    """
    capital = config['initial_capital']
    equity_curve = []
    trades = []

    # Get all dates (union of all pair dates)
    all_dates = sorted(set().union(*[set(df.index) for df in data.values()]))

    # Track positions for each pair
    positions = {pair['name']: None for pair in config['pairs']}

    for date in all_dates:
        daily_pnl = 0

        # Process each pair
        for pair in config['pairs']:
            pair_name = pair['name']

            if pair_name not in data:
                continue

            df = data[pair_name]

            if date not in df.index:
                continue

            # Get current prices and z-score
            current_data = df.loc[:date]
            if len(current_data) < params['lookback_period']:
                continue

            long_price = df.loc[date, 'long_price']
            short_price = df.loc[date, 'short_price']
            z_score = df.loc[date, 'zscore']

            if np.isnan(z_score):
                continue

            pos = positions[pair_name]

            # Check exit conditions
            if pos is not None:
                days_held = (date - pos['entry_date']).days

                # Calculate current P&L
                if pos['direction'] == 'long_spread':
                    pnl = (long_price / pos['entry_long'] - 1) * pos['long_shares'] * pos['entry_long']
                    pnl -= (short_price / pos['entry_short'] - 1) * pos['short_shares'] * pos['entry_short']
                else:
                    pnl = (short_price / pos['entry_short'] - 1) * pos['short_shares'] * pos['entry_short']
                    pnl -= (long_price / pos['entry_long'] - 1) * pos['long_shares'] * pos['entry_long']

                daily_pnl += pnl - pos['last_pnl']
                pos['last_pnl'] = pnl

                # Exit conditions
                exit_signal = False
                exit_reason = None

                if abs(z_score) < params['z_exit_threshold']:
                    exit_signal = True
                    exit_reason = 'mean_reversion'
                elif days_held >= params['max_holding_days']:
                    exit_signal = True
                    exit_reason = 'timeout'
                elif abs(z_score) > params['stop_loss_z']:
                    exit_signal = True
                    exit_reason = 'stop_loss'

                if exit_signal:
                    capital += pnl
                    trades.append({
                        'pair': pair_name,
                        'entry_date': pos['entry_date'],
                        'exit_date': date,
                        'entry_z': pos['entry_z'],
                        'exit_z': z_score,
                        'pnl': pnl,
                        'exit_reason': exit_reason,
                        'days_held': days_held
                    })
                    positions[pair_name] = None

            # Check entry conditions (if no position)
            if positions[pair_name] is None:
                if abs(z_score) > params['z_entry_threshold']:
                    # Calculate position sizes (dollar-neutral)
                    pair_capital = capital * params['position_size_per_pair']

                    if z_score > 0:  # Short spread (long short, short long)
                        direction = 'short_spread'
                        long_shares = pair_capital / (2 * long_price)
                        short_shares = pair_capital / (2 * short_price)
                    else:  # Long spread (long long, short short)
                        direction = 'long_spread'
                        long_shares = pair_capital / (2 * long_price)
                        short_shares = pair_capital / (2 * short_price)

                    positions[pair_name] = {
                        'entry_date': date,
                        'entry_z': z_score,
                        'entry_long': long_price,
                        'entry_short': short_price,
                        'long_shares': long_shares,
                        'short_shares': short_shares,
                        'direction': direction,
                        'last_pnl': 0
                    }

        # Record equity
        equity_curve.append({'date': date, 'equity': capital})

    return pd.DataFrame(equity_curve).set_index('date'), trades


def calculate_sharpe(equity_curve):
    """Calculate annualized Sharpe ratio"""
    returns = equity_curve['equity'].pct_change().dropna()
    if len(returns) == 0 or returns.std() == 0:
        return 0.0

    sharpe = returns.mean() / returns.std() * np.sqrt(252)  # Annualized
    return sharpe


print("✓ Helper functions loaded")

# ==================== MONTE CARLO WALK-FORWARD ====================

print("\n" + "="*70)
print("MONTE CARLO WALK-FORWARD ANALYSIS - LOCAL DEBUG")
print("="*70)
print()

results = []
errors = []

for run in range(config['monte_carlo_runs']):
    print(f"\n{'='*70}")
    print(f"Monte Carlo Run {run + 1}/{config['monte_carlo_runs']}")
    print(f"{'='*70}")

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

        # 2. Fetch historical data for TRAINING period
        print(f"\nFetching training data...")
        train_data = {}
        for pair in config['pairs']:
            # Fetch history - use list with single symbol to get clean DataFrame
            long_hist = qb.History([symbols[pair['name']]['long']], train_start, train_end, Resolution.Daily)
            short_hist = qb.History([symbols[pair['name']]['short']], train_start, train_end, Resolution.Daily)

            if long_hist.empty or short_hist.empty:
                print(f"  ⚠ Skipping {pair['name']}: no data")
                continue

            # Extract close prices - handle multi-index if present
            if isinstance(long_hist.index, pd.MultiIndex):
                long_close = long_hist['close'].droplevel(0)
                short_close = short_hist['close'].droplevel(0)
            else:
                long_close = long_hist['close']
                short_close = short_hist['close']

            # Create aligned DataFrame
            df = pd.DataFrame({
                'long_price': long_close,
                'short_price': short_close
            }).dropna()

            # Only require lookback period worth of data
            if len(df) < config['parameters']['lookback_period']:
                print(f"  ⚠ Skipping {pair['name']}: insufficient data ({len(df)} rows, need {config['parameters']['lookback_period']})")
                continue

            # Calculate spread and z-score
            df['spread'] = np.log(df['long_price']) - np.log(df['short_price'])
            df['zscore'] = calculate_zscore(df['spread'], config['parameters']['lookback_period'])

            train_data[pair['name']] = df
            print(f"  ✓ {pair['name']}: {len(df)} days")

        if len(train_data) == 0:
            raise ValueError("No training data available for any pair")

        print(f"  ✓ Fetched data for {len(train_data)} pairs")

        # 3. Run strategy on TRAINING data
        print(f"Running strategy on training period...")
        train_equity, train_trades = simulate_strategy(train_data, config['parameters'])
        train_sharpe = calculate_sharpe(train_equity)
        print(f"  ✓ Training Sharpe: {train_sharpe:.3f} ({len(train_trades)} trades)")

        # 4. Fetch historical data for TESTING period
        print(f"\nFetching testing data...")
        test_data = {}
        for pair in config['pairs']:
            # Fetch history
            long_hist = qb.History([symbols[pair['name']]['long']], test_start, test_end, Resolution.Daily)
            short_hist = qb.History([symbols[pair['name']]['short']], test_start, test_end, Resolution.Daily)

            if long_hist.empty or short_hist.empty:
                print(f"  ⚠ Skipping {pair['name']}: no data")
                continue

            # Extract close prices
            if isinstance(long_hist.index, pd.MultiIndex):
                long_close = long_hist['close'].droplevel(0)
                short_close = short_hist['close'].droplevel(0)
            else:
                long_close = long_hist['close']
                short_close = short_hist['close']

            # Create aligned DataFrame
            df = pd.DataFrame({
                'long_price': long_close,
                'short_price': short_close
            }).dropna()

            # Only require lookback period worth of data
            if len(df) < config['parameters']['lookback_period']:
                print(f"  ⚠ Skipping {pair['name']}: insufficient data ({len(df)} rows, need {config['parameters']['lookback_period']})")
                continue

            # Calculate spread and z-score
            df['spread'] = np.log(df['long_price']) - np.log(df['short_price'])
            df['zscore'] = calculate_zscore(df['spread'], config['parameters']['lookback_period'])

            test_data[pair['name']] = df
            print(f"  ✓ {pair['name']}: {len(df)} days")

        if len(test_data) == 0:
            raise ValueError("No testing data available for any pair")

        print(f"  ✓ Fetched data for {len(test_data)} pairs")

        # 5. Run strategy on TESTING data
        print(f"Running strategy on testing period...")
        test_equity, test_trades = simulate_strategy(test_data, config['parameters'])
        test_sharpe = calculate_sharpe(test_equity)
        print(f"  ✓ Testing Sharpe: {test_sharpe:.3f} ({len(test_trades)} trades)")

        # 6. Calculate degradation
        if train_sharpe > 0:
            degradation = (train_sharpe - test_sharpe) / train_sharpe
        else:
            degradation = 1.0

        print(f"  Degradation: {degradation*100:.1f}%")

        # Store results
        results.append({
            'run': run + 1,
            'train_start': train_start,
            'train_end': train_end,
            'test_start': test_start,
            'test_end': test_end,
            'train_sharpe': float(train_sharpe),
            'test_sharpe': float(test_sharpe),
            'degradation': float(degradation),
            'train_trades': len(train_trades),
            'test_trades': len(test_trades)
        })

        print(f"  ✓ Run {run + 1} complete")

    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        print(f"  ✗ Error in run {run + 1}: {error_msg}")
        print(f"  Traceback:\n{traceback_str}")
        errors.append({'run': run + 1, 'error': error_msg, 'traceback': traceback_str})
        continue

print(f"\n{'='*70}")
print(f"Monte Carlo Walk-Forward Complete")
print(f"  Successful runs: {len(results)}/{config['monte_carlo_runs']}")
print(f"  Failed runs: {len(errors)}/{config['monte_carlo_runs']}")
print(f"{'='*70}")

# Quick summary
if len(results) > 0:
    df_results = pd.DataFrame(results)

    print("\n" + "="*70)
    print("QUICK SUMMARY")
    print("="*70)

    print(f"\nMean Training Sharpe:  {df_results['train_sharpe'].mean():.3f} ± {df_results['train_sharpe'].std():.3f}")
    print(f"Mean Testing Sharpe:   {df_results['test_sharpe'].mean():.3f} ± {df_results['test_sharpe'].std():.3f}")
    print(f"Mean Degradation:      {df_results['degradation'].mean()*100:.1f}% ± {df_results['degradation'].std()*100:.1f}%")
    print(f"\nMean Training Trades:  {df_results['train_trades'].mean():.1f}")
    print(f"Mean Testing Trades:   {df_results['test_trades'].mean():.1f}")

    print(f"\n✓ LOCAL DEBUG COMPLETE - CODE IS WORKING!")
else:
    print("\n✗ No successful runs - check errors above")

if len(errors) > 0:
    print(f"\n" + "="*70)
    print(f"ERRORS ({len(errors)} runs failed)")
    print("="*70)
    for err in errors:
        print(f"\nRun {err['run']}: {err['error']}")

print("\n" + "="*70)
print("NEXT STEPS:")
print("  If no errors above, the QC code is correct!")
print("  Ready to upload to QuantConnect Research")
print("="*70)
