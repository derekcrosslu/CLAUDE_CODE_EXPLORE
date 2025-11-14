# Workflow Verification Checklist

**Purpose**: Verify that the workflow commands create files in correct locations

**Date Created**: 2025-11-14
**Version**: 2.0.0 (After Directory-First Pattern Fix)

---

## Pre-Test Cleanup

Before testing, ensure clean workspace:

```bash
# 1. Switch to main branch
git checkout main

# 2. Delete any test hypothesis branches
git branch -D hypotheses/hypothesis-test-* 2>/dev/null || true

# 3. Delete any test hypothesis directories
rm -rf STRATEGIES/hypothesis_test_* STRATEGIES/hypothesis_7_*

# 4. Delete any files at root (except allowed)
# Check for violations first
ls -1 *.py *.json 2>/dev/null

# If found, remove them
rm -f iteration_state.json *.py optimization_*.json oos_*.json backtest_*.json

# 5. Run BOOTSTRAP.sh to verify clean state
./BOOTSTRAP.sh
```

Expected: BOOTSTRAP.sh shows "✅ Root directory is clean - no violations found"

---

## Test 1: /qc-init Command

**Objective**: Verify /qc-init creates directory structure FIRST

### Steps:

1. Run `/qc-init` with test hypothesis
2. Provide test data:
   - Name: "Test Workflow"
   - Description: "Workflow verification test"
   - Rationale: "Testing directory-first pattern"

### Verification Checklist:

- [ ] Directory created: `STRATEGIES/hypothesis_X_test_workflow/`
- [ ] File created IN directory: `STRATEGIES/hypothesis_X_test_workflow/iteration_state.json`
- [ ] NO `iteration_state.json` at root
- [ ] Git branch created: `hypotheses/hypothesis-X-test-workflow`
- [ ] Git commit successful with structured message
- [ ] Pre-flight checks passed without errors

### Commands to Verify:

```bash
# Check directory exists
ls -d STRATEGIES/hypothesis_*_test_workflow/

# Check iteration_state.json in hypothesis directory
ls STRATEGIES/hypothesis_*_test_workflow/iteration_state.json

# Check NO iteration_state.json at root
ls iteration_state.json 2>/dev/null && echo "❌ FAIL: Found at root!" || echo "✅ PASS: Not at root"

# Check git branch
git branch | grep hypothesis-.*-test-workflow

# Check git log
git log -1 --oneline
```

**Expected Result**: All files in hypothesis directory, none at root

---

## Test 2: /qc-backtest Command

**Objective**: Verify /qc-backtest creates strategy file IN hypothesis directory

### Prerequisites:

- Test 1 completed successfully
- Hypothesis directory exists with iteration_state.json

### Steps:

1. Run `/qc-backtest`
2. Use simple test strategy or simulated backtest

### Verification Checklist:

- [ ] Pre-flight checks passed
- [ ] Strategy file created IN directory: `STRATEGIES/hypothesis_X_test_workflow/*.py`
- [ ] NO `.py` files at root
- [ ] Backtest log created: `PROJECT_LOGS/backtest_result_hX_*.json`
- [ ] NO `backtest_result*.json` at root
- [ ] iteration_state.json updated IN hypothesis directory
- [ ] Git commit successful with results in message

### Commands to Verify:

```bash
# Find hypothesis directory
HYPOTHESIS_DIR=$(find STRATEGIES -maxdepth 1 -name "hypothesis_*_test_workflow" -type d)

# Check strategy file in hypothesis directory
ls "${HYPOTHESIS_DIR}"/*.py

# Check NO .py files at root
ls -1 *.py 2>/dev/null && echo "❌ FAIL: Python files at root!" || echo "✅ PASS: No .py at root"

# Check backtest log in PROJECT_LOGS
ls PROJECT_LOGS/backtest_result_h*.json

# Check NO backtest log at root
ls backtest_result*.json 2>/dev/null && echo "❌ FAIL: Backtest log at root!" || echo "✅ PASS: Log in PROJECT_LOGS"

# Check iteration_state.json updated
cat "${HYPOTHESIS_DIR}/iteration_state.json" | jq '.phase_results.backtest.completed'

# Check git log
git log -1 --oneline
```

**Expected Result**: Strategy in hypothesis dir, logs in PROJECT_LOGS, nothing at root

---

## Test 3: /qc-optimize Command

**Objective**: Verify /qc-optimize creates optimization results IN hypothesis directory

### Prerequisites:

- Test 2 completed successfully
- Baseline backtest exists

### Steps:

1. Run `/qc-optimize`
2. Use simulated optimization (fast test)

### Verification Checklist:

- [ ] Pre-flight checks passed (baseline backtest verified)
- [ ] Optimization results created: `STRATEGIES/hypothesis_X_test_workflow/optimization_results_*.json`
- [ ] NO `optimization_*.json` at root
- [ ] iteration_state.json updated IN hypothesis directory
- [ ] Git commit successful with optimization metrics

### Commands to Verify:

```bash
# Find hypothesis directory
HYPOTHESIS_DIR=$(find STRATEGIES -maxdepth 1 -name "hypothesis_*_test_workflow" -type d)

# Check optimization results in hypothesis directory
ls "${HYPOTHESIS_DIR}"/optimization_results_*.json

# Check NO optimization files at root
ls -1 optimization_*.json 2>/dev/null && echo "❌ FAIL: Optimization at root!" || echo "✅ PASS: Results in hypothesis dir"

# Check iteration_state.json updated
cat "${HYPOTHESIS_DIR}/iteration_state.json" | jq '.phase_results.optimization.completed'

# Check git log
git log -1 --oneline
```

**Expected Result**: All optimization files in hypothesis directory, none at root

---

## Test 4: /qc-validate Command

**Objective**: Verify /qc-validate creates validation results IN hypothesis directory

### Prerequisites:

- Test 3 completed successfully (or can skip directly from Test 2)
- Strategy file exists

### Steps:

1. Run `/qc-validate`
2. Use simulated OOS validation (fast test)

### Verification Checklist:

- [ ] Pre-flight checks passed
- [ ] Validation results created: `STRATEGIES/hypothesis_X_test_workflow/oos_validation_results.json`
- [ ] NO `oos_*.json` at root
- [ ] iteration_state.json updated IN hypothesis directory
- [ ] Git commit successful with validation metrics
- [ ] Git tag created if validation passed (optional)

### Commands to Verify:

```bash
# Find hypothesis directory
HYPOTHESIS_DIR=$(find STRATEGIES -maxdepth 1 -name "hypothesis_*_test_workflow" -type d)

# Check validation results in hypothesis directory
ls "${HYPOTHESIS_DIR}"/oos_validation_results.json

# Check NO validation files at root
ls -1 oos_*.json 2>/dev/null && echo "❌ FAIL: Validation at root!" || echo "✅ PASS: Results in hypothesis dir"

# Check iteration_state.json updated
cat "${HYPOTHESIS_DIR}/iteration_state.json" | jq '.phase_results.validation.completed'

# Check git log
git log -1 --oneline

# Check git tag (if validation passed)
git tag | grep "v1.0.0-h.*-test-workflow"
```

**Expected Result**: All validation files in hypothesis directory, none at root

---

## Final Verification: BOOTSTRAP.sh File Organization Check

Run BOOTSTRAP.sh after all tests:

```bash
./BOOTSTRAP.sh
```

### Expected Output:

```
================================================
🔍 FILE ORGANIZATION CHECK
================================================

Checking for root-level violations...

✅ Root directory is clean - no violations found

================================================
```

**If violations found**: Workflow fix FAILED - investigate which command created files at root

**If no violations**: Workflow fix SUCCESSFUL ✅

---

## Post-Test Cleanup

After testing, clean up test hypothesis:

```bash
# 1. Switch to main branch
git checkout main

# 2. Delete test branch
git branch -D hypotheses/hypothesis-*-test-workflow

# 3. Delete test hypothesis directory
rm -rf STRATEGIES/hypothesis_*_test_workflow/

# 4. Delete test logs
rm -f PROJECT_LOGS/backtest_result_h*_*.json
rm -f PROJECT_LOGS/validation_h*_*.json

# 5. Reset to clean state
git status
```

---

## Success Criteria

All 4 tests pass if:

1. ✅ NO `iteration_state.json` at root
2. ✅ NO `.py` files at root
3. ✅ NO `optimization_*.json` at root
4. ✅ NO `oos_*.json` at root
5. ✅ NO `backtest_result*.json` at root
6. ✅ ALL hypothesis files in `STRATEGIES/hypothesis_X_*/`
7. ✅ Logs in `PROJECT_LOGS/`
8. ✅ BOOTSTRAP.sh shows "✅ Root directory is clean"

---

## Failure Scenarios

### If Test 1 Fails:

- `/qc-init` is still creating `iteration_state.json` at root
- **Fix**: Review `.claude/commands/qc-init.md` Step 3 (directory creation)
- **Check**: Pre-flight checks section

### If Test 2 Fails:

- `/qc-backtest` is creating strategy `.py` files at root
- **Fix**: Review `.claude/commands/qc-backtest.md` Step 3 (strategy file creation)
- **Check**: Path validation before file creation

### If Test 3 Fails:

- `/qc-optimize` is creating `optimization_*.json` at root
- **Fix**: Review `.claude/commands/qc-optimize.md` Step 8 (results file creation)
- **Check**: Path validation in results saving

### If Test 4 Fails:

- `/qc-validate` is creating `oos_*.json` at root
- **Fix**: Review `.claude/commands/qc-validate.md` Git Integration section
- **Check**: Results file path construction

---

## Quick Test Script

For automated testing, you can create a script:

```bash
#!/bin/bash
# quick_workflow_test.sh

set -e

echo "🧪 Starting workflow verification test..."

# Run all commands in sequence
/qc-init
/qc-backtest
/qc-optimize
/qc-validate

# Run BOOTSTRAP.sh and check for violations
OUTPUT=$(./BOOTSTRAP.sh | grep -A5 "FILE ORGANIZATION CHECK")

if echo "$OUTPUT" | grep -q "✅ Root directory is clean"; then
    echo "✅ WORKFLOW TEST PASSED - No file organization violations"
    exit 0
else
    echo "❌ WORKFLOW TEST FAILED - File organization violations found"
    echo "$OUTPUT"
    exit 1
fi
```

---

**Created**: 2025-11-14
**Last Updated**: 2025-11-14
**Status**: Ready for testing
**Version**: 2.0.0 (Directory-First Pattern)
