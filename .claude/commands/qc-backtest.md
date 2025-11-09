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
9. **Commit backtest results to git automatically**

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

---

## Git Integration (AUTOMATIC)

After backtest completes and results are logged, **automatically commit**:

```bash
# Extract metrics from iteration_state.json
SHARPE=$(cat iteration_state.json | grep '"sharpe_ratio"' | head -1 | sed 's/[^0-9.-]*//g')
TRADES=$(cat iteration_state.json | grep '"total_trades"' | head -1 | sed 's/[^0-9]*//g')
RETURN=$(cat iteration_state.json | grep '"total_return"' | head -1 | sed 's/[^0-9.-]*//g')
DECISION=$(cat iteration_state.json | grep '"decision"' | head -1 | sed 's/.*: "//;s/",//')
REASON=$(cat iteration_state.json | grep '"reason"' | head -1 | sed 's/.*: "//;s/",//')
BACKTEST_ID=$(cat iteration_state.json | grep '"backtest_id"' | head -1 | sed 's/.*: "//;s/",//')
ITERATION=$(cat iteration_state.json | grep '"iteration_count"' | head -1 | sed 's/[^0-9]*//g')

# Stage files
git add iteration_state.json decisions_log.md

# Commit with structured message including metrics
git commit -m "$(cat <<EOF
backtest: Complete backtest iteration ${ITERATION}

Results:
- Sharpe Ratio: ${SHARPE}
- Total Return: ${RETURN}%
- Total Trades: ${TRADES}
- Backtest ID: ${BACKTEST_ID}

Decision: ${DECISION}
Reason: ${REASON}

Phase: backtest → $(echo ${DECISION} | tr '[:upper:]' '[:lower:]' | sed 's/_/ /g')
Iteration: ${ITERATION}

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

echo "✅ Committed backtest results to git"
echo "📝 Commit: $(git log -1 --oneline)"
```
