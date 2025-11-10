---
description: Run a backtest for the current hypothesis and make autonomous routing decision (project)
---

Run a backtest on QuantConnect for the current hypothesis and automatically determine the next phase based on results.

This command implements Phase 2 (Implementation) and Phase 3 (Backtest + Decision) of the 5-phase autonomous workflow.

## What This Command Does

1. Reads current hypothesis from iteration_state.json
2. Loads QuantConnect Skill for strategy implementation guidance
3. Generates strategy code from hypothesis (Phase 2)
4. Validates implementation (syntax, entry/exit logic, risk management)
5. Creates/updates QuantConnect project via API
6. Uploads strategy file to project
7. Runs backtest via qc_backtest.py wrapper
8. Waits for backtest completion
9. Parses results (Sharpe, drawdown, trades, etc.)
10. Applies Phase 3 decision framework
11. Makes autonomous routing decision
12. Updates iteration_state.json with results and decision
13. Commits to git with structured message including metrics

## Usage

```bash
/qc-backtest
```

No parameters required - reads everything from iteration_state.json.

## Decision Framework (Phase 3)

The command applies 4-tier threshold system to determine next action:

### Tier 1: ABANDON_HYPOTHESIS
- Sharpe < 0.5 (below minimum_viable)
- OR max_drawdown > 0.40
- OR total_trades < 30
- OR fatal implementation errors

### Tier 2: PROCEED_TO_OPTIMIZATION
- Sharpe >= 0.7 (optimization_worthy)
- AND max_drawdown <= 0.35
- AND total_trades >= 50
- Decent performance, worth optimizing

### Tier 3: PROCEED_TO_VALIDATION
- Sharpe >= 1.0 (production_ready)
- AND max_drawdown <= 0.30
- AND total_trades >= 100
- Strong baseline, can skip optimization

### Tier 4: ESCALATE_TO_HUMAN
- Sharpe > 3.0 (too_perfect_sharpe - overfitting signal)
- OR total_trades < 20 (too_few_trades)
- OR win_rate > 0.75 (win_rate_too_high)
- Suspicious results, needs human review

### Edge Cases
- If Sharpe >= 0.5 but < 0.7: PROCEED_TO_OPTIMIZATION (try to improve)
- If iteration > max_iterations: ABANDON_HYPOTHESIS (too many attempts)

## Implementation Steps

When this command is executed, perform these steps:

### Step 1: Read Current State

```bash
# Read iteration_state.json
HYPOTHESIS_NAME=$(cat iteration_state.json | jq -r '.hypothesis.name')
HYPOTHESIS_DESC=$(cat iteration_state.json | jq -r '.hypothesis.description')
HYPOTHESIS_RATIONALE=$(cat iteration_state.json | jq -r '.hypothesis.rationale')
PROJECT_ID=$(cat iteration_state.json | jq -r '.project.project_id')
ITERATION=$(cat iteration_state.json | jq -r '.workflow.iteration')
```

### Step 2: Load QuantConnect Skill

Load the QuantConnect skill to access:
- Strategy templates
- Indicator usage examples
- Entry/exit logic patterns
- Risk management best practices
- Common error patterns (NoneType checks, off-by-one)

### Step 3: Implement Strategy (Phase 2)

Generate strategy code based on hypothesis:

```python
# File: {hypothesis_name_slug}.py
# Template structure:
class HypothesisStrategy(QCAlgorithm):
    def Initialize(self):
        # Set dates, cash, resolution
        # Add equities/assets
        # Configure indicators
        # Set warmup period
        
    def OnData(self, data):
        # Entry logic (from hypothesis)
        # Exit logic (from hypothesis)
        # Risk management (stop loss, position sizing)
        
# Error handling:
# - Check for None before accessing data
# - Validate indicators are ready
# - Handle missing data gracefully
```

### Step 4: Validate Implementation

Check for common issues:
- Syntax errors
- Missing entry logic
- Missing exit logic
- Missing risk management
- NoneType access (data[symbol] without checking)
- Off-by-one errors in loops
- Indicator warmup not handled

If validation fails:
- Increment fix_attempts
- If fix_attempts >= 3: ESCALATE_TO_HUMAN
- Otherwise: Fix and retry

### Step 5: Create/Update QC Project

```bash
# If PROJECT_ID is null, create new project
if [ "$PROJECT_ID" == "null" ]; then
    python SCRIPTS/qc_backtest.py --create --name "${HYPOTHESIS_NAME}_$(date +%Y%m%d)" --output project_result.json
    PROJECT_ID=$(cat project_result.json | jq -r '.projects.projects[0].projectId')
    PROJECT_URL="https://www.quantconnect.com/project/${PROJECT_ID}"
    
    # Update iteration_state.json:
    # project.project_id = $PROJECT_ID
    # project.project_name = ...
    # project.strategy_file = ...
    # project.qc_url = $PROJECT_URL
fi
```

### Step 6: Upload Strategy and Run Backtest

```bash
# Upload strategy file to project (qc_backtest.py handles this)
# Run backtest
python SCRIPTS/qc_backtest.py --run \
    --name "${HYPOTHESIS_NAME}" \
    --file "${STRATEGY_FILE}" \
    --output backtest_result.json

# Check if backtest succeeded
if [ $? -ne 0 ]; then
    echo "ERROR: Backtest failed"
    # Update iteration_state.json with error
    # ESCALATE_TO_HUMAN or retry
fi
```

### Step 7: Parse Results

```bash
# Extract metrics from backtest_result.json
BACKTEST_ID=$(cat backtest_result.json | jq -r '.backtest_id')
SHARPE=$(cat backtest_result.json | jq -r '.performance.sharpe_ratio')
MAX_DRAWDOWN=$(cat backtest_result.json | jq -r '.performance.max_drawdown')
TOTAL_RETURN=$(cat backtest_result.json | jq -r '.performance.total_return')
TOTAL_TRADES=$(cat backtest_result.json | jq -r '.performance.total_trades')
WIN_RATE=$(cat backtest_result.json | jq -r '.performance.win_rate')
```

### Step 8: Apply Decision Framework

**Use decision_logic.py module for consistent, tested decision-making:**

```python
# Call decision_logic.py module to evaluate backtest results
python3 << 'PYTHON_EOF'
import json
import sys
sys.path.insert(0, 'SCRIPTS')
from decision_logic import evaluate_backtest

# Load backtest results
with open('PROJECT_LOGS/backtest_result.json', 'r') as f:
    results = json.load(f)

# Load thresholds from iteration_state.json
with open('iteration_state.json', 'r') as f:
    state = json.load(f)

performance = results['performance']
thresholds = state['thresholds']

# Evaluate using tested decision framework
decision, reason, details = evaluate_backtest(performance, thresholds)

# Output for bash to capture
output = {
    'decision': decision,
    'reason': reason,
    'details': details
}

print(json.dumps(output, indent=2))
PYTHON_EOF
```

**Alternative: Simple bash wrapper**

```bash
# Create Python script to call decision_logic
cat > /tmp/evaluate_decision.py << 'EOF'
import json
import sys
sys.path.insert(0, 'SCRIPTS')
from decision_logic import evaluate_backtest

with open('PROJECT_LOGS/backtest_result.json') as f:
    results = json.load(f)
with open('iteration_state.json') as f:
    state = json.load(f)

decision, reason, details = evaluate_backtest(
    results['performance'],
    state['thresholds']
)

print(f"DECISION={decision}")
print(f"REASON={reason}")
EOF

# Run decision logic
python3 /tmp/evaluate_decision.py > /tmp/decision_output.txt

# Parse output
source /tmp/decision_output.txt
echo "Decision: $DECISION"
echo "Reason: $REASON"
```

### Step 9: Update iteration_state.json

```bash
# Update phase_results.backtest section
# - completed: true
# - timestamp: now
# - backtest_id: $BACKTEST_ID
# - performance: {sharpe, drawdown, return, trades, win_rate}
# - decision: $DECISION
# - decision_reason: $REASON

# Update workflow section
# - current_phase: based on decision
# - iteration: increment if iterating
# - updated_at: now

# Update decisions_log
# Append: {phase: "backtest", decision: $DECISION, reason: $REASON, timestamp: now}

# Update cost_tracking
# - api_calls: increment
# - backtests_run: increment

# Update next_action based on decision
```

### Step 10: Git Commit

```bash
git add iteration_state.json

# Structured commit message
git commit -m "backtest: Complete iteration ${ITERATION} - ${DECISION}

Results:
- Sharpe Ratio: ${SHARPE}
- Max Drawdown: ${MAX_DRAWDOWN}
- Total Return: ${TOTAL_RETURN}
- Total Trades: ${TOTAL_TRADES}
- Win Rate: ${WIN_RATE}
- Backtest ID: ${BACKTEST_ID}

Decision: ${DECISION}
Reason: ${REASON}

Phase: backtest → $(echo ${DECISION} | tr '[:upper:]' '[:lower:]' | sed 's/_/ /g')
Iteration: ${ITERATION}

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 11: Display Summary

```
✅ Backtest complete!

Hypothesis: {name}
Iteration: {iteration}

📊 Results:
  Sharpe Ratio: {sharpe}
  Max Drawdown: {drawdown}%
  Total Return: {return}%
  Total Trades: {trades}
  Win Rate: {win_rate}%
  
✅ DECISION: {decision}
📝 Reason: {reason}

Next Action:
- PROCEED_TO_OPTIMIZATION → Run /qc-optimize
- PROCEED_TO_VALIDATION → Run /qc-validate
- ABANDON_HYPOTHESIS → Run /qc-init for new hypothesis
- ESCALATE_TO_HUMAN → Review results manually
```

## Notes

- Automatically loads QuantConnect Skill for implementation guidance
- Decision framework uses 4-tier thresholds from iteration_state.json
- Git commit message includes all key metrics for audit trail
- Overfitting signals checked before performance thresholds
- Implementation validation prevents common bugs (NoneType, off-by-one)
- Max 3 fix attempts before escalating to human

## Next Steps

Based on decision:
- **PROCEED_TO_OPTIMIZATION**: Run `/qc-optimize` to improve parameters
- **PROCEED_TO_VALIDATION**: Run `/qc-validate` for out-of-sample testing
- **ABANDON_HYPOTHESIS**: Run `/qc-init` to start new hypothesis
- **ESCALATE_TO_HUMAN**: Review results, adjust strategy, rerun backtest

Corresponds to Week 1 Implementation checklist items:
- "Create /qc-backtest command (Phase 2 & 3)"
- "Load QuantConnect Skill"
- "Generate strategy code from hypothesis"
- "Evaluate backtest results (Phase 3 decision logic)"
