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

**⚠️ AUTONOMOUS MODE: AUTO-FIX ERRORS WITHOUT USER INTERVENTION**

Check for common issues:
- Syntax errors
- Missing entry logic
- Missing exit logic
- Missing risk management
- NoneType access (data[symbol] without checking)
- Off-by-one errors in loops
- Indicator warmup not handled

If validation fails:
- **Automatically fix** the issue
- Increment fix_attempts
- Retry backtest
- If fix_attempts >= 3: **THEN** ESCALATE_TO_HUMAN (blocker)
- Otherwise: Continue autonomously

### Step 5: Create/Update QC Project

**⚠️ CRITICAL RULE: ONE PROJECT ID PER HYPOTHESIS**

**IMPERATIVE**: Reuse the SAME project_id for:
- All backtests of this hypothesis
- All optimizations of this hypothesis
- All validations of this hypothesis

**ONLY create new project if**:
- project_id is null (first time)
- User explicitly requests new project
- Major strategy rewrite (not bug fixes)

```bash
# If PROJECT_ID is null, create new project ONLY ONCE
if [ "$PROJECT_ID" == "null" ]; then
    python SCRIPTS/qc_backtest.py --create --name "${HYPOTHESIS_NAME}" --output project_result.json
    PROJECT_ID=$(cat project_result.json | jq -r '.projects.projects[0].projectId')
    PROJECT_URL="https://www.quantconnect.com/project/${PROJECT_ID}"

    # Update iteration_state.json with project_id (SAVE THIS!)
    # project.project_id = $PROJECT_ID
    # project.project_name = ...
    # project.strategy_file = ...
    # project.qc_url = $PROJECT_URL
fi

# For ALL subsequent backtests: REUSE existing PROJECT_ID
# Update code in existing project, don't create new one
```

### Step 6: Upload Strategy and Run Backtest

**⚠️ CRITICAL: Always use --project-id flag to reuse existing project**

```bash
# ALWAYS pass existing project_id to reuse the same project
# This updates code in existing project instead of creating new one
python SCRIPTS/qc_backtest.py --run \
    --project-id "${PROJECT_ID}" \
    --name "Backtest_iteration_${ITERATION}" \
    --file "${STRATEGY_FILE}" \
    --output backtest_result.json

# Check if backtest succeeded
if [ $? -ne 0 ]; then
    echo "ERROR: Backtest failed"
    # Update iteration_state.json with error
    # ESCALATE_TO_HUMAN or retry
fi
```

**Project ID Lifecycle**:
- `/qc-init` → Creates project, saves PROJECT_ID to iteration_state.json
- `/qc-backtest` → Reuses PROJECT_ID (updates code, runs new backtest)
- `/qc-optimize` → Reuses PROJECT_ID (runs optimization)
- `/qc-validate` → Reuses PROJECT_ID (runs validation)

**Result**: One hypothesis = One project with complete history

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

```bash
# Decision logic (pseudocode - implement in actual command)
DECISION="UNKNOWN"
REASON=""

# Check overfitting signals first
if (( $(echo "$SHARPE > 3.0" | bc -l) )); then
    DECISION="ESCALATE_TO_HUMAN"
    REASON="Sharpe ratio too perfect ($SHARPE > 3.0), possible overfitting"
elif (( $TOTAL_TRADES < 20 )); then
    DECISION="ESCALATE_TO_HUMAN"
    REASON="Too few trades ($TOTAL_TRADES < 20), unreliable statistics"
elif (( $(echo "$WIN_RATE > 0.75" | bc -l) )); then
    DECISION="ESCALATE_TO_HUMAN"
    REASON="Win rate suspiciously high ($WIN_RATE > 0.75)"
    
# Check minimum viable
elif (( $(echo "$SHARPE < 0.5" | bc -l) )); then
    DECISION="ABANDON_HYPOTHESIS"
    REASON="Sharpe ratio below minimum viable ($SHARPE < 0.5)"
elif (( $(echo "$MAX_DRAWDOWN > 0.40" | bc -l) )); then
    DECISION="ABANDON_HYPOTHESIS"
    REASON="Max drawdown too high ($MAX_DRAWDOWN > 0.40)"
elif (( $TOTAL_TRADES < 30 )); then
    DECISION="ABANDON_HYPOTHESIS"
    REASON="Insufficient trades for statistical significance ($TOTAL_TRADES < 30)"
    
# Check production ready (can skip optimization)
elif (( $(echo "$SHARPE >= 1.0" | bc -l) )) && (( $(echo "$MAX_DRAWDOWN <= 0.30" | bc -l) )) && (( $TOTAL_TRADES >= 100 )); then
    DECISION="PROCEED_TO_VALIDATION"
    REASON="Strong baseline performance (Sharpe $SHARPE, DD $MAX_DRAWDOWN), ready for validation"
    
# Check optimization worthy
elif (( $(echo "$SHARPE >= 0.7" | bc -l) )) && (( $(echo "$MAX_DRAWDOWN <= 0.35" | bc -l) )) && (( $TOTAL_TRADES >= 50 )); then
    DECISION="PROCEED_TO_OPTIMIZATION"
    REASON="Decent performance (Sharpe $SHARPE), worth optimizing parameters"
    
# Marginal case - try optimization
elif (( $(echo "$SHARPE >= 0.5" | bc -l) )); then
    DECISION="PROCEED_TO_OPTIMIZATION"
    REASON="Marginal performance (Sharpe $SHARPE), attempting optimization"
    
else
    DECISION="ABANDON_HYPOTHESIS"
    REASON="Performance does not meet criteria"
fi
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

### Step 11: Execute Next Action Autonomously

**⚠️ AUTONOMOUS MODE: AUTO-EXECUTE NEXT PHASE**

Based on decision, **automatically proceed**:

- **PROCEED_TO_OPTIMIZATION** → Auto-run `/qc-optimize` (no user interaction)
- **PROCEED_TO_VALIDATION** → Auto-run `/qc-validate` (no user interaction)
- **ABANDON_HYPOTHESIS** → Display summary and STOP (wait for user to create new hypothesis)
- **ESCALATE_TO_HUMAN** → Display results and STOP (blocker - needs review)

Display summary only for ABANDON or ESCALATE:
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

[If PROCEED decisions: Already executed /qc-optimize or /qc-validate autonomously]
[If ABANDON/ESCALATE: Awaiting user action]
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
