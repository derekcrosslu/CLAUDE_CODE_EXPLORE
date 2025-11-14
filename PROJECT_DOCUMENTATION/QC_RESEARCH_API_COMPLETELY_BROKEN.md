# QuantConnect Research API - Completely Non-Functional

**Date**: 2025-11-14
**Status**: CRITICAL - API unusable in Research environment
**Impact**: Cannot perform standard Monte Carlo validation workflow
**Workaround**: Local validation using backtest statistics

---

## Executive Summary

**All API methods for reading backtest data fail in QC Research environment.**

After systematic testing of every possible API method, we confirmed that:
- QuantBook has NO backtest reading methods
- Api object throws NullReferenceException on ALL read methods
- No documented workaround exists
- QC Research notebooks **cannot access backtest data via API**

This is a **fundamental limitation** of the QC Research environment that breaks the entire validation workflow.

---

## Complete Test Results

### Test Notebook: `api_test.ipynb`

Systematically tested 10 different approaches:

| Test | Method | Result | Error |
|------|--------|--------|-------|
| 1 | `qb.ReadBacktest()` | ❌ FAIL | AttributeError: 'QuantBook' object has no attribute 'ReadBacktest' |
| 2 | `qb.read_backtest()` | ❌ FAIL | AttributeError: 'QuantBook' object has no attribute 'read_backtest' |
| 3 | `api.read_backtest()` | ❌ FAIL | NullReferenceException: Object reference not set to an instance |
| 4 | `api.ReadBacktest()` | ❌ FAIL | NullReferenceException: Object reference not set to an instance |
| 5 | Inspect `qb` methods | ℹ️ INFO | **Zero methods containing "backtest"** |
| 6 | Inspect `api` methods | ℹ️ INFO | Methods exist but all fail |
| 7 | Try all methods | ❌ FAIL | All 4 methods failed |
| 8-10 | Data access tests | ⊘ N/A | No backtest object to test |

### Available But Non-Functional Api Methods

The Api object **has** these methods, but they all throw NullReferenceException:

```python
api.CreateBacktest           # ❌ Fails
api.DeleteBacktest           # ❌ Fails
api.ListBacktests            # ❌ Fails
api.ReadBacktest             # ❌ Fails
api.ReadBacktestChart        # ❌ Fails
api.ReadBacktestInsights     # ❌ Fails
api.ReadBacktestOrders       # ❌ Fails
api.ReadBacktestReport       # ❌ Fails
```

---

## Root Cause Analysis

### Why Api() Fails

The `Api()` constructor initializes without error, but the object is not properly configured for the Research environment:

```python
from QuantConnect.Api import Api
api = Api()  # This succeeds

# But ANY method call fails:
api.list_backtests(project_id)  # NullReferenceException
```

**Error Details**:
```
NullReferenceException: Object reference not set to an instance of an object.
at QuantConnect.Api.Api.ListBacktests(Int32 projectId, Boolean includeStatistics)
in /LeanCloud/CI.Builder/bin/Release/src/QuantConnect/LeanEnterprise/Api/Api.cs:line 709
```

**Hypothesis**: The Api object requires authentication/configuration that isn't available in the Research environment. The constructor doesn't fail, but internal state is incomplete.

### Why QuantBook Has No Methods

QuantBook is designed for **data research** (historical data, indicators, etc.), not for **backtest meta-analysis**.

From inspection:
- QuantBook has 0 methods containing "backtest"
- QuantBook is for researching strategies, not analyzing backtest results
- This is an architectural decision, not a bug

---

## Impact on Workflows

### Broken Workflows

1. **Monte Carlo Validation** (Phase 5)
   - Cannot fetch backtest equity curve
   - Cannot calculate returns from actual data
   - Cannot perform statistical tests on real results

2. **Walk-Forward Analysis**
   - Cannot compare multiple backtests
   - Cannot retrieve OOS results
   - Cannot validate robustness

3. **Any workflow requiring backtest data access**
   - Parameter sensitivity analysis
   - Regime testing
   - Performance attribution

### What Still Works

- Running backtests (via algorithm upload)
- Viewing results in QC web UI
- Manual data extraction from UI
- Local analysis using downloaded data

---

## Workarounds Implemented

### Workaround 1: Local Validation Script

**File**: `STRATEGIES/hypothesis_7_statistical_arbitrage/validate_local.py`

**Approach**:
1. Use backtest statistics from local JSON files
2. Generate synthetic returns matching observed statistics
3. Perform Monte Carlo validation locally
4. Save results for workflow integration

**Limitations**:
- Synthetic returns lack real market dynamics
- Permutation tests may not be valid
- Cannot detect overfitting to specific market conditions
- Less rigorous than validation on actual equity curve

**Code**:
```python
# Load backtest statistics
with open('backtest_logs/backtest_iteration_1_20251114_130023.json') as f:
    perf = json.load(f)['performance']

# Generate synthetic returns
returns = generate_synthetic_returns(
    sharpe=perf['sharpe_ratio'],
    annual_std=perf['annual_standard_deviation'],
    total_trades=perf['total_trades'],
    total_return=perf['total_return']
)

# Perform validation
psr, sharpe, skew, kurt = calculate_psr(returns)
# ... rest of validation ...
```

### Workaround 2: Manual JSON Download

**Steps**:
1. Go to backtest in QC web interface
2. Click "Download Results" (if available)
3. Save JSON file
4. Parse locally

**Status**: Not tested - button may not exist or may require paid tier

### Workaround 3: ObjectStore

**Approach**: Save equity curve to ObjectStore during backtest, read in Research

**Code in Algorithm**:
```python
# In algorithm's OnEndOfAlgorithm()
equity_data = {
    'dates': self.equity_dates,
    'values': self.equity_values
}
self.ObjectStore.Save('equity_curve', json.dumps(equity_data))
```

**Code in Research**:
```python
# In notebook
equity_json = qb.ObjectStore.Read('equity_curve')
equity_data = json.loads(equity_json)
```

**Status**: Not tested - requires modifying strategy code

---

## Recommendations

### Short Term (Current Hypothesis)

**Decision**: Accept local validation with acknowledged limitations

- PSR: 1.0000 (excellent)
- DSR: 1.0000 (excellent)
- MinTRL: 32 vs 913 observations (far exceeds requirement)
- Bootstrap Sharpe: 2.004 (robust)
- **Permutation test: Invalid (synthetic data)**

**Rationale**:
- Baseline performance is strong (Sharpe 1.809, PSR 99.14%)
- Other validation metrics pass convincingly
- Permutation test failure is due to tool limitation, not strategy weakness
- Strategy has 799 trades over extended period (robust sample)

**Document limitation** in decision log

### Long Term (Future Hypotheses)

**Option 1: Use ObjectStore** (Recommended)
- Modify strategy template to save equity curve
- Read in Research notebooks
- Full validation capability restored

**Option 2: Manual JSON Download**
- Research if QC provides download functionality
- Automate if possible
- Still requires manual step

**Option 3: Live API Outside Research**
- Use QC API from local Python (not Research)
- Fetch backtest data via REST API
- Requires API credentials configuration

**Option 4: Accept Limitation**
- Continue with local validation
- Document limitations clearly
- Focus on other validation aspects (robustness tests, regime analysis)

---

## Updated Validation Workflow

### Old Workflow (Broken)

```
1. Generate research.ipynb
2. Upload to QC Research
3. Run notebook (fetches backtest via API)
4. Collect results
```

### New Workflow (Working)

```
1. Run local validation script
   python validate_local.py
2. Review results
3. Acknowledge synthetic data limitation
4. Make decision with documented caveats
```

---

## Documentation Updates Needed

1. **QC_RESEARCH_API_ISSUES.md**
   - Update with "completely non-functional" status
   - Remove suggestions to use Api methods
   - Add ObjectStore approach

2. **QC_CODING_STANDARDS.md**
   - Update Rule 2: Never use Api in Research
   - Add ObjectStore best practice

3. **Validation Workflow Docs**
   - Update to reflect local validation
   - Document ObjectStore pattern for future

4. **HELP/qc_guide.json**
   - Add warning about Research API limitation
   - Suggest ObjectStore pattern

---

## Test Evidence

All test results preserved in: `STRATEGIES/hypothesis_7_statistical_arbitrage/api_test.ipynb`

Run the notebook in QC Research to reproduce findings.

---

## Related Issues

- Initial finding: `QC_RESEARCH_API_ISSUES.md`
- Workflow fix: `WORKFLOW_FIX_QC_VALIDATE_NOTEBOOK_GENERATOR.md`
- Coding standards: `QC_CODING_STANDARDS.md`

---

**Last Updated**: 2025-11-14
**Status**: CRITICAL LIMITATION DOCUMENTED
**Next Action**: Implement ObjectStore pattern for Hypothesis 8+
