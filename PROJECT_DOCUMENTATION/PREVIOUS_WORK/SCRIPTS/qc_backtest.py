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
import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Install with: pip install requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("WARNING: python-dotenv not installed. Using environment variables directly.")
    load_dotenv = None


class QuantConnectAPI:
    """Wrapper for QuantConnect API"""

    BASE_URL = "https://www.quantconnect.com/api/v2"

    def __init__(self, user_id=None, api_token=None):
        """Initialize with credentials from .env or parameters"""

        # Load .env if available
        if load_dotenv:
            load_dotenv()

        self.user_id = user_id or os.getenv("QUANTCONNECT_USER_ID")
        self.api_token = api_token or os.getenv("QUANTCONNECT_API_TOKEN")

        if not self.user_id or not self.api_token:
            raise ValueError(
                "QuantConnect credentials not found. "
                "Set QUANTCONNECT_USER_ID and QUANTCONNECT_API_TOKEN in .env file "
                "or pass as parameters."
            )

    def _get_auth(self):
        """Generate HMAC authentication for QuantConnect API v2"""
        timestamp = str(int(time.time()))
        message = f"{self.api_token}:{timestamp}".encode('utf-8')
        signature = hashlib.sha256(message).hexdigest()

        return (self.user_id, signature), {"Timestamp": timestamp}

    def _request(self, method, endpoint, **kwargs):
        """Make authenticated API request with HMAC"""
        url = f"{self.BASE_URL}/{endpoint}"

        # Get authentication
        auth, headers = self._get_auth()

        # Merge with any existing headers
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        try:
            response = requests.request(method, url, auth=auth, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def list_projects(self):
        """List all projects"""
        return self._request("GET", "projects/read")

    def create_project(self, name, language="Py"):
        """Create new project"""
        return self._request("POST", "projects/create", json={
            "name": name,
            "language": language
        })

    def read_project(self, project_id):
        """Read project details"""
        return self._request("GET", f"projects/read", params={
            "projectId": project_id
        })

    def create_file(self, project_id, name, content):
        """Create or update file in project"""
        # Try update first (files/update endpoint)
        result = self._request("POST", "files/update", json={
            "projectId": project_id,
            "name": name,
            "content": content
        })

        # If update fails because file doesn't exist, try create
        if not result.get("success") and "does not exist" in str(result.get("errors", [])):
            result = self._request("POST", "files/create", json={
                "projectId": project_id,
                "name": name,
                "content": content
            })

        return result

    def compile_project(self, project_id):
        """Compile project and return compile ID"""
        return self._request("POST", "compile/create", json={
            "projectId": project_id
        })

    def create_backtest(self, project_id, compile_id=None, name=None):
        """Submit backtest for project"""
        backtest_name = name or f"Backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # If no compile_id provided, compile first
        if not compile_id:
            compile_result = self.compile_project(project_id)
            if not compile_result.get("success"):
                return compile_result
            compile_id = compile_result.get("compileId")

        return self._request("POST", "backtests/create", json={
            "projectId": project_id,
            "compileId": compile_id,
            "backtestName": backtest_name
        })

    def read_backtest(self, project_id, backtest_id):
        """Read backtest status and results"""
        return self._request("GET", "backtests/read", params={
            "projectId": project_id,
            "backtestId": backtest_id
        })

    def wait_for_backtest(self, project_id, backtest_id, timeout=300, poll_interval=5):
        """
        Wait for backtest to complete

        Args:
            project_id: Project ID
            backtest_id: Backtest ID
            timeout: Max wait time in seconds (default 5 min)
            poll_interval: Seconds between status checks

        Returns:
            Final backtest result
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > timeout:
                return {
                    "success": False,
                    "error": f"Backtest timed out after {timeout}s"
                }

            result = self.read_backtest(project_id, backtest_id)

            if not result.get("success"):
                return result

            backtest = result.get("backtest", {})
            status = backtest.get("status")
            completed = backtest.get("completed", False)

            print(f"Status: {status}, Completed: {completed}, Elapsed: {elapsed:.0f}s")

            if completed:
                return result

            time.sleep(poll_interval)

    def create_optimization(self, project_id, name, target, parameters, compile_id=None,
                           target_to="max", strategy="QuantConnect.Optimizer.Strategies.GridSearchOptimizationStrategy",
                           node_type="O2-8", parallel_nodes=2):
        """
        Create optimization job via QuantConnect API

        Args:
            project_id: Project ID
            name: Optimization job name
            target: Target metric (e.g., "TotalPerformance.PortfolioStatistics.SharpeRatio")
            parameters: List of dicts with {name, min, max, step}
            compile_id: Optional compile ID (will compile if not provided)
            target_to: "max" or "min"
            strategy: Optimization strategy class name
            node_type: Node type (O2-8, O4-12, O8-16)
            parallel_nodes: Number of parallel nodes

        Returns:
            API response with optimization ID
        """
        # Compile project if no compile_id provided
        if not compile_id:
            compile_result = self.compile_project(project_id)
            if not compile_result.get("success"):
                return compile_result
            compile_id = compile_result.get("compileId")

        # Estimate cost first
        estimate_result = self.estimate_optimization(project_id, parameters, node_type, parallel_nodes)
        estimated_cost = estimate_result.get("estimatedCost", 0) if estimate_result.get("success") else 0

        # Create optimization request
        data = {
            "projectId": project_id,
            "name": name,
            "target": target,
            "targetTo": target_to,
            "strategy": strategy,
            "compileId": compile_id,
            "parameters": parameters,
            "estimatedCost": estimated_cost,
            "nodeType": node_type,
            "parallelNodes": parallel_nodes
        }

        return self._request("POST", "optimizations/create", json=data)

    def estimate_optimization(self, project_id, parameters, node_type="O2-8", parallel_nodes=2):
        """
        Estimate cost of optimization

        Args:
            project_id: Project ID
            parameters: List of parameter dicts with {name, min, max, step}
            node_type: Node type
            parallel_nodes: Number of parallel nodes

        Returns:
            Estimated cost
        """
        data = {
            "projectId": project_id,
            "parameters": parameters,
            "nodeType": node_type,
            "parallelNodes": parallel_nodes
        }

        return self._request("POST", "optimizations/estimate", json=data)

    def read_optimization(self, optimization_id):
        """
        Read optimization status and results

        Args:
            optimization_id: Optimization ID

        Returns:
            Optimization data
        """
        return self._request("GET", "optimizations/read", params={
            "optimizationId": optimization_id
        })

    def wait_for_optimization(self, optimization_id, timeout=1800, poll_interval=15):
        """
        Wait for optimization to complete

        Args:
            optimization_id: Optimization ID
            timeout: Max wait time in seconds (default 30 min)
            poll_interval: Seconds between status checks

        Returns:
            Final optimization result
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time

            if elapsed > timeout:
                return {
                    "success": False,
                    "error": f"Optimization timed out after {timeout}s"
                }

            result = self.read_optimization(optimization_id)

            if not result.get("success"):
                return result

            optimization = result.get("optimization", {})
            status = optimization.get("status")

            print(f"Optimization Status: {status}, Elapsed: {elapsed:.0f}s")

            if status in ["Completed", "Aborted", "Error"]:
                return result

            time.sleep(poll_interval)

    def upload_file(self, project_id, filename, content):
        """
        Upload/update file in project (alias for create_file)

        Args:
            project_id: QC project ID
            filename: File name
            content: File content

        Returns:
            API response
        """
        return self.create_file(project_id, filename, content)

    def read_backtest_results(self, project_id, backtest_id):
        """
        Read and parse backtest results into standardized format

        Args:
            project_id: Project ID
            backtest_id: Backtest ID

        Returns:
            Parsed results dict with performance, trading, and risk metrics
        """
        # Wait for backtest to complete
        result = self.wait_for_backtest(project_id, backtest_id, timeout=600)

        if not result.get('success'):
            return result

        # Parse using module-level function
        return parse_backtest_results(result)


def parse_backtest_results(backtest_data):
    """
    Parse backtest results into structured format for decision-making

    Returns:
        dict with key metrics and analysis
    """
    if not backtest_data.get("success"):
        return {
            "success": False,
            "error": backtest_data.get("error", "Unknown error")
        }

    backtest = backtest_data.get("backtest", {})
    result = backtest.get("result", {})
    statistics = result.get("Statistics", {})

    # Extract key metrics
    metrics = {
        "success": True,
        "backtest_id": backtest.get("backtestId"),
        "project_id": backtest.get("projectId"),
        "name": backtest.get("name"),
        "status": backtest.get("status"),
        "completed": backtest.get("completed"),
        "created": backtest.get("created"),
        "performance": {
            "sharpe_ratio": float(statistics.get("Sharpe Ratio", 0)),
            "sortino_ratio": float(statistics.get("Sortino Ratio", 0)),
            "max_drawdown": float(statistics.get("Drawdown", "0%").replace("%", "")) / 100,
            "total_return": float(statistics.get("Total Net Profit", "0%").replace("%", "")) / 100,
            "annual_return": float(statistics.get("Annual Return", "0%").replace("%", "")) / 100,
            "win_rate": float(statistics.get("Win Rate", "0%").replace("%", "")) / 100,
            "loss_rate": float(statistics.get("Loss Rate", "0%").replace("%", "")) / 100,
        },
        "trading": {
            "total_trades": int(statistics.get("Total Orders", 0)),
            "average_win": float(statistics.get("Average Win", "0%").replace("%", "")) / 100,
            "average_loss": float(statistics.get("Average Loss", "0%").replace("%", "")) / 100,
            "profit_loss_ratio": float(statistics.get("Profit-Loss Ratio", 0)),
        },
        "risk": {
            "alpha": float(statistics.get("Alpha", 0)),
            "beta": float(statistics.get("Beta", 0)),
            "volatility": float(statistics.get("Annual Standard Deviation", 0)),
        },
        "raw_statistics": statistics
    }

    # Add error/runtime info if available
    if backtest.get("error"):
        metrics["error"] = backtest.get("error")

    if backtest.get("stacktrace"):
        metrics["stacktrace"] = backtest.get("stacktrace")

    return metrics


def find_project_by_name(api, name):
    """Find project by name, return project_id if found"""
    result = api.list_projects()
    if not result.get("success"):
        return None

    for project in result.get("projects", []):
        if project.get("name") == name:
            return project.get("projectId")

    return None


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
        if not args.name or not args.file:
            print("ERROR: --name and --file required for --run")
            sys.exit(1)

        result = create_project_workflow(api, args.name, args.file)

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
