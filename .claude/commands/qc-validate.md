---
description: Run out-of-sample validation for the current strategy
---

Run out-of-sample (OOS) validation to test strategy generalization on unseen data.

**⚠️ CRITICAL RULE: REUSE SAME PROJECT_ID FROM HYPOTHESIS**

**IMPERATIVE**: Use the existing project_id from iteration_state.json
- Do NOT create a new project for validation
- Validation runs on the SAME project created during /qc-init
- Keeps entire hypothesis lifecycle in one project

**⚠️ AUTONOMOUS MODE: AUTO-CONFIGURE OOS PERIOD**

This command will:
1. Read current strategy and best parameters
2. **Auto-configure** OOS time period (no prompts)
   - If in-sample: 2022-2024 → OOS: 2024-2025
   - Use last 20-30% of data as OOS
3. Run OOS backtest via QuantConnect API (using EXISTING project_id)
4. Compare OOS vs in-sample performance
5. Check for degradation (Sharpe drop > 30% = fail)
6. Make final validation decision
7. Update iteration_state.json
8. **Auto-proceed or STOP** based on result
9. Log validation results to decisions_log.md

**User intervention**: NONE (unless validation fails - blocker)

**Usage**:
```
/qc-validate
```

**Automatic OOS Period Selection**:
The command will automatically select an OOS period that doesn't overlap with the in-sample period:

- In-sample: 2023-01-01 to 2023-12-31
- Out-of-sample: 2024-01-01 to 2024-12-31

**Manual OOS Period**:
```
/qc-validate --oos-start 2024-01-01 --oos-end 2024-12-31
```

**Decision Framework**:

Based on OOS degradation:

- **oos_degradation > 50%** → RETRY_OPTIMIZATION or ABANDON
- **oos_degradation > 30%** → ESCALATE (significant degradation)
- **oos_sharpe >= 1.0** → STRATEGY_COMPLETE ✅
- **else** → STRATEGY_VALIDATED_SUBOPTIMAL

Where degradation = (in_sample_sharpe - oos_sharpe) / in_sample_sharpe

**Output**:
```
🧪 Running Out-of-Sample Validation...
   Strategy: RSI Mean Reversion
   Parameters: rsi_period=14, oversold=30, overbought=70

📅 Time Periods:
   In-Sample (IS): 2023-01-01 to 2023-12-31
   Out-of-Sample (OOS): 2024-01-01 to 2024-12-31

⏳ Running OOS backtest...
   ✅ Complete (18s)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 VALIDATION RESULTS:

Performance Comparison:
┌────────────────┬──────────┬──────────┬──────────────┐
│ Metric         │ In-Sample│Out-Sample│ Degradation  │
├────────────────┼──────────┼──────────┼──────────────┤
│ Sharpe Ratio   │   1.45   │   1.28   │    11.7% ✅  │
│ Total Return   │   23%    │   18%    │    21.7%     │
│ Max Drawdown   │   12%    │   15%    │    25.0%     │
│ Win Rate       │   62%    │   58%    │     6.5%     │
│ Total Trades   │   45     │   38     │    15.6%     │
└────────────────┴──────────┴──────────┴──────────────┘

🔍 Degradation Analysis:
   ├─ Sharpe Degradation: 11.7% (ACCEPTABLE ✅)
   ├─ Return Degradation: 21.7% (ACCEPTABLE ✅)
   ├─ Drawdown Increase: 25.0% (ACCEPTABLE ✅)
   └─ Trade Count: Similar (45 → 38)

✅ Generalization: GOOD
   Strategy performs consistently on unseen data

✅ DECISION: STRATEGY_COMPLETE
📝 Reason: OOS Sharpe 1.28 >= 1.0, degradation < 30%

📄 Updated: iteration_state.json (validation: complete)
📝 Logged: decisions_log.md
🎉 Strategy validated and ready for deployment consideration

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 NEXT STEPS:

1. ✅ Review validation results
2. 📸 Capture screenshots from QuantConnect UI for visual validation
3. 📊 Compare IS vs OOS equity curves visually
4. 🔍 Check for regime changes between periods
5. 📝 Document strategy in strategy_report.md
6. 🚀 Consider paper trading before live deployment

Use these commands:
  /qc-report     - Generate complete strategy report
  /qc-init       - Start new hypothesis
```

**Visual Validation Reminder**:
```
⚠️  IMPORTANT: Statistical validation passed, but you should:
   1. Open QuantConnect UI
   2. Compare IS and OOS equity curves visually
   3. Check for visual overfitting signs
   4. Verify trade distribution across time

   Statistical metrics can be misleading without visual confirmation!
```

**Degradation Thresholds**:

- **< 20% degradation** → Excellent generalization ✅
- **20-30% degradation** → Acceptable ⚠️
- **30-50% degradation** → Poor generalization, needs work ⚠️⚠️
- **> 50% degradation** → Failed validation ❌

**Failure Scenarios**:
```
❌ DECISION: RETRY_OPTIMIZATION
📝 Reason: OOS degradation 52% (> 50%)

Suggestions:
  - Simplify strategy (remove parameters)
  - Use more robust indicators
  - Consider walk-forward optimization
  - Test on different market regimes
```

**Complete Strategy**:
```
🎉 STRATEGY VALIDATED AND COMPLETE

Summary:
├─ Hypothesis: RSI Mean Reversion with Trend Filter
├─ In-Sample Sharpe: 1.45
├─ Out-of-Sample Sharpe: 1.28
├─ Degradation: 11.7% (Excellent)
├─ Total Trades (OOS): 38
└─ Status: READY FOR DEPLOYMENT CONSIDERATION

Next Actions:
1. Generate full report: /qc-report
2. Start paper trading
3. Monitor for 30 days before live

---

## Git Integration (AUTOMATIC)

After validation completes, **automatically commit AND tag if successful**:

```bash
# Extract validation metrics
IS_SHARPE=$(cat iteration_state.json | grep '"is_sharpe"' | sed 's/[^0-9.-]*//g')
OOS_SHARPE=$(cat iteration_state.json | grep '"oos_sharpe"' | sed 's/[^0-9.-]*//g')
DEGRADATION=$(cat iteration_state.json | grep '"degradation"' | sed 's/[^0-9.-]*//g')
OOS_BACKTEST_ID=$(cat iteration_state.json | grep '"oos_backtest_id"' | sed 's/.*: "//;s/",//')
DECISION=$(cat iteration_state.json | grep 'validation.*decision' | sed 's/.*: "//;s/",//')
HYPOTHESIS_NAME=$(cat iteration_state.json | grep '"name"' | head -1 | sed 's/.*: "//;s/",//')

# Stage files
git add iteration_state.json oos_results*.json decisions_log.md

# Commit with structured message
git commit -m "$(cat <<EOF
validate: Out-of-sample validation $(echo ${DECISION} | tr '[:lower:]' '[:upper:]')

In-Sample Performance:
- Sharpe Ratio: ${IS_SHARPE}

Out-of-Sample Performance:
- Sharpe Ratio: ${OOS_SHARPE}
- Degradation: ${DEGRADATION}%
- Backtest ID: ${OOS_BACKTEST_ID}

Decision: ${DECISION}
Status: $([ "${DECISION}" = "strategy_complete" ] && echo "READY FOR DEPLOYMENT" || echo "NEEDS REVIEW")
Phase: validation → complete
Iteration: $(cat iteration_state.json | grep '"iteration_count"' | sed 's/[^0-9]*//g')

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# If validation PASSED, create git tag
if [ "${DECISION}" = "strategy_complete" ] || [ "${DEGRADATION}" -lt 30 ]; then
    VERSION="v1.0.0-$(echo ${HYPOTHESIS_NAME} | tr ' ' '-' | tr '[:upper:]' '[:lower:]')"

    git tag -a "${VERSION}" -m "Validated Strategy - ${HYPOTHESIS_NAME}
OOS Sharpe: ${OOS_SHARPE}
Degradation: ${DEGRADATION}%
Validated: $(date +%Y-%m-%d)
Status: Ready for paper trading"

    echo "🏷️  Created tag: ${VERSION}"
fi

echo "✅ Committed validation results to git"
echo "📝 Commit: $(git log -1 --oneline)"
```

**Tag created only if**:
- Decision = STRATEGY_COMPLETE, OR
- Degradation < 30% (acceptable performance)
4. Document in strategy library
```
