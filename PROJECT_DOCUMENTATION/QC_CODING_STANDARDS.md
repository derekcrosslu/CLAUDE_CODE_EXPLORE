# QuantConnect Coding Standards

**Status**: ENFORCED via automated validation
**Applies to**: All code uploaded to QuantConnect platform
**Validation**: Automatic checks in `qc_validate.py`, `qc_backtest.py`, notebook generation

---

## Mandatory Rules

### Rule 1: No Emojis in Code

**Rule**: Code uploaded to QuantConnect MUST NOT contain emoji characters.

**Rationale**:
- Emojis can cause encoding issues in QC Research environment
- Violates professional code standards
- May break in different terminal/editor environments
- Creates compatibility issues with version control and diff tools

**Examples**:

```python
# ❌ VIOLATION
print(f"Status: {'✅ PASS' if result else '❌ FAIL'}")

# ✅ CORRECT
print(f"Status: {'PASS' if result else 'FAIL'}")
```

**Enforcement**:
- Automatic validation before upload
- Regex pattern: `[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]`
- Checks: Python files, notebooks, markdown cells

**Common Violations**:
- Status indicators: ✅ ❌ ⚠️ 🔴 🟢 🟡
- Arrows: ➡️ ⬅️ ⬆️ ⬇️ ↗️ ↘️
- Symbols: 📊 📈 📉 💰 💵 🎯 🔍 📋
- Faces: 😀 😢 😡 🤔 👍 👎

---

### Rule 2: Use Official QuantConnect API

**Rule**: Only use documented QuantConnect API methods. Do NOT invent or assume API methods exist. Prefer QuantBook methods over Api() methods in Research environment.

**Rationale**:
- Prevents runtime errors in QC Research environment
- Ensures code portability across QC versions
- Avoids breaking changes from undocumented APIs
- QuantBook methods are more reliable than Api() in Research

**Official API Reference**: https://www.quantconnect.com/docs/v2/research-environment

**Common Mistakes**:

```python
# ❌ VIOLATION - qb.ReadProject() doesn't exist
project = qb.ReadProject(project_id)
backtests = project['backtests']

# ⚠️ UNRELIABLE - api.list_backtests() may fail in Research
from QuantConnect.Api import Api
api = Api()
backtests = api.list_backtests(qb.project_id)  # May throw NullReferenceException

# ✅ CORRECT - Use QuantBook methods with try/except fallback
project_id = qb.project_id

try:
    from QuantConnect.Api import Api
    api = Api()
    backtests = api.list_backtests(project_id)
    # ... use backtests ...
except Exception as e:
    # Fallback: prompt for manual input
    backtest_id = input('Enter backtest ID: ')

# Always use QuantBook to read backtest (most reliable)
backtest = qb.ReadBacktest(project_id, backtest_id)
```

**Preferred Methods in Research**:

| Task | Prefer | Avoid | Reason |
|------|--------|-------|--------|
| Read backtest | `qb.ReadBacktest()` | `api.read_backtest()` | More reliable |
| Get project ID | `qb.project_id` | Hardcode | Always works |
| List backtests | Try/except both | Assume API works | API may fail |

**Required Imports for Research**:
```python
from QuantConnect import *
from QuantConnect.Research import *
from QuantConnect.Api import Api  # Optional - may be unreliable
```

**Enforcement**:
- Use try/except for all Api() calls
- Provide fallback for critical operations
- Test in QC Research before committing
- See: `PROJECT_DOCUMENTATION/QC_RESEARCH_API_ISSUES.md`

---

### Rule 3: Proper JSON Escaping in Notebooks

**Rule**: Jupyter notebook source cells must use actual newline characters (`\n`), not escaped strings (`\\n`).

**Rationale**:
- `json.dump()` will properly escape `\n` to `\\n` in JSON output
- Using `\\n` in Python source creates `\\\\n` in JSON (double-escaped)
- Results in literal backslash-n displayed in Jupyter

**Examples**:

```python
# ❌ VIOLATION - Will create literal \n in Jupyter
cell = {
    "source": [
        "# Title\\n",
        "print('hello')\\n"
    ]
}

# ✅ CORRECT - json.dump() will properly escape
cell = {
    "source": [
        "# Title\n",
        "print('hello')\n"
    ]
}
```

**Enforcement**:
- Automatic validation after notebook generation
- Check for `\\\\n` in generated JSON
- Fail if double-escaped newlines detected

---

### Rule 4: Validate Backtest IDs Before Use

**Rule**: Never hardcode or use placeholder backtest IDs. Always fetch latest or validate existence.

**Rationale**:
- Placeholder IDs (e.g., `'manual_from_screenshot'`) don't exist in QC
- Hardcoded IDs break when new backtests are created
- Leads to runtime errors in Research notebooks

**Examples**:

```python
# ❌ VIOLATION - Placeholder ID
backtest_id = 'manual_from_screenshot'
backtest = api.read_backtest(project_id, backtest_id)  # FAILS

# ✅ CORRECT - Fetch latest completed backtest
backtests = api.list_backtests(project_id)
completed = [b for b in backtests.backtests if b.progress == 1]
latest = sorted(completed, key=lambda x: x.created, reverse=True)[0]
backtest_id = latest.backtest_id
backtest = api.read_backtest(project_id, backtest_id)
```

**Enforcement**:
- Check for known placeholder values: `'manual_from_screenshot'`, `'REPLACE_ME'`, `'TODO'`
- Validate backtest_id format (QC uses specific format)
- Require explicit fetching from API

---

### Rule 5: No Duplicate Files for Same Purpose

**Rule**: Never create multiple files serving the same purpose (e.g., `research.ipynb` and `research_fixed.ipynb`).

**Rationale**:
- Creates confusion about which file is authoritative
- Future Claude Code sessions won't know which to use
- Wastes storage and creates sync issues
- QC expects specific filenames (`research.ipynb`, `main.py`)
- Leads to editing wrong file accidentally

**Examples**:

```bash
# ❌ VIOLATION - Multiple notebooks for same purpose
STRATEGIES/hypothesis_7/
├── research.ipynb
├── research_fixed.ipynb        # DUPLICATE - DELETE
├── research_corrected.ipynb    # DUPLICATE - DELETE
└── research_backup.ipynb       # DUPLICATE - DELETE

# ✅ CORRECT - Single authoritative file
STRATEGIES/hypothesis_7/
└── research.ipynb              # Only one file
```

**Proper Workflow**:
1. Edit the canonical file directly (e.g., `research.ipynb`)
2. Use git for versioning, not file duplication
3. If you need a backup, use git commits: `git commit -m "backup before changes"`
4. Delete any temporary or duplicate files immediately after fixing

**Enforcement**:
- Manual check before committing
- Git status should not show duplicate files
- Pre-commit hook can detect common patterns (file_fixed, file_backup, file_v2)

---

## Automated Validation

### Pre-Upload Checks

All code/notebooks uploaded to QC must pass these checks:

```python
def validate_qc_code(content: str, file_type: str) -> List[str]:
    """
    Validate code against QC coding standards.

    Args:
        content: File content as string
        file_type: 'python' | 'notebook' | 'markdown'

    Returns:
        List of violation messages (empty if passes)
    """
    violations = []

    # Rule 1: Check for emojis
    emoji_pattern = r'[\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]'
    if re.search(emoji_pattern, content):
        violations.append("RULE 1 VIOLATION: Emojis detected in code")

    # Rule 2: Check for invalid API calls (basic check)
    if 'qb.ReadProject' in content:
        violations.append("RULE 2 VIOLATION: Invalid API call 'qb.ReadProject()' - use 'api.list_backtests()'")

    # Rule 3: Check for double-escaped newlines (notebooks only)
    if file_type == 'notebook':
        if '\\\\\\\\n' in content or '"\\\\\\\\n"' in content:
            violations.append("RULE 3 VIOLATION: Double-escaped newlines detected in notebook JSON")

    # Rule 4: Check for placeholder backtest IDs
    placeholder_ids = ['manual_from_screenshot', 'REPLACE_ME', 'TODO']
    for placeholder in placeholder_ids:
        if f"backtest_id = '{placeholder}'" in content or f'backtest_id = "{placeholder}"' in content:
            violations.append(f"RULE 4 VIOLATION: Placeholder backtest_id '{placeholder}' detected")

    return violations
```

### Integration Points

1. **qc_validate.py generate-notebook**: Validate after generation
2. **qc_validate.py upload-notebook**: Validate before upload
3. **qc_backtest.py**: Validate strategy code before upload
4. **Pre-commit hook**: Optional git hook for local validation

---

## Violation Handling

### When Violations Detected

1. **HALT**: Stop the workflow immediately
2. **REPORT**: Display all violations clearly
3. **FIX**: Correct violations before proceeding
4. **DOCUMENT**: Log violation in session notes
5. **PREVENT**: Update validation rules to catch similar issues

### Example Output

```
⚠️ QC CODING STANDARDS VIOLATIONS DETECTED

File: research.ipynb
Violations:
  [RULE 1] Line 82: Emoji '✅' detected in print statement
  [RULE 1] Line 123: Emoji '⚠️' detected in print statement
  [RULE 2] Line 45: Invalid API call 'qb.ReadProject()'
  [RULE 4] Line 67: Placeholder backtest_id 'manual_from_screenshot'

❌ UPLOAD BLOCKED - Fix violations before proceeding

See: PROJECT_DOCUMENTATION/QC_CODING_STANDARDS.md
```

---

## Adding New Rules

When adding a new coding standard:

1. **Document**: Add to this file with rationale and examples
2. **Validate**: Implement automated check in validation function
3. **Test**: Create test cases for violations
4. **Enforce**: Add to pre-upload validation
5. **Communicate**: Update relevant workflow docs

---

## Historical Context

### Why These Rules Exist

This document was created after **three workflow-blocking issues** in Hypothesis 7 validation (2025-11-14):

1. **Double-escaped newlines**: Generated notebook had literal `\n` instead of line breaks
2. **Invalid API call**: Used non-existent `qb.ReadProject()` method
3. **Emoji violations**: Manual workaround included ✅❌⚠️ emojis

Each issue required manual investigation, fix, re-upload, and documentation. These rules prevent recurrence.

**Root Cause**: No enforceable coding standards or automated validation

**Solution**: This document + automated validation in workflow scripts

---

## References

- QuantConnect API Docs: https://www.quantconnect.com/docs/v2/research-environment
- Workflow Fix Report: `PROJECT_DOCUMENTATION/WORKFLOW_FIX_QC_VALIDATE_NOTEBOOK_GENERATOR.md`
- Implementation Mismatch Protocol: `PROJECT_DOCUMENTATION/WORKFLOW_SPEC_IMPLEMENTATION_MISMATCH_PROTOCOL.md`

---

**Last Updated**: 2025-11-14
**Status**: Active - Enforced in all QC upload workflows
