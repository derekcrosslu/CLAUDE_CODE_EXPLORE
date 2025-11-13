#!/usr/bin/env python3
"""
QuantConnect Backtest Wrapper Script

Provides a simple CLI interface to:
- Create QuantConnect projects
- Submit backtests
- Monitor execution
- Download and parse results

Usage:
    python qc_backtest.py --create --name "MyStrategy"
    python qc_backtest.py --backtest --project-id 12345 --file main.py
    python qc_backtest.py --status --backtest-id abc123
    python qc_backtest.py --results --backtest-id abc123
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Import shared QC API module (Progressive Disclosure)
try:
    from qc_api import QuantConnectAPI, parse_backtest_results, find_project_by_name
except ImportError:
    print("ERROR: qc_api.py not found. Ensure it exists in SCRIPTS/", file=sys.stderr)
    sys.exit(1)


# All API functionality now imported from qc_api.py


def update_and_run_existing_project(api, project_id, code_file):
    """
    Upload code to existing project and run backtest

    Args:
        api: QuantConnectAPI instance
        project_id: Existing project ID to use
        code_file: Path to Python strategy file

    Returns:
        Backtest results
    """
    print(f"\n=== Using Existing Project: {project_id} ===")

    # Read code file
    code_path = Path(code_file)
    if not code_path.exists():
        return {"success": False, "error": f"File not found: {code_file}"}

    code_content = code_path.read_text()
    filename = code_path.name

    # Upload code to project
    print(f"Uploading code from {code_file}...")
    upload_result = api.upload_file(project_id, filename, code_content)

    # Create and run backtest
    print(f"Submitting backtest...")
    backtest_result = api.create_backtest(project_id)

    if not backtest_result.get("success"):
        return backtest_result

    backtest_id = backtest_result.get("backtestId")
    print(f"Backtest submitted: {backtest_id}")

    # Wait for completion and parse results
    print(f"\nWaiting for backtest to complete...")
    final_result = api.read_backtest_results(project_id, backtest_id)

    return final_result


def create_project_workflow(api, name, code_file, reuse_existing=True):
    """
    Complete workflow: create/reuse project, upload code, run backtest

    Args:
        api: QuantConnectAPI instance
        name: Project name
        code_file: Path to Python strategy file
        reuse_existing: If True, reuse existing project with same name

    Returns:
        Backtest results
    """
    print(f"\n=== Workflow for Project: {name} ===")

    # Check if project exists
    project_id = None
    if reuse_existing:
        project_id = find_project_by_name(api, name)
        if project_id:
            print(f"Found existing project: {project_id}")

    # Create new project if not found
    if not project_id:
        print(f"Creating new project...")
        result = api.create_project(name)
        if not result.get("success"):
            return result

        project_id = result["projects"][0]["projectId"]
        print(f"Project created: {project_id}")

    # Read code file
    code_path = Path(code_file)
    if not code_path.exists():
        return {"success": False, "error": f"Code file not found: {code_file}"}

    code_content = code_path.read_text()

    # Upload code
    print(f"Uploading code from {code_file}...")
    file_result = api.create_file(project_id, "main.py", code_content)
    if not file_result.get("success"):
        return file_result

    # Create backtest
    print("Submitting backtest...")
    backtest_result = api.create_backtest(project_id)
    if not backtest_result.get("success"):
        return backtest_result

    backtest_id = backtest_result["backtest"]["backtestId"]
    print(f"Backtest submitted: {backtest_id}")

    # Wait for completion
    print("\nWaiting for backtest to complete...")
    final_result = api.wait_for_backtest(project_id, backtest_id, timeout=600)

    # Parse results
    metrics = parse_backtest_results(final_result)

    return metrics


def optimize_strategy(api, project_id, parameter_sets, base_name="Optimization"):
    """
    Run parameter optimization by backtesting multiple parameter combinations

    Args:
        api: QuantConnectAPI instance
        project_id: Project ID to optimize
        parameter_sets: List of dicts with parameter combinations
        base_name: Base name for optimization runs

    Returns:
        List of results for each parameter set
    """
    print(f"\n=== Running Optimization: {len(parameter_sets)} parameter sets ===")

    results = []

    for i, params in enumerate(parameter_sets):
        print(f"\n--- Parameter Set {i+1}/{len(parameter_sets)} ---")
        print(f"Parameters: {params}")

        # Create backtest name with parameters
        param_str = "_".join([f"{k}={v}" for k, v in params.items()])
        backtest_name = f"{base_name}_{param_str}"

        # Submit backtest
        backtest_result = api.create_backtest(project_id, backtest_name)
        if not backtest_result.get("success"):
            print(f"ERROR: Failed to create backtest: {backtest_result.get('error')}")
            results.append({
                "parameters": params,
                "success": False,
                "error": backtest_result.get("error")
            })
            continue

        backtest_id = backtest_result["backtest"]["backtestId"]
        print(f"Backtest submitted: {backtest_id}")

        # Wait for completion
        final_result = api.wait_for_backtest(project_id, backtest_id, timeout=600)

        # Parse results
        metrics = parse_backtest_results(final_result)
        metrics["parameters"] = params

        results.append(metrics)

        # Print key metrics
        if metrics.get("success"):
            perf = metrics["performance"]
            print(f"Sharpe: {perf['sharpe_ratio']:.2f}, "
                  f"Return: {perf['total_return']:.2%}, "
                  f"Drawdown: {perf['max_drawdown']:.2%}")

    return results


def analyze_optimization_results(results):
    """
    Analyze optimization results and find best parameters

    Args:
        results: List of backtest results from optimize_strategy

    Returns:
        Analysis dict with best parameters and rankings
    """
    # Filter successful results
    successful = [r for r in results if r.get("success")]

    if not successful:
        return {
            "success": False,
            "error": "No successful optimization runs",
            "total_runs": len(results),
            "successful_runs": 0
        }

    # Rank by Sharpe ratio
    ranked = sorted(successful,
                   key=lambda x: x["performance"]["sharpe_ratio"],
                   reverse=True)

    # Calculate statistics
    sharpe_values = [r["performance"]["sharpe_ratio"] for r in successful]
    return_values = [r["performance"]["total_return"] for r in successful]

    analysis = {
        "success": True,
        "total_runs": len(results),
        "successful_runs": len(successful),
        "failed_runs": len(results) - len(successful),
        "best_parameters": ranked[0]["parameters"],
        "best_sharpe": ranked[0]["performance"]["sharpe_ratio"],
        "best_return": ranked[0]["performance"]["total_return"],
        "best_drawdown": ranked[0]["performance"]["max_drawdown"],
        "statistics": {
            "mean_sharpe": sum(sharpe_values) / len(sharpe_values),
            "max_sharpe": max(sharpe_values),
            "min_sharpe": min(sharpe_values),
            "mean_return": sum(return_values) / len(return_values),
            "max_return": max(return_values),
            "min_return": min(return_values)
        },
        "top_5": [
            {
                "rank": i + 1,
                "parameters": r["parameters"],
                "sharpe": r["performance"]["sharpe_ratio"],
                "return": r["performance"]["total_return"],
                "drawdown": r["performance"]["max_drawdown"]
            }
            for i, r in enumerate(ranked[:5])
        ],
        "all_results": ranked
    }

    return analysis


def main():
    parser = argparse.ArgumentParser(description="QuantConnect Backtest Wrapper")

    # Actions
    parser.add_argument("--create", action="store_true", help="Create new project")
    parser.add_argument("--backtest", action="store_true", help="Run backtest on existing project")
    parser.add_argument("--status", action="store_true", help="Check backtest status")
    parser.add_argument("--results", action="store_true", help="Get backtest results")
    parser.add_argument("--run", action="store_true", help="Complete workflow: create + backtest")
    parser.add_argument("--optimize", action="store_true", help="Run parameter optimization")
    parser.add_argument("--list", action="store_true", help="List all projects")

    # Parameters
    parser.add_argument("--name", help="Project name")
    parser.add_argument("--project-id", type=int, help="Project ID")
    parser.add_argument("--backtest-id", help="Backtest ID")
    parser.add_argument("--file", help="Path to strategy Python file")
    parser.add_argument("--output", help="Output file for results (JSON)")
    parser.add_argument("--params-file", help="JSON file with parameter sets for optimization")

    args = parser.parse_args()

    # Initialize API
    try:
        api = QuantConnectAPI()
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    # Execute action
    result = None

    if args.list:
        result = api.list_projects()

    elif args.create:
        if not args.name:
            print("ERROR: --name required for --create")
            sys.exit(1)
        result = api.create_project(args.name)

    elif args.backtest:
        if not args.project_id:
            print("ERROR: --project-id required for --backtest")
            sys.exit(1)
        result = api.create_backtest(args.project_id)

    elif args.status or args.results:
        if not args.project_id or not args.backtest_id:
            print("ERROR: --project-id and --backtest-id required")
            sys.exit(1)

        raw_result = api.read_backtest(args.project_id, args.backtest_id)

        if args.results:
            result = parse_backtest_results(raw_result)
        else:
            result = raw_result

    elif args.run:
        if not args.file:
            print("ERROR: --file required for --run")
            sys.exit(1)

        # If project_id provided, use existing project (NEVER create new)
        if args.project_id:
            print(f"Using existing project ID: {args.project_id}")
            result = update_and_run_existing_project(api, args.project_id, args.file)
        # Otherwise require name for project creation workflow
        elif args.name:
            print(f"WARNING: Creating new project is deprecated. Use /qc-init command instead.")
            print(f"Proceeding with name-based workflow for backward compatibility...")
            result = create_project_workflow(api, args.name, args.file)
        else:
            print("ERROR: Either --project-id or --name required for --run")
            print("RECOMMENDED: Use --project-id with ID from iteration_state.json")
            sys.exit(1)

    elif args.optimize:
        if not args.project_id or not args.params_file:
            print("ERROR: --project-id and --params-file required for --optimize")
            sys.exit(1)

        # Load parameter configuration from JSON file
        params_path = Path(args.params_file)
        if not params_path.exists():
            print(f"ERROR: Parameter file not found: {args.params_file}")
            sys.exit(1)

        params_config = json.loads(params_path.read_text())

        # Expect format: {parameters: [{name, min, max, step}], target: "...", ...}
        parameters = params_config.get("parameters", [])
        target = params_config.get("target", "TotalPerformance.PortfolioStatistics.SharpeRatio")
        target_to = params_config.get("targetTo", "max")
        node_type = params_config.get("nodeType", "O2-8")
        parallel_nodes = params_config.get("parallelNodes", 2)

        if not parameters:
            print("ERROR: Parameter file must contain 'parameters' array with {name, min, max, step}")
            sys.exit(1)

        print(f"\n=== Creating QC Native Optimization ===")
        print(f"Project ID: {args.project_id}")
        print(f"Parameters: {parameters}")
        print(f"Target: {target} ({target_to})")
        print(f"Nodes: {parallel_nodes} x {node_type}")

        # Create optimization using native QC API
        opt_result = api.create_optimization(
            project_id=args.project_id,
            name=args.name or "Optimization",
            target=target,
            parameters=parameters,
            target_to=target_to,
            node_type=node_type,
            parallel_nodes=parallel_nodes
        )

        if not opt_result.get("success"):
            print(f"ERROR: Failed to create optimization: {opt_result.get('error')}")
            result = opt_result
        else:
            # Extract optimization ID from optimizations array
            optimizations = opt_result.get("optimizations", [])
            if not optimizations:
                print("ERROR: No optimizations returned in response")
                result = opt_result
            else:
                optimization_id = optimizations[0].get("optimizationId")
                print(f"\nOptimization created: {optimization_id}")
                print("Waiting for completion...")

                # Wait for optimization to complete
                final_result = api.wait_for_optimization(optimization_id, timeout=1800)

                if final_result.get("success"):
                    # Parse and analyze results
                    optimization = final_result.get("optimization", {})
                    result = {
                        "success": True,
                        "optimization_id": optimization_id,
                        "status": optimization.get("status"),
                        "best_parameters": optimization.get("parameterSet"),
                        "best_backtest_id": optimization.get("backtestId"),
                        "statistics": optimization.get("statistics", {}),
                        "raw_data": optimization
                    }
                else:
                    result = final_result

    else:
        parser.print_help()
        sys.exit(1)

    # Output results
    if result:
        json_output = json.dumps(result, indent=2)

        # Print to stdout
        print("\n=== RESULTS ===")
        print(json_output)

        # Save to file if requested
        if args.output:
            Path(args.output).write_text(json_output)
            print(f"\nResults saved to: {args.output}")

        # Exit code based on success
        if result.get("success") is False:
            sys.exit(1)


if __name__ == "__main__":
    main()
