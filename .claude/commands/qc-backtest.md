---
description: Run a backtest for the current hypothesis and make autonomous routing decision
---

Run a backtest on QuantConnect for the current hypothesis and automatically determine the next phase based on results.

This command will:
1. Read current hypothesis from iteration_state.json
2. Upload strategy file to QuantConnect (if needed)
3. Run backtest via API
4. Wait for completion
5. Analyze results with decision framework
6. Make autonomous routing decision
7. Update iteration_state.json
8. Log decision to decisions_log.md

**Usage**:
```
/qc-backtest
```

**Decision Framework**:
The command will automatically analyze results and decide:

- **PROCEED_TO_VALIDATION** - Sharpe >= 1.0 AND drawdown <= 20%
- **PROCEED_TO_OPTIMIZATION** - Sharpe >= 0.7 (decent performance)
- **ABANDON_HYPOTHESIS** - Sharpe < 0.5 (poor performance)
- **ESCALATE** - Too good (Sharpe > 3.0), too few trades (<10), or win rate > 80%

**Output**:
```
🚀 Running backtest for: RSI Mean Reversion
📦 Project: TestStrategy_v1 (ID: 12345)
⏳ Backtest submitted: abc123
✅ Backtest complete (15s)

📊 Results:
   Sharpe Ratio: 1.45
   Max Drawdown: 12%
   Total Return: 23%
   Win Rate: 62%
   Total Trades: 45

✅ DECISION: PROCEED_TO_VALIDATION
📝 Reason: Good performance, ready for OOS validation

📄 Updated: iteration_state.json
📝 Logged: decisions_log.md
```

**Manual Override**:
If you disagree with the autonomous decision:
```
/qc-backtest --override proceed_to_optimization
```

**Next Steps**:
- If PROCEED_TO_VALIDATION → Use `/qc-validate`
- If PROCEED_TO_OPTIMIZATION → Use `/qc-optimize`
- If ESCALATE → Review results manually, adjust strategy
- If ABANDON → Use `/qc-init` for new hypothesis
