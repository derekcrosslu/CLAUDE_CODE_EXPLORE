#!/usr/bin/env python3
"""
QuantConnect API Client - Shared Module

Progressive Disclosure Pattern (Beyond MCP):
- Single source of truth for QC API operations
- Used by qc_backtest.py, qc_optimize.py, qc_validate.py
- DRY principle - no duplication across scripts

Usage:
    from qc_api import QuantConnectAPI
    api = QuantConnectAPI()
    api.create_file(project_id, "main.py", code_content)
"""

import hashlib
import os
import time
from datetime import datetime

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Install with: pip install requests")
    import sys
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


class QuantConnectAPI:
    """
    QuantConnect API v2 Client

    Provides authenticated access to QC API for:
    - Project management (create, read)
    - File operations (create, update, read)
    - Compilation
    - Backtesting
    - Optimization

    Authentication: HMAC-SHA256
    """

    BASE_URL = "https://www.quantconnect.com/api/v2"

    def __init__(self, user_id=None, api_token=None):
        """
        Initialize API client with credentials

        Args:
            user_id: QC user ID (from .env or parameter)
            api_token: QC API token (from .env or parameter)

        Environment Variables:
            QUANTCONNECT_USER_ID
            QUANTCONNECT_API_TOKEN
        """
        if load_dotenv:
            load_dotenv()

        self.user_id = user_id or os.getenv("QUANTCONNECT_USER_ID")
        self.api_token = api_token or os.getenv("QUANTCONNECT_API_TOKEN")

        if not self.user_id or not self.api_token:
            raise ValueError(
                "QuantConnect credentials not found. "
                "Set QUANTCONNECT_USER_ID and QUANTCONNECT_API_TOKEN in .env file"
            )

    def _get_auth(self):
        """
        Generate HMAC authentication for QuantConnect API v2

        Returns:
            tuple: (auth_tuple, headers_dict)
        """
        timestamp = str(int(time.time()))
        message = f"{self.api_token}:{timestamp}".encode('utf-8')
        signature = hashlib.sha256(message).hexdigest()
        return (self.user_id, signature), {"Timestamp": timestamp}

    def _request(self, method, endpoint, **kwargs):
        """
        Make authenticated API request with HMAC

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "projects/create")
            **kwargs: Additional requests kwargs

        Returns:
            dict: API response as JSON
        """
        url = f"{self.BASE_URL}/{endpoint}"
        auth, headers = self._get_auth()

        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers

        try:
            response = requests.request(method, url, auth=auth, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    # =========================================================================
    # Project Operations
    # =========================================================================

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
        return self._request("GET", "projects/read", params={
            "projectId": project_id
        })

    def delete_project(self, project_id):
        """Delete project"""
        return self._request("POST", "projects/delete", json={
            "projectId": project_id
        })

    # =========================================================================
    # File Operations
    # =========================================================================

    def read_files(self, project_id, filename=None):
        """
        Read files from a project

        Args:
            project_id: Project ID
            filename: Optional specific filename. If None, reads all files.

        Returns:
            dict: API response with files array
        """
        payload = {"projectId": project_id}
        if filename:
            payload["name"] = filename
        return self._request("POST", "files/read", json=payload)

    def create_file(self, project_id, name, content):
        """
        Create or update file in project

        Automatically tries update first, creates if file doesn't exist.

        Args:
            project_id: Project ID
            name: Filename (e.g., "main.py", "research.ipynb")
            content: File content as string

        Returns:
            dict: API response
        """
        # Try update first
        result = self._request("POST", "files/update", json={
            "projectId": project_id,
            "name": name,
            "content": content
        })

        # If file doesn't exist, create it
        if not result.get("success"):
            errors_str = str(result.get("errors", []))
            if "does not exist" in errors_str or "not found" in errors_str.lower():
                result = self._request("POST", "files/create", json={
                    "projectId": project_id,
                    "name": name,
                    "content": content
                })
        return result

    def upload_file(self, project_id, name, content):
        """
        Upload file to project (alias for create_file for semantic clarity)

        This is the preferred method name for uploading files to QC projects.
        Internally uses create_file() which handles both create and update.

        Args:
            project_id: Project ID
            name: Filename (e.g., "main.py", "research.ipynb")
            content: File content as string

        Returns:
            dict: API response
        """
        return self.create_file(project_id, name, content)

    def delete_file(self, project_id, name):
        """Delete file from project"""
        return self._request("POST", "files/delete", json={
            "projectId": project_id,
            "name": name
        })

    # =========================================================================
    # Compilation
    # =========================================================================

    def compile_project(self, project_id):
        """
        Compile project and return compile ID

        Returns:
            dict: Contains compileId on success
        """
        return self._request("POST", "compile/create", json={
            "projectId": project_id
        })

    def read_compile(self, project_id, compile_id):
        """Read compile status"""
        return self._request("GET", "compile/read", params={
            "projectId": project_id,
            "compileId": compile_id
        })

    # =========================================================================
    # Backtesting
    # =========================================================================

    def create_backtest(self, project_id, compile_id=None, name=None):
        """
        Submit backtest for project

        Args:
            project_id: Project ID
            compile_id: Optional compile ID. If None, compiles first.
            name: Optional backtest name

        Returns:
            dict: Contains backtestId on success
        """
        backtest_name = name or f"Backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Compile if no compile_id provided
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
        """
        Read backtest status and results

        Returns:
            dict: Contains backtest status and performance metrics
        """
        return self._request("GET", "backtests/read", params={
            "projectId": project_id,
            "backtestId": backtest_id
        })

    def delete_backtest(self, project_id, backtest_id):
        """Delete backtest"""
        return self._request("POST", "backtests/delete", json={
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
            dict: Final backtest result
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
            completed = backtest.get("completed", False)

            if completed:
                return result

            # Check for errors
            if backtest.get("error"):
                return {
                    "success": False,
                    "error": backtest.get("error")
                }

            # Still running
            progress = backtest.get("progress", 0.0)
            print(f"⏳ Progress: {progress*100:.1f}% (elapsed: {int(elapsed)}s)")
            time.sleep(poll_interval)

    # =========================================================================
    # Optimization
    # =========================================================================

    def estimate_optimization(self, project_id, parameters, node_type="O2-8", parallel_nodes=2):
        """
        Estimate optimization cost

        Args:
            project_id: Project ID
            parameters: List of parameter dicts with min/max/step
            node_type: Node type (e.g., "O2-8")
            parallel_nodes: Number of parallel nodes

        Returns:
            dict: Contains estimatedCost
        """
        return self._request("POST", "optimizations/estimate", json={
            "projectId": project_id,
            "parameters": parameters,
            "nodeType": node_type,
            "parallelNodes": parallel_nodes
        })

    def create_optimization(self, project_id, name, target, parameters,
                          target_to="max", strategy="QuantConnect.Optimizer.Strategies.GridSearchOptimizationStrategy",
                          node_type="O2-8", parallel_nodes=2, compile_id=None):
        """
        Create optimization job

        Args:
            project_id: Project ID
            name: Optimization name
            target: Target metric (e.g., "TotalPerformance.PortfolioStatistics.SharpeRatio")
            parameters: List of parameter dicts
            target_to: "max" or "min"
            strategy: Optimization strategy class
            node_type: Node type
            parallel_nodes: Number of parallel nodes
            compile_id: Optional compile ID. If None, compiles first.

        Returns:
            dict: Contains optimizationId on success
        """
        # Compile if no compile_id provided
        if not compile_id:
            compile_result = self.compile_project(project_id)
            if not compile_result.get("success"):
                return compile_result
            compile_id = compile_result.get("compileId")

        return self._request("POST", "optimizations/create", json={
            "projectId": project_id,
            "compileId": compile_id,
            "name": name,
            "target": target,
            "targetTo": target_to,
            "targetValue": None,
            "strategy": strategy,
            "constraints": [],
            "nodeType": node_type,
            "parallelNodes": parallel_nodes,
            "parameters": parameters
        })

    def read_optimization(self, optimization_id):
        """
        Read optimization status and results

        Returns:
            dict: Contains optimization status and best parameters
        """
        return self._request("GET", "optimizations/read", params={
            "optimizationId": optimization_id
        })

    def delete_optimization(self, optimization_id):
        """Cancel/delete optimization"""
        return self._request("POST", "optimizations/delete", json={
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
            dict: Final optimization result
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
            status = optimization.get("status", "").lower()

            if status == "completed":
                return result
            elif status in ["error", "failed", "cancelled"]:
                return {
                    "success": False,
                    "error": f"Optimization {status}: {optimization.get('error', 'Unknown error')}"
                }

            # Still running
            progress = optimization.get("progress", 0.0)
            print(f"⏳ Progress: {progress*100:.1f}% (elapsed: {int(elapsed)}s)")
            time.sleep(poll_interval)

    def get_optimization_status(self, optimization_id):
        """
        Get optimization status (alias for read_optimization)

        Args:
            optimization_id: Optimization ID

        Returns:
            dict: Optimization data
        """
        return self.read_optimization(optimization_id)

    def get_optimization_results(self, optimization_id):
        """
        Get optimization results (alias for read_optimization)

        Args:
            optimization_id: Optimization ID

        Returns:
            dict: Optimization data with results
        """
        return self.read_optimization(optimization_id)

    def parse_backtest_results(self, backtest_data):
        """
        Parse backtest results into structured format for decision-making
        (Instance method wrapper for module-level function)

        Args:
            backtest_data: Raw backtest data from read_backtest()

        Returns:
            dict: Parsed metrics with performance, trading, and risk data
        """
        return parse_backtest_results(backtest_data)

    def read_backtest_results(self, project_id, backtest_id):
        """
        Read and parse backtest results into standardized format

        Args:
            project_id: Project ID
            backtest_id: Backtest ID

        Returns:
            dict: Parsed results with performance, trading, and risk metrics
        """
        # Wait for backtest to complete
        result = self.wait_for_backtest(project_id, backtest_id, timeout=600)

        if not result.get('success'):
            return result

        # Parse using module-level function
        return parse_backtest_results(result)


# =============================================================================
# Helper Functions
# =============================================================================

def parse_backtest_results(backtest_data):
    """
    Parse backtest results into structured format for decision-making

    Args:
        backtest_data: Raw backtest API response

    Returns:
        dict: Parsed metrics with key performance indicators
    """
    if not backtest_data.get("success"):
        return {
            "success": False,
            "error": backtest_data.get("error", "Unknown error")
        }

    backtest = backtest_data.get("backtest", {})

    # Get statistics (formatted strings)
    statistics = backtest.get("statistics", {})

    # Get totalPerformance (numeric values)
    total_perf = backtest.get("totalPerformance", {})
    portfolio_stats = total_perf.get("portfolioStatistics", {})
    trade_stats = total_perf.get("tradeStatistics", {})

    # Extract key metrics using totalPerformance for numeric values
    metrics = {
        "success": True,
        "backtest_id": backtest.get("backtestId"),
        "project_id": backtest.get("projectId"),
        "name": backtest.get("name"),
        "status": backtest.get("status"),
        "completed": backtest.get("completed"),
        "created": backtest.get("created"),
        "performance": {
            "sharpe_ratio": float(portfolio_stats.get("sharpeRatio", 0)),
            "sortino_ratio": float(portfolio_stats.get("sortinoRatio", 0)),
            "max_drawdown": float(portfolio_stats.get("drawdown", 0)),
            "total_return": float(portfolio_stats.get("totalNetProfit", 0)),
            "annual_return": float(portfolio_stats.get("compoundingAnnualReturn", 0)),
            "win_rate": float(portfolio_stats.get("winRate", 0)),
            "loss_rate": float(portfolio_stats.get("lossRate", 0)),
            "psr": float(portfolio_stats.get("probabilisticSharpeRatio", 0)),
        },
        "trading": {
            "total_orders": int(statistics.get("Total Orders", "0").replace(",", "")),
            "total_trades": int(trade_stats.get("totalNumberOfTrades", 0)),
            "winning_trades": int(trade_stats.get("numberOfWinningTrades", 0)),
            "losing_trades": int(trade_stats.get("numberOfLosingTrades", 0)),
            "average_win": float(trade_stats.get("averageProfit", 0)),
            "average_loss": float(trade_stats.get("averageLoss", 0)),
            "profit_loss_ratio": float(trade_stats.get("profitLossRatio", 0)),
            "largest_win": float(trade_stats.get("largestProfit", 0)),
            "largest_loss": float(trade_stats.get("largestLoss", 0)),
        },
        "risk": {
            "alpha": float(portfolio_stats.get("alpha", 0)),
            "beta": float(portfolio_stats.get("beta", 0)),
            "volatility": float(portfolio_stats.get("annualStandardDeviation", 0)),
        },
        "raw_statistics": statistics,
        "raw_portfolio_stats": portfolio_stats,
        "raw_trade_stats": trade_stats
    }

    # Add error/runtime info if available
    if backtest.get("error"):
        metrics["error"] = backtest.get("error")

    if backtest.get("stacktrace"):
        metrics["stacktrace"] = backtest.get("stacktrace")

    return metrics


def find_project_by_name(api, name):
    """
    Find project by name, return project_id if found

    Args:
        api: QuantConnectAPI instance
        name: Project name to search for

    Returns:
        int: Project ID if found, None otherwise
    """
    result = api.list_projects()
    if not result.get("success"):
        return None

    for project in result.get("projects", []):
        if project.get("name") == name:
            return project.get("projectId")

    return None


# Convenience function for loading from .env
def create_api():
    """Create API client from environment variables"""
    return QuantConnectAPI()
