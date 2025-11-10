# Project Timeline - Autonomous Framework Development

**Approach**: Research-driven development with validation gates
**Duration**: 6 weeks (90-120 hours)
**Start Date**: November 11, 2025 (proposed)

---

## Timeline Philosophy

**Not**: Build everything then test
**Instead**: Research → Prototype → Validate → Build → Test (iterative)

**Key Principle**: Resolve unknowns BEFORE implementation to avoid rework

---

## Phase 1: Critical Research (Weeks 1-2)

**Goal**: Resolve architecture-blocking questions

**Duration**: 2 weeks, 20-30 hours

### Week 1: Phase 5 Research (Priority 0)

#### Research Question 1: QuantBook Capabilities

**Task**: Test QuantBook in QC Research environment

Steps:
1. Create QC Research notebook
2. Test if these methods exist:
   ```python
   from QuantConnect.Research import QuantBook
   qb = QuantBook()

   # Test 1: Data access
   data = qb.History(["SPY"], 252, Resolution.Daily)

   # Test 2: Does qb.Optimize() exist?
   optimization = qb.Optimize(...)  # ???

   # Test 3: Does qb.Backtest() exist?
   backtest = qb.Backtest(...)  # ???
   ```

3. Document what exists vs what doesn't
4. Test if pure Python strategy simulation is feasible

**Deliverables**:
- Research report: "QuantBook Capabilities Assessment"
- Decision: Option A (API) or Option B (QuantBook) for Phase 5
- If Option B: Prototype pure Python strategy simulator

**Time**: 6-8 hours

**Decision Point**: By end of Week 1, we commit to Phase 5 approach

---

#### Research Question 2: iteration_state.json Schema

**Task**: Define authoritative schema for state machine

Steps:
1. Review all 5 phases
2. List what data each phase needs to READ
3. List what data each phase needs to WRITE
4. Design minimal schema (Phase 1) vs full schema (Phase 5)
5. Define schema versioning strategy

**Deliverables**:
- `iteration_state_schema.json` - Complete schema with comments
- `iteration_state_minimal.json` - Template for /qc-init
- Documentation: "State Machine Design"

**Time**: 3-4 hours

---

#### Implementation: Minimal Prototype (Phase 1-3)

**Task**: Build working Phase 1-3 to validate concepts

Components:
1. `/qc-init` command
   - Prompts for hypothesis details
   - Creates iteration_state.json (minimal schema)
   - Creates git branch
   - Initial commit

2. `qc_backtest.py` wrapper
   - HMAC authentication
   - Project creation
   - File upload
   - Backtest execution
   - Result parsing

3. `/qc-backtest` command
   - Reads iteration_state.json
   - Calls qc_backtest.py
   - Parses results
   - Makes ABANDON/PROCEED decision (hard-coded thresholds)
   - Updates iteration_state.json
   - Commits to git

**Deliverables**:
- Working /qc-init and /qc-backtest commands
- qc_backtest.py tested with real QC API
- 3 test hypotheses run through Phase 1-3

**Time**: 10-12 hours

**Validation**: Can run hypothesis from idea → backtest → decision without manual intervention

---

### Week 1 Checkpoint

**Expected State**:
- ✅ Phase 5 approach decided (API or QuantBook)
- ✅ iteration_state.json schema defined
- ✅ Phase 1-3 prototype working
- ✅ 3 hypotheses tested (proof of concept)

**Go/No-Go Decision**:
- Can we proceed with chosen Phase 5 approach?
- Are Phase 1-3 concepts validated?

---

### Week 2: Decision Framework Research

#### Research Question 3: Decision Threshold Calibration

**Task**: Test decision thresholds with real backtests

Steps:
1. Generate 10 diverse hypotheses:
   - Momentum strategies (3)
   - Mean reversion strategies (3)
   - Trend following strategies (2)
   - Contrarian strategies (2)

2. Run all through Phase 3 (backtest)

3. For each result, manually classify:
   - Should proceed to optimization? (yes/no)
   - Why? (record reasoning)

4. Compare manual decisions to threshold-based decisions:
   ```python
   # Current thresholds (to test)
   if sharpe < 0.5: ABANDON
   if trades < 10: ABANDON
   if sharpe > 2.0: ESCALATE
   else: PROCEED
   ```

5. Calculate false positive and false negative rates

6. Refine thresholds to minimize errors

**Deliverables**:
- Research report: "Backtest Decision Threshold Calibration"
- 10 hypothesis test results
- Refined decision thresholds with confidence intervals
- False positive/negative analysis

**Time**: 8-10 hours

---

#### Implementation: Phase 2 + Skills

**Task**: Complete strategy implementation automation

Components:
1. **QuantConnect Skill** (refine existing)
   - Strategy templates
   - Example algorithms
   - Common patterns
   - Error reference

2. **Backtesting Analysis Skill** (NEW)
   - How to interpret Sharpe ratio
   - Trade frequency analysis
   - Drawdown interpretation
   - Overfitting detection patterns
   - Strategy-specific thresholds

3. **Project structure**
   - .claude/skills/quantconnect/
   - .claude/skills/backtesting-analysis/
   - Documentation and examples

**Deliverables**:
- Complete QuantConnect Skill
- Backtesting Analysis Skill
- Phase 2 implementation complete

**Time**: 6-8 hours

---

### Week 2 Checkpoint

**Expected State**:
- ✅ Decision thresholds calibrated with real data
- ✅ Phase 1-3 fully operational
- ✅ Skills created and integrated
- ✅ 10+ hypotheses tested end-to-end (Phase 1-3)

**Go/No-Go Decision**:
- Are decision thresholds reliable (<20% false positive rate)?
- Is autonomous decision-making working as expected?

---

## Phase 2: Optimization & Validation (Weeks 3-4)

**Goal**: Complete Phase 4-5, validate full workflow

**Duration**: 2 weeks, 30-40 hours

### Week 3: Phase 4 Implementation & Research

#### Research Question 4: Optimization Cost & Approach

**Task**: Test QC optimization API on paid tier

Steps:
1. Subscribe to QC paid tier ($8/month minimum)

2. Run 5 optimization tests:
   - Different grid sizes (3x3, 5x5, 10x10)
   - Different target metrics (Sharpe, Sortino, etc.)
   - Different strategies

3. Measure for each:
   - Actual cost charged
   - Time to complete
   - Quality of results

4. Test alternative: Manual parameter testing
   - Run same 5 tests using multiple backtests
   - Compare cost (# of backtests, API calls)
   - Compare results quality

5. Decision: Paid optimization or manual approach?

**Deliverables**:
- Research report: "Optimization Cost Analysis"
- Paid vs manual comparison
- Recommendation: Approach for Phase 4

**Time**: 8-10 hours + $8-60 cost

---

#### Implementation: Phase 4 (Optimization)

**Task**: Build optimization workflow (based on research outcome)

**Option A: Paid Tier Optimization**

Components:
1. `qc_optimize_wrapper.py`
   - Parameter grid configuration
   - Cost estimation
   - api.create_optimization() call
   - Progress monitoring
   - Result parsing

2. `/qc-optimize` command
   - Reads baseline from iteration_state.json
   - Calls wrapper
   - Decision framework (improvement thresholds)
   - Updates state
   - Commits results

**Option B: Manual Parameter Testing**

Components:
1. `manual_optimize.py`
   - Parameter grid generator
   - Multiple backtest orchestration
   - Result aggregation
   - Best parameter selection

2. `/qc-optimize` command
   - Same interface as Option A
   - Different implementation

**Deliverables**:
- Working Phase 4 (optimization)
- Optimization Skill (parameter tuning theory)
- Decision framework for optimization results
- Cost tracking in iteration_state.json

**Time**: 10-12 hours

---

#### Research Question 5: Overfitting Detection

**Task**: Test how optimization results perform in validation

Steps:
1. Take 5 strategies that passed Phase 3
2. Optimize parameters (Phase 4)
3. Note improvement percentage
4. Run validation (Phase 5) on each
5. Measure degradation (in-sample vs out-of-sample)
6. Correlate: Does high improvement predict high degradation?

**Analysis**:
- If improvement >30%, does degradation >40%?
- What improvement threshold indicates overfitting risk?

**Deliverables**:
- Research report: "Overfitting Detection Patterns"
- Refined Phase 4 decision framework
- ESCALATE thresholds for Phase 4

**Time**: 6-8 hours (part of Phase 5 testing)

---

### Week 3 Checkpoint

**Expected State**:
- ✅ Optimization approach validated (paid or manual)
- ✅ Phase 1-4 fully operational
- ✅ Optimization Skill created
- ✅ 5 strategies optimized and tested

**Go/No-Go Decision**:
- Is optimization economically viable?
- Are overfitting detection heuristics working?

---

### Week 4: Phase 5 Implementation

#### Implementation: Phase 5 (Validation)

**Task**: Build walk-forward validation (based on Week 1 research)

**Option A: API-Based Wrapper**

Components:
1. `qc_walkforward_wrapper.py`
   - Monte Carlo train/test split generator
   - Multiple optimization API calls (training periods)
   - Multiple backtest API calls (test periods)
   - Statistical analysis (degradation distribution)
   - Robustness scoring

2. `/qc-validate` command
   - Reads optimized parameters
   - Calls wrapper
   - Decision framework (robustness thresholds)
   - Updates state
   - Commits results

**Option B: QuantBook Research Notebook**

Components:
1. `monte_carlo_validation.ipynb`
   - QuantBook data access
   - Pure Python strategy simulator
   - Monte Carlo sampling
   - Statistical analysis

2. `upload_notebook.py`
   - Uploads notebook to QC Research
   - API: api.create_file() for notebooks

3. `/qc-validate` command
   - Uploads notebook
   - Instructions: "Run All in QC Research"
   - Reads results (manual download or API)
   - Decision framework
   - Updates state

**Deliverables**:
- Working Phase 5 (validation)
- Validation Skill (walk-forward theory)
- Monte Carlo decision framework
- Complete autonomous workflow (Phase 1-5)

**Time**: 12-16 hours

---

#### Research Question 6: Validation Reliability

**Task**: Test validation predictive power

Steps:
1. Run 10 strategies through Phase 1-5
2. For those marked "DEPLOY", simulate live trading:
   - Run backtest on most recent 3 months (out-of-sample)
   - Treat as "live" performance

3. Measure:
   - Did "robust" strategies actually perform well?
   - Did "abandon" decisions correctly filter bad strategies?
   - What's the false positive rate? (marked deploy, failed live)

**Deliverables**:
- Research report: "Validation Predictive Power"
- Confidence intervals for deployment decisions
- Framework reliability metrics

**Time**: 8-10 hours

---

### Week 4 Checkpoint

**Expected State**:
- ✅ Complete Phase 1-5 operational
- ✅ 10+ strategies tested end-to-end
- ✅ Validation reliability measured
- ✅ All skills created

**Go/No-Go Decision**:
- Is the framework making good decisions?
- Is it faster than manual workflow?
- Is the cost acceptable?

---

## Phase 3: Integration & Polish (Weeks 5-6)

**Goal**: Production-ready framework with documentation

**Duration**: 2 weeks, 40-50 hours

### Week 5: Integration & Error Handling

#### Tasks

1. **Error handling**
   - API failure recovery
   - Retry logic with backoff
   - State corruption detection
   - Resume from error state

2. **Additional commands**
   - /qc-status: Show current state, progress
   - /qc-report: Generate complete hypothesis report
   - /qc-rollback: Reset to previous phase

3. **Logging & debugging**
   - Detailed logs for each phase
   - Debug mode for troubleshooting
   - Performance metrics collection

4. **Configuration**
   - Make thresholds configurable (config.json)
   - Strategy-specific overrides
   - Cost limits and budgets

5. **Skills refinement**
   - Test skills with real usage
   - Add examples from actual errors
   - Refine decision guidance

**Deliverables**:
- Robust error handling
- Additional commands operational
- Logging and debugging infrastructure
- Configuration system

**Time**: 20-25 hours

---

### Week 6: Testing & Documentation

#### Tasks

1. **End-to-end testing**
   - Run 20 diverse hypotheses through full workflow
   - Measure:
     - Time per hypothesis
     - Cost per hypothesis
     - Decision quality (manual review)
     - Error rate

2. **Performance optimization**
   - Identify bottlenecks
   - Optimize slow operations
   - Reduce API calls where possible

3. **Documentation**
   - User guide: How to use the framework
   - Architecture documentation
   - Decision framework documentation
   - Troubleshooting guide
   - Schema reference

4. **Framework validation**
   - Calculate ROI (time saved vs investment)
   - Measure decision quality metrics
   - Assess cost efficiency
   - Identify improvement areas

**Deliverables**:
- 20+ hypotheses tested
- Performance benchmarks
- Complete documentation
- Framework validation report

**Time**: 20-25 hours

---

### Week 6 Final Checkpoint

**Expected State**:
- ✅ Production-ready autonomous framework
- ✅ 20+ hypotheses tested end-to-end
- ✅ Complete documentation
- ✅ ROI validated
- ✅ Ready for ongoing use

**Success Criteria**:
- Can test 10 hypotheses in 40 hours (vs 60 manual)
- <20% false positive rate
- <$20 average cost per hypothesis
- <10% manual intervention needed

---

## Resource Requirements

### Time Investment

| Phase | Weeks | Hours | Focus |
|-------|-------|-------|-------|
| Research | 1-2 | 20-30 | Critical unknowns |
| Optimization & Validation | 3-4 | 30-40 | Complete workflow |
| Integration & Polish | 5-6 | 40-50 | Production ready |
| **Total** | **6** | **90-120** | Full framework |

### Financial Investment

| Item | Cost | When |
|------|------|------|
| QuantConnect (free tier) | $0 | Ongoing |
| QuantConnect (paid tier) | $8-60 | Week 3-6 (optional) |
| API usage (backtests) | ~$0 | Free tier |
| API usage (optimizations) | $0-50 | Week 3-4 (if paid tier) |
| **Total** | **$8-110** | **Over 6 weeks** |

### Risk Budget

| Risk | Probability | Mitigation Cost |
|------|-------------|-----------------|
| Phase 5 QuantBook infeasible | 30% | +20-30h (API fallback) |
| Decision thresholds unreliable | 20% | +10-15h (refinement) |
| Optimization too expensive | 40% | +0h (use manual) |
| **Worst case** | - | **+30-45h total** |

---

## Milestones & Deliverables

### Milestone 1: Phase 1-3 Working (End Week 2)
- ✅ Hypothesis → Backtest → Decision automated
- ✅ iteration_state.json schema defined
- ✅ 10+ hypotheses tested
- ✅ Decision thresholds calibrated

### Milestone 2: Phase 1-4 Working (End Week 3)
- ✅ Optimization integrated
- ✅ Overfitting detection working
- ✅ 5 strategies optimized
- ✅ Cost analysis complete

### Milestone 3: Phase 1-5 Complete (End Week 4)
- ✅ Full autonomous workflow operational
- ✅ Validation approach validated
- ✅ 10 strategies tested end-to-end
- ✅ Framework reliability measured

### Milestone 4: Production Ready (End Week 6)
- ✅ Error handling robust
- ✅ 20+ hypotheses tested
- ✅ Documentation complete
- ✅ ROI validated

---

## Metrics & Success Tracking

### Process Metrics

| Metric | Target | Measure |
|--------|--------|---------|
| Time per hypothesis | <4 hours | Track actual time |
| Cost per hypothesis | <$20 | Sum API costs |
| Manual intervention | <10% | Count manual steps |
| Error recovery rate | >90% | Errors recovered / total errors |

### Decision Quality Metrics

| Metric | Target | Measure |
|--------|--------|---------|
| False positive rate | <20% | Bad strategies marked DEPLOY |
| False negative rate | <30% | Good strategies marked ABANDON |
| Decision confidence | >80% | Clear outcome (not ESCALATE) |

### Business Metrics

| Metric | Target | Measure |
|--------|--------|---------|
| Time savings vs manual | >50% | (Manual time - Auto time) / Manual time |
| Viable strategies found | 1-2 | From 20+ hypotheses |
| Framework reliability | >90% | Successful runs / total runs |
| ROI (time) | >2x | Time saved / time invested |

---

## Weekly Review Questions

### Every Week: Progress Check

1. **Are we on schedule?** (compare actual vs planned hours)
2. **Are blockers resolved?** (decision points addressed)
3. **What did we learn?** (update gaps report)
4. **What changed?** (architecture adjustments)
5. **Are metrics on track?** (time, cost, quality)

### Major Decision Points

- **End Week 1**: Phase 5 approach committed
- **End Week 2**: Decision thresholds validated
- **End Week 3**: Optimization approach committed
- **End Week 4**: Full workflow validated
- **End Week 6**: Production readiness assessed

---

## Post-MVP Roadmap (Week 7+)

Once MVP is validated, potential enhancements:

1. **Master autonomous loop** (/qc-auto-iterate)
   - Fully autonomous multi-hypothesis testing
   - Automatic new hypothesis generation
   - Batch processing

2. **Strategy library**
   - Catalog tested hypotheses
   - Pattern recognition across strategies
   - Reuse successful components

3. **Adaptive thresholds**
   - Learn from outcomes
   - Strategy-type specific thresholds
   - Dynamic adjustment based on market regime

4. **Live trading integration**
   - Deployment automation
   - Position sizing
   - Risk management
   - Performance monitoring

---

## Conclusion

**Timeline**: 6 weeks, 90-120 hours
**Investment**: $8-110 + time
**Outcome**: Production-ready autonomous framework

**Critical Path**:
1. Week 1: Resolve Phase 5 approach (blocker)
2. Week 2: Validate decision thresholds
3. Week 3-4: Complete Phase 4-5
4. Week 5-6: Polish and validate

**Success Criteria**: Testing 10 hypotheses in 40 hours (33% less than manual) with good decision quality

**Next Step**: Write current_state.md to baseline what exists now vs this plan

---

**Created**: November 10, 2025
**Status**: Proposed timeline, pending approval
**Next**: Finalize approach, begin Week 1 research
