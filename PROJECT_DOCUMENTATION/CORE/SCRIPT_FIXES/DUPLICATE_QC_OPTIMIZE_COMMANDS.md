# Investigation: Duplicate /qc-optimize Commands

**Date:** 2025-11-13
**Issue:** Two separate command files for `/qc-optimize` exist
**Status:** INVESTIGATION COMPLETE - Awaiting user decision

---

## The Two Commands

### Command 1: `qc-optimize.md` (native QC API)
**File:** `.claude/commands/qc-optimize.md`
**Lines:** 203 lines

**Key Characteristics:**
- **Method:** Uses **native QuantConnect optimization API** (`/optimizations/create` endpoint)
- **Workflow:** Single optimization job with grid search on QC cloud
- **Prerequisites:** Requires baseline backtest first (blocks if missing)
- **Format:** Native QC parameter format with `{"name", "min", "max", "step"}`
- **Target:** Optimizes by `TotalPerformance.PortfolioStatistics.SharpeRatio`
- **Cost:** Uses QC cloud credits, estimates cost before running
- **Duration:** 10-30 minutes for complete grid search
- **Script:** Uses `qc_backtest.py --optimize` (native QC API)
- **Decision Framework:** Autonomous routing based on improvement
- **Git Integration:** Automatic commit after completion

**Workflow Steps:**
1. Verify baseline backtest exists (BLOCKS if missing)
2. Check current state from iteration_state.json
3. Upload parameterized strategy
4. Configure optimization with `optimization_params.json`
5. Run SINGLE native QC optimization job
6. Analyze results
7. Apply decision framework
8. Update iteration_state.json
9. Auto-commit to git

**Example output:**
```
🔧 Optimization ID: abc123
📊 Combinations Tested: 24
⏱️  Duration: 15 minutes

🏆 Best Parameters:
   rsi_oversold: 35
   bb_distance_pct: 1.06

📈 Performance:
   Baseline Sharpe: 0.45
   Optimized Sharpe: 0.92
   Improvement: +104%

⚠️  DECISION: ESCALATE
```

---

### Command 2: `qc-optimize.md` (hyphen)
**File:** `.claude/commands/qc-optimize.md`
**Lines:** 145 lines

**Key Characteristics:**
- **Method:** **Manual backtest loops** (multiple individual backtest API calls)
- **Workflow:** Auto-detect parameters, run multiple backtests sequentially
- **Prerequisites:** Requires project_id from iteration_state.json
- **Format:** Custom JSON array format `[{"param": value}, ...]`
- **Target:** Optimizes by Sharpe ratio (customizable to Sortino)
- **Cost:** Uses backtest API credits (per backtest)
- **Duration:** Variable (depends on parameter combinations)
- **Script:** Uses `qc_optimize.py` (custom loop implementation)
- **Decision Framework:** Autonomous routing based on improvement
- **Autonomous:** Auto-executes `/qc-validate` if improvement > 5%

**Workflow Steps:**
1. Auto-detect parameters from strategy code
2. Generate sensible ranges (±30% from baseline)
3. Generate parameter grid (3-5 values per parameter)
4. Run MULTIPLE individual backtests via API
5. Analyze results and rank by Sharpe
6. Check for overfitting
7. Update iteration_state.json
8. Auto-execute `/qc-validate` if improvement > 5%

**Example output:**
```
⏳ [1/27] Testing rsi_period=10, oversold=25, overbought=75
   ✅ Complete - Sharpe: 0.82, Return: 15%, Trades: 32

⏳ [2/27] Testing rsi_period=14, oversold=30, overbought=70
   ✅ Complete - Sharpe: 1.45, Return: 23%, Trades: 45

📊 OPTIMIZATION RESULTS:
🏆 Best Parameters (by Sharpe):
   rsi_period: 14
   Improvement: 78% vs baseline

✅ DECISION: PROCEED_TO_VALIDATION
```

---

## Key Differences

| Feature | `qc-optimize.md` (native API) | `qc-optimize.md` (manual - DELETED) |
|---------|-------------------------------|---------------------------|
| **API Method** | Native QC Optimization API | Manual backtest loops |
| **Execution** | Single optimization job | Multiple sequential backtests |
| **Speed** | Faster (parallel on QC cloud) | Slower (sequential API calls) |
| **Cost** | Optimization credits | Backtest credits (per run) |
| **Parameter Detection** | Manual config required | Auto-detects from code |
| **Baseline Check** | BLOCKS if missing | No explicit check |
| **Parameter Format** | Native QC (min/max/step) | Custom JSON array |
| **Script** | `qc_backtest.py --optimize` | `qc_optimize.py` |
| **Git Integration** | Automatic commit | Not mentioned |
| **Auto-validation** | No | Yes (if improvement > 5%) |
| **Duration** | 10-30 minutes (documented) | Variable (not specified) |

---

## Which One Should We Keep?

### Recommendation: **KEEP `qc-optimize.md` - Native QC API**

**Reasons:**

1. **Native QC Optimization is Faster**
   - Runs optimization in parallel on QC cloud
   - More efficient than sequential backtest loops
   - 10-30 minutes vs potentially hours for manual loops

2. **Lower Cost**
   - Uses QC optimization credits (designed for this purpose)
   - Manual loops consume backtest credits for each iteration

3. **Production-Grade**
   - Native QC optimization is the official, supported method
   - Handles parallelization, failures, retries automatically
   - Built for grid search at scale

4. **Better Error Handling**
   - Native API has built-in job management
   - Can resume/cancel optimization jobs
   - Less prone to API rate limits

5. **Baseline Safety Check**
   - BLOCKS if no baseline backtest exists
   - Prevents wasted optimization on unvalidated strategy

**Cons of Native API:**
- Requires manual parameter configuration (no auto-detection)
- More complex setup with `optimization_params.json`

---

### Alternative: **KEEP `qc-optimize.md` (hyphen) - Manual Loops**

**Reasons:**

1. **Auto-Detection**
   - Automatically detects parameters from code
   - No manual configuration needed
   - Faster to get started

2. **Autonomous Workflow**
   - Auto-executes `/qc-validate` if improvement > 5%
   - More integrated with autonomous decision framework

3. **Custom Metric Support**
   - Can optimize by Sortino or other metrics
   - More flexible than native API targets

**Cons of Manual Loops:**
- Slower (sequential backtests)
- Higher cost (per-backtest credits)
- More prone to failures/timeouts
- No built-in job management

---

## Hybrid Approach?

**Option 3: Keep BOTH, but rename for clarity**

Rename to distinguish use cases:
- `/qc-optimize-native` → Native QC optimization (grid search, parallel)
- `/qc-optimize-quick` → Manual loops (auto-detect, quick tests)

**Use Cases:**
- **Native**: Final optimization before validation (thorough)
- **Quick**: Exploratory parameter testing (fast iteration)

---

## User Decision Required

**Question for user:**

1. **Keep ONLY native QC optimization** (`qc-optimize.md`)?
   - Delete duplicate manual loops version
   - Faster, production-grade, lower cost
   - Requires manual parameter config

2. **Keep ONLY manual loops**?
   - Delete native API version
   - Auto-detection, more autonomous
   - Slower, higher cost

3. **Keep BOTH with renamed commands**?
   - `/qc-optimize-native` for thorough optimization
   - `/qc-optimize-quick` for exploratory testing
   - More complex (two commands to maintain)

---

## Recommendation

**KEEP: `qc-optimize.md` (native QC API)**
**DELETE: Duplicate manual loops version**

**Reason:** Native QC optimization is the production-grade solution for parameter tuning. Manual loops were likely a workaround before native API integration was implemented.

**Mitigation for auto-detection loss:**
- Add auto-detection logic to native API workflow
- Scan strategy code for parameters
- Generate `optimization_params.json` automatically

---

**Waiting for user decision before making changes.**
