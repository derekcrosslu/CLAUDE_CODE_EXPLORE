#!/usr/bin/env python3
"""
Pair Weight Optimization for H6 Regime-Diversified StatArb

Tests different weight configurations by modifying strategy file and running backtests.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add SCRIPTS to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "SCRIPTS"))
from qc_backtest import QuantConnectAPI

# Project ID from iteration_state
PROJECT_ID = 26160217
STRATEGY_FILE = Path(__file__).parent / "regime_diversified_statarb.py"
RESULTS_FILE = Path(__file__).parent / "weight_optimization_results.json"

# Weight configurations to test
WEIGHT_CONFIGS = [
    {
        "name": "baseline",
        "qt_weights": [0.60, 0.10, 0.10, 0.10],  # PNC, ARCC, RBA, ENB
        "zirp_weights": [0.40, 0.20, 0.20, 0.20]  # CAKE, QRVO, CRON, PSEC
    },
    {
        "name": "qt_balanced",
        "qt_weights": [0.25, 0.25, 0.25, 0.25],
        "zirp_weights": [0.40, 0.20, 0.20, 0.20]
    },
    {
        "name": "qt_top2",
        "qt_weights": [0.50, 0.30, 0.10, 0.10],
        "zirp_weights": [0.40, 0.20, 0.20, 0.20]
    },
    {
        "name": "zirp_balanced",
        "qt_weights": [0.60, 0.10, 0.10, 0.10],
        "zirp_weights": [0.25, 0.25, 0.25, 0.25]
    },
    {
        "name": "zirp_cake_dominant",
        "qt_weights": [0.60, 0.10, 0.10, 0.10],
        "zirp_weights": [0.60, 0.15, 0.15, 0.10]
    },
    {
        "name": "all_balanced",
        "qt_weights": [0.25, 0.25, 0.25, 0.25],
        "zirp_weights": [0.25, 0.25, 0.25, 0.25]
    }
]


def modify_strategy_weights(qt_weights, zirp_weights):
    """Modify strategy file with new weights."""

    with open(STRATEGY_FILE, 'r') as f:
        code = f.read()

    # Replace QT weights
    qt_pairs = ['PNC_KBE', 'ARCC_AMLP', 'RBA_SMFG', 'ENB_WEC']
    for i, pair in enumerate(qt_pairs):
        # Find the pair definition and update weight
        old_pattern = f"'name': '{pair}'"
        if old_pattern in code:
            # Find the weight line after this pair
            pair_start = code.find(old_pattern)
            weight_start = code.find("'weight':", pair_start)
            weight_end = code.find("\n", weight_start)
            if weight_start != -1 and weight_end != -1:
                # Replace weight value
                old_weight_line = code[weight_start:weight_end]
                new_weight_line = f"'weight': {qt_weights[i]}"
                code = code.replace(old_weight_line, new_weight_line)

    # Replace ZIRP weights
    zirp_pairs = ['CAKE_URBN', 'QRVO-EWY', 'CRON-ITRI', 'PSEC_KIM']
    for i, pair in enumerate(zirp_pairs):
        old_pattern = f"'name': '{pair}'"
        if old_pattern in code:
            pair_start = code.find(old_pattern)
            weight_start = code.find("'weight':", pair_start)
            weight_end = code.find("\n", weight_start)
            if weight_start != -1 and weight_end != -1:
                old_weight_line = code[weight_start:weight_end]
                new_weight_line = f"'weight': {zirp_weights[i]}"
                code = code.replace(old_weight_line, new_weight_line)

    return code


def run_backtest(api, config_name, qt_weights, zirp_weights):
    """Run a single backtest with given weights."""

    print(f"\n{'='*60}")
    print(f"Testing: {config_name}")
    print(f"QT Weights: {qt_weights}")
    print(f"ZIRP Weights: {zirp_weights}")
    print(f"{'='*60}")

    # Modify strategy code
    modified_code = modify_strategy_weights(qt_weights, zirp_weights)

    # Upload to QC
    print(f"⏳ Uploading strategy to project {PROJECT_ID}...")
    upload_result = api._request("POST", f"files/update", json={
        "projectId": PROJECT_ID,
        "name": "main.py",
        "content": modified_code
    })

    if not upload_result.get("success"):
        print(f"❌ Upload failed: {upload_result}")
        return None

    # Compile
    print(f"⏳ Compiling...")
    compile_result = api._request("POST", f"projects/{PROJECT_ID}/compile")

    if not compile_result.get("success"):
        print(f"❌ Compile failed: {compile_result}")
        return None

    compile_id = compile_result.get("compileId")

    # Wait for compile
    time.sleep(3)

    # Run backtest
    print(f"⏳ Running backtest...")
    backtest_result = api._request("POST", f"backtests/create", json={
        "projectId": PROJECT_ID,
        "compileId": compile_id,
        "backtestName": f"WeightOpt_{config_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    })

    if not backtest_result.get("success"):
        print(f"❌ Backtest creation failed: {backtest_result}")
        return None

    backtest_id = backtest_result.get("backtestId")
    print(f"✅ Backtest submitted: {backtest_id}")

    # Poll for completion
    print(f"⏳ Waiting for completion...")
    max_wait = 300  # 5 minutes
    elapsed = 0

    while elapsed < max_wait:
        time.sleep(10)
        elapsed += 10

        status_result = api._request("GET", f"backtests/{PROJECT_ID}/read", params={"backtestId": backtest_id})

        if status_result.get("completed"):
            print(f"✅ Completed in {elapsed}s")

            # Extract metrics
            stats = status_result.get("statistics", {})
            sharpe = float(stats.get("sharpeRatio", 0))
            total_return = float(stats.get("totalNetProfit", 0))
            drawdown = float(stats.get("drawdown", 0))
            trades = int(stats.get("totalOrders", 0)) // 2

            print(f"\n📊 Results:")
            print(f"   Sharpe: {sharpe:.3f}")
            print(f"   Return: {total_return*100:.2f}%")
            print(f"   Drawdown: {drawdown*100:.2f}%")
            print(f"   Trades: {trades}")

            return {
                "config_name": config_name,
                "qt_weights": qt_weights,
                "zirp_weights": zirp_weights,
                "backtest_id": backtest_id,
                "metrics": {
                    "sharpe": sharpe,
                    "return": total_return,
                    "drawdown": drawdown,
                    "trades": trades
                }
            }

        print(f"   Status: {status_result.get('status', 'Unknown')}, Elapsed: {elapsed}s")

    print(f"❌ Timeout after {max_wait}s")
    return None


def main():
    """Run weight optimization."""

    print("🔧 Pair Weight Optimization")
    print("="*60)
    print(f"Project ID: {PROJECT_ID}")
    print(f"Configurations to test: {len(WEIGHT_CONFIGS)}")
    print("="*60)

    # Initialize API
    api = QuantConnectAPI()

    results = []

    for i, config in enumerate(WEIGHT_CONFIGS):
        print(f"\n[{i+1}/{len(WEIGHT_CONFIGS)}] {config['name']}")

        result = run_backtest(
            api,
            config['name'],
            config['qt_weights'],
            config['zirp_weights']
        )

        if result:
            results.append(result)

        # Rate limit
        if i < len(WEIGHT_CONFIGS) - 1:
            print("\n⏸️  Waiting 10s before next test...")
            time.sleep(10)

    # Save results
    print(f"\n{'='*60}")
    print("📊 OPTIMIZATION COMPLETE")
    print(f"{'='*60}")

    # Sort by Sharpe
    results_sorted = sorted(results, key=lambda x: x['metrics']['sharpe'], reverse=True)

    print(f"\n🏆 Results (ranked by Sharpe):\n")
    for i, result in enumerate(results_sorted):
        print(f"{i+1}. {result['config_name']:<20} Sharpe: {result['metrics']['sharpe']:.3f}  "
              f"Return: {result['metrics']['return']*100:6.2f}%  "
              f"DD: {result['metrics']['drawdown']*100:5.2f}%  "
              f"Trades: {result['metrics']['trades']}")

    # Save to file
    output = {
        "timestamp": datetime.now().isoformat(),
        "project_id": PROJECT_ID,
        "baseline_config": WEIGHT_CONFIGS[0],
        "results": results_sorted
    }

    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n💾 Results saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
