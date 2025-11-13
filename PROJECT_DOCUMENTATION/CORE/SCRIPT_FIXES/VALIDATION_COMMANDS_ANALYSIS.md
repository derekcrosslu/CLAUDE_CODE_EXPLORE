# Investigation: Overlapping Validation Commands Analysis

**Date:** 2025-11-13
**Issue:** Two validation commands serve overlapping purposes
**Commands:** `/qc-validate` and `/qc-walkforward`
**Goal:** Unify into single command implementing full Monte Carlo validation on QC Research QuantBook

---

## The Two Commands

### Command 1: `/qc-validate`
**File:** `.claude/commands/qc-validate.md`
**Purpose:** Single out-of-sample validation

**What it does:**
1. Runs ONE OOS backtest on unseen data period
2. Compares OOS vs In-Sample performance
3. Checks for degradation (Sharpe drop > 30% = fail)
4. Makes final validation decision
5. Auto-commits with git tag if successful

**Key Characteristics:**
- **Method:** Simple train/test split (single OOS period)
- **Execution:** Single backtest via QC API
- **Decision Framework:** Based on degradation thresholds
  - `<20%` degradation: Excellent
  - `20-30%`: Acceptable
  - `30-50%`: Poor
  - `>50%`: Failed
- **Metrics:** Sharpe ratio, returns, drawdown, win rate
- **Output:** Single comparison table (IS vs OOS)
- **Time:** Fast (1 backtest, ~18 seconds)
- **Cost:** Low (1 backtest credit)

**What it DOESN'T do:**
- ❌ No Monte Carlo simulations
- ❌ No multiple train/test splits
- ❌ No parameter stability analysis
- ❌ No regime robustness testing
- ❌ No probabilistic metrics (PSR, DSR, MinTRL)
- ❌ No bootstrap resampling
- ❌ Doesn't use QC Research QuantBook

---

### Command 2: `/qc-walkforward`
**File:** `.claude/commands/qc-walkforward.md`
**Purpose:** Monte Carlo walk-forward optimization

**What it does:**
1. Runs MULTIPLE Monte Carlo iterations
2. For each run:
   - Randomly samples training period (60% of data)
   - Runs optimization on training data
   - Tests optimized parameters on OOS period
   - Records performance degradation
3. Analyzes aggregate results across all runs
4. Calculates statistics (mean/std degradation, overfitting %)
5. Assesses parameter stability

**Key Characteristics:**
- **Method:** Monte Carlo random sampling (N runs)
- **Execution:** N × 2 backtests (N optimizations + N validations)
- **Decision Framework:** Based on aggregate statistics
  - `>50%` runs overfit: ABANDON
  - Mean degradation `>40%`: HIGH_RISK
  - Std deviation `>25%`: UNSTABLE_PARAMETERS
  - Mean `<15%` + Std `<10%`: ROBUST_STRATEGY
- **Metrics:** Degradation distribution, parameter consensus
- **Output:** Aggregate statistics across all MC runs
- **Time:** Slow (hours for N×2 backtests)
- **Cost:** High (N×2 backtest/optimization credits)

**What it DOESN'T do:**
- ❌ No advanced Monte Carlo metrics (PSR, DSR, MinTRL)
- ❌ No bootstrap resampling of trade sequences
- ❌ No MACHR (Market Condition Historical Randomization)
- ❌ No permutation testing
- ❌ No Monte Carlo drawdown distribution analysis
- ❌ Doesn't use QC Research QuantBook

---

## The Disconnect

### What User Actually Needs

Based on `PROJECT_DOCUMENTATION/MONTECARLO_VALIDATION/CLAUDE_MC_VALIDATION_GUIDE.md`, the user wants **FULL advanced Monte Carlo validation** with:

1. **Probabilistic Sharpe Ratio (PSR)**
   - Industry threshold: PSR ≥ 0.95
   - Accounts for skewness, kurtosis, track record length
   - 10th percentile PSR across MC simulations

2. **Deflated Sharpe Ratio (DSR)**
   - Corrects for multiple testing bias
   - Adjusts for number of trials/variations tested

3. **Minimum Track Record Length (MinTRL)**
   - Required observation count for statistical confidence

4. **Walk-Forward Efficiency (WFE)**
   - Industry standard: WFE ≥ 50-60%
   - Ratio of OOS returns to IS returns

5. **Bootstrap Resampling**
   - Generate alternative equity curves
   - Monte Carlo drawdown distribution (2-3x larger than backtest)
   - 1,000-10,000 simulations for stability

6. **Market Condition Historical Randomization (MACHR)**
   - Block-based bootstrapping
   - Tests performance across different regime sequences
   - 500+ simulations

7. **Permutation Testing**
   - 1,000-100,000 permutations
   - Exact significance without distributional assumptions
   - p < 0.05 threshold

### What Current Commands Do

| Feature | `/qc-validate` | `/qc-walkforward` | **User Needs** |
|---------|---------------|-------------------|----------------|
| **Monte Carlo Runs** | ❌ 0 (single run) | ✅ N runs (10+) | ✅ 1,000-10,000 |
| **PSR Calculation** | ❌ No | ❌ No | ✅ YES (≥0.95) |
| **DSR Calculation** | ❌ No | ❌ No | ✅ YES |
| **MinTRL** | ❌ No | ❌ No | ✅ YES |
| **WFE** | ❌ No | ✅ Implicit | ✅ YES (≥50%) |
| **Bootstrap Resampling** | ❌ No | ❌ No | ✅ YES (trades) |
| **MACHR** | ❌ No | ❌ No | ✅ YES (regimes) |
| **Permutation Testing** | ❌ No | ❌ No | ✅ YES |
| **MC Drawdown Dist** | ❌ No | ❌ No | ✅ YES (2-3x) |
| **Parameter Stability** | ❌ No | ✅ YES | ✅ YES |
| **Regime Robustness** | ❌ No | ❌ No | ✅ YES |
| **QC Research QuantBook** | ❌ No | ❌ No | ✅ YES (online) |
| **Execution Location** | API (backtests) | API (backtests) | **Research (QuantBook)** |

### The Gap

**CRITICAL FINDING:** Both commands use QC **Backtest API**, not QC **Research QuantBook**

- User wants Monte Carlo validation executed **ONLINE** in QC Research notebook
- Advanced metrics (PSR, DSR, MACHR, bootstrap) require **research.ipynb**
- Current commands run backtests via API (simpler but less powerful)
- **No integration with research.ipynb** for advanced Monte Carlo

---

## Why Two Commands Exist

### Historical Evolution (Hypothesis)

1. **Phase 1:** `/qc-validate` created for simple OOS validation
   - Quick, cheap, single train/test split
   - Good enough for basic validation

2. **Phase 2:** User learned about Monte Carlo methods
   - Discovered advanced validation literature
   - Created `/qc-walkforward` for more robust testing
   - But still limited to API-based backtests

3. **Phase 3:** User discovered advanced Monte Carlo metrics
   - PSR, DSR, MinTRL, MACHR, bootstrap
   - Documented in `MONTECARLO_VALIDATION/`
   - **Gap:** No command implements these methods!

### Why They're Both Inadequate

**`/qc-validate`:**
- Too simple (single OOS split)
- No Monte Carlo randomization
- No advanced metrics
- Research shows single OOS drastically underestimates risk

**`/qc-walkforward`:**
- Runs MC optimization + validation (expensive)
- Focuses on parameter stability
- Missing advanced statistical metrics
- Still uses API, not Research QuantBook

**Neither command:**
- Implements PSR, DSR, MinTRL
- Uses bootstrap resampling
- Performs MACHR regime testing
- Executes in QC Research environment
- Generates Monte Carlo drawdown distributions

---

## The Solution: Unified Command

### Proposed: `/qc-validate` (Redesigned)

**Concept:** Single command that intelligently chooses validation depth

**Three Levels:**

#### Level 1: QUICK (Current `/qc-validate`)
```
/qc-validate --quick
```
- Single OOS backtest
- Fast, cheap validation
- Use for iteration/debugging
- **Execution:** API backtest

#### Level 2: STANDARD (Current `/qc-walkforward`)
```
/qc-validate
```
- Monte Carlo walk-forward (10-50 runs)
- Parameter stability analysis
- Aggregate degradation statistics
- **Execution:** API backtests (multiple)

#### Level 3: ADVANCED (NEW - Full Monte Carlo)
```
/qc-validate --monte-carlo
```
- **Execution:** QC Research QuantBook (online)
- **Upload:** research.ipynb to QC project
- **User runs:** Notebook in QC web interface
- **Implements:**
  - PSR (≥0.95 threshold)
  - DSR (multiple testing correction)
  - MinTRL (required track record length)
  - WFE (walk-forward efficiency ≥50%)
  - Bootstrap resampling (1,000-10,000 runs)
  - MACHR (regime randomization)
  - Permutation testing (p < 0.05)
  - MC drawdown distribution (99th percentile)
  - Parameter jitter testing
  - Regime stress testing

### Command Workflow

```bash
# Step 1: Auto-detect validation depth needed
/qc-validate

# Claude checks:
- If baseline only → Quick validation (Level 1)
- If optimized params → Standard walk-forward (Level 2)
- If user requests full MC → Advanced Monte Carlo (Level 3)

# Step 2: Execute appropriate method
# Level 1: Single API backtest
# Level 2: Multiple API backtests (N runs)
# Level 3: Upload research.ipynb, prompt user to run online

# Step 3: Collect results
# Level 1: Single OOS metrics
# Level 2: Aggregate statistics
# Level 3: Wait for user to return with QuantBook results

# Step 4: Make decision
# Apply appropriate thresholds for each level
# Update iteration_state.json
# Git commit with results
```

### research.ipynb Integration

**For Level 3 (Advanced MC):**

1. **Preparation:**
   - Read iteration_state.json
   - Extract backtest_id, parameters, time periods
   - Generate research.ipynb with:
     - QuantBook API initialization
     - Load historical backtest results
     - Implement all advanced MC metrics
     - Generate visualizations (equity curves, drawdown dist, param surfaces)

2. **Upload:**
   ```python
   python qc_backtest.py --upload-notebook \
     --project-id {PROJECT_ID} \
     --file research.ipynb
   ```

3. **User Execution:**
   ```
   ═══════════════════════════════════════════════════
   ADVANCED MONTE CARLO VALIDATION READY
   ═══════════════════════════════════════════════════

   📊 research.ipynb uploaded to project {PROJECT_ID}

   🔗 Open in QuantConnect:
      https://www.quantconnect.com/project/{PROJECT_ID}

   ⚡ Instructions:
   1. Click "Research" tab in QC web interface
   2. Open research.ipynb
   3. Run all cells (this executes Monte Carlo analysis online)
   4. Wait for completion (~5-30 minutes depending on settings)
   5. Return here when done

   Press [ENTER] when Monte Carlo validation is complete...
   ```

4. **Result Collection:**
   - User downloads results JSON from notebook
   - Or: Claude fetches results via QC API if available
   - Parse MC metrics (PSR, DSR, MinTRL, WFE, etc.)
   - Update iteration_state.json
   - Make final decision

---

## Recommendation

### Option A: Merge into Single `/qc-validate` Command ✅ RECOMMENDED

**Action:**
1. Keep `/qc-validate` as the unified validation command
2. Delete `/qc-walkforward` (functionality absorbed into validate)
3. Implement three-level validation depth
4. Add Level 3 (Advanced MC) with research.ipynb integration

**Benefits:**
- Single clear command for validation
- User chooses depth via flags
- Implements full advanced Monte Carlo
- Uses QC Research QuantBook as intended
- Bridges gap to PSR/DSR/MACHR metrics

**Implementation:**
```bash
# Quick validation (single OOS)
/qc-validate --quick

# Standard validation (walk-forward MC)
/qc-validate

# Advanced Monte Carlo (research notebook)
/qc-validate --monte-carlo
/qc-validate --advanced  # alias
```

**Migration:**
- `/qc-walkforward` users → use `/qc-validate` (default behavior)
- Add `--quick` flag for fast iterations
- Add `--monte-carlo` flag for full validation

### Option B: Keep Both, Add Third Command

**Action:**
1. Keep `/qc-validate` (quick OOS)
2. Keep `/qc-walkforward` (MC walk-forward)
3. Add `/qc-monte-carlo` (advanced metrics + QuantBook)

**Benefits:**
- Clear separation of use cases
- Explicit command for each validation level

**Drawbacks:**
- Three commands confusing
- Unclear which to use when
- Duplication of Monte Carlo logic

---

## Implementation Plan (Option A)

### Phase 1: Design Unified Command
- [ ] Read current `/qc-validate.md` and `/qc-walkforward.md`
- [ ] Design new `/qc-validate` with three levels
- [ ] Document flag-based behavior (--quick, --monte-carlo)

### Phase 2: Implement research.ipynb Integration
- [ ] Create template research.ipynb with:
  - QuantBook initialization
  - PSR/DSR/MinTRL calculations
  - Bootstrap resampling
  - MACHR regime testing
  - Permutation testing
  - MC drawdown distribution
  - Visualization (equity curves, param surfaces)
- [ ] Add upload logic to qc_validate.py
- [ ] Implement user prompt flow ("run notebook, return when done")

### Phase 3: Update validation_state.json Schema
- [ ] Add fields for advanced MC metrics:
  ```json
  {
    "validation": {
      "method": "monte_carlo_advanced",
      "monte_carlo_runs": 1000,
      "psr": 0.98,
      "dsr": 0.94,
      "min_trl": 245,
      "wfe": 0.67,
      "machr_consistency": 0.12,
      "permutation_pvalue": 0.018,
      "mc_drawdown_99th": 0.187,
      "decision": "robust_strategy"
    }
  }
  ```

### Phase 4: Implement Decision Framework
- [ ] Level 1 thresholds (quick):
  - Degradation < 30%
- [ ] Level 2 thresholds (standard):
  - Mean degradation < 15%
  - Std degradation < 10%
  - Overfitting rate < 50%
- [ ] Level 3 thresholds (advanced):
  - PSR ≥ 0.95
  - WFE ≥ 0.50
  - Permutation p < 0.05
  - MC drawdown within tolerance

### Phase 5: Delete `/qc-walkforward`
- [ ] Migrate functionality to `/qc-validate`
- [ ] Delete `.claude/commands/qc-walkforward.md`
- [ ] Update all references in skills
- [ ] Update documentation

### Phase 6: Update Skills
- [ ] Update `quantconnect-validation/skill.md`
- [ ] Document three-level validation
- [ ] Add research.ipynb workflow
- [ ] Add advanced MC metrics guide

---

## User Decision Required

**Question:** Which option do you prefer?

**Option A: Merge into single `/qc-validate` command** ✅
- Three levels: --quick, (default), --monte-carlo
- Single command for all validation needs
- Implements full advanced Monte Carlo

**Option B: Keep both + add third**
- `/qc-validate`: Quick OOS
- `/qc-walkforward`: MC walk-forward
- `/qc-monte-carlo`: Advanced metrics (NEW)

**Recommended:** Option A (simpler, clearer, single unified command)

---

**Waiting for user decision before making changes.**
