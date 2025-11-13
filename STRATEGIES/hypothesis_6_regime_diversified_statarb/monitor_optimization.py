#!/usr/bin/env python3
"""
Monitor H6 Optimization Progress

Polls QuantConnect API to check optimization status and display results.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add SCRIPTS to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "SCRIPTS"))
from qc_backtest import QuantConnectAPI

# Load optimization ID from iteration_state
STATE_FILE = Path(__file__).parent / "iteration_state.json"

def load_optimization_id():
    """Load optimization ID from iteration state."""
    with open(STATE_FILE, 'r') as f:
        state = json.load(f)

    opt_data = state.get('optimization_results', {}).get('weight_optimization', {})
    opt_id = opt_data.get('optimization_id')
    project_id = state['project']['project_id']

    if not opt_id:
        print("❌ No optimization ID found in iteration_state.json")
        sys.exit(1)

    return project_id, opt_id, opt_data


def monitor_optimization(project_id, opt_id, poll_interval=30, max_wait=7200):
    """Monitor optimization until completion."""

    api = QuantConnectAPI()

    print("🔍 H6 Optimization Monitor")
    print("="*60)
    print(f"Project ID: {project_id}")
    print(f"Optimization ID: {opt_id}")
    print(f"Poll interval: {poll_interval}s")
    print("="*60)

    elapsed = 0
    last_status = None

    while elapsed < max_wait:
        # Get optimization status
        result = api._request('GET', 'optimizations/read', params={
            'projectId': project_id,
            'optimizationId': opt_id
        })

        if not result.get('success'):
            print(f"\n❌ API error: {result}")
            time.sleep(poll_interval)
            elapsed += poll_interval
            continue

        opt = result.get('optimization', {})
        status = opt.get('status', 'unknown')

        # Print status update if changed
        if status != last_status:
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"\n[{timestamp}] Status: {status}")
            last_status = status

        # Check if complete
        if status == 'completed':
            print(f"\n{'='*60}")
            print("✅ OPTIMIZATION COMPLETE")
            print(f"{'='*60}")

            # Get backtests
            backtests = opt.get('backtests', {})
            print(f"\nTotal backtests: {len(backtests)}")

            # Find best result
            best_backtest = None
            best_sharpe = -999

            for bt_id, bt_data in backtests.items():
                sharpe = bt_data.get('sharpeRatio', -999)
                if sharpe > best_sharpe:
                    best_sharpe = sharpe
                    best_backtest = bt_data

            if best_backtest:
                print(f"\n🏆 BEST RESULT:")
                print(f"   Sharpe Ratio: {best_backtest.get('sharpeRatio', 'N/A'):.4f}")
                print(f"   Total Return: {best_backtest.get('totalPerformance', {}).get('portfolioStatistics', {}).get('totalNetProfit', 0)*100:.2f}%")
                print(f"   Drawdown: {best_backtest.get('totalPerformance', {}).get('portfolioStatistics', {}).get('drawdown', 0)*100:.2f}%")
                print(f"   Trades: {best_backtest.get('totalOrders', 0) // 2}")

                # Show parameters
                params = best_backtest.get('parameterSet', {})
                if params:
                    print(f"\n📊 Optimal Parameters:")
                    for param_name, param_value in params.items():
                        print(f"   {param_name}: {param_value}")

                # Save results
                save_results(project_id, opt_id, opt, best_backtest)

            return True

        elif status == 'error' or status == 'cancelled':
            print(f"\n❌ Optimization {status}")
            print(f"   Details: {opt}")
            return False

        # Still running - show progress
        backtests = opt.get('backtests', {})
        if backtests:
            completed = len([bt for bt in backtests.values() if bt.get('completed', False)])
            total = len(backtests)
            print(f"   Progress: {completed}/{total} backtests completed", end='\r')

        # Wait
        time.sleep(poll_interval)
        elapsed += poll_interval

    print(f"\n⚠️ Timeout after {max_wait}s ({max_wait//60} minutes)")
    print(f"   Optimization may still be running on QuantConnect")
    print(f"   Check: https://www.quantconnect.com/project/{project_id}")
    return False


def save_results(project_id, opt_id, optimization_data, best_backtest):
    """Save optimization results to iteration_state."""

    print(f"\n💾 Saving results to iteration_state.json...")

    with open(STATE_FILE, 'r') as f:
        state = json.load(f)

    # Update optimization results
    state['optimization_results']['weight_optimization'] = {
        'optimization_id': opt_id,
        'timestamp': datetime.now().isoformat(),
        'status': 'completed',
        'total_backtests': len(optimization_data.get('backtests', {})),
        'best_result': {
            'sharpe_ratio': best_backtest.get('sharpeRatio'),
            'total_return': best_backtest.get('totalPerformance', {}).get('portfolioStatistics', {}).get('totalNetProfit'),
            'drawdown': best_backtest.get('totalPerformance', {}).get('portfolioStatistics', {}).get('drawdown'),
            'trades': best_backtest.get('totalOrders', 0) // 2,
            'parameters': best_backtest.get('parameterSet', {})
        }
    }

    # Update phase
    state['current_phase'] = 'optimization_complete'
    if 'optimization' not in state.get('phases_completed', []):
        state['phases_completed'].append('optimization')

    # Update cost tracking
    state['cost_tracking']['backtests_run'] = state['cost_tracking'].get('backtests_run', 0) + len(optimization_data.get('backtests', {}))

    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

    print("✅ Results saved!")
    print(f"\n📝 Next step: Review results and update strategy with optimal parameters")


def main():
    """Main monitoring loop."""

    project_id, opt_id, opt_data = load_optimization_id()

    # Monitor
    success = monitor_optimization(project_id, opt_id, poll_interval=30, max_wait=7200)

    if success:
        print(f"\n✅ Optimization monitoring complete")
        print(f"   View full results: https://www.quantconnect.com/project/{project_id}")
    else:
        print(f"\n⚠️ Optimization did not complete within timeout")
        print(f"   Check QuantConnect console for status")
        sys.exit(1)


if __name__ == "__main__":
    main()
