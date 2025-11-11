#!/usr/bin/env python3
"""
QuantConnect Walk-Forward Validation CLI

Usage:
    qc_validate run --strategy strategy.py --state iteration_state.json
    qc_validate analyze --results validation_result.json

Progressive Disclosure Pattern (Beyond MCP):
- Only load validation logic when needed
- Simple in-sample vs out-of-sample split (80/20)
- CLI works for humans, teams, AND agents (trifecta)
"""

import click
import json
import sys
import re
from pathlib import Path
from datetime import datetime

# Absolute path resolution (Beyond MCP pattern)
SCRIPT_DIR = Path(__file__).resolve().parent

# Import QC API
try:
    sys.path.insert(0, str(SCRIPT_DIR))
    from qc_backtest import QuantConnectAPI
except ImportError:
    click.echo("❌ Error: qc_backtest.py not found. Ensure it exists in SCRIPTS/", err=True)
    sys.exit(1)


@click.group()
def cli():
    """QuantConnect walk-forward validation CLI.
    
    Phase 5 of autonomous workflow - tests out-of-sample robustness.
    """
    pass


@cli.command()
@click.option('--strategy', required=True, help='Strategy file path')
@click.option('--state', default='iteration_state.json', help='Iteration state JSON')
@click.option('--output', default='PROJECT_LOGS/validation_result.json', help='Output file')
@click.option('--split', default=0.80, type=float, help='Train/test split ratio (default: 0.80 = 80/20)')
def run(strategy: str, state: str, output: str, split: float):
    """Run walk-forward validation.
    
    Splits data into in-sample (training) and out-of-sample (testing).
    Compares performance degradation.
    
    Examples:
        qc_validate run --strategy strategy.py
        qc_validate run --strategy strategy.py --split 0.70  # 70/30 split
    """
    click.echo("🔬 QuantConnect Walk-Forward Validation")
    click.echo("=" * 60)
    
    # Load strategy code
    try:
        with open(strategy) as f:
            strategy_code = f.read()
    except FileNotFoundError:
        click.echo(f"❌ Strategy file not found: {strategy}", err=True)
        sys.exit(1)
    
    # Load iteration state
    try:
        with open(state) as f:
            iteration_state = json.load(f)
    except FileNotFoundError:
        click.echo(f"❌ State file not found: {state}", err=True)
        sys.exit(1)
    
    project_id = iteration_state.get('project', {}).get('project_id')
    if not project_id:
        click.echo("❌ No project_id in iteration_state.json", err=True)
        sys.exit(1)
    
    # Extract date range from strategy
    start_match = re.search(r'SetStartDate\((\d+),\s*(\d+),\s*(\d+)\)', strategy_code)
    end_match = re.search(r'SetEndDate\((\d+),\s*(\d+),\s*(\d+)\)', strategy_code)
    
    if not start_match or not end_match:
        click.echo("❌ Could not find SetStartDate/SetEndDate in strategy", err=True)
        sys.exit(1)
    
    start_year, start_month, start_day = map(int, start_match.groups())
    end_year, end_month, end_day = map(int, end_match.groups())
    
    # Calculate split point (80/20 by default)
    total_years = end_year - start_year
    train_years = int(total_years * split)
    split_year = start_year + train_years
    
    click.echo(f"\n📊 Data Split ({split*100:.0f}/{(1-split)*100:.0f}):")
    click.echo(f"   Full Period: {start_year}-{start_month:02d}-{start_day:02d} to {end_year}-{end_month:02d}-{end_day:02d}")
    click.echo(f"   In-Sample (Training): {start_year}-{start_month:02d}-{start_day:02d} to {split_year}-{end_month:02d}-{end_day:02d}")
    click.echo(f"   Out-of-Sample (Testing): {split_year+1}-{start_month:02d}-{start_day:02d} to {end_year}-{end_month:02d}-{end_day:02d}")
    
    # Initialize API
    api = QuantConnectAPI()
    
    # Step 1: Run in-sample backtest
    click.echo(f"\n🔄 Running in-sample backtest...")
    strategy_is = re.sub(
        r'SetEndDate\(\d+,\s*\d+,\s*\d+\)',
        f'SetEndDate({split_year}, {end_month}, {end_day})',
        strategy_code
    )
    
    upload_result = api.upload_file(project_id, strategy_is, "Main.py")
    if not upload_result.get('success'):
        click.echo(f"❌ Failed to upload in-sample strategy: {upload_result.get('errors', upload_result.get('error', 'Unknown'))}", err=True)
        sys.exit(1)

    backtest_is = api.create_backtest(project_id, "InSample_Validation")

    if not backtest_is.get('success'):
        click.echo(f"❌ In-sample backtest failed: {backtest_is.get('error', 'Unknown')}", err=True)
        sys.exit(1)
    
    backtest_is_id = backtest_is['backtestId']
    click.echo(f"   Backtest ID: {backtest_is_id}")
    
    result_is = api.wait_for_backtest(project_id, backtest_is_id, timeout=600)
    
    if not result_is.get('success'):
        click.echo(f"❌ In-sample backtest failed", err=True)
        sys.exit(1)
    
    perf_is = api.parse_backtest_results(result_is)
    click.echo(f"   ✓ In-sample Sharpe: {perf_is.get('sharpe_ratio', 0.0):.3f}")
    
    # Step 2: Run out-of-sample backtest
    click.echo(f"\n🔄 Running out-of-sample backtest...")
    strategy_oos = re.sub(
        r'SetStartDate\(\d+,\s*\d+,\s*\d+\)',
        f'SetStartDate({split_year+1}, {start_month}, {start_day})',
        strategy_code
    )
    
    upload_result = api.upload_file(project_id, strategy_oos, "Main.py")
    if not upload_result.get('success'):
        click.echo(f"❌ Failed to upload out-of-sample strategy: {upload_result.get('errors', upload_result.get('error', 'Unknown'))}", err=True)
        sys.exit(1)

    backtest_oos = api.create_backtest(project_id, "OutOfSample_Validation")

    if not backtest_oos.get('success'):
        click.echo(f"❌ Out-of-sample backtest failed: {backtest_oos.get('error', 'Unknown')}", err=True)
        sys.exit(1)
    
    backtest_oos_id = backtest_oos['backtestId']
    click.echo(f"   Backtest ID: {backtest_oos_id}")
    
    result_oos = api.wait_for_backtest(project_id, backtest_oos_id, timeout=600)
    
    if not result_oos.get('success'):
        click.echo(f"❌ Out-of-sample backtest failed", err=True)
        sys.exit(1)
    
    perf_oos = api.parse_backtest_results(result_oos)
    click.echo(f"   ✓ Out-of-sample Sharpe: {perf_oos.get('sharpe_ratio', 0.0):.3f}")
    
    # Step 3: Calculate metrics
    sharpe_is = perf_is.get('sharpe_ratio', 0.0)
    sharpe_oos = perf_oos.get('sharpe_ratio', 0.0)
    
    degradation_pct = (sharpe_is - sharpe_oos) / sharpe_is if sharpe_is != 0 else 1.0
    robustness_score = sharpe_oos / sharpe_is if sharpe_is != 0 else 0.0
    
    # Build result
    result = {
        'in_sample': perf_is,
        'out_of_sample': perf_oos,
        'degradation_pct': degradation_pct,
        'robustness_score': robustness_score,
        'split_ratio': split,
        'in_sample_period': f"{start_year}-{split_year}",
        'out_of_sample_period': f"{split_year+1}-{end_year}",
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Save results
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    # Display results
    click.echo(f"\n{'=' * 60}")
    click.echo("✅ VALIDATION COMPLETE")
    click.echo(f"{'=' * 60}")
    click.echo(f"\n📊 Results:")
    click.echo(f"   In-Sample Sharpe: {sharpe_is:.3f}")
    click.echo(f"   Out-of-Sample Sharpe: {sharpe_oos:.3f}")
    click.echo(f"   Degradation: {degradation_pct*100:.1f}%")
    click.echo(f"   Robustness Score: {robustness_score:.2f}")
    
    # Interpret degradation
    if degradation_pct < 0.15:
        click.echo(f"\n✅ Excellent robustness (<15% degradation)")
    elif degradation_pct < 0.30:
        click.echo(f"\n⚠️  Acceptable degradation (15-30%)")
    elif degradation_pct < 0.40:
        click.echo(f"\n⚠️  Concerning degradation (30-40%)")
    else:
        click.echo(f"\n❌ Severe degradation (>40%) - likely overfit")
    
    click.echo(f"\n💾 Results saved to: {output}")


@cli.command()
@click.option('--results', required=True, help='Validation results JSON')
def analyze(results: str):
    """Analyze validation results.
    
    Examples:
        qc_validate analyze --results PROJECT_LOGS/validation_result.json
    """
    try:
        with open(results) as f:
            validation = json.load(f)
    except FileNotFoundError:
        click.echo(f"❌ Results file not found: {results}", err=True)
        sys.exit(1)
    
    click.echo("📊 Validation Analysis")
    click.echo("=" * 60)
    
    in_sample = validation.get('in_sample', {})
    out_of_sample = validation.get('out_of_sample', {})
    degradation_pct = validation.get('degradation_pct', 0.0)
    robustness_score = validation.get('robustness_score', 0.0)
    
    click.echo(f"\n📈 Performance Comparison:")
    click.echo(f"   Metric              In-Sample    Out-of-Sample    Degradation")
    click.echo(f"   {'-' * 60}")
    click.echo(f"   Sharpe Ratio        {in_sample.get('sharpe_ratio', 0.0):8.3f}     {out_of_sample.get('sharpe_ratio', 0.0):8.3f}       {degradation_pct*100:6.1f}%")
    click.echo(f"   Max Drawdown        {in_sample.get('max_drawdown', 0.0):8.1%}     {out_of_sample.get('max_drawdown', 0.0):8.1%}")
    click.echo(f"   Total Trades        {in_sample.get('total_trades', 0):8}     {out_of_sample.get('total_trades', 0):8}")
    click.echo(f"   Win Rate            {in_sample.get('win_rate', 0.0):8.1%}     {out_of_sample.get('win_rate', 0.0):8.1%}")
    
    click.echo(f"\n🎯 Robustness Assessment:")
    click.echo(f"   Robustness Score: {robustness_score:.2f} (OOS/IS Sharpe ratio)")
    
    if robustness_score > 0.75:
        click.echo(f"   ✅ HIGH robustness (>0.75)")
    elif robustness_score > 0.60:
        click.echo(f"   ⚠️  MODERATE robustness (0.60-0.75)")
    else:
        click.echo(f"   ❌ LOW robustness (<0.60)")


if __name__ == '__main__':
    cli()
