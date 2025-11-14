# Workflow Spec/Implementation Mismatch Protocol

**Created**: 2025-11-14
**Purpose**: Define protocol for handling mismatches between command documentation and actual script implementation
**Severity**: CRITICAL - Prevents workflow breaks

---

## Problem Statement

**Issue**: Command documentation (`.claude/commands/*.md`) sometimes specifies functionality that doesn't match the actual script implementation (`SCRIPTS/*.py`).

**Example from H7 validation**:
- **Command spec** (`qc-validate.md`): Says run `qc_validate.py run --monte-carlo-runs 1000 --bootstrap-runs 5000`
- **Actual implementation** (`qc_validate.py`): `run` command only accepts `--strategy --state --output --split` (walk-forward validation, NOT Monte Carlo)
- **Result**: Workflow breaks because Claude Code follows documentation that doesn't match reality

---

## Root Cause Analysis

### Why This Happens

1. **Documentation drift**: Command markdown updated without updating Python script
2. **Implementation drift**: Python script updated without updating command markdown
3. **Incomplete implementation**: Documentation describes planned features not yet implemented
4. **Legacy documentation**: Old command specs referencing deprecated functionality

### Why This is Critical

- Claude Code **follows command documentation as primary source of truth**
- If documentation is wrong, Claude Code will attempt invalid operations
- No automatic detection of spec/implementation mismatches
- Breaks workflow mid-execution requiring human intervention

---

## Detection Protocol

### When to Investigate

**ALWAYS investigate spec/implementation match BEFORE executing any command if:**

1. You haven't run this command recently in this project
2. Command documentation shows complex arguments (>3 parameters)
3. Command involves API calls or external systems
4. You're seeing errors like "unrecognized arguments" or "missing required options"

### How to Detect Mismatch

**Step 1: Read Command Spec**
```bash
cat .claude/commands/qc-validate.md | grep "python.*SCRIPTS" -A5
```

**Step 2: Check Actual Script Help**
```bash
source venv/bin/activate  # if using venv
python SCRIPTS/qc_validate.py --help
python SCRIPTS/qc_validate.py <subcommand> --help
```

**Step 3: Compare**
- Does command spec match script arguments?
- Do parameter names match?
- Do parameter types match?
- Are all documented subcommands available?

**Step 4: Document Findings**
Create comparison table:

| Feature | Command Spec | Script Implementation | Match? |
|---------|--------------|----------------------|--------|
| Subcommand | `run --monte-carlo-runs` | `run --strategy --state` | ❌ NO |
| Parameters | 5 parameters | 4 parameters | ❌ NO |
| Workflow | Local Python MC | QC Research notebook | ❌ NO |

---

## Resolution Protocol

### Priority Order (Follow This Sequence)

When mismatch detected, resolve in this order:

#### 1. **Trust Implementation Over Documentation** (Default)

**Rationale**: Implementation is source of truth - it's what actually executes

**Action**:
1. Use `--help` output as authoritative source
2. Follow actual script capabilities
3. Document the mismatch
4. Create fix task for later

**When to use**:
- ✅ Script works correctly, documentation is just wrong
- ✅ Script has been recently updated
- ✅ Time-sensitive execution needed

#### 2. **Investigate Which is Correct** (If Unclear)

**Action**:
1. Check git history: When was each last updated?
   ```bash
   git log --oneline .claude/commands/qc-validate.md | head -5
   git log --oneline SCRIPTS/qc_validate.py | head -5
   ```

2. Check related documentation:
   ```bash
   find PROJECT_DOCUMENTATION -name "*validate*" -type f
   grep -r "monte.*carlo" PROJECT_DOCUMENTATION/
   ```

3. Check for README or help system in script:
   ```bash
   python SCRIPTS/qc_validate.py help 2>&1
   ```

4. Make determination based on:
   - Which was updated more recently?
   - Which has supporting documentation?
   - Which makes more sense for the workflow?

#### 3. **Fix the Mismatch** (Before Proceeding)

**If you have time and fixing is straightforward**:

**Option A: Fix Documentation**
```bash
# Update .claude/commands/qc-validate.md to match actual implementation
```

**Option B: Fix Implementation**
```bash
# Update SCRIPTS/qc_validate.py to match documented spec
# (Only if spec is correct and implementation is wrong)
```

**Option C: Document Workaround**
```bash
# Create PROJECT_DOCUMENTATION/WORKAROUNDS/qc_validate_mismatch.md
```

#### 4. **Ask User for Clarification** (If Blocking)

**When to escalate to user**:
- ❌ Can't determine which is correct
- ❌ Both seem wrong or incomplete
- ❌ Fixing would take significant time
- ❌ High risk of breaking existing functionality

**How to ask**:
```
WORKFLOW BROKEN: Spec/Implementation Mismatch Detected

Command: /qc-validate
Issue: Documentation specifies Monte Carlo validation with local Python execution,
       but actual script uses QC Research notebook-based workflow.

Documentation says: python qc_validate.py run --monte-carlo-runs 1000
Actual script has:  python qc_validate.py generate-notebook → upload-notebook → collect-results

Which is correct?
A) Follow actual implementation (notebook workflow)
B) Fix script to match documentation (local Python)
C) Fix documentation to match script
D) Other (please specify)
```

---

## Prevention Protocol

### For Future Development

1. **When Updating Command Documentation**:
   ```bash
   # ALWAYS test the documented command actually works
   source venv/bin/activate
   python SCRIPTS/qc_validate.py <documented_command> --help
   # Verify arguments match documentation
   ```

2. **When Updating Python Scripts**:
   ```bash
   # ALWAYS update corresponding .claude/commands/*.md
   # Document new parameters
   # Update examples
   git add SCRIPTS/qc_validate.py .claude/commands/qc-validate.md
   git commit -m "feat: update validation + sync docs"
   ```

3. **Add Verification Step to BOOTSTRAP.sh**:
   ```bash
   # Check for common spec/implementation mismatches
   # Compare documented commands with actual --help output
   # Flag discrepancies at session start
   ```

4. **Create Automated Tests** (Optional):
   ```python
   # tests/test_command_spec_match.py
   # Parse command markdown
   # Extract documented arguments
   # Compare with argparse --help output
   # Fail if mismatch detected
   ```

---

## Current Known Mismatches

### qc_validate.py

**Status**: ❌ MISMATCH CONFIRMED

**Command Spec** (`.claude/commands/qc-validate.md` lines 120-136):
```bash
python ../../SCRIPTS/qc_validate.py run \
    --strategy "${STRATEGY_FILE}" \
    --state iteration_state.json \
    --output validation_logs/monte_carlo_results.json \
    --monte-carlo-runs 1000 \
    --bootstrap-runs 5000 \
    --permutation-runs 10000 \
    --machr-runs 500 \
    --cpcv-splits 500
```

**Actual Implementation** (`SCRIPTS/qc_validate.py`):
```bash
# Available commands:
generate-notebook  # Generate research.ipynb with MC validation
upload-notebook    # Upload to QC project
collect-results    # Download results from QC
run                # Simple walk-forward validation (NOT Monte Carlo)

# Actual 'run' signature:
run --strategy TEXT --state TEXT --output TEXT --split FLOAT
```

**Correct Workflow** (per implementation):
1. `generate-notebook` → Creates research.ipynb
2. `upload-notebook --project-id X` → Uploads to QC
3. **User manually runs notebook in QC Research**
4. `collect-results --project-id X` → Downloads results

**Resolution**: Use actual implementation (notebook workflow) until documentation is fixed

**Fix Required**: Update `.claude/commands/qc-validate.md` lines 120-200 to document actual notebook-based workflow

---

## Template for Documenting New Mismatches

```markdown
### <script_name>.py

**Status**: ❌ MISMATCH CONFIRMED | ⚠️ UNDER INVESTIGATION | ✅ RESOLVED

**Command Spec** (file + line numbers):
<quoted command from markdown>

**Actual Implementation**:
<output from --help>

**Discrepancy**:
- Parameter X: spec says Y, implementation says Z
- Workflow: spec says A, implementation says B

**Root Cause**: <why mismatch occurred>

**Resolution**: <which to trust + why>

**Fix Required**: <what needs to be updated>

**Workaround** (if any): <temporary solution>
```

---

## Quick Reference Decision Tree

```
Spec/Implementation Mismatch Detected
│
├─ Is execution time-sensitive?
│  ├─ YES → Trust implementation, document mismatch, proceed
│  └─ NO → Investigate which is correct
│
├─ Can you determine which is correct?
│  ├─ YES → Use correct one, document fix needed
│  └─ NO → Ask user for clarification
│
└─ Is fixing straightforward (<15 min)?
   ├─ YES → Fix mismatch, update both to match
   └─ NO → Document workaround, create fix task
```

---

## Success Criteria

This protocol is successful when:

✅ Mismatches are detected BEFORE attempting execution
✅ Clear decision path exists for resolving mismatches
✅ Workflow doesn't break mid-execution due to spec/implementation divergence
✅ All mismatches are documented in this file
✅ Fixes are tracked and completed over time

---

## Related Documents

- **WORKFLOW_FIX_COMPLETE.md** - File organization protocol
- **WORKFLOW_VERIFICATION_CHECKLIST.md** - Testing procedures
- **BOOTSTRAP.sh** - Session startup checks

---

**Version**: 1.0.0
**Status**: ACTIVE
**Next Review**: After 5 workflow executions or when new mismatch discovered
