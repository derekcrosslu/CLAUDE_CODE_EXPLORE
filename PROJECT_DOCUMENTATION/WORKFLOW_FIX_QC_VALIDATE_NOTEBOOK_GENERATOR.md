# Workflow Fix: qc_validate.py Notebook Generator Bugs

**Date**: 2025-11-14
**Status**: 🔍 INVESTIGATION COMPLETE - FIX NEEDED
**Script**: `SCRIPTS/qc_validate.py`
**Function**: `generate_notebook()` (lines 333-727)

---

## Problems Identified

### Problem 1: Literal `\n` Characters in Notebook Output

**Symptom**: Generated research.ipynb contains literal backslash-n (`\n`) instead of actual newlines

**Example from generated notebook**:
```json
"source": [
  "# Advanced Monte Carlo Validation\\n",
  "\\n",
  "**Project ID:** 26204235\\n"
]
```

**Should be**:
```json
"source": [
  "# Advanced Monte Carlo Validation\n",
  "\n",
  "**Project ID:** 26204235\n"
]
```

**Root Cause**:
- Line 369+ in qc_validate.py uses double-escaped newlines: `"text\\n"`
- When `json.dump()` writes this (line 720), it DOUBLE-escapes: `"text\\n"` → `"text\\\\n"` in JSON
- JSON reader interprets `\\\\n` as literal backslash followed by n
- Result: Markdown cells display `\n` literally instead of line breaks

**Why This Happens**:
```python
# In Python source (line 369):
"source": ["# Advanced Monte Carlo Validation\\n"]

# After json.dump():
"source": ["# Advanced Monte Carlo Validation\\\\n"]

# When Jupyter reads JSON:
Displays: "# Advanced Monte Carlo Validation\n" (literal backslash-n)
```

**Correct Pattern**:
```python
# In Python source:
"source": ["# Advanced Monte Carlo Validation\n"]  # Single backslash

# After json.dump():
"source": ["# Advanced Monte Carlo Validation\\n"]  # Properly escaped

# When Jupyter reads JSON:
Displays: "# Advanced Monte Carlo Validation"  (actual newline)
```

---

### Problem 2: Invalid backtest_id

**Symptom**: Notebook tries to load `backtest_id = 'manual_from_screenshot'` which doesn't exist in QuantConnect

**Example from generated notebook** (line 411):
```python
backtest_id = 'manual_from_screenshot'
backtest = qb.ReadBacktest(project_id, backtest_id)  # FAILS - backtest doesn't exist
```

**Root Cause**:
- Line 359-360: Reads `backtest_id` from `iteration_state.json`
- In our case, `iteration_state.json` has placeholder value `'manual_from_screenshot'`
- This was set when we manually extracted results from QC UI screenshot
- QuantConnect has no backtest with this ID

**Why This Happens**:
1. During /qc-backtest, we viewed results in QC UI
2. We manually created backtest results JSON from screenshot
3. Set backtest_id to `'manual_from_screenshot'` as placeholder
4. This invalid ID propagated to iteration_state.json
5. generate_notebook() blindly uses this invalid ID

**Fix Needed**:
Option A: Fetch latest backtest ID from project
```python
# In notebook cell:
project = qb.ReadProject(project_id)
latest_backtest_id = project['backtests'][0]['backtestId']
backtest = qb.ReadBacktest(project_id, latest_backtest_id)
```

Option B: Let user specify backtest ID
```python
# In notebook cell with instruction:
# TODO: Replace with your backtest ID from QC
backtest_id = 'REPLACE_ME'
```

Option C: Check if backtest_id is valid, fallback to latest
```python
if not backtest_id or backtest_id == 'manual_from_screenshot':
    # Fetch latest
    project = qb.ReadProject(project_id)
    backtest_id = project['backtests'][0]['backtestId']
```

---

## Affected Code Sections

### Section 1: Markdown Cells (Every `\\n` needs to become `\n`)

**Lines with Issue**:
- Line 369-382: First markdown cell
- Line 431-434: PSR markdown cell
- Line 471-473: DSR markdown cell
- Line 505-507: MinTRL markdown cell
- Line 537-539: Bootstrap markdown cell
- Line 594-596: Permutation test markdown cell
- Line 625-627: Final decision markdown cell

**Pattern to Fix**:
```python
# BEFORE (line 369):
"source": [
    "# Advanced Monte Carlo Validation\\n",
    "\\n",
    "**Project ID:** {project_id}\\n",

# AFTER:
"source": [
    "# Advanced Monte Carlo Validation\n",
    "\n",
    f"**Project ID:** {project_id}\n",
```

### Section 2: Code Cells (Every `\\n` needs to become `\n`)

**Lines with Issue**: 391-693 (all code cell "source" arrays)

**Pattern to Fix**:
```python
# BEFORE (line 391):
"source": [
    "# Initialize QuantBook\\n",
    "from QuantConnect import *\\n",

# AFTER:
"source": [
    "# Initialize QuantBook\n",
    "from QuantConnect import *\n",
```

### Section 3: Backtest ID Handling (Line 409-424)

**Current Code** (line 409-424):
```python
"source": [
    "# Load backtest results\\n",
    f"project_id = {project_id}\\n",
    f"backtest_id = '{backtest_id}'\\n",  # ← INVALID ID
    "\\n",
    "# Fetch backtest from QC\\n",
    "backtest = qb.ReadBacktest(project_id, backtest_id)\\n",
```

**Fixed Code**:
```python
"source": [
    "# Load backtest results\n",
    f"project_id = {project_id}\n",
    "\n",
    "# Get latest backtest (or specify manually)\n",
    "project = qb.ReadProject(project_id)\n",
    "latest_backtest_id = project['backtests'][0]['backtestId']\n",
    "print(f'Using backtest: {latest_backtest_id}')\n",
    "\n",
    "# Fetch backtest from QC\n",
    "backtest = qb.ReadBacktest(project_id, latest_backtest_id)\n",
```

---

## Fix Implementation

### Quick Fix (Line-by-Line Replacement)

Use find-replace in qc_validate.py:

1. **Find**: `"\\n"`  (with quotes)
   **Replace**: `"\n"`  (with quotes)
   **Scope**: Lines 369-693
   **Count**: ~300 replacements

2. **Find**: `f"backtest_id = '{backtest_id}'\\n",`
   **Replace**: (see "Fixed Code" in Section 3 above)
   **Scope**: Line 411
   **Count**: 1 replacement

### Verification After Fix

1. Regenerate notebook:
   ```bash
   cd STRATEGIES/hypothesis_7_statistical_arbitrage
   python ../../SCRIPTS/qc_validate.py generate-notebook --output test_notebook.ipynb
   ```

2. Check JSON output:
   ```bash
   grep '\\\\n' test_notebook.ipynb  # Should return NOTHING
   grep '\\"\\\\n\\"' test_notebook.ipynb  # Should return NOTHING
   ```

3. Check backtest ID handling:
   ```bash
   grep "backtest_id.*manual_from_screenshot" test_notebook.ipynb  # Should return NOTHING
   grep "ReadProject" test_notebook.ipynb  # Should find it
   ```

4. Visual inspection:
   - Open in Jupyter/VS Code
   - Markdown cells should NOT show literal `\n`
   - Code cells should NOT show literal `\n`
   - Backtest loading should use `ReadProject` to get latest ID

---

## Testing Checklist

After implementing fix:

- [ ] Generate notebook with `qc_validate generate-notebook`
- [ ] Open in text editor, verify no `\\n` in JSON
- [ ] Open in Jupyter/VS Code, verify markdown renders properly
- [ ] Check code cells have proper Python syntax (no literal `\n`)
- [ ] Verify backtest loading uses `ReadProject` or valid ID
- [ ] Upload to QC and run - should execute without errors
- [ ] Verify output JSON is well-formed

---

## Impact Assessment

**Severity**: HIGH - Workflow completely broken

**Affected Workflows**:
- `/qc-validate` command - Cannot proceed with validation
- Any user trying to validate strategies

**Workaround** (until fix deployed):
- Use manually created research_fixed.ipynb (created in this session)
- Or manually fix generated notebook before uploading

**Permanent Fix Required**:
- Update `SCRIPTS/qc_validate.py` with corrections
- Test with fresh hypothesis
- Document in WORKFLOW_SPEC_IMPLEMENTATION_MISMATCH_PROTOCOL.md
- Add to automated testing (prevent regression)

---

## Related Issues

This is similar to the spec/implementation mismatch documented in:
- `WORKFLOW_SPEC_IMPLEMENTATION_MISMATCH_PROTOCOL.md`

But this is different - this is a **bug in implementation**, not a mismatch between docs and implementation.

**Category**: Implementation Bug
**Type**: String escaping error + invalid data propagation

---

## Prevention Measures

1. **Add unit tests**:
   ```python
   def test_generate_notebook():
       # Generate notebook
       nb_path = generate_notebook("test.ipynb")

       # Read JSON
       with open(nb_path) as f:
           nb = json.load(f)

       # Check no double-escaped newlines
       for cell in nb['cells']:
           for line in cell['source']:
               assert '\\\\n' not in line, "Found double-escaped newline"
               assert line.endswith('\n') or line.endswith(''), "Invalid line ending"
   ```

2. **Add validation step**:
   ```python
   # After json.dump(), validate the output
   with open(output_path) as f:
       nb = json.load(f)

   # Check for common issues
   issues = []
   for cell in nb['cells']:
       for line in cell['source']:
           if '\\\\n' in json.dumps(line):
               issues.append(f"Double-escaped newline in: {line[:50]}")

   if issues:
       click.echo("⚠️ WARNING: Generated notebook may have issues:")
       for issue in issues:
           click.echo(f"  - {issue}")
   ```

3. **Document notebook generation pattern**:
   - Add docstring explaining proper JSON string escaping
   - Include examples of CORRECT vs INCORRECT patterns
   - Reference Jupyter notebook JSON specification

---

## Next Steps

1. ⏸️ HALT current validation workflow
2. 🔧 Fix `SCRIPTS/qc_validate.py` (lines 369-693 + line 411)
3. ✅ Test fix with fresh notebook generation
4. 📤 Re-upload fixed notebook to QC
5. ▶️ Resume validation workflow

---

**Status**: INVESTIGATION COMPLETE - WORKAROUND APPLIED
**Resolution**: Using manually-corrected research.ipynb (STRATEGIES/hypothesis_7_statistical_arbitrage/research_fixed.ipynb)
**Permanent Fix**: DEFERRED - Requires significant refactoring of notebook generation logic in SCRIPTS/qc_validate.py

**WORKAROUND APPLIED (2025-11-14)**:
- Created manually-corrected research.ipynb with proper JSON formatting
- Fixed issues:
  1. Proper newlines (not literal `\n`)
  2. Uses correct QC API: `api.list_backtests()` instead of `qb.ReadProject()`
  3. Removed all emojis (violates QC code standards)
- Uploaded corrected notebook to QC project 26204235
- Workflow can proceed with validation

**Final Notebook Corrections Applied**:
1. **API Fix**: Changed from non-existent `qb.ReadProject()` to proper QC API:
   ```python
   from QuantConnect.Api import Api
   api = Api()
   backtests = api.list_backtests(qb.project_id)
   latest_backtest = sorted([b for b in backtests.backtests if b.progress == 1],
                           key=lambda x: x.created, reverse=True)[0]
   backtest_id = latest_backtest.backtest_id
   ```

2. **Emoji Removal**: Removed all emoji characters (✅, ❌, ⚠️) from print statements
   - Changed `'✅ PASS'` to `'PASS'`
   - Changed `'❌ FAIL'` to `'FAIL'`
   - Changed `'⚠️ MARGINAL'` to `'MARGINAL'`

**Permanent Fix Required**: qc_validate.py generate_notebook() function needs complete rewrite
- Cannot use raw string literals with `"\\n"` - creates wrong JSON output
- Need to build notebook dict with actual `\n` characters (not escaped)
- Then json.dump will properly escape them for Jupyter
- Alternative: Use nbformat library instead of raw JSON manipulation
- Must use correct QC API (api.list_backtests) not invalid qb.ReadProject()
- Must not include emojis in generated code
