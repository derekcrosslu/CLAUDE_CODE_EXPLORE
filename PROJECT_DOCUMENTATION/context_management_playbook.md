# Context Management Playbook for Long-Running Autonomous Tasks

## Overview
This playbook provides practical strategies for managing Claude Code's context window during long-running autonomous QuantConnect strategy development sessions.

---

## CONTEXT WINDOW BASICS

### Limits by Plan
| Plan | Context Limit | Recommended Max Usage |
|------|--------------|----------------------|
| Pro  | ~200K tokens | 150K tokens (75%)   |
| Max  | ~200K tokens | 150K tokens (75%)   |

**Note**: Exact limits may vary. Use `/context` and `/usage` commands to monitor.

### What Consumes Context
1. **Conversation History** - All messages and responses
2. **Tool Results** - File contents, bash output, search results
3. **Active Code** - Code in current editing session
4. **Checkpoints** - Stored conversation states
5. **Skills** - Loaded skill content
6. **MCP Tools** - Tool definitions and results

### What Doesn't Consume Context (After Writing)
- External files (after Write tool completes)
- Previous checkpoint states (unless rewinding)
- Compacted conversation history (summaries only)

---

## CONTEXT MONITORING COMMANDS

### `/context` - View Current Usage
```bash
/context
```

**Output**:
- Current token usage
- Percentage of limit
- Breakdown by type (messages, tools, etc.)

**When to Use**:
- Before starting new phase
- After large tool results (backtest, optimization)
- When noticing slow responses

### `/usage` - View Rate Limits
```bash
/usage
```

**Output**:
- Current session usage
- Daily/weekly/monthly limits
- Remaining capacity

**When to Use**:
- Before starting expensive operations (optimization)
- When planning multiple iterations
- To estimate remaining budget

---

## CONTEXT MANAGEMENT STRATEGIES

### Strategy 1: Progressive Disclosure (Prevent Bloat)

**Principle**: Only load information when needed, not upfront.

**Implementation**:
```
❌ BAD: Load all QuantConnect documentation at start
✅ GOOD: Load QuantConnect Skill only when implementing

❌ BAD: Read all previous backtest results at start
✅ GOOD: Read specific backtest result when comparing

❌ BAD: Keep full trade logs in context
✅ GOOD: Write trade logs to file, keep summary metrics only
```

**Skills Usage**:
```markdown
# Instead of this:
Load all QuantConnect documentation and keep it in context

# Do this:
When implementing algorithm, load QuantConnect skill
# Skill auto-loads only what's relevant, progressive disclosure
```

---

### Strategy 2: External State Files (Offload Memory)

**Principle**: Store state in files, not in conversation context.

**File Structure**:
```
strategy_research/
├── iteration_state.json        # Current state (always read at start of phase)
├── hypotheses_log.md           # All hypotheses tested (append-only)
├── decisions_log.md            # All autonomous decisions (append-only)
├── backtest_results/
│   ├── h1_run1_20250115.json  # Full backtest output
│   ├── h1_run2_20250115.json
│   └── h2_run1_20250116.json
├── strategies/
│   ├── momentum_v1.py
│   ├── momentum_v2_optimized.py
│   └── mean_reversion_v1.py
└── analysis/
    ├── optimization_results.csv
    └── performance_comparison.md
```

**Pattern**:
```python
# At start of phase: Read current state
state = read_file("iteration_state.json")

# During phase: Make decisions, execute actions
results = run_backtest(state.current_strategy)

# At end of phase: Write results externally, update state
write_file(f"backtest_results/h{state.hypothesis_id}_run{state.run}.json", results)
state.last_backtest = {"sharpe": results.sharpe, "file": filename}  # Summary only
write_file("iteration_state.json", state)

# Context only holds: current state (small), summary of results (small)
# Full results in files (zero context impact)
```

**Benefits**:
- Context stays minimal (only current state + summary)
- Full history preserved externally
- Can reference past results without loading into context
- Survives session restarts

---

### Strategy 3: Checkpoints (Safe Exploration)

**When to Checkpoint**:
```
✅ After each phase completion
✅ Before risky operations (optimization, major code changes)
✅ After generating valuable results
✅ Before trying experimental approaches

❌ Not every single tool call (too many checkpoints)
❌ Not mid-phase (checkpoints are phase-level)
```

**Checkpoint Pattern**:
```markdown
# Completed implementation phase
Current implementation validated. Creating checkpoint before backtest.

# About to try risky optimization
Creating checkpoint before wide-parameter-range optimization.

# Generated valuable hypothesis list
Created 5 hypotheses. Checkpointing before selecting one to implement.
```

**Rewind Pattern**:
```markdown
# If optimization goes wrong
/rewind

# Select checkpoint from before optimization
Select: "After backtest phase (Sharpe 0.85)"

# Options:
- Rewind code only (keep conversation learnings)
- Rewind context only (keep code changes)
- Rewind both (full reset to checkpoint)

# For autonomous iterations: Usually rewind both
```

**Limitation**: Can only rewind backwards, not jump between checkpoints. Plan accordingly.

---

### Strategy 4: Micro-Compact (Automatic)

**What It Does**: Automatically clears tool results when context gets large.

**Triggers**:
- Large tool outputs (backtest logs, optimization results)
- Context approaching limit
- Automatically by Claude Code 2.0

**What Gets Compacted**:
- Tool call results (file reads, bash outputs)
- Detailed logs
- Large data structures

**What's Preserved**:
- Summaries of results
- Decision outcomes
- Key metrics

**How to Leverage**:
```markdown
# After running backtest with verbose logs
Backtest completed. Results:
- Sharpe: 1.2
- Drawdown: 15%
- Trades: 87
- Win rate: 45%

Full results saved to backtest_results/h2_run1.json

# Micro-compact will auto-clear verbose logs
# Keep only summary metrics above in context
# Full logs in file for later reference if needed
```

**Pro Tip**: Explicitly save large results to files, then reference summary only. This makes micro-compact more effective.

---

### Strategy 5: Manual Compact (Phase Transitions)

**When to Use `/compact`**:
```
✅ After completing research phase (before implementation)
✅ After optimization (before validation)
✅ After abandoning hypothesis (before trying next)
✅ When switching research directions

❌ Mid-phase (loses context needed for current work)
❌ Before analyzing backtest results (need details)
```

**What It Does**:
- Clears conversation history
- Keeps AI-generated summary of key information
- Resets context window

**Pattern**:
```markdown
# Completed research, selected hypothesis
Research phase complete. Selected hypothesis: Multi-timeframe momentum.

Key learnings:
- Momentum strategies work well in trending crypto markets
- Need 2+ timeframes to filter noise
- RSI + MACD combination shows promise

/compact

# Summary preserved, conversation details cleared
# Ready to start implementation with clean context
```

**What Gets Summarized**:
- Key decisions made
- Important findings
- Current state
- Next steps

**What's Lost**:
- Detailed reasoning
- Exploratory dead-ends
- Verbose tool outputs

---

### Strategy 6: Clear (Fresh Start)

**When to Use `/clear`**:
```
✅ Switching to completely different research (crypto → equity)
✅ Starting new session after break
✅ After completing strategy (ready for next)

❌ Mid-research (loses all context)
❌ When current approach just needs adjustment
```

**What It Does**:
- Complete context reset
- No summary preserved
- Full fresh start

**Pattern**:
```markdown
# Completed crypto momentum strategy
Strategy validated: Crypto Momentum v2 (Sharpe 1.4, ready for paper trading)

Documented in strategies/crypto_momentum_v2_validated.md

Ready to start fresh research on equity mean-reversion strategies.

/clear

# Complete reset, starting new research direction
```

---

## PHASE-SPECIFIC CONTEXT PATTERNS

### Research Phase

**Context Budget**: 30-50K tokens

**What to Keep**:
- User's initial research direction
- Hypotheses generated (3-5)
- Key literature findings (summary)
- Selected hypothesis

**What to Externalize**:
- Full academic papers (save URLs, key quotes only)
- All forum threads searched (save links, insights only)
- Detailed comparison matrices (save to file)

**Transition**:
```markdown
Research complete. 5 hypotheses generated and ranked.

Selected: H2 - Multi-timeframe momentum (BTC/ETH)

Writing hypotheses to hypotheses_log.md for reference.

/compact  # Clear research details, keep hypothesis summary

Loading QuantConnect skill for implementation.
```

---

### Implementation Phase

**Context Budget**: 40-60K tokens

**What to Keep**:
- Current hypothesis (from research)
- Current code being written
- QuantConnect skill (loaded on-demand)
- Syntax errors and fixes

**What to Externalize**:
- Final strategy code (write to file)
- Template code (read once, use, don't keep)
- Documentation references (link only)

**Transition**:
```markdown
Implementation complete. Code validated:
- No syntax errors
- Entry/exit logic implemented
- Risk management in place

Strategy saved to strategies/momentum_v1.py

Checkpoint created.

# Don't compact - need implementation context for debugging if backtest fails
# Micro-compact will handle code cleanup automatically
```

---

### Backtest Phase

**Context Budget**: 40-70K tokens

**What to Keep**:
- Current strategy code (from implementation)
- Backtest execution status
- **Summary metrics** (Sharpe, drawdown, trades, win rate)
- Analysis and decision

**What to Externalize**:
- **Full backtest results JSON** (always write to file)
- Trade-by-trade logs (file only)
- Equity curve data (file only)
- Detailed statistics (file only)

**Critical Pattern**:
```markdown
# Backtest completed
Backtest ID: abc123 completed.

Reading results from QuantConnect API...

# IMMEDIATELY externalize
Full results saved to backtest_results/h2_run1_20250115.json

Summary metrics:
- Sharpe Ratio: 0.85
- Max Drawdown: 22%
- Total Trades: 67
- Win Rate: 42%
- Annual Return: 18%

Analysis: Performance meets optimization threshold (Sharpe >= 0.7).

Decision: PROCEED_TO_OPTIMIZATION

# Micro-compact will clear full results
# Only summary metrics stay in context
# Can always read file later if needed for comparison
```

**Transition**:
```markdown
Backtest analysis complete. Decision logged.

Updating iteration_state.json with results summary.

Checkpoint created (can rewind if optimization fails).

# Don't compact yet - optimization needs backtest context for comparison
```

---

### Optimization Phase

**Context Budget**: 60-90K tokens (highest)

**What to Keep**:
- Baseline backtest summary (from previous phase)
- Parameter grid being tested
- Optimization progress tracking
- **Summary of top 5 parameter sets** (not all 27)
- Sensitivity analysis
- Selected optimal parameters

**What to Externalize**:
- **All optimization run results** (CSV file: params, sharpe, drawdown, trades)
- Full backtest JSONs for each param set (30+ files)
- Detailed sensitivity plots (if generated)

**Critical Pattern**:
```markdown
# Running optimization: 27 parameter combinations
Grid: lookback=[10,20,30], threshold=[0.3,0.5,0.7], position_size=[0.5,0.75,1.0]

Progress: 27/27 complete

Writing all results to analysis/optimization_results.csv
(File contains all 27 runs with full metrics)

Top 5 parameter sets:
1. lookback=20, threshold=0.5, size=0.75 → Sharpe 1.02
2. lookback=20, threshold=0.3, size=0.75 → Sharpe 0.98
3. lookback=30, threshold=0.5, size=0.75 → Sharpe 0.96
4. lookback=20, threshold=0.5, size=0.50 → Sharpe 0.94
5. lookback=10, threshold=0.5, size=0.75 → Sharpe 0.91

Sensitivity Analysis:
- Lookback period: Medium sensitivity (0.35)
- Threshold: Low sensitivity (0.18)
- Position size: Medium sensitivity (0.28)

Selected parameters: Set #1 (most robust)

# Only top 5 + analysis in context
# Full 27 results in CSV (read later if needed)
```

**Transition**:
```markdown
Optimization complete. Parameters selected and validated.

/compact  # Heavy phase complete, clear details, keep summary

Ready for out-of-sample validation.
```

---

### Validation Phase

**Context Budget**: 30-50K tokens

**What to Keep**:
- In-sample backtest summary (from optimization or baseline)
- Out-of-sample backtest summary
- Degradation analysis
- Validation decision

**What to Externalize**:
- Out-of-sample full results (JSON file)
- Comparison charts (if generated)
- Final strategy documentation

**Transition**:
```markdown
Validation complete.

In-sample Sharpe: 1.02
Out-of-sample Sharpe: 0.78
Degradation: 24% (acceptable, <30%)

Decision: STRATEGY_VALIDATED

Writing final documentation to strategies/momentum_v2_validated.md

Checkpoint created.

/compact  # Iteration complete, prepare for next hypothesis or completion
```

---

## MONITORING TRIGGERS

### Automated Monitoring Pattern

```markdown
# At start of each phase
Current context usage: {usage} tokens ({percent}%)

if percent > 70%:
    Warning: Context at 70%. Consider compact after this phase.

if percent > 85%:
    ALERT: Context at 85%. Compacting now to prevent auto-compact mid-task.
    /compact
```

### Hook Implementation

**hooks/context-warning.sh**:
```bash
#!/bin/bash

USAGE=$(claude context --json | jq '.usage_percent')

if (( $(echo "$USAGE > 70" | bc -l) )); then
    echo "⚠️  Context at ${USAGE}% - consider /compact at next phase transition"
fi

if (( $(echo "$USAGE > 85" | bc -l) )); then
    echo "🚨 Context at ${USAGE}% - /compact recommended NOW"
fi
```

---

## CONTEXT BUDGET PLANNING

### Full Research Cycle Budget

| Phase | Context Budget | Cumulative | Notes |
|-------|---------------|------------|-------|
| Research | 30-50K | 50K | Compact after |
| Implementation | 40-60K | 60K | Micro-compact handles code |
| Backtest | 40-70K | 70K | Externalize results immediately |
| Optimization | 60-90K | 90K | Compact after (heaviest phase) |
| Validation | 30-50K | 50K | Compact after |

**Total per hypothesis**: 50K - 90K tokens (with good management)

**Hypotheses per session**: 2-3 hypotheses (with compacting between)

**Without management**: 1-2 hypotheses (context overflow)

---

## TROUBLESHOOTING

### Problem: Context Filling Too Fast

**Symptoms**:
- Auto-compact triggering mid-phase
- Slow response times
- "Approaching limit" warnings

**Solutions**:
1. Check what's consuming context: `/context`
2. Externalize large results immediately (don't keep in context)
3. Use progressive disclosure (load skills only when needed)
4. Compact more frequently (after each phase)

**Prevention**:
- Always write large results to files
- Reference files instead of keeping content in context
- Use skills (not full documentation dumps)

---

### Problem: Auto-Compact Mid-Task

**Symptoms**:
- Context suddenly cleared while working
- Lost important context for current task

**Solutions**:
1. Rewind to checkpoint before auto-compact
2. Read iteration_state.json to recover state
3. Reference external files for detailed data

**Prevention**:
- Monitor context proactively (`/context` before each phase)
- Manually compact at phase transitions (before auto-compact)
- Set up context warning hook

---

### Problem: Lost Important Context After Compact

**Symptoms**:
- Can't remember why decision was made
- Need details from previous hypothesis

**Solutions**:
1. Read external log files:
   - decisions_log.md (all decisions with rationales)
   - hypotheses_log.md (all hypotheses and outcomes)
   - backtest_results/*.json (full backtest details)
2. Check iteration_state.json (current state)

**Prevention**:
- Log all important decisions to external files
- Write detailed rationales in decision logs
- Structure external files for easy reference

---

### Problem: Can't Rewind to Needed Point

**Symptoms**:
- Checkpoints only go backwards
- Can't get back to specific state

**Solutions**:
1. Use iteration_state.json to reconstruct state
2. Read relevant result files to restore context
3. Manually recreate needed context from files

**Prevention**:
- Create checkpoints at important decision points
- Label checkpoints clearly ("After successful optimization")
- Use Git for code versioning (parallel to checkpoints)

---

## BEST PRACTICES SUMMARY

### DO ✅

1. **Monitor Proactively**
   - Check `/context` before each phase
   - Set up context warning hooks
   - Plan compact points in advance

2. **Externalize Aggressively**
   - Write large results to files immediately
   - Keep only summaries in context
   - Reference files instead of re-reading

3. **Compact Strategically**
   - After phase completions
   - Between hypotheses
   - When switching directions

4. **Checkpoint Frequently**
   - After each phase
   - Before risky operations
   - At valuable states

5. **Use Progressive Disclosure**
   - Load skills when needed
   - Read files when needed
   - Don't front-load everything

### DON'T ❌

1. **Don't Keep Large Data in Context**
   - Not full backtest results
   - Not all optimization runs
   - Not complete trade logs

2. **Don't Compact Mid-Phase**
   - Wait for phase completion
   - Finish current work first
   - Preserve working context

3. **Don't Load Everything Upfront**
   - Not all documentation
   - Not all past results
   - Not all skills at once

4. **Don't Ignore Warnings**
   - Context at 70%+ = action needed
   - Auto-compact risk = manual compact now
   - Slow responses = context bloat

5. **Don't Rely Only on Context**
   - External files are primary storage
   - Context is working memory
   - Logs for auditability

---

## CONTEXT MANAGEMENT CHECKLIST

### Start of Session
- [ ] Check `/usage` for rate limits
- [ ] Load iteration_state.json
- [ ] Review previous decisions_log.md
- [ ] Set up context monitoring

### Start of Phase
- [ ] Check `/context` usage
- [ ] Load only required files/skills
- [ ] Create checkpoint (if major phase)

### During Phase
- [ ] Write large results to files immediately
- [ ] Keep only summaries in context
- [ ] Monitor for slow responses

### End of Phase
- [ ] Update iteration_state.json
- [ ] Log decision to decisions_log.md
- [ ] Create checkpoint
- [ ] Check `/context` usage
- [ ] Compact if >70% (or next phase transition)

### End of Session
- [ ] Save all state to files
- [ ] Document current phase in iteration_state.json
- [ ] Create final checkpoint
- [ ] Can clear context (state in files)

---

## QUICK REFERENCE

```bash
# Monitor context
/context                    # Current usage
/usage                      # Rate limits

# Manage context
/compact                    # Clear history, keep summary
/clear                      # Full reset
/rewind                     # Return to checkpoint

# Checkpoints
# Automatic after tool use
# Manual: after each phase

# External files (always)
iteration_state.json        # Current state
decisions_log.md           # All decisions
hypotheses_log.md          # All hypotheses
backtest_results/*.json    # All backtest outputs
```

---

## EXAMPLE: FULL CYCLE WITH GOOD CONTEXT MANAGEMENT

```markdown
# START
Check usage: 0 tokens
Load iteration_state.json

# RESEARCH PHASE
Load QuantConnect skill
Research momentum strategies
Generate 5 hypotheses
Write to hypotheses_log.md

Context: 45K tokens
/compact (research → implementation transition)

# IMPLEMENTATION PHASE
Context: 5K tokens (post-compact)
Skill already loaded (persists through compact)
Implement momentum_v1.py
Write code to file

Context: 55K tokens
Checkpoint created
# Don't compact (need context if backtest fails)

# BACKTEST PHASE
Run backtest (background)
Read results
IMMEDIATELY write to backtest_results/h1_run1.json
Keep summary only:
- Sharpe: 0.85
- Decision: PROCEED_TO_OPTIMIZATION

Context: 68K tokens
Checkpoint created

# OPTIMIZATION PHASE
Run 27 parameter combinations
Write all to optimization_results.csv
Keep top 5 + analysis only

Context: 89K tokens (heaviest phase)
/compact (optimization → validation transition)

# VALIDATION PHASE
Context: 15K tokens (post-compact)
Run out-of-sample backtest
Write to backtest_results/h1_oos.json
Compare: in-sample vs out-of-sample
Decision: VALIDATED

Context: 42K tokens
Write final documentation

Total context peak: 89K tokens
Hypotheses tested: 1
Remaining budget: 61K tokens (enough for 1-2 more)

/compact (ready for next hypothesis)
```

**Result**: Successfully validated 1 strategy using only 89K peak context (well under 150K limit). Can test 1-2 more hypotheses in same session.

---

## ADVANCED: MULTI-HYPOTHESIS MANAGEMENT

### Session-Level Planning

```markdown
Goal: Test 3 hypotheses in one session
Budget: 150K tokens max
Per-hypothesis budget: 50K tokens average

Strategy:
1. Aggressive externalization (all results to files)
2. Compact after EVERY hypothesis
3. Read only current hypothesis from iteration_state.json
4. Don't load past hypothesis contexts

Tracking:
- iteration_state.json: Current hypothesis only
- hypotheses_log.md: All hypotheses (read for comparison, don't load all)
```

### Pattern

```markdown
# Hypothesis 1
Research → Implement → Backtest → Optimize → Validate
Peak context: 85K
Write results, log outcome
/compact

# Hypothesis 2 (fresh context)
Context: 10K tokens
Read iteration_state.json (next hypothesis)
Research → Implement → Backtest (fail)
Abandon hypothesis, log outcome
Context: 55K tokens
/compact

# Hypothesis 3 (fresh context)
Context: 10K tokens
...

# Session total: 3 hypotheses tested, 1 validated
# Peak context never exceeded 85K
# Success rate: 33% (1/3)
```

This playbook should serve as your practical guide for managing context during long autonomous sessions!
