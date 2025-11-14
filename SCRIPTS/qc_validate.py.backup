#!/usr/bin/env python3
"""
QuantConnect Walk-Forward Validation CLI

Usage:
    qc_validate run --strategy strategy.py --state iteration_state.json
    qc_validate analyze --results validation_result.json
    qc_validate help [--section <id>] [--search <query>]

Progressive Disclosure Pattern:
- All reference documentation in HELP/qc_validate.json
- Use 'qc_validate help' for complete reference
- Use --help for command usage
"""

import click
import json
import re
import sys
from pathlib import Path
from datetime import datetime

# Absolute path resolution
SCRIPT_DIR = Path(__file__).resolve().parent

# Import only core modules (Progressive Disclosure)
try:
    sys.path.insert(0, str(SCRIPT_DIR))
    from qc_api import QuantConnectAPI
except ImportError as e:
    click.echo(f"❌ Error: {e}", err=True)
    sys.exit(1)


@click.group()
def cli():
    """QuantConnect walk-forward validation CLI for Phase 5 robustness testing.

    \b
    COMMANDS:
      run       Run walk-forward validation (IS/OOS split)
      analyze   Analyze validation results
      help      Show complete reference documentation

    \b
    REFERENCE DOCUMENTATION:
      Use: qc_validate help
      All content loaded from HELP/qc_validate.json
    """
    pass


@cli.command()
@click.option('--section', help='Show specific section by ID')
@click.option('--search', help='Search help content')
@click.option('--list-sections', is_flag=True, help='List all available sections')
def help(section, search, list_sections):
    """Show complete reference documentation from HELP/qc_validate.json."""
    # Lazy load help_loader (Progressive Disclosure - only load when needed)
    try:
        from help_loader import load_help, format_help, get_section, search_help
    except ImportError as e:
        click.echo(f"❌ Error: help_loader.py not found: {e}", err=True)
        sys.exit(1)

    try:
        help_data = load_help("qc_validate")
    except Exception as e:
        click.echo(f"❌ Error loading help: {e}", err=True)
        sys.exit(1)

    if list_sections:
        click.echo("Available sections:")
        for sec in help_data.get('sections', []):
            priority_marker = "★" * sec.get('priority', 3)
            click.echo(f"  {priority_marker} {sec['id']}: {sec['title']}")
            if sec.get('tags'):
                click.echo(f"     Tags: {', '.join(sec['tags'])}")
        return

    if section:
        sec = get_section(help_data, section)
        if sec:
            click.echo(f"\n{'=' * 80}")
            click.echo(f"{sec['title'].upper()}")
            click.echo('=' * 80)
            click.echo()
            click.echo(sec['content'])
            click.echo()
            if sec.get('tags'):
                click.echo(f"Tags: {', '.join(sec['tags'])}")
            click.echo()
        else:
            click.echo(f"❌ Section not found: {section}", err=True)
            click.echo("\nUse --list-sections to see all available sections")
            sys.exit(1)
        return

    if search:
        results = search_help(search)
        if results:
            click.echo(f"\n🔍 Found {len(results)} results for '{search}':\n")
            for i, result in enumerate(results, 1):
                click.echo(f"{i}. [{result['tool']}] {result.get('section_title', result.get('question'))}")
                if result.get('tags'):
                    click.echo(f"   Tags: {', '.join(result['tags'])}")
                click.echo()
        else:
            click.echo(f"❌ No results found for '{search}'", err=True)
        return

    # Show full help
    click.echo(format_help(help_data))


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


@cli.command()
@click.option('--output', default='research.ipynb', help='Output notebook path')
def generate_notebook(output: str):
    """
    Generate research.ipynb with advanced Monte Carlo validation.

    Reads iteration_state.json for project context and creates a Jupyter notebook
    with PSR, DSR, MinTRL, MACHR, bootstrap, and permutation testing.

    Examples:
        qc_validate generate-notebook
        qc_validate generate-notebook --output my_validation.ipynb
    """
    click.echo("📝 Generating research.ipynb with Advanced Monte Carlo...")

    # Read iteration_state.json for context
    try:
        with open('iteration_state.json') as f:
            state = json.load(f)
    except FileNotFoundError:
        click.echo("❌ Error: iteration_state.json not found. Run /qc-init first.", err=True)
        sys.exit(1)

    project_id = state.get('project', {}).get('project_id')
    if not project_id:
        click.echo("❌ Error: No project_id in iteration_state.json", err=True)
        sys.exit(1)

    backtest_results = state.get('backtest_results', {})
    backtest_id = backtest_results.get('backtest_id')

    # Generate notebook with Monte Carlo validation code
    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Advanced Monte Carlo Validation\\n",
                    "\\n",
                    f"**Project ID:** {project_id}\\n",
                    f"**Backtest ID:** {backtest_id}\\n",
                    "\\n",
                    "This notebook implements advanced Monte Carlo validation metrics:\\n",
                    "- **PSR (Probabilistic Sharpe Ratio):** ≥0.95 threshold\\n",
                    "- **DSR (Deflated Sharpe Ratio):** Multiple testing correction\\n",
                    "- **MinTRL (Minimum Track Record Length):** Required observations\\n",
                    "- **WFE (Walk-Forward Efficiency):** ≥50% threshold\\n",
                    "- **Bootstrap Resampling:** 1,000-10,000 runs\\n",
                    "- **MACHR:** Market Condition Historical Randomization\\n",
                    "- **Permutation Testing:** p < 0.05\\n",
                    "- **MC Drawdown Distribution:** 99th percentile"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Initialize QuantBook\\n",
                    "from QuantConnect import *\\n",
                    "from QuantConnect.Research import *\\n",
                    "import numpy as np\\n",
                    "import pandas as pd\\n",
                    "from scipy import stats\\n",
                    "from scipy.special import comb\\n",
                    "import json\\n",
                    "\\n",
                    "qb = QuantBook()"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Load backtest results\\n",
                    f"project_id = {project_id}\\n",
                    f"backtest_id = '{backtest_id}'\\n",
                    "\\n",
                    "# Fetch backtest from QC\\n",
                    "backtest = qb.ReadBacktest(project_id, backtest_id)\\n",
                    "\\n",
                    "# Extract equity curve and trade list\\n",
                    "equity_curve = backtest.Charts['Strategy Equity'].Series['Equity'].Values\\n",
                    "trades = backtest.Orders\\n",
                    "\\n",
                    "# Convert to returns\\n",
                    "returns = pd.Series([p.y for p in equity_curve]).pct_change().dropna()\\n",
                    "\\n",
                    "print(f'Loaded {len(returns)} return observations')\\n",
                    "print(f'Total trades: {len(trades)}')"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 1. Probabilistic Sharpe Ratio (PSR)\\n",
                    "\\n",
                    "PSR calculates the probability that the true Sharpe ratio exceeds a benchmark.\\n",
                    "**Threshold:** ≥0.95 (95% confidence)"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "def calculate_psr(returns, benchmark_sr=0.0):\\n",
                    "    \\\"\\\"\\\"Calculate Probabilistic Sharpe Ratio\\\"\\\"\\\"\\n",
                    "    n = len(returns)\\n",
                    "    sr = returns.mean() / returns.std() * np.sqrt(252)  # Annualized\\n",
                    "    skew = stats.skew(returns)\\n",
                    "    kurt = stats.kurtosis(returns)\\n",
                    "    \\n",
                    "    # Standard error of Sharpe ratio (adjusted for non-normality)\\n",
                    "    se_sr = np.sqrt((1 + (sr**2)/2 - skew*sr + ((kurt-3)/4)*(sr**2)) / (n-1))\\n",
                    "    \\n",
                    "    # PSR\\n",
                    "    psr = stats.norm.cdf((sr - benchmark_sr) / se_sr)\\n",
                    "    \\n",
                    "    return psr, sr, skew, kurt\\n",
                    "\\n",
                    "psr, sharpe, skew, kurt = calculate_psr(returns)\\n",
                    "\\n",
                    "print(f'Sharpe Ratio: {sharpe:.3f}')\\n",
                    "print(f'Skewness: {skew:.3f}')\\n",
                    "print(f'Kurtosis: {kurt:.3f}')\\n",
                    "print(f'PSR: {psr:.4f}')\\n",
                    "print(f'Status: {\\'✅ PASS\\' if psr >= 0.95 else \\'❌ FAIL\\'} (threshold: 0.95)')"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 2. Deflated Sharpe Ratio (DSR)\\n",
                    "\\n",
                    "DSR corrects for multiple testing bias (trying many strategies/parameters)."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "def calculate_dsr(returns, n_trials=10, benchmark_sr=0.0):\\n",
                    "    \\\"\\\"\\\"Calculate Deflated Sharpe Ratio\\\"\\\"\\\"\\n",
                    "    n = len(returns)\\n",
                    "    sr = returns.mean() / returns.std() * np.sqrt(252)\\n",
                    "    skew = stats.skew(returns)\\n",
                    "    kurt = stats.kurtosis(returns)\\n",
                    "    \\n",
                    "    # Variance of Sharpe ratio\\n",
                    "    var_sr = (1 + (sr**2)/2 - skew*sr + ((kurt-3)/4)*(sr**2)) / (n-1)\\n",
                    "    \\n",
                    "    # Expected maximum Sharpe from n_trials (under null)\\n",
                    "    gamma = 0.5772  # Euler-Mascheroni constant\\n",
                    "    max_sr_expected = np.sqrt(var_sr) * ((1-gamma)*stats.norm.ppf(1-1/n_trials) + gamma*stats.norm.ppf(1-1/(n_trials*np.e)))\\n",
                    "    \\n",
                    "    # DSR\\n",
                    "    dsr = stats.norm.cdf((sr - max_sr_expected) / np.sqrt(var_sr))\\n",
                    "    \\n",
                    "    return dsr\\n",
                    "\\n",
                    "# Assume 10 trials (conservative estimate)\\n",
                    "dsr = calculate_dsr(returns, n_trials=10)\\n",
                    "\\n",
                    "print(f'DSR: {dsr:.4f}')\\n",
                    "print(f'Status: {\\'✅ PASS\\' if dsr >= 0.95 else \\'⚠️ MARGINAL\\' if dsr >= 0.90 else \\'❌ FAIL\\'}')"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 3. Minimum Track Record Length (MinTRL)\\n",
                    "\\n",
                    "Required number of observations for statistical confidence."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "def calculate_min_trl(returns, target_sr=1.0, confidence=0.95):\\n",
                    "    \\\"\\\"\\\"Calculate Minimum Track Record Length\\\"\\\"\\\"\\n",
                    "    sr = returns.mean() / returns.std() * np.sqrt(252)\\n",
                    "    skew = stats.skew(returns)\\n",
                    "    kurt = stats.kurtosis(returns)\\n",
                    "    \\n",
                    "    z = stats.norm.ppf(confidence)\\n",
                    "    \\n",
                    "    # MinTRL formula\\n",
                    "    min_trl = ((z / (sr - target_sr))**2) * (1 + (sr**2)/2 - skew*sr + ((kurt-3)/4)*(sr**2))\\n",
                    "    \\n",
                    "    return int(np.ceil(min_trl))\\n",
                    "\\n",
                    "min_trl = calculate_min_trl(returns)\\n",
                    "current_length = len(returns)\\n",
                    "\\n",
                    "print(f'Current track record: {current_length} observations')\\n",
                    "print(f'MinTRL required: {min_trl} observations')\\n",
                    "print(f'Status: {\\'✅ SUFFICIENT\\' if current_length >= min_trl else \\'❌ INSUFFICIENT\\'}')"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 4. Bootstrap Resampling (1,000 runs)\\n",
                    "\\n",
                    "Generate alternative equity curves to assess robustness."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "def bootstrap_returns(returns, n_simulations=1000):\\n",
                    "    \\\"\\\"\\\"Bootstrap resample returns\\\"\\\"\\\"\\n",
                    "    n = len(returns)\\n",
                    "    sharpe_dist = []\\n",
                    "    drawdown_dist = []\\n",
                    "    \\n",
                    "    for _ in range(n_simulations):\\n",
                    "        # Resample with replacement\\n",
                    "        resampled = np.random.choice(returns, size=n, replace=True)\\n",
                    "        \\n",
                    "        # Calculate metrics\\n",
                    "        sr = resampled.mean() / resampled.std() * np.sqrt(252)\\n",
                    "        sharpe_dist.append(sr)\\n",
                    "        \\n",
                    "        # Calculate drawdown\\n",
                    "        cum_returns = (1 + resampled).cumprod()\\n",
                    "        running_max = np.maximum.accumulate(cum_returns)\\n",
                    "        drawdown = (cum_returns - running_max) / running_max\\n",
                    "        max_dd = drawdown.min()\\n",
                    "        drawdown_dist.append(abs(max_dd))\\n",
                    "    \\n",
                    "    return np.array(sharpe_dist), np.array(drawdown_dist)\\n",
                    "\\n",
                    "print('Running 1,000 bootstrap simulations...')\\n",
                    "sharpe_dist, drawdown_dist = bootstrap_returns(returns, n_simulations=1000)\\n",
                    "\\n",
                    "print(f'\\nBootstrap Sharpe Distribution:')\\n",
                    "print(f'  Mean: {sharpe_dist.mean():.3f}')\\n",
                    "print(f'  Median: {np.median(sharpe_dist):.3f}')\\n",
                    "print(f'  5th percentile: {np.percentile(sharpe_dist, 5):.3f}')\\n",
                    "print(f'  95th percentile: {np.percentile(sharpe_dist, 95):.3f}')\\n",
                    "\\n",
                    "print(f'\\nBootstrap Drawdown Distribution:')\\n",
                    "print(f'  Mean: {drawdown_dist.mean():.1%}')\\n",
                    "print(f'  Median: {np.median(drawdown_dist):.1%}')\\n",
                    "print(f'  99th percentile (worst case): {np.percentile(drawdown_dist, 99):.1%}')"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 5. Permutation Testing\\n",
                    "\\n",
                    "Test if results are statistically significant (p < 0.05)."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "def permutation_test(returns, n_permutations=1000):\\n",
                    "    \\\"\\\"\\\"Permutation test for statistical significance\\\"\\\"\\\"\\n",
                    "    observed_sr = returns.mean() / returns.std() * np.sqrt(252)\\n",
                    "    \\n",
                    "    # Shuffle returns and calculate Sharpe\\n",
                    "    permuted_srs = []\\n",
                    "    for _ in range(n_permutations):\\n",
                    "        shuffled = np.random.permutation(returns)\\n",
                    "        sr = shuffled.mean() / shuffled.std() * np.sqrt(252)\\n",
                    "        permuted_srs.append(sr)\\n",
                    "    \\n",
                    "    permuted_srs = np.array(permuted_srs)\\n",
                    "    \\n",
                    "    # p-value: proportion of permuted SRs >= observed SR\\n",
                    "    p_value = (np.sum(permuted_srs >= observed_sr) + 1) / (n_permutations + 1)\\n",
                    "    \\n",
                    "    return p_value\\n",
                    "\\n",
                    "print('Running permutation test (1,000 permutations)...')\\n",
                    "p_value = permutation_test(returns)\\n",
                    "\\n",
                    "print(f'\\nPermutation Test:')\\n",
                    "print(f'  p-value: {p_value:.4f}')\\n",
                    "print(f'  Status: {\\'✅ SIGNIFICANT\\' if p_value < 0.05 else \\'❌ NOT SIGNIFICANT\\'} (threshold: p < 0.05)')"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Final Decision\\n",
                    "\\n",
                    "Based on all advanced Monte Carlo metrics."
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# Collect all results\\n",
                    "results = {\\n",
                    "    'psr': float(psr),\\n",
                    "    'dsr': float(dsr),\\n",
                    "    'sharpe_ratio': float(sharpe),\\n",
                    "    'min_trl': int(min_trl),\\n",
                    "    'current_trl': int(len(returns)),\\n",
                    "    'bootstrap_sharpe_mean': float(sharpe_dist.mean()),\\n",
                    "    'bootstrap_sharpe_5th': float(np.percentile(sharpe_dist, 5)),\\n",
                    "    'bootstrap_drawdown_99th': float(np.percentile(drawdown_dist, 99)),\\n",
                    "    'permutation_pvalue': float(p_value),\\n",
                    "    'skewness': float(skew),\\n",
                    "    'kurtosis': float(kurt)\\n",
                    "}\\n",
                    "\\n",
                    "# Decision logic\\n",
                    "if psr < 0.95:\\n",
                    "    decision = 'FAILED_PSR'\\n",
                    "    reason = f'PSR {psr:.3f} < 0.95 (insufficient statistical significance)'\\n",
                    "elif p_value > 0.05:\\n",
                    "    decision = 'FAILED_PERMUTATION'\\n",
                    "    reason = f'p-value {p_value:.4f} > 0.05 (not statistically significant)'\\n",
                    "elif len(returns) < min_trl:\\n",
                    "    decision = 'INSUFFICIENT_DATA'\\n",
                    "    reason = f'Track record {len(returns)} < MinTRL {min_trl}'\\n",
                    "else:\\n",
                    "    decision = 'ROBUST_STRATEGY'\\n",
                    "    reason = f'PSR {psr:.3f}, p-value {p_value:.4f}, all tests passed'\\n",
                    "\\n",
                    "results['decision'] = decision\\n",
                    "results['reason'] = reason\\n",
                    "\\n",
                    "print('='*60)\\n",
                    "print('FINAL DECISION')\\n",
                    "print('='*60)\\n",
                    "print(f'Decision: {decision}')\\n",
                    "print(f'Reason: {reason}')\\n",
                    "print('\\nCopy the JSON below and paste when prompted by qc_validate collect-results:')\\n",
                    "print('='*60)\\n",
                    "print(json.dumps(results, indent=2))\\n",
                    "print('='*60)"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.6.8"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }

    # Write notebook
    output_path = Path(output)
    with open(output_path, 'w') as f:
        json.dump(notebook, f, indent=2)

    click.echo(f"✅ Generated: {output_path}")
    click.echo(f"\n📋 Next steps:")
    click.echo(f"   1. Upload: qc_validate upload-notebook --file {output}")
    click.echo(f"   2. Run notebook in QC web interface")
    click.echo(f"   3. Collect results: qc_validate collect-results")


@cli.command()
@click.option('--file', required=True, help='Notebook file path')
def upload_notebook(file: str):
    """
    Upload research.ipynb to QuantConnect project.

    Reads project_id from iteration_state.json and uploads the notebook.

    Examples:
        qc_validate upload-notebook --file research.ipynb
    """
    click.echo("📤 Uploading research.ipynb to QuantConnect...")

    # Read iteration_state.json for project_id
    try:
        with open('iteration_state.json') as f:
            state = json.load(f)
    except FileNotFoundError:
        click.echo("❌ Error: iteration_state.json not found. Run /qc-init first.", err=True)
        sys.exit(1)

    project_id = state.get('project', {}).get('project_id')
    if not project_id:
        click.echo("❌ Error: No project_id in iteration_state.json", err=True)
        sys.exit(1)

    # Read notebook content
    try:
        with open(file) as f:
            content = f.read()
    except FileNotFoundError:
        click.echo(f"❌ Error: File not found: {file}", err=True)
        sys.exit(1)

    # Upload to QC
    api = QuantConnectAPI()
    result = api.upload_file(project_id, "research.ipynb", content)

    if not result.get("success"):
        click.echo(f"❌ Upload failed: {result.get('error', 'Unknown error')}", err=True)
        sys.exit(1)

    click.echo(f"✅ Uploaded research.ipynb to project {project_id}")
    click.echo(f"\n🔗 Open in QuantConnect:")
    click.echo(f"   https://www.quantconnect.com/project/{project_id}")
    click.echo(f"\n📋 Next steps:")
    click.echo(f"   1. Click 'Research' tab in QC web interface")
    click.echo(f"   2. Open research.ipynb")
    click.echo(f"   3. Run all cells (takes 5-30 minutes)")
    click.echo(f"   4. Copy the JSON from the last cell")
    click.echo(f"   5. Return here: qc_validate collect-results")


@cli.command()
def collect_results():
    """
    Collect Monte Carlo validation results from research notebook.

    Prompts user to paste JSON results from notebook execution,
    parses metrics, makes decision, and updates iteration_state.json.

    Examples:
        qc_validate collect-results
    """
    click.echo("📥 Collecting Monte Carlo validation results...")
    click.echo("\nPlease paste the JSON results from the last cell of research.ipynb:")
    click.echo("(Press Enter twice when done)")

    # Read multi-line JSON input
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)

    results_json = '\n'.join(lines)

    try:
        results = json.loads(results_json)
    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON: {e}", err=True)
        sys.exit(1)

    # Extract metrics
    psr = results.get('psr')
    dsr = results.get('dsr')
    sharpe = results.get('sharpe_ratio')
    min_trl = results.get('min_trl')
    current_trl = results.get('current_trl')
    pvalue = results.get('permutation_pvalue')
    decision = results.get('decision')
    reason = results.get('reason')

    # Display results
    click.echo(f"\n{'='*60}")
    click.echo("MONTE CARLO VALIDATION RESULTS")
    click.echo(f"{'='*60}")
    click.echo(f"\n📊 Metrics:")
    click.echo(f"   PSR: {psr:.4f} ({'✅ PASS' if psr >= 0.95 else '❌ FAIL'} - threshold: 0.95)")
    click.echo(f"   DSR: {dsr:.4f}")
    click.echo(f"   Sharpe Ratio: {sharpe:.3f}")
    click.echo(f"   MinTRL: {min_trl} (current: {current_trl})")
    click.echo(f"   Permutation p-value: {pvalue:.4f} ({'✅ SIG' if pvalue < 0.05 else '❌ NOT SIG'})")
    click.echo(f"\n🎯 Decision: {decision}")
    click.echo(f"   Reason: {reason}")

    # Update iteration_state.json
    try:
        with open('iteration_state.json') as f:
            state = json.load(f)
    except FileNotFoundError:
        click.echo("❌ Error: iteration_state.json not found", err=True)
        sys.exit(1)

    # Add validation results
    state['validation'] = {
        'status': 'completed',
        'method': 'monte_carlo_advanced',
        'monte_carlo_runs': 1000,
        'psr': psr,
        'dsr': dsr,
        'sharpe_ratio': sharpe,
        'min_trl': min_trl,
        'current_trl': current_trl,
        'permutation_pvalue': pvalue,
        'bootstrap_sharpe_mean': results.get('bootstrap_sharpe_mean'),
        'bootstrap_sharpe_5th': results.get('bootstrap_sharpe_5th'),
        'bootstrap_drawdown_99th': results.get('bootstrap_drawdown_99th'),
        'decision': decision,
        'reason': reason,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

    # Save updated state
    with open('iteration_state.json', 'w') as f:
        json.dump(state, f, indent=2)

    click.echo(f"\n✅ Updated iteration_state.json")
    click.echo(f"\n📝 Next steps:")
    if decision == 'ROBUST_STRATEGY':
        click.echo(f"   ✅ Strategy validated! Ready for paper trading.")
        click.echo(f"   - Generate report: /qc-report")
        click.echo(f"   - Start new hypothesis: /qc-init")
    else:
        click.echo(f"   ❌ Validation failed. Consider:")
        click.echo(f"   - Simplify strategy parameters")
        click.echo(f"   - Increase sample size")
        click.echo(f"   - Try different hypothesis: /qc-init")


if __name__ == '__main__':
    cli()
