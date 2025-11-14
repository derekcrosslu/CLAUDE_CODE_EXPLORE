# QuantConnect Research API Known Issues

**Date Created**: 2025-11-14
**Status**: DOCUMENTED - Workaround implemented
**Affects**: QC Research notebooks using API to list/read backtests

---

## Issue 1: api.list_backtests() NullReferenceException

### Symptom

When calling `api.list_backtests(project_id)` in QC Research notebook:

```
NullReferenceException: Object reference not set to an instance of an object.
at QuantConnect.Api.Api.Api12 projectId, Boolean includeStatistics) in /LeanCloud/CI.Builder/bin/Release/src/QuantConnect/LeanEnterprise/Api/Api.cs:line 709
```

### Root Cause

The `Api()` object in QuantConnect Research environment may not be fully initialized or may require different initialization than expected. The API methods that work in local development may behave differently in the cloud Research environment.

### Failed Approach

```python
# ❌ FAILS in QC Research
from QuantConnect.Api import Api

api = Api()
project_id = qb.project_id

# This throws NullReferenceException
backtests = api.list_backtests(project_id)
completed = [b for b in backtests.backtests if b.progress == 1]
```

### Working Solution

Use a **try/except with manual fallback** pattern:

```python
# ✅ WORKS in QC Research
project_id = qb.project_id

try:
    from QuantConnect.Api import Api
    api = Api()

    # Try to list backtests
    backtests_response = api.list_backtests(project_id)

    if backtests_response and hasattr(backtests_response, 'backtests'):
        completed = [b for b in backtests_response.backtests if b.progress == 1]
        if completed:
            latest = sorted(completed, key=lambda x: x.created, reverse=True)[0]
            backtest_id = latest.backtest_id
            print(f'Using latest backtest: {backtest_id}')
        else:
            raise ValueError("No completed backtests found")
    else:
        raise ValueError("Could not list backtests")

except Exception as e:
    print(f'Note: Could not auto-fetch backtest list: {e}')
    print('Please manually enter your backtest ID below:')

    # MANUAL FALLBACK: User provides backtest ID
    backtest_id = input('Enter backtest ID: ').strip()

    if not backtest_id:
        raise ValueError("No backtest ID provided!")

# Read backtest using QuantBook's built-in method
backtest = qb.ReadBacktest(project_id, backtest_id)
```

### Key Insights

1. **QuantBook methods are more reliable** than Api() methods in Research
   - Use `qb.ReadBacktest()` instead of `api.read_backtest()`
   - Use `qb.project_id` to get current project ID

2. **API initialization is unreliable** in Research environment
   - `Api()` constructor may not fully initialize
   - Methods that require authentication/state may fail
   - No clear documentation on why this happens

3. **Always provide fallback** for production notebooks
   - Automatic detection is nice-to-have
   - Manual input ensures notebook always works
   - User can copy backtest ID from QC web interface

### Recommended Pattern for Research Notebooks

```python
# Standard pattern for QC Research notebooks
from QuantConnect import *
from QuantConnect.Research import *
import numpy as np
import pandas as pd
import json

qb = QuantBook()
project_id = qb.project_id

# METHOD 1: Manual backtest ID (most reliable)
backtest_id = 'paste-your-backtest-id-here'
backtest = qb.ReadBacktest(project_id, backtest_id)

# METHOD 2: Try automatic with fallback (user-friendly)
try:
    from QuantConnect.Api import Api
    api = Api()
    backtests = api.list_backtests(project_id)
    # ... auto-detection logic ...
except:
    backtest_id = input('Enter backtest ID: ')

backtest = qb.ReadBacktest(project_id, backtest_id)
```

---

## Issue 2: Accessing Backtest Data Structures

### Symptom

Different data structure access patterns work/fail:

```python
# ❌ May fail
equity_curve = backtest.Charts['Strategy Equity'].Series['Equity'].Values
returns = pd.Series([p.y for p in equity_curve]).pct_change().dropna()

# ❌ May fail
trades = backtest.Orders
```

### Working Solution

Use defensive programming with attribute checks:

```python
# ✅ Defensive approach
if 'Strategy Equity' not in backtest.Charts:
    raise ValueError("Strategy Equity chart not found!")

equity_series = backtest.Charts['Strategy Equity'].Series['Equity']
equity_values = [point.y for point in equity_series.Values]
returns = pd.Series(equity_values).pct_change().dropna()

# For orders
order_count = len(backtest.Orders) if hasattr(backtest, 'Orders') else 0

# For statistics
sharpe = backtest.Statistics.get("Sharpe Ratio", "N/A")
```

### Key Insights

1. **Chart names are case-sensitive** - "Strategy Equity" not "strategy equity"
2. **Series structure varies** - sometimes nested, sometimes flat
3. **Orders may not exist** - check with `hasattr()` first
4. **Statistics dict is safest** - use `.get()` with defaults

---

## Issue 3: API Methods vs QuantBook Methods

### When to Use Each

| Task | Use | Don't Use | Reason |
|------|-----|-----------|--------|
| Read backtest | `qb.ReadBacktest()` | `api.read_backtest()` | More reliable in Research |
| List backtests | Try/except both | Assume API works | API may fail |
| Get project ID | `qb.project_id` | Hardcode | Works in all contexts |
| Read orders | `backtest.Orders` | `api.read_backtest_orders()` | Simpler, faster |
| Get statistics | `backtest.Statistics` | Parse manually | Already parsed |

### Why QuantBook is Preferred

1. **Research environment optimized** - QuantBook designed for Research
2. **No authentication issues** - Already authenticated in session
3. **Better error messages** - QC-specific exceptions
4. **Simpler API** - Fewer parameters, clearer intent

---

## Documentation Gaps

### What's Missing from Official QC Docs

1. **Api() initialization requirements** in Research environment
   - Does it need credentials?
   - Why does it fail silently?
   - What's the correct initialization?

2. **Backtest data structure schema**
   - What fields are guaranteed?
   - What's optional?
   - How to handle missing data?

3. **Research vs Local API differences**
   - Which methods work where?
   - Different behavior documented?

### Where to Find Info

- Official docs: https://www.quantconnect.com/docs/v2/research-environment
- Forum: https://www.quantconnect.com/forum
- **Empirical testing**: Try in Research, handle exceptions

---

## Testing Checklist

When creating Research notebooks, always test:

- [ ] QuantBook initialization works
- [ ] Project ID accessible via `qb.project_id`
- [ ] Backtest can be read with `qb.ReadBacktest()`
- [ ] Charts exist and have expected structure
- [ ] Orders/trades accessible
- [ ] Statistics dict populated
- [ ] Fallback logic handles API failures gracefully
- [ ] User prompts work in interactive mode
- [ ] Error messages are clear and actionable

---

## Prevention Strategy

### Rule for Generated Notebooks

**ALWAYS use this pattern in cell 2 of validation notebooks:**

```python
# Safe pattern for loading backtests
project_id = qb.project_id
print(f'Project ID: {project_id}')

# Try automatic detection, fallback to manual
try:
    from QuantConnect.Api import Api
    api = Api()
    backtests_response = api.list_backtests(project_id)

    if backtests_response and hasattr(backtests_response, 'backtests'):
        completed = [b for b in backtests_response.backtests if b.progress == 1]
        if completed:
            latest = sorted(completed, key=lambda x: x.created, reverse=True)[0]
            backtest_id = latest.backtest_id
        else:
            raise ValueError("No completed backtests")
    else:
        raise ValueError("Could not list backtests")
except Exception as e:
    print(f'Auto-detection failed: {e}')
    backtest_id = input('Enter backtest ID: ').strip()
    if not backtest_id:
        raise ValueError("No backtest ID provided")

# Use QuantBook method (most reliable)
backtest = qb.ReadBacktest(project_id, backtest_id)

# Defensive data extraction
if 'Strategy Equity' not in backtest.Charts:
    raise ValueError("Strategy Equity chart not found")

equity_series = backtest.Charts['Strategy Equity'].Series['Equity']
equity_values = [point.y for point in equity_series.Values]
returns = pd.Series(equity_values).pct_change().dropna()

print(f'Loaded {len(returns)} return observations')
```

### Update to qc_validate.py

The `generate_notebook()` function should use this safe pattern, not assume API works.

**Current status**: Fixed in research.ipynb (2025-11-14)
**TODO**: Update qc_validate.py generator to use safe pattern by default

---

## Historical Context

### When This Was Discovered

- **Date**: 2025-11-14
- **Hypothesis**: 7 - Statistical Arbitrage
- **Phase**: Validation (Phase 5)
- **Error**: NullReferenceException in api.list_backtests()

### Impact

- Blocked validation workflow for ~30 minutes
- Required manual investigation and fix
- Would have blocked future hypotheses without documentation

### Resolution

1. Identified error in QC Research execution
2. Researched QC API documentation
3. Tested alternative approaches
4. Implemented try/except fallback pattern
5. Updated notebook and re-uploaded
6. Documented for future sessions

---

## Related Documentation

- QC Coding Standards: `PROJECT_DOCUMENTATION/QC_CODING_STANDARDS.md`
- Workflow Fixes: `PROJECT_DOCUMENTATION/WORKFLOW_FIX_QC_VALIDATE_NOTEBOOK_GENERATOR.md`
- QC Guide: `HELP/qc_guide.json`

---

**Last Updated**: 2025-11-14
**Status**: Active - Use safe pattern in all Research notebooks
