---
description: Run parameter optimization for the current strategy
---

Run parameter optimization to find the best parameter combinations for the current strategy.

**⚠️ CRITICAL RULE: REUSE SAME PROJECT_ID FROM HYPOTHESIS**

**IMPERATIVE**: Use the existing project_id from iteration_state.json
- Do NOT create a new project for optimization
- Optimization runs on the SAME project created during /qc-init
- Keeps all work (backtests, optimizations) in one place

This command will:
1. Prompt for parameters to optimize
2. Generate parameter grid
3. Run multiple backtests via QuantConnect API (using EXISTING project_id)
4. Analyze results and rank by Sharpe ratio
5. Check for overfitting (parameter sensitivity)
6. Update iteration_state.json with best parameters
7. Log optimization results to decisions_log.md

**Usage**:
```
/qc-optimize
```

**Interactive Mode**:
You will be prompted for:
- Parameters to optimize (e.g., rsi_period, stop_loss_pct)
- Value ranges for each parameter
- Number of combinations to test (default: 5-10)

**Example**:
```
/qc-optimize

> Parameters to optimize: rsi_period, rsi_oversold, rsi_overbought
> rsi_period values: 10, 14, 20
> rsi_oversold values: 25, 30, 35
> rsi_overbought values: 65, 70, 75

Generating 27 parameter combinations...
```

**With Parameter File**:
```
/qc-optimize --params optimization_params.json
```

Where optimization_params.json contains:
```json
[
  {"rsi_period": 10, "rsi_oversold": 25, "rsi_overbought": 75},
  {"rsi_period": 14, "rsi_oversold": 30, "rsi_overbought": 70},
  {"rsi_period": 20, "rsi_oversold": 35, "rsi_overbought": 65}
]
```

**Decision Framework**:

After optimization, autonomous decisions:

- **improvement > 30%** → ESCALATE (suspicious improvement, possible overfitting)
- **parameter_sensitivity > 0.5** → USE_ROBUST_PARAMS (median of top quartile)
- **improvement > 5%** → PROCEED_TO_VALIDATION (with optimized params)
- **improvement < 5%** → PROCEED_TO_VALIDATION (with baseline params)

**Output**:
```
🔧 Running Optimization...
   Strategy: RSI Mean Reversion
   Parameters: rsi_period, rsi_oversold, rsi_overbought
   Combinations: 27

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏳ [1/27] Testing rsi_period=10, oversold=25, overbought=75
   ✅ Complete - Sharpe: 0.82, Return: 15%, Trades: 32

⏳ [2/27] Testing rsi_period=14, oversold=30, overbought=70
   ✅ Complete - Sharpe: 1.45, Return: 23%, Trades: 45

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 OPTIMIZATION RESULTS:

🏆 Best Parameters (by Sharpe):
   rsi_period: 14
   rsi_oversold: 30
   rsi_overbought: 70

   Performance:
   ├─ Sharpe: 1.45
   ├─ Return: 23%
   ├─ Drawdown: 12%
   └─ Trades: 45

📈 Statistics:
   ├─ Mean Sharpe: 1.12
   ├─ Max Sharpe: 1.45
   ├─ Min Sharpe: 0.68
   └─ Improvement: 78% vs baseline (0.82)

🔍 Robustness Check:
   ├─ Parameter Sensitivity: 0.32 (LOW ✅)
   ├─ Top Quartile Median: 1.38
   └─ Assessment: Robust performance across parameters

✅ DECISION: PROCEED_TO_VALIDATION
📝 Reason: Significant improvement (78%), low parameter sensitivity

📄 Updated: iteration_state.json (best_parameters saved)
📝 Logged: decisions_log.md
💾 Saved: optimization_results_20251109.json
```

**Overfitting Detection**:

The command checks for:
- **Too good improvement** (>30%) → Suspicious
- **Sharp peak** in parameter space → Overfitted
- **High sensitivity** to small parameter changes → Not robust

**Next Steps**:
- Review optimization_results.json for full data
- If PROCEED_TO_VALIDATION → Use `/qc-validate`
- If ESCALATE → Review results, consider simpler parameters

**Advanced Options**:
```
/qc-optimize --max-combinations 20    # Limit number of tests
/qc-optimize --parallel               # Run multiple backtests in parallel (future)
/qc-optimize --metric sortino         # Optimize by Sortino instead of Sharpe
```
