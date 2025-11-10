#!/usr/bin/env python3
"""
Run backtest for current hypothesis with autonomous decision framework
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Import QC API wrapper
from qc_backtest import QuantConnectAPI, find_project_by_name

def load_iteration_state():
    """Load current hypothesis from iteration_state.json"""
    with open("iteration_state.json", "r") as f:
        return json.load(f)

def save_iteration_state(state):
    """Save updated iteration state"""
    state["metadata"]["updated_at"] = datetime.now().isoformat() + "Z"
    with open("iteration_state.json", "w") as f:
        json.dump(state, f, indent=2)
    print("✅ Updated iteration_state.json")

def autonomous_decision(metrics):
    """
    Apply autonomous decision framework based on backtest results

    Decision hierarchy:
    1. ESCALATE - Suspicious metrics (overfitting indicators)
    2. ABANDON_HYPOTHESIS - Poor performance
    3. PROCEED_TO_VALIDATION - Excellent performance
    4. PROCEED_TO_OPTIMIZATION - Decent performance
    """
    performance = metrics["performance"]
    trading = metrics["trading"]

    sharpe = performance["sharpe_ratio"]
    max_dd = performance["max_drawdown"]
    total_trades = trading["total_trades"]
    win_rate = performance["win_rate"]
    total_return = performance["total_return"]

    # ESCALATE: Too few trades
    if total_trades < 10:
        return {
            "decision": "escalate",
            "reason": f"Too few trades ({total_trades} < 10), insufficient data for evaluation",
            "next_phase": "review"
        }

    # ESCALATE: Suspiciously high Sharpe
    if sharpe > 3.0:
        return {
            "decision": "escalate",
            "reason": f"Sharpe ratio too high ({sharpe:.2f} > 3.0), likely overfitting",
            "next_phase": "review"
        }

    # ESCALATE: Suspiciously high win rate
    if win_rate > 0.80 and total_trades >= 10:
        return {
            "decision": "escalate",
            "reason": f"Win rate too high ({win_rate:.1%} > 80%), possible overfitting",
            "next_phase": "review"
        }

    # ABANDON: Poor performance
    if sharpe < 0.5:
        return {
            "decision": "abandon_hypothesis",
            "reason": f"Poor performance (Sharpe {sharpe:.2f} < 0.5)",
            "next_phase": "abandoned"
        }

    # PROCEED TO VALIDATION: Excellent performance
    if sharpe >= 1.0 and max_dd <= 0.20:
        return {
            "decision": "proceed_to_validation",
            "reason": f"Good performance (Sharpe {sharpe:.2f}, DD {max_dd:.1%}), ready for OOS validation",
            "next_phase": "validation"
        }

    # PROCEED TO OPTIMIZATION: Decent performance
    if sharpe >= 0.7:
        return {
            "decision": "proceed_to_optimization",
            "reason": f"Decent performance (Sharpe {sharpe:.2f}), optimize parameters",
            "next_phase": "optimization"
        }

    # DEFAULT: Try optimization
    return {
        "decision": "proceed_to_optimization",
        "reason": f"Marginal performance (Sharpe {sharpe:.2f}), attempt optimization",
        "next_phase": "optimization"
    }

def main():
    print("=" * 63)
    print("🚀 QUANTCONNECT BACKTEST - AUTONOMOUS WORKFLOW")
    print("=" * 63)
    print()

    # Load current hypothesis
    state = load_iteration_state()
    hypothesis = state["current_hypothesis"]
    project_config = state["project"]

    print(f"📊 Hypothesis: {hypothesis['name']}")
    print(f"📝 Description: {hypothesis['description']}")
    print(f"🔬 Strategy File: {project_config['strategy_file']}")
    print()

    # Initialize API
    print("🔐 Initializing QuantConnect API...")
    api = QuantConnectAPI()
    print("✅ API initialized")
    print()

    # Find or create project
    project_name = project_config["project_name"]
    project_id = project_config.get("project_id")

    if not project_id:
        print(f"🔍 Searching for project: {project_name}")
        project_id = find_project_by_name(api, project_name)

        if project_id:
            print(f"✅ Found existing project: {project_id}")
        else:
            print(f"📦 Creating new project: {project_name}")
            result = api.create_project(project_name, language="Py")
            if not result.get("success"):
                print(f"❌ Failed to create project: {result.get('errors')}")
                sys.exit(1)
            project_id = result["projects"][0]["projectId"]
            print(f"✅ Created project: {project_id}")

            # Update state
            state["project"]["project_id"] = project_id
            save_iteration_state(state)
    else:
        print(f"📦 Using existing project: {project_id}")

    print()

    # Upload strategy file
    strategy_file = project_config["strategy_file"]
    print(f"📤 Uploading strategy file: {strategy_file}")

    with open(strategy_file, "r") as f:
        strategy_content = f.read()

    result = api.upload_file(project_id, "main.py", strategy_content)
    if not result.get("success"):
        print(f"❌ Failed to upload file: {result.get('errors')}")
        sys.exit(1)

    print("✅ Strategy file uploaded")
    print()

    # Compile project
    print("🔨 Compiling project...")
    result = api.compile_project(project_id)
    if not result.get("success"):
        print(f"❌ Compilation failed: {result.get('errors')}")
        sys.exit(1)

    compile_id = result.get("compileId")
    print(f"✅ Compilation successful: {compile_id}")
    print()

    # Submit backtest
    backtest_name = f"Backtest_H{hypothesis['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"🚀 Submitting backtest: {backtest_name}")

    result = api.create_backtest(project_id, compile_id, backtest_name)
    if not result.get("success"):
        print(f"❌ Backtest submission failed: {result.get('errors')}")
        sys.exit(1)

    backtest_id = result.get("backtestId")
    print(f"✅ Backtest submitted: {backtest_id}")
    print()

    # Wait for completion and get results
    print("⏳ Waiting for backtest to complete...")
    metrics = api.read_backtest_results(project_id, backtest_id)

    if not metrics.get("success"):
        print(f"❌ Backtest failed: {metrics.get('error')}")
        if metrics.get("stacktrace"):
            print(f"\n📋 Stacktrace:\n{metrics.get('stacktrace')}")
        sys.exit(1)

    print("✅ Backtest complete!")
    print()

    # Display results
    print("=" * 63)
    print("📊 BACKTEST RESULTS")
    print("=" * 63)
    print()

    perf = metrics["performance"]
    trading = metrics["trading"]
    risk = metrics["risk"]

    print(f"Performance:")
    print(f"  • Sharpe Ratio: {perf['sharpe_ratio']:.2f}")
    print(f"  • Total Return: {perf['total_return']:.2%}")
    print(f"  • Max Drawdown: {perf['max_drawdown']:.2%}")
    print(f"  • Annual Return: {perf['annual_return']:.2%}")
    print(f"  • Win Rate: {perf['win_rate']:.1%}")
    print()

    print(f"Trading:")
    print(f"  • Total Trades: {trading['total_trades']}")
    print(f"  • Average Win: {trading['average_win']:.2%}")
    print(f"  • Average Loss: {trading['average_loss']:.2%}")
    print(f"  • Profit/Loss Ratio: {trading['profit_loss_ratio']:.2f}")
    print()

    print(f"Risk:")
    print(f"  • Alpha: {risk['alpha']:.2f}")
    print(f"  • Beta: {risk['beta']:.2f}")
    print(f"  • Volatility: {risk['volatility']:.2%}")
    print()

    # Apply autonomous decision framework
    print("=" * 63)
    print("🤖 AUTONOMOUS DECISION FRAMEWORK")
    print("=" * 63)
    print()

    decision = autonomous_decision(metrics)

    print(f"✅ DECISION: {decision['decision'].upper()}")
    print(f"📝 Reason: {decision['reason']}")
    print(f"🎯 Next Phase: {decision['next_phase']}")
    print()

    # Update iteration state
    state["iteration_count"] += 1
    state["backtest_results"] = {
        "backtest_id": backtest_id,
        "completed": True,
        "performance": {
            "sharpe_ratio": perf["sharpe_ratio"],
            "max_drawdown": perf["max_drawdown"],
            "total_return": perf["total_return"],
            "total_trades": trading["total_trades"]
        },
        "decision": decision["decision"],
        "reason": decision["reason"]
    }

    state["current_phase"] = decision["next_phase"]
    if "backtest" not in state["phases_completed"]:
        state["phases_completed"].append("backtest")

    state["cost_tracking"]["backtests_run"] += 1
    state["cost_tracking"]["api_calls"] += 5  # Approximate: compile, backtest, 3x status checks

    # Add to decisions log
    decision_entry = {
        "timestamp": datetime.now().isoformat() + "Z",
        "phase": "backtest",
        "decision": decision["decision"],
        "reason": decision["reason"],
        "metrics": {
            "sharpe_ratio": perf["sharpe_ratio"],
            "total_trades": trading["total_trades"],
            "total_return": perf["total_return"],
            "max_drawdown": perf["max_drawdown"]
        },
        "next_action": decision["next_phase"]
    }
    state["decisions_log"].append(decision_entry)

    save_iteration_state(state)

    # Update decisions_log.md
    with open("decisions_log.md", "a") as f:
        f.write(f"\n### {decision_entry['timestamp']} - Backtest Complete (Iteration {state['iteration_count']})\n\n")
        f.write(f"**Phase**: Backtest\n")
        f.write(f"**Hypothesis**: {hypothesis['name']}\n")
        f.write(f"**Backtest ID**: {backtest_id}\n\n")
        f.write(f"**Results**:\n")
        f.write(f"- Sharpe Ratio: {perf['sharpe_ratio']:.2f}\n")
        f.write(f"- Max Drawdown: {perf['max_drawdown']:.1%}\n")
        f.write(f"- Total Return: {perf['total_return']:.1%}\n")
        f.write(f"- Win Rate: {perf['win_rate']:.1%}\n")
        f.write(f"- Total Trades: {trading['total_trades']}\n\n")
        f.write(f"**Decision**: `{decision['decision'].upper()}`\n\n")
        f.write(f"**Reasoning**: {decision['reason']}\n\n")
        f.write(f"**Next Action**: {decision['next_phase']}\n\n")
        f.write(f"**Iteration Status**: {state['iteration_count']}/{state['max_iterations']}\n\n")
        f.write("---\n")

    print("✅ Updated decisions_log.md")
    print()

    # Show next steps
    print("=" * 63)
    print("📋 NEXT STEPS")
    print("=" * 63)
    print()

    if decision["decision"] == "proceed_to_validation":
        print("✅ Strategy performed well!")
        print("🎯 Next: Run out-of-sample validation")
        print("   Command: /qc-validate")
    elif decision["decision"] == "proceed_to_optimization":
        print("📊 Strategy shows promise")
        print("🎯 Next: Optimize parameters")
        print("   Command: /qc-optimize")
    elif decision["decision"] == "escalate":
        print("⚠️  Manual review required")
        print("🎯 Review results and adjust strategy if needed")
    elif decision["decision"] == "abandon_hypothesis":
        print("❌ Strategy underperformed")
        print("🎯 Consider new hypothesis")
        print("   Command: /qc-init")

    print()
    print("=" * 63)

    return 0

if __name__ == "__main__":
    sys.exit(main())
