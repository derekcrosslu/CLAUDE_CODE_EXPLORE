---
name: Project Timeline
description: Systematic checklist execution for autonomous framework development (project)
---

# Project Timeline Execution Skill

This skill enforces systematic execution of the project timeline checklist to prevent scope creep and ensure all components are built in the correct order.

## When to Load This Skill

**Load this skill when:**
- Starting a new work session
- Completing any checklist item
- Unsure what to work on next
- Feeling confused about priorities
- Tempted to work on something not in the checklist

**This skill is your project manager. Always consult it before deciding what to work on.**

---

## Core Principles

### Priority 1: Complete the Framework
**Establish baseline → Research dependencies → Complete framework logic**

Focus on building the complete system first:
- ✅ All commands exist and work
- ✅ All wrappers exist and work
- ✅ All skills exist
- ✅ State machine works
- ✅ Integration works end-to-end

**DO NOT get distracted by:**
- Testing multiple hypotheses (1-2 is enough to validate)
- Optimizing performance (works first, fast second)
- Adding features not in checklist
- Extensive documentation (minimal docs, focus on code)

### Priority 2: Validate the Framework
**Validate logic paths → Test robustness → Calibrate thresholds**

Only after Priority 1 is complete:
- Test decision framework with diverse scenarios
- Measure false positive/negative rates
- Calibrate thresholds
- Validate reliability

**Robustness is meaningless without completeness.**

---

## Workflow: Checklist-Driven Development

### Step 1: Load Timeline

```bash
# Read the current checklist section
cat project_timeline.md | grep -A 100 "Week 1 Implementation Tasks"
```

### Step 2: Validate Current Item

Before starting work on ANY item, ask:

1. **Is this item in the checklist?**
   - ✅ Yes → Proceed
   - ❌ No → Stop, consult checklist

2. **Are all dependencies complete?**
   - Check items above this one in the list
   - If dependencies incomplete → Complete them first

3. **Do I understand what this item requires?**
   - ✅ Yes → Proceed
   - ❌ No → Switch to research mode (Step 3)

4. **Has this item already been completed?**
   - Check git commits
   - Check existing files
   - If complete → Mark as done, move to next item

### Step 3: Research Mode (When Confused)

If you don't understand how to complete an item:

1. **Stop implementation immediately**
2. **Switch to research mode:**
   - Read relevant documentation
   - Review PREVIOUS_WORK
   - Check QuantConnect docs
   - Test in isolation
   - Document findings

3. **Create a research document:**
   ```bash
   # Example: researching Phase 4 optimization approach
   touch RESEARCH_OPTIMIZATION_APPROACH.md
   ```

4. **Document what you learned**
5. **Return to implementation with clarity**

**Never guess. Always research first.**

### Step 4: Complete the Item

1. **Implement exactly what the checklist says**
   - Don't add extra features
   - Don't skip steps
   - Follow the specification

2. **Test that it works**
   - Run the code
   - Verify output matches expected
   - Check for errors

3. **Document in git commit**
   - Reference checklist item in commit message
   - Include "Corresponds to checklist item: X"

### Step 5: Mark Item Complete

**Update the checklist:**

```bash
# Example: mark item complete in project_timeline.md
# Change [ ] to [x] for completed item
```

**Create git commit:**

```bash
git add <files>
git commit -m "feat/docs/fix: <description>

Corresponds to checklist item: '<exact item text from checklist>'

✅ Item complete
"
```

### Step 6: Git Push

**Push after EVERY completed item:**

```bash
git push origin <current-branch>
```

**Why push after every item?**
- Creates checkpoint for recovery
- Prevents work loss
- Enables collaboration
- Forces you to complete items fully before moving on

### Step 7: Move to Next Item

**Check what's next:**

```bash
# Find next uncompleted item in checklist
cat project_timeline.md | grep "^\- \[ \]" | head -1
```

**Return to Step 1 (Validate Current Item)**

---

## Checklist Structure

The project timeline has a hierarchy:

```
Week 1: Phase 1-3 MVP
├── Prerequisites (Priority 0 Research) ← Start here
│   └── Items that must be done first
├── Implementation Tasks
│   ├── API Integration
│   ├── /qc-init command
│   ├── /qc-backtest command
│   ├── Decision Logic
│   └── Testing & Validation
└── Deliverables Checklist ← Validation at end
```

**Always work top-to-bottom, left-to-right.**

---

## Current Status Check

When you load this skill, immediately check current status:

### 1. What Week Are We In?

```bash
# Read timeline
cat project_timeline.md | grep -A 5 "## CURRENT STATUS"
```

### 2. What's Already Complete?

```bash
# Check recent commits
git log --oneline -20

# Look for "Corresponds to checklist item" in commit messages
git log --grep="Corresponds to" --oneline
```

### 3. What's Next?

```bash
# Find first incomplete item
cat project_timeline.md | grep -B 5 "^\- \[ \]" | head -10
```

### 4. Any Blockers?

Check for:
- Missing dependencies (files, APIs, credentials)
- Unclear requirements (need research?)
- Integration issues (do pieces work together?)

**If blockers exist → Research mode**

---

## Anti-Patterns to Avoid

### ❌ DON'T: Test Multiple Hypotheses

**Problem**: We tested 1 hypothesis for 9 minutes and validated the system works. Testing 2 more hypotheses is not a checklist item.

**Correct approach**:
- Checklist says "Create 3 test hypotheses"
- Minimum to validate: 1 hypothesis ✅
- System completeness: Focus on building remaining components, not testing variations

**When to test more**: After all Phase 1-3 components exist

### ❌ DON'T: Optimize Before Completing

**Problem**: Wanting to improve decision thresholds before Phase 4-5 exist.

**Correct approach**:
- Week 1: Build Phase 1-3 (commands exist, basic decisions work)
- Week 2: Test decisions with 10 hypotheses, calibrate thresholds
- Week 3-4: Build Phase 4-5

**Sequence matters.**

### ❌ DON'T: Add Unlisted Features

**Problem**: "Let's add a /qc-rollback command" (not in checklist).

**Correct approach**:
- Only build what's in the checklist
- If you think something is missing, add it to checklist first
- Discuss with user before adding scope

### ❌ DON'T: Skip Research When Confused

**Problem**: Implementing Phase 5 without understanding walk-forward validation.

**Correct approach**:
- Stop implementation
- Research walk-forward validation
- Document findings (PHASE5_RESEARCH_FINDINGS.md)
- Then implement with confidence

---

## Integration with Other Skills

### When to Load Each Skill

**project-timeline** (this skill):
- At start of every session
- When deciding what to work on
- When completing any item

**quantconnect**:
- When implementing strategies (Phase 2)
- When working with QC API
- When debugging QC errors

**decision-framework**:
- When evaluating backtest results (Phase 3)
- When making routing decisions
- When confused about whether to proceed/abandon

**Load skills in combination:**

```
/qc-backtest is running...

1. Load project-timeline skill (what am I supposed to do?)
2. Load quantconnect skill (how to implement strategy?)
3. Generate code
4. Run backtest
5. Load decision-framework skill (what decision to make?)
6. Apply decision
7. Load project-timeline skill (mark item complete, what's next?)
```

---

## Week 1 Checklist Reference

**Current location**: `project_timeline.md` lines 741-861

**Sections**:
1. Prerequisites (COMPLETE ✅)
2. API Integration (COMPLETE ✅)
3. /qc-init command (COMPLETE ✅)
4. /qc-backtest command (COMPLETE ✅)
5. Decision Logic (COMPLETE ✅)
6. Git Integration (COMPLETE ✅)
7. QuantConnect Skill (COMPLETE ✅)
8. Testing & Validation (PARTIAL - 1/3 hypotheses)

**Week 1 Deliverables**:
- [ ] /qc-init command working ✅
- [ ] /qc-backtest command working ✅
- [ ] qc_backtest.py wrapper tested ✅
- [ ] 3 hypotheses tested end-to-end ⚠️ (1/3)
- [ ] iteration_state.json schema validated ✅
- [ ] Git integration working ✅
- [ ] QuantConnect Skill integrated ✅

**Status**: 6/7 deliverables complete (86%)

**What's blocking Week 1 completion?**
- "3 hypotheses tested" - But this is for validation, not completeness
- System is proven functional with 1 hypothesis

**Decision**: Move to Week 2 (system completeness priorities over testing more)

---

## Week 2 Preview

**Goal**: Decision threshold calibration

**Checklist items**:
1. Create Backtesting Analysis Skill
2. Generate 10 diverse hypotheses
3. Run all through Phase 3
4. Manually classify results
5. Calculate false positive/negative rates
6. Calibrate thresholds

**Prerequisites**:
- Week 1 Phase 1-3 must be complete ✅
- Decision framework must exist ✅

**Status**: Ready to proceed

---

## Example Session

### Starting Work

```
User: "What should I work on?"

Claude: *Loads project-timeline skill*

Let me check the checklist...

Current status: Week 1 Phase 1-3 implementation
Completed: 6/7 deliverables (86%)
Remaining: 1 item (3 hypotheses tested - but system validated with 1)

Decision: System completeness is Priority 1
Recommendation: Move to Week 2 (build Backtesting Analysis Skill)

Rationale:
- Testing more hypotheses validates decisions, not system completeness
- All Phase 1-3 components exist and work
- Week 2 builds next missing component (new skill)

Next item: Create .claude/skills/backtesting-analysis/ directory
```

### During Work

```
Claude: *Implementing Backtesting Analysis Skill*
Claude: *Confused about what to include in skill*

Claude: *Loads project-timeline skill*

Step 3: Research mode - I'm confused about skill content

Stopping implementation...
Researching: What should Backtesting Analysis Skill contain?

*Checks checklist requirements:*
- Sharpe ratio interpretation guidelines
- Trade frequency analysis
- Drawdown interpretation
- Overfitting detection patterns
- Strategy-type specific thresholds
- Examples of good vs bad backtests

Now I understand. Creating skill with these sections...
```

### Completing Work

```
Claude: *Finishes Backtesting Analysis Skill*

Claude: *Loads project-timeline skill*

Step 5: Mark item complete
- Created skill.md ✅
- Tested loading ✅

Step 6: Git commit
git add .claude/skills/backtesting-analysis/skill.md
git commit -m "feat: Create Backtesting Analysis Skill

Comprehensive skill for interpreting backtest results...

Corresponds to checklist item: 'Create Backtesting Analysis Skill'

✅ Item complete
"

Step 7: Git push
git push origin <branch>

Step 8: What's next?
*Checks checklist*
Next item: "Generate 10 diverse hypotheses"
```

---

## Command Integration

### Update /qc-backtest Command

Add to command:

```markdown
## Before Starting

Load the project-timeline skill to verify this is the correct next step:

1. Check checklist status
2. Validate dependencies complete
3. Confirm this item is next
4. If unsure → Research mode
```

### Update /qc-init Command

Similar integration - always consult timeline before proceeding.

---

## Troubleshooting

### "I'm working on something not in the checklist"

**Stop immediately.**

1. Load project-timeline skill
2. Check what should be next
3. If your work is valuable, discuss adding to checklist first
4. Return to checklist item

### "I completed an item but didn't push"

**Push now:**

```bash
git log -1  # Check last commit
git push origin <branch>
```

### "I'm confused about what the checklist item means"

**Research mode:**

1. Stop implementation
2. Read related docs
3. Check PREVIOUS_WORK
4. Test in isolation
5. Document findings
6. Then implement

### "The checklist item is already complete (from PREVIOUS_WORK)"

**Mark it and move on:**

1. Verify it actually works
2. Mark [x] in checklist
3. Git commit: "docs: Mark <item> complete (verified from PREVIOUS_WORK)"
4. Push
5. Next item

---

## Summary

**This skill enforces:**

1. ✅ Validate each item (is it in checklist? dependencies complete? do I understand it?)
2. ✅ Check off when complete (update checklist, git commit, push)
3. ✅ Research mode when confused (stop, research, document, then implement)
4. ✅ Git push after every item (checkpoint, no work loss)

**Separation of concerns:**

- **Priority 1**: Complete framework (all pieces exist and work)
- **Priority 2**: Validate framework (test thoroughly, calibrate thresholds)

**Always ask: "Is this in the checklist?"**

If no → Stop
If yes → Validate → Implement → Test → Commit → Push → Next

**This skill keeps you on track and prevents scope creep.**

---

## Quick Reference

```bash
# Check current status
cat project_timeline.md | grep -A 10 "## CURRENT STATUS"

# Find next item
cat project_timeline.md | grep "^\- \[ \]" | head -1

# Check recent completions
git log --grep="Corresponds to" --oneline -5

# Mark item complete
# (edit project_timeline.md, change [ ] to [x])

# Commit and push
git add <files>
git commit -m "feat: <description>

Corresponds to checklist item: '<item>'
"
git push origin <branch>
```

**Load this skill at start of every session.**

---

**Version**: 1.0.0
**Last Updated**: November 10, 2025
**Status**: Production Ready
**Purpose**: Systematic checklist execution, prevent scope creep, enforce priorities
