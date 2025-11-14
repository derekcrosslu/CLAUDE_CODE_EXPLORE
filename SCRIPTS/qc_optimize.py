#!/usr/bin/env python3
"""
QuantConnect Optimization CLI

Usage:
    qc_optimize run --config optimization_params.json --state iteration_state.json
    qc_optimize status --optimization-id abc123
    qc_optimize results --optimization-id abc123 --output results.json
    qc_optimize help [--section <id>] [--search <query>]

Progressive Disclosure Pattern:
- All reference documentation in HELP/qc_optimize.json
- Use 'qc_optimize help' for complete reference
- Use --help for command usage
"""

import click
import json
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
    """QuantConnect optimization CLI for parameter tuning (Phase 4).

    \b
    COMMANDS:
      run       Run parameter optimization
      status    Check optimization status
      results   Download optimization results
      help      Show complete reference documentation

    \b
    REFERENCE DOCUMENTATION:
      Use: qc_optimize help
      All content loaded from HELP/qc_optimize.json
    """
    pass


@cli.command()
@click.option('--section', help='Show specific section by ID')
@click.option('--search', help='Search help content')
@click.option('--list-sections', is_flag=True, help='List all available sections')
def help(section, search, list_sections):
    """Show complete reference documentation from HELP/qc_optimize.json."""
    # Lazy load help_loader (Progressive Disclosure - only load when needed)
    try:
        from help_loader import load_help, format_help, get_section, search_help
    except ImportError as e:
        click.echo(f"❌ Error: help_loader.py not found: {e}", err=True)
        sys.exit(1)

    try:
        help_data = load_help("qc_optimize")
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
        else:
            click.echo(f"❌ Section not found: {section}")
            click.echo("\nUse --list-sections to see available sections")
            sys.exit(1)
        return

    if search:
        results = search_help(search)
        results = [r for r in results if r.get('tool') == 'qc_optimize']

        if results:
            click.echo(f"\n{'=' * 80}")
            click.echo(f"Search results for '{search}' ({len(results)} found)")
            click.echo('=' * 80)
            for result in results:
                if result.get('section_title'):
                    click.echo(f"\n### {result['section_title']}")
                    click.echo(f"Section ID: {result['section_id']}")
                    click.echo(f"Tags: {', '.join(result.get('tags', []))}")
                elif result.get('question'):
                    click.echo(f"\n### FAQ: {result['question']}")
                    click.echo(f"A: {result['answer']}")
            click.echo()
        else:
            click.echo(f"\n❌ No results found for '{search}'")
        return

    # No options: show full help
    formatted = format_help(help_data)
    click.echo(formatted)


@cli.command()
@click.option('--config', required=True, help='Optimization parameters JSON')
@click.option('--state', default='iteration_state.json', help='Iteration state JSON')
@click.option('--output', default='PROJECT_LOGS/optimization_result.json', help='Output file')
@click.option('--estimate-only', is_flag=True, help='Only estimate cost, don\'t run')
@click.option('--strategy', default='grid', help='Optimization strategy: grid (exhaustive), euler (random sampling), or custom class name')
@click.option('--max-backtests', type=int, help='Maximum backtests (for Euler/random strategies)')
def run(config: str, state: str, output: str, estimate_only: bool, strategy: str, max_backtests: int):
    """Run parameter optimization on QuantConnect.
    
    Requires baseline backtest to be completed first.
    
    Examples:
        qc_optimize run --config optimization_params.json
        qc_optimize run --config params.json --estimate-only
    """
    click.echo("🔧 QuantConnect Parameter Optimization")
    click.echo("=" * 60)
    
    # Load configuration
    try:
        with open(config) as f:
            opt_config = json.load(f)
    except FileNotFoundError:
        click.echo(f"❌ Config file not found: {config}", err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON in {config}: {e}", err=True)
        sys.exit(1)
    
    # Load iteration state
    try:
        with open(state) as f:
            iteration_state = json.load(f)
    except FileNotFoundError:
        click.echo(f"❌ State file not found: {state}. Run /qc-init first.", err=True)
        sys.exit(1)
    
    # Check prerequisites
    backtest_results = iteration_state.get('phase_results', {}).get('backtest', {})
    if not backtest_results:
        click.echo("❌ No baseline backtest found. Run /qc-backtest first.", err=True)
        sys.exit(1)
    
    project_id = iteration_state.get('project', {}).get('project_id')
    if not project_id:
        click.echo("❌ No project_id in iteration_state.json", err=True)
        sys.exit(1)
    
    baseline_sharpe = backtest_results.get('sharpe_ratio', 0.0)
    
    # Initialize API
    api = QuantConnectAPI()
    
    # Extract parameters
    parameters = opt_config.get('parameters', [])
    target = opt_config.get('target', 'TotalPerformance.PortfolioStatistics.SharpeRatio')
    target_to = opt_config.get('targetTo', 'max')
    node_type = opt_config.get('nodeType', 'O2-8')
    parallel_nodes = opt_config.get('parallelNodes', 2)

    # Map strategy name to QC class
    strategy_map = {
        'grid': 'QuantConnect.Optimizer.Strategies.GridSearchOptimizationStrategy',
        'euler': 'QuantConnect.Optimizer.Strategies.EulerSearchOptimizationStrategy',
    }

    opt_strategy = strategy_map.get(strategy, strategy)  # Use custom name if not in map

    # Override with config if specified
    if 'strategy' in opt_config:
        opt_strategy = opt_config['strategy']
    
    # Calculate combinations
    total_combinations = 1
    for param in parameters:
        param_min = float(param['min'])
        param_max = float(param['max'])
        param_step = float(param['step'])
        n_values = int((param_max - param_min) / param_step) + 1
        total_combinations *= n_values
    
    click.echo(f"\n📊 Configuration:")
    click.echo(f"   Project ID: {project_id}")
    click.echo(f"   Parameters: {len(parameters)}")
    click.echo(f"   Combinations: {total_combinations}")
    click.echo(f"   Baseline Sharpe: {baseline_sharpe:.3f}")
    
    # Estimate cost
    click.echo(f"\n💰 Estimating cost...")
    estimate = api.estimate_optimization(
        project_id=project_id,
        parameters=parameters,
        node_type=node_type,
        parallel_nodes=parallel_nodes
    )
    
    if estimate.get('success'):
        estimated_cost = estimate.get('estimatedCost', 'Unknown')
        click.echo(f"   Estimated cost: ${estimated_cost}")
    else:
        click.echo(f"   ⚠️  Could not estimate cost: {estimate.get('errors', 'Unknown')}")
    
    if estimate_only:
        click.echo("\n✓ Estimate complete (--estimate-only mode)")
        return
    
    # Run optimization
    opt_name = f"Optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    click.echo(f"\n🚀 Creating optimization: {opt_name}...")
    click.echo(f"   Strategy: {opt_strategy.split('.')[-1]}")

    opt_result = api.create_optimization(
        project_id=project_id,
        name=opt_name,
        target=target,
        parameters=parameters,
        target_to=target_to,
        strategy=opt_strategy,
        node_type=node_type,
        parallel_nodes=parallel_nodes
    )
    
    if not opt_result.get('success'):
        error_msg = opt_result.get('errors', ['Unknown error'])[0]
        click.echo(f"❌ Failed: {error_msg}", err=True)
        sys.exit(1)
    
    # Extract optimization ID
    optimizations = opt_result.get('optimizations', [])
    if not optimizations:
        click.echo("❌ No optimization returned", err=True)
        sys.exit(1)
    
    optimization_id = optimizations[0].get('optimizationId')
    click.echo(f"✓ Optimization created: {optimization_id}")
    click.echo(f"\n⏳ Waiting for completion (10-30 minutes)...")
    click.echo(f"   Use: qc_optimize status --optimization-id {optimization_id}")
    
    # Wait for completion
    final_result = api.wait_for_optimization(optimization_id, timeout=1800, poll_interval=15)
    
    if not final_result.get('success'):
        error_msg = final_result.get('error', 'Unknown error')
        click.echo(f"\n❌ Optimization failed: {error_msg}", err=True)
        sys.exit(1)
    
    # Parse results
    optimization_data = final_result.get('optimization', {})
    best_backtest_id = optimization_data.get('backtestId')
    best_sharpe = optimization_data.get('sharpeRatio', 0.0)
    
    # Get best parameters
    parameter_set = optimization_data.get('parameterSet', [])
    best_params = {}
    for param in parameter_set:
        best_params[param.get('name')] = param.get('value')
    
    # Calculate improvement
    improvement = (best_sharpe - baseline_sharpe) / baseline_sharpe if baseline_sharpe > 0 else 0.0
    
    # Build result
    result = {
        'optimization_id': optimization_id,
        'best_backtest_id': best_backtest_id,
        'best_sharpe': best_sharpe,
        'baseline_sharpe': baseline_sharpe,
        'improvement': improvement,
        'best_parameters': best_params,
        'total_combinations': total_combinations,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Save results
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    # Display results
    click.echo(f"\n{'=' * 60}")
    click.echo("✅ OPTIMIZATION COMPLETE")
    click.echo(f"{'=' * 60}")
    click.echo(f"\n📊 Results:")
    click.echo(f"   Best Sharpe: {best_sharpe:.3f}")
    click.echo(f"   Baseline Sharpe: {baseline_sharpe:.3f}")
    click.echo(f"   Improvement: {improvement*100:+.1f}%")
    click.echo(f"\n📈 Best Parameters:")
    for param_name, param_value in best_params.items():
        click.echo(f"   {param_name}: {param_value}")
    click.echo(f"\n💾 Results saved to: {output}")
    click.echo(f"\n🔗 Best Backtest: https://www.quantconnect.com/terminal/{project_id}/backtests/{best_backtest_id}")


@cli.command()
@click.option('--optimization-id', required=True, help='Optimization ID from QC')
def status(optimization_id: str):
    """Check optimization status.
    
    Examples:
        qc_optimize status --optimization-id abc123def456
    """
    api = QuantConnectAPI()
    
    click.echo(f"🔍 Checking status: {optimization_id}")
    
    # Get status
    result = api.get_optimization_status(optimization_id)
    
    if not result.get('success'):
        click.echo(f"❌ Failed to get status: {result.get('error', 'Unknown error')}", err=True)
        sys.exit(1)
    
    optimization = result.get('optimization', {})
    status_text = optimization.get('status', 'unknown')
    progress = optimization.get('progress', 0.0)
    
    click.echo(f"\n📊 Status: {status_text}")
    click.echo(f"   Progress: {progress*100:.1f}%")


@cli.command()
@click.option('--optimization-id', required=True, help='Optimization ID from QC')
@click.option('--output', default='PROJECT_LOGS/optimization_result.json', help='Output file')
def results(optimization_id: str, output: str):
    """Download optimization results.
    
    Examples:
        qc_optimize results --optimization-id abc123
        qc_optimize results --optimization-id abc123 --output results.json
    """
    api = QuantConnectAPI()
    
    click.echo(f"📥 Fetching results: {optimization_id}")
    
    result = api.get_optimization_results(optimization_id)
    
    if not result.get('success'):
        click.echo(f"❌ Failed: {result.get('error', 'Unknown error')}", err=True)
        sys.exit(1)
    
    # Save results
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    click.echo(f"✓ Results saved to: {output}")


# REMOVED: docs subcommand
# Per PROGRESSIVE_DISCLOSURE_RULES.md: ALL reference documentation
# accessible ONLY via --help (not via docs subcommand)


if __name__ == '__main__':
    cli()
