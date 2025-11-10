# Gaps Report - Research vs Implementation

**Purpose**: Identify what we know (validated research) vs what we need to discover (research gaps) vs what we can implement directly.

**Date**: November 10, 2025

---

## Framework: Research vs Implementation

**Baseline**: PREVIOUS_WORK/PROJECT_DOCUMENTATION/autonomous_decision_framework.md

This document contains the complete routing logic - the CORE of autonomous operation. All gaps are measured against this baseline.

### Research Gaps
Things we **don't know** and must **discover through experimentation**:
- Requires testing in actual QC environment
- May change architecture
- Blocks confident implementation

### Implementation Tasks
Things we **know how to do** and just need to **build**:
- Straightforward coding
- Follows established patterns
- Low risk, high confidence

### Calibration Tasks
Things that **exist in baseline** but need **tuning with real data**:
- Performance thresholds (minimum_viable, optimization_worthy, production_ready)
- Overfitting signals (too_perfect_sharpe, too_few_trades)
- Iteration limits (max attempts, max cost)

---

## Routing Logic Status (from Baseline)

### ✅ Validated: Baseline Architecture

The autonomous decision framework (from PREVIOUS_WORK) defines:

1. **Performance Thresholds** (to calibrate):
   - minimum_viable: Sharpe 0.5, DD 0.35, Trades 20
   - optimization_worthy: Sharpe 0.7, DD 0.30, Trades 30
   - production_ready: Sharpe 1.0, DD 0.20, Trades 50

2. **Overfitting Signals** (to calibrate):
   - too_perfect_sharpe: 3.0
   - too_few_trades: 10
   - win_rate_too_high: 0.80

3. **Iteration Limits** (configured):
   - max_hypotheses_per_session: 5
   - max_optimization_attempts: 3
   - max_total_iterations: 15
   - max_cost_usd: 50

4. **Routing Actions** (to implement):
   - PROCEED_TO_VALIDATION
   - PROCEED_TO_OPTIMIZATION
   - ABANDON_HYPOTHESIS
   - FIX_BUG
   - ASK_USER
   - ESCALATE_TO_HUMAN
   - STRATEGY_COMPLETE

5. **Master Control Loop** (to implement):
   - While loop with phase routing
   - Global limit checks
   - abandon_and_next_hypothesis()
   - Checkpoint creation
   - State persistence

---

## Phase-by-Phase Analysis

### Phase 1: RESEARCH → Generate Hypotheses

#### ✅ Validated Knowledge

1. **Git branch strategy works**
   - Validated: Created hypothesis branches in testing
   - Pattern: `hypotheses/hypothesis-{id}-{name}`
   - Confidence: 100%

2. **State initialization approach**
   - Validated: JSON structure can store hypothesis metadata
   - Tool: iteration_state.json
   - Confidence: 100%

#### 🔍 Research Gaps

1. **iteration_state.json complete schema**
   - Unknown: Which sections are created by /qc-init vs added later?
   - Unknown: What's the minimal schema vs full schema?
   - Unknown: How to version/migrate schema changes?
   - **Priority**: HIGH - This is foundational
   - **Research needed**: Define authoritative schema with examples

2. **Hypothesis generation methodology**
   - Unknown: How to generate diverse hypotheses systematically?
   - Unknown: How to avoid repeating failed approaches?
   - Unknown: What hypothesis metadata is needed for learning?
   - **Priority**: MEDIUM - Can start with manual hypotheses
   - **Research needed**: Study strategy taxonomy, factor libraries

#### 📋 Implementation Tasks

- Write /qc-init slash command (reads schema, writes JSON, creates git branch)
- Create template iteration_state.json
- Write hypothesis validation logic
- Git integration (branch creation, initial commit)

**Estimated**: 4-6 hours once schema defined

---

### Phase 2: IMPLEMENTATION → Code with QC Skill

#### ✅ Validated Knowledge

1. **QuantConnect Lean Framework**
   - Validated: Extensive documentation exists
   - Validated: Created comprehensive skill (2,588 lines)
   - Coverage: Algorithm structure, indicators, data access, order handling
   - Confidence: 90%

2. **File upload via API**
   - Validated: api.create_file() works in testing
   - Method: HTTP POST with HMAC auth
   - Confidence: 95%

3. **Project creation**
   - Validated: api.create_project() works
   - Returns: project_id for subsequent calls
   - Confidence: 95%

#### 🔍 Research Gaps

1. **Strategy compilation verification**
   - Unknown: How to verify strategy compiles before backtesting?
   - Unknown: Does QC API provide compile endpoint?
   - Unknown: How to parse compile errors for autonomous fixing?
   - **Priority**: MEDIUM - Can run backtest and catch errors there
   - **Research needed**: Check QC API docs for compile endpoint

2. **Skill integration with code generation**
   - Unknown: How does Claude actually USE the skill when coding?
   - Unknown: Should skill contain templates that Claude fills in?
   - Unknown: How to ensure generated code follows QC best practices?
   - **Priority**: LOW - Claude's inherent capability handles this
   - **Research needed**: Test Claude's code generation with skill loaded

#### 📋 Implementation Tasks

- Complete QuantConnect Skill with examples
- Create strategy templates (momentum, mean reversion, etc.)
- Write code validation logic
- File upload wrapper function
- Error parsing for common mistakes

**Estimated**: 6-8 hours (skill exists, needs refinement)

---

### Phase 3: BACKTEST → API Execution

#### ✅ Validated Knowledge

1. **Backtest API works**
   - Validated: api.create_backtest() tested successfully
   - Validated: Returns backtest_id for status checking
   - Returns: Statistics JSON with all metrics
   - Confidence: 95%

2. **Result parsing**
   - Validated: Can extract Sharpe, trades, drawdown from JSON
   - Validated: Statistics are reliable
   - Confidence: 90%

3. **Decision thresholds (preliminary)**
   - Research: Industry standards suggest Sharpe > 1.0 for live trading
   - Research: Minimum 20-30 trades for statistical significance
   - Confidence: 60% - needs validation with real results

#### 🔍 Research Gaps

1. **Decision threshold calibration**
   - Unknown: What Sharpe threshold has best predictive power?
   - Unknown: Does threshold vary by strategy type (momentum vs mean reversion)?
   - Unknown: How to detect curve-fitting from backtest alone?
   - **Priority**: HIGH - Bad thresholds = bad decisions
   - **Research needed**: Test 20+ hypotheses, measure false positive/negative rates

2. **Backtest reliability**
   - Unknown: How often do QC backtests have data issues?
   - Unknown: What checks should we add (data gaps, splits, dividends)?
   - Unknown: How to detect "too good to be true" results?
   - **Priority**: MEDIUM - Can start conservatively and refine
   - **Research needed**: Run 50+ backtests, catalog failure modes

3. **Time period selection**
   - Unknown: What historical period best predicts future performance?
   - Unknown: Should we test multiple periods in Phase 3?
   - Unknown: How to handle regime changes (2008 crisis, COVID, etc.)?
   - **Priority**: MEDIUM - Start with recent 3-5 years
   - **Research needed**: Literature review + empirical testing

#### 📋 Implementation Tasks

- Write qc_backtest.py wrapper (mostly exists)
- Implement decision framework with conservative thresholds
- Parse backtest results into standard format
- Update iteration_state.json with results
- Write decisions_log.md entry
- Git commit with metrics

**Estimated**: 8-10 hours

---

### Phase 4: OPTIMIZATION → Parameter Tuning

#### ✅ Validated Knowledge

1. **Optimization API exists**
   - Validated: api.create_optimization() documented
   - Requires: Paid QC tier ($8/month minimum)
   - Returns: optimization_id for results retrieval
   - Confidence: 80% (documented but not tested on paid tier)

2. **Parameter definition format**
   - Validated: QC uses OptimizationParameter objects
   - Format: (name, min, max, step)
   - Confidence: 85%

3. **Overfitting detection heuristics**
   - Research: >30% improvement often indicates overfitting
   - Research: Parameters should be economically interpretable
   - Confidence: 50% - heuristic, not validated

#### 🔍 Research Gaps

1. **Optimization cost and time**
   - Unknown: How much does one optimization cost?
   - Unknown: How long does optimization take (for budgeting)?
   - Unknown: Does grid size affect cost?
   - **Priority**: HIGH - Affects framework economics
   - **Research needed**: Run 5-10 optimizations, measure cost/time

2. **Alternative: Manual parameter testing**
   - Unknown: Can we achieve same results with manual grid search?
   - Unknown: How many parameter combinations is feasible on free tier?
   - Unknown: Would this take too long for autonomous workflow?
   - **Priority**: HIGH - Could eliminate paid tier requirement
   - **Research needed**: Prototype manual optimization, compare results

3. **Overfitting detection**
   - Unknown: Can we detect overfitting from optimization results alone?
   - Unknown: What patterns indicate over-parameterization?
   - Unknown: Should we use regularization or parameter limits?
   - **Priority**: HIGH - False positives are expensive
   - **Research needed**: Test optimized strategies in Phase 5, measure failure rate

4. **Parameter stability**
   - Unknown: Should "good" parameters be stable across multiple optimizations?
   - Unknown: How to measure parameter sensitivity?
   - Unknown: What variance in optimal parameters is acceptable?
   - **Priority**: MEDIUM - Adds confidence to decisions
   - **Research needed**: Run same optimization 10 times, measure variance

#### 📋 Implementation Tasks

- Write qc_optimize_wrapper.py
- Parameter configuration format (JSON)
- Decision framework (improvement thresholds)
- Cost estimation logic
- Update iteration_state.json
- Git commit with parameter results

**Estimated**: 10-12 hours

**Blocker**: Requires paid QC tier OR alternative manual approach

---

### Phase 5: VALIDATION → Walk-Forward Testing

#### ✅ Validated Knowledge

1. **Walk-forward concept**
   - Validated: Industry-standard robustness test
   - Method: Train on period A, test on period B (out-of-sample)
   - Repeat: Monte Carlo sampling of train/test splits
   - Confidence: 90% (methodology well-established)

2. **Degradation metric**
   - Validated: (In-sample Sharpe - OOS Sharpe) / In-sample Sharpe
   - Threshold: <15% degradation suggests robust
   - Confidence: 70% (heuristic, needs calibration)

3. **Synthetic data generation**
   - Validated: GARCH + Jump-Diffusion can model volatility
   - Tool: scipy, arch library
   - Use case: Generate scenarios for stress testing
   - Confidence: 60% - generates realistic data, but unclear if helpful for decisions

#### 🔍 Research Gaps (CRITICAL - ARCHITECTURE BLOCKERS)

1. **⚠️ Implementation Approach (CRITICAL)**
   - Unknown: Should we use API calls or QuantBook?

   **Option A: External API Wrapper**
   ```python
   # qc_walkforward_wrapper.py
   for run in monte_carlo_runs:
       train_start, train_end, test_start, test_end = generate_split()
       # Create optimization for train period
       opt = api.create_optimization(project_id, train_start, train_end, params)
       best_params = wait_for_optimization(opt)
       # Create backtest for test period
       backtest = api.create_backtest(project_id, test_start, test_end, best_params)
       test_sharpe = wait_for_backtest(backtest)
   ```
   - **Pros**: Fully autonomous, uses real QC engine
   - **Cons**: Expensive ($3-5 per run × 10 runs = $30-50 per hypothesis), requires paid tier
   - **Confidence**: 80% this works technically, 40% it's the right approach economically

   **Option B: Research Notebook with QuantBook**
   ```python
   # Inside QC Research notebook
   from QuantConnect.Research import QuantBook
   qb = QuantBook()

   for run in monte_carlo_runs:
       # Get data via QuantBook
       data = qb.History(["SPY"], 252*2, Resolution.Daily)
       train, test = random_split(data)

       # Pure Python strategy simulation???
       # Or qb.Optimize()??? Does this exist???
       best_params = optimize_in_python(train, param_grid)
       test_sharpe = run_strategy_python(test, best_params)
   ```
   - **Pros**: Free, integrated with QC data
   - **Cons**: Requires manual "Run All" (not 100% autonomous), uncertain if qb.Optimize() exists
   - **Confidence**: 40% this is feasible, 60% it's the right approach IF feasible

   **Priority**: **CRITICAL** - This is the #1 research question blocking architecture

   **Research needed**:
   - Upload test notebook to QC Research
   - Test if qb.Optimize() and qb.Backtest() exist
   - Test if pure Python strategy simulation works
   - Measure execution time and reliability
   - **Decision point**: Choose Option A or B based on results

2. **Pure Python strategy execution**
   - Unknown: Can we run a QC strategy in pure Python without QC engine?
   - Unknown: How to replicate data access (Securities[], MarketOrder, etc.)?
   - Unknown: Would results match QC backtest results?
   - **Priority**: HIGH if Option B chosen
   - **Research needed**: Prototype strategy simulator in Python

3. **Monte Carlo statistical methodology**
   - Unknown: How many runs needed for statistical significance?
   - Unknown: Should we use synthetic data or real time periods?
   - Unknown: How to measure "robustness" objectively?
   - **Priority**: MEDIUM - start with 10 runs, refine
   - **Research needed**: Literature review on walk-forward validation

4. **Synthetic data utility**
   - Unknown: Does synthetic data improve decisions?
   - Unknown: Should it match specific backtest or general market?
   - Unknown: How to validate synthetic data is realistic?
   - **Priority**: LOW - nice to have, not essential
   - **Research needed**: A/B test with vs without synthetic data

#### 📋 Implementation Tasks

**Depends on research outcome (Option A or B)**

**Option A: API Wrapper**
- Write qc_walkforward_wrapper.py
- Monte Carlo train/test split generator
- API orchestration (multiple optimizations + backtests)
- Statistical analysis of results
- Decision framework (degradation thresholds)
- Cost estimation and budgeting

**Option B: Research Notebook**
- Write monte_carlo_validation.ipynb
- QuantBook integration
- Pure Python strategy simulator (if needed)
- Upload automation (api.create_file for notebooks)
- Manual execution instructions
- Results retrieval and parsing

**Estimated**: 12-16 hours (after research clarifies approach)

**Blocker**: CRITICAL research gap - must resolve before implementation

---

### Cross-Cutting Concerns

#### ✅ Validated Knowledge

1. **Git integration**
   - Validated: Can commit from Claude Code
   - Validated: Can create branches, tags
   - Confidence: 100%

2. **HMAC authentication**
   - Validated: QC API uses HMAC-SHA256
   - Validated: Python hmac library works
   - Confidence: 100%

3. **JSON state management**
   - Validated: JSON is reliable for persistent state
   - Validated: Can read/write atomically
   - Confidence: 100%

#### 🔍 Research Gaps

1. **Skills integration with autonomous decisions**
   - Unknown: How should Claude USE skills to make decisions?
   - Unknown: Should thresholds be in skills or iteration_state.json?
   - Unknown: Can skills provide dynamic thresholds based on strategy type?
   - **Priority**: MEDIUM - can hard-code thresholds initially
   - **Research needed**: Test different skill structures, measure decision quality

2. **Error handling and recovery**
   - Unknown: What happens if API call fails mid-workflow?
   - Unknown: How to resume from error state?
   - Unknown: Should we retry or fail fast?
   - **Priority**: MEDIUM - affects reliability
   - **Research needed**: Inject failures, test recovery paths

3. **Iteration limit logic**
   - Unknown: Should we allow re-testing with different parameters?
   - Unknown: How to prevent infinite loops?
   - Unknown: When to generate new hypothesis vs refine current?
   - **Priority**: LOW - start with strict 3-iteration limit
   - **Research needed**: Observe patterns in real usage

---

## Baseline Routing Logic Implementation Gaps

**From**: PREVIOUS_WORK/PROJECT_DOCUMENTATION/autonomous_decision_framework.md

The baseline defines complete routing logic. Here's what needs to be implemented:

### 1. Decision Functions (Implementation Task)

**Status**: Defined in baseline, need to implement

**Functions to build**:
```python
# Phase 3
evaluate_backtest(results, thresholds, state, config) → Action

# Phase 4
evaluate_optimization(opt_results, baseline, thresholds, state) → Action
calculate_sensitivity(optimization_results) → float
calculate_median_parameters(top_quartile) → params

# Phase 5
evaluate_validation(in_sample, out_of_sample, thresholds, state, config) → Action

# Special cases
handle_exceptional_performance(results, thresholds) → Action or None
detect_systematic_failure(state) → Action or None
handle_context_overflow(state, config) → void
```

**Estimated**: 12-16 hours for all decision functions

**Confidence**: 90% (logic defined, just needs coding)

---

### 2. Action Functions (Implementation Task)

**Status**: Defined in baseline, need to implement

**Actions to build**:
```python
# Routing actions
PROCEED_TO_VALIDATION(results)
PROCEED_TO_OPTIMIZATION(results)
PROCEED_TO_VALIDATION_WITH_PARAMS(params)
ABANDON_HYPOTHESIS(reason)
FIX_BUG(error_message)
ASK_USER(question_dict)
ESCALATE_TO_HUMAN(reason)
STRATEGY_COMPLETE(results)
STRATEGY_VALIDATED_SUBOPTIMAL(results)
RETRY_OPTIMIZATION_WALKFORWARD()

# State management
checkpoint_create()
save_state(state)
log_hypothesis_outcome(hypothesis, outcome, results)
document_strategy(state, results)
```

**Estimated**: 8-10 hours for all action functions

**Confidence**: 95% (straightforward state updates and logging)

---

### 3. Master Control Loop (Implementation Task)

**Status**: Fully defined in baseline, need to implement

**Components**:
```python
autonomous_strategy_development(initial_config) → Result
abandon_and_next_hypothesis(state) → state
execute_research_phase(state) → hypotheses
execute_implementation_phase(hypothesis) → code
execute_backtest_phase(code) → results
execute_optimization_phase(code, baseline) → opt_results
execute_validation_phase(code) → oos_results
```

**Estimated**: 16-20 hours for complete control loop

**Confidence**: 80% (complex orchestration, needs testing)

---

### 4. Threshold Calibration (Research + Tuning)

**Status**: Initial values in baseline, need empirical validation

**To calibrate**:
```json
{
  "minimum_viable": {"sharpe_ratio": 0.5}, // Is 0.5 correct?
  "optimization_worthy": {"sharpe_ratio": 0.7}, // Is 0.7 correct?
  "production_ready": {"sharpe_ratio": 1.0}, // Is 1.0 correct?
  "too_perfect_sharpe": 3.0, // Is 3.0 correct?
  "too_few_trades": 10, // Is 10 correct?
  "improvement_threshold": 0.05, // 5% minimum improvement?
  "degradation_threshold": 0.30 // 30% degradation acceptable?
}
```

**Method**:
1. Use baseline thresholds initially
2. Test with 20+ hypotheses
3. Measure false positive/negative rates
4. Adjust based on outcomes

**Estimated**: 20-30 hours (spread across testing phase)

**Confidence**: 60% (empirical, requires iteration)

---

### 5. Configuration Schema (Implementation Task)

**Status**: Defined in baseline, need to create files

**Files to create**:
```
config/
├── thresholds.json (performance criteria, overfitting signals)
├── limits.json (iteration limits, cost limits)
├── autonomy_mode.json (minimal, medium, full)
└── README.md (configuration guide)
```

**Estimated**: 2-3 hours

**Confidence**: 100% (straightforward JSON)

---

### 6. Logging & Auditability (Implementation Task)

**Status**: Formats defined in baseline, need to implement

**To implement**:
```python
# Decision logging
log_decision(timestamp, phase, decision_point, inputs, decision, rationale, confidence)

# Hypothesis logging
log_hypothesis(hypothesis_id, name, attempts, results, outcome, cost, time)

# Parseable formats
decisions_log.md (human-readable)
decisions_log.json (machine-readable)
hypotheses_log.json (complete history)
```

**Estimated**: 4-6 hours

**Confidence**: 95% (logging is straightforward)

---

### 7. Phase 5 Implementation (STILL UNCLEAR - Research Gap)

**Status**: Routing logic defined, but HOW to execute validation unclear

**Baseline assumes**:
```python
oos_results = execute_validation_phase(state.current_code)
```

**But HOW**?
- Option A: API calls (qc_walkforward_wrapper.py) - expensive
- Option B: QuantBook notebook - needs research

**This is still Priority 0 research gap** (unchanged from before)

---

### Total Implementation from Baseline

| Component | Hours | Type | Confidence |
|-----------|-------|------|------------|
| Decision functions | 12-16 | Implementation | 90% |
| Action functions | 8-10 | Implementation | 95% |
| Master control loop | 16-20 | Implementation | 80% |
| Threshold calibration | 20-30 | Research | 60% |
| Configuration files | 2-3 | Implementation | 100% |
| Logging system | 4-6 | Implementation | 95% |
| Phase 5 approach | 4-8 | Research | 40% |
| **Total** | **66-93 hours** | **Mixed** | **80% avg** |

---

## Summary: Research Priorities

### P0: CRITICAL (Blocks Architecture)

1. **Phase 5 Implementation Approach**
   - API wrapper vs QuantBook notebook
   - Does qb.Optimize()/qb.Backtest() exist?
   - Cost/autonomy trade-off
   - **Action**: Upload test notebook to QC Research, experiment
   - **ETA**: 4-8 hours research

2. **iteration_state.json Complete Schema**
   - Define minimal vs full schema
   - Document which commands write which sections
   - Create authoritative template
   - **Action**: Review all phases, define complete JSON structure
   - **ETA**: 2-4 hours

### P1: HIGH (Affects Quality)

3. **Decision Threshold Calibration**
   - Test thresholds with real data
   - Measure false positive/negative rates
   - Refine based on empirical results
   - **Action**: Run 20+ hypotheses, analyze outcomes
   - **ETA**: 20-30 hours (spread over testing)

4. **Optimization Cost and Feasibility**
   - Test paid tier optimization
   - Measure cost per optimization
   - Evaluate manual alternative
   - **Action**: Subscribe to paid tier for 1 month, run tests
   - **ETA**: 8-12 hours + $8-60 cost

5. **Overfitting Detection**
   - Pattern recognition in optimization results
   - Validation failure analysis
   - Regularization techniques
   - **Action**: Collect data from Phase 4/5 testing
   - **ETA**: Ongoing during testing phase

### P2: MEDIUM (Can Iterate)

6. **Skills Architecture**
   - Test integration with decisions
   - Dynamic threshold capability
   - Strategy-specific knowledge
   - **Action**: Prototype different skill structures
   - **ETA**: 4-6 hours

7. **Pure Python Strategy Simulator**
   - If QuantBook approach chosen
   - Replicate QC engine behavior
   - Validate accuracy vs QC backtest
   - **Action**: Build simulator, compare results
   - **ETA**: 12-16 hours

### P3: LOW (Nice to Have)

8. **Synthetic Data Utility**
   - A/B test with real strategies
   - Measure impact on decisions
   - Refine generation parameters
   - **Action**: Include in some Phase 5 tests
   - **ETA**: 4-8 hours

9. **Hypothesis Generation**
   - Systematic approach
   - Factor library
   - Avoid repeating failures
   - **Action**: Study strategy taxonomy
   - **ETA**: 8-12 hours

---

## Research Phase Timeline

### Week 1-2: Critical Research (P0)

**Goal**: Resolve architecture-blocking questions

Tasks:
1. Phase 5 approach research (QuantBook testing)
2. Define iteration_state.json schema
3. Build minimal Phase 1-3 prototype

**Deliverables**:
- Validated Phase 5 approach (Option A or B)
- Authoritative iteration_state.json schema
- Working /qc-init, /qc-backtest commands

**ETA**: 20-30 hours

### Week 3-4: High Priority Research (P1)

**Goal**: Validate decision frameworks

Tasks:
1. Test decision thresholds with 10 hypotheses
2. Measure false positive/negative rates
3. Refine thresholds based on data
4. Test optimization (paid tier or manual)

**Deliverables**:
- Calibrated decision thresholds
- Phase 4 approach validated
- Complete Phase 1-4 working

**ETA**: 30-40 hours

### Week 5-6: Integration & Testing (P1 + P2)

**Goal**: Full framework operational

Tasks:
1. Implement Phase 5 (validated approach)
2. Skills integration
3. End-to-end testing with 10+ hypotheses
4. Error handling and recovery

**Deliverables**:
- Complete autonomous framework
- 10+ hypotheses tested
- Framework documentation

**ETA**: 40-50 hours

**Total Research + MVP**: 90-120 hours over 6 weeks

---

## Risk Assessment

### High Risk (Could Fail)

1. **Phase 5 QuantBook approach infeasible**
   - Risk: qb.Optimize() doesn't exist, pure Python too different from QC
   - Impact: Forced to use expensive API approach or abandon Phase 5
   - Mitigation: Research immediately (P0), prepare API fallback
   - Probability: 30%

2. **Decision thresholds unreliable**
   - Risk: No threshold reliably separates good from bad strategies
   - Impact: High false positive/negative rates, manual review still needed
   - Mitigation: Conservative thresholds + ESCALATE decisions
   - Probability: 20%

### Medium Risk (Solvable)

3. **Optimization too expensive**
   - Risk: $30-50 per hypothesis makes framework uneconomical
   - Impact: Need to find cheaper approach or skip Phase 4
   - Mitigation: Manual parameter testing, or accept cost
   - Probability: 40%

4. **Skills don't improve decisions**
   - Risk: Claude makes same decisions with or without skills
   - Impact: Wasted effort on skills, not harmful
   - Mitigation: Start with hard-coded thresholds
   - Probability: 30%

### Low Risk (Manageable)

5. **API rate limits**
   - Risk: QC throttles requests
   - Impact: Slower execution
   - Mitigation: Backoff and retry logic
   - Probability: 50% but low impact

6. **Git conflicts**
   - Risk: Merge issues with hypothesis branches
   - Impact: Manual git fixes
   - Mitigation: Simple branch strategy (never merge to main)
   - Probability: 20%

---

## Go/No-Go Decision Points

### Decision Point 1: After Week 2 Research

**Question**: Is Phase 5 feasible with QuantBook?

**Go**: qb.Optimize() works OR pure Python simulator is accurate
**No-Go**: Must use expensive API, changes economics

**Action if No-Go**: Evaluate API cost, consider skipping Phase 5 for MVP

### Decision Point 2: After Week 4 Testing

**Question**: Are decision thresholds reliable?

**Go**: <20% false positive rate, <30% false negative rate
**No-Go**: Thresholds too unreliable, high manual review needed

**Action if No-Go**: Pivot to "human-in-loop" model with decision recommendations

### Decision Point 3: After Week 6 Integration

**Question**: Is the framework providing value?

**Go**: Testing 10+ hypotheses faster than manual, good decisions
**No-Go**: Still too much manual work, or bad decision quality

**Action if No-Go**: Simplify to "assisted workflow" instead of "autonomous"

---

## Conclusion

### What We Know (Can Implement)
- Phase 1-3 are straightforward
- Git integration works
- QuantConnect API is reliable
- Skill approach is viable

### What We Don't Know (Must Research)
1. **Phase 5 implementation approach** (CRITICAL)
2. **Decision threshold calibration** (HIGH)
3. **Optimization cost and approach** (HIGH)

### Recommended Path Forward

**Phase 1: Research (Weeks 1-2)**
- Resolve P0 questions (Phase 5 approach, schema)
- Build minimal prototype (Phase 1-3)
- Test with 3-5 hypotheses

**Phase 2: Validate (Weeks 3-4)**
- Resolve P1 questions (thresholds, optimization)
- Expand to Phase 1-4
- Test with 10 hypotheses

**Phase 3: Complete (Weeks 5-6)**
- Implement Phase 5 (validated approach)
- Full integration testing
- Documentation

**Total**: 6 weeks, 90-120 hours

**Success Criteria**: Testing 10 hypotheses in 40 hours (vs 60 hours manual) with <20% false positive rate

---

**Status**: Research gaps identified, timeline proposed
**Next**: new_project_timeline.md with detailed plan
**Blocker**: Phase 5 approach must be researched before full implementation
