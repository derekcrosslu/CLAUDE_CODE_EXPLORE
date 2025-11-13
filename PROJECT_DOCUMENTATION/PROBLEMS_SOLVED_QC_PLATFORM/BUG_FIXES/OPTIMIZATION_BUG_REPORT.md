# Optimization Bug Report - Project ID Proliferation

## Issue: 19 Orphaned Projects Created

**Date**: 2025-11-10
**Affected Strategy**: Hypothesis 5 - Statistical Arbitrage
**Root Cause**: `run_optimization.py` using wrong optimization approach

---

## The Bug

`run_optimization.py` claimed to "REUSE same project ID" but was actually creating **separate projects for each parameter combination**.

### What Happened:
```
27 parameter combinations → 27 file uploads → 19+ new projects created
```

Projects created:
- `Opt_1_z15_lb40_mh15` (26140949)
- `Opt_2_z15_lb40_mh20` (26140955)
- ...
- `Opt_18_z20_lb80_mh30` (26141037)

### Why It's Wrong:

**Line 90-102 of run_optimization.py**:
```python
# Run backtest using qc_backtest.py with REUSE project_id
backtest_name = f"Opt_{combo_index}_z{params['z_entry_threshold']}_lb{params['lookback_period']}_mh{params['max_holding_days']}"

cmd = [
    sys.executable,
    str(BACKTEST_SCRIPT),
    "--run",
    "--project-id", str(PROJECT_ID),  # REUSE project ID!  ← LIES!
    "--name", backtest_name,
    "--file", str(temp_strategy),      # ← Uploads NEW file each time
    "--output", str(output_file)
]
```

**Problem**: Each `--file` upload to QC creates a **new project**, despite passing `--project-id`. The QC API creates projects based on unique code uploads, not the project ID parameter.

---

## Correct Approach

**Use QuantConnect's built-in Optimization API** via `qc_optimize` CLI:

### What Should Happen:
```
1 API call → QC runs 140 combinations internally → 1 project (26140717)
```

### How It Works:

**Line 240 of SCRIPTS/qc_backtest.py**:
```python
return self._request("POST", "optimizations/create", json=data)
```

**Line 196 - Uses QC's GridSearchOptimizationStrategy**:
```python
strategy="QuantConnect.Optimizer.Strategies.GridSearchOptimizationStrategy"
```

### Benefits:
- ✅ **No project proliferation** - All work in one project
- ✅ **Parallel execution** - QC distributes across nodes
- ✅ **Cost estimation** - API provides cost before running
- ✅ **Progress tracking** - Single optimization ID to monitor
- ✅ **Result consolidation** - All results in one response

---

## The Fix

### 1. Delete Broken Script
```bash
rm STRATEGIES/hypothesis_5_statistical_arbitrage/run_optimization.py
```

**Reason**: Fundamentally broken approach. Cannot be fixed without complete rewrite.

### 2. Use Correct Command
```bash
./qc_optimize run --config optimization_params.json --state iteration_state.json
```

**Current Run**: `O-446cc7c9624ee4fef4e2c798df9616ce` (140 combinations on project 26140717)

### 3. Clean Up Orphaned Projects

Delete the 19+ "Opt_X" projects created by the broken script:
- Opt_1 through Opt_18 (project IDs 26140949 - 26141037)

---

## Architecture Principle Violated

**From qc-optimize.md**:
```
⚠️ CRITICAL RULE: REUSE SAME PROJECT_ID FROM HYPOTHESIS

IMPERATIVE: Use the existing project_id from iteration_state.json
- Do NOT create a new project for optimization
- Optimization runs on the SAME project created during /qc-init
- Keeps all work (backtests, optimizations) in one place
```

**run_optimization.py violated this by**:
1. Creating temporary strategy files per combination
2. Uploading each file separately
3. QC treating each upload as new project

---

## Correct Project Architecture

```
Hypothesis 4 (RSI)
  └── Project 26140290
       ├── Baseline backtest
       ├── Optimization (if run)
       └── Validation (if run)

Hypothesis 5 (Stat Arb)
  └── Project 26140717
       ├── Baseline backtest ✅
       ├── Optimization (running) ✅
       └── Validation (pending)
```

**Not**:
```
Hypothesis 5
  ├── Project 26140717 (baseline)
  ├── Project 26140949 (Opt_1) ❌
  ├── Project 26140955 (Opt_2) ❌
  └── ... 17 more garbage projects ❌
```

---

## Lessons Learned

1. **Always use native API features** when available (QC has optimization API)
2. **File uploads create projects** - Don't loop file uploads
3. **Test with small grids first** - Would've caught this with 3 combos instead of 27
4. **Read API docs** - QC optimization API was designed for this exact use case
5. **Comments lie** - Code said "REUSE project ID" but didn't

---

## Status

- ✅ Bug identified
- ✅ Correct optimization running (O-446cc7c9624ee4fef4e2c798df9616ce)
- 🔄 Broken script to be deleted
- 🔄 Orphaned projects to be cleaned up
- ✅ Documentation created

**Reference**: See `qc_optimize` CLI and `SCRIPTS/qc_optimize.py` for correct implementation.
