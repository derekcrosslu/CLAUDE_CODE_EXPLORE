# QuantConnect API Capabilities Assessment

**Date**: 2025-11-10
**Project**: Autonomous Strategy Development Framework
**Purpose**: Determine what can be automated vs what requires manual intervention

---

## Tested API Endpoints

### ✅ WORKING - Can Automate

| Endpoint | Purpose | Cost | Tested |
|----------|---------|------|--------|
| `POST /projects/list` | List all projects | FREE | ✅ |
| `POST /projects/read` | Get project details | FREE | ✅ |
| `POST /files/read` | Read file contents | FREE | ✅ |
| `POST /files/create` | Create/upload files | FREE | ✅ |
| `POST /files/update` | Update file contents | FREE | ✅ |
| `POST /compile/create` | Compile project | FREE | ✅ |
| `POST /backtests/list` | List backtests | FREE | ✅ |
| `POST /backtests/read` | Get backtest results | FREE | ✅ |
| `POST /backtests/create` | Run backtest | FREE (with limits) | ✅ |

### ⚠️ LIMITED - Costs Money or Has Constraints

| Endpoint | Purpose | Cost | Issue |
|----------|---------|------|-------|
| `POST /optimizations/create` | Run optimization | 💰 $0.50-$5+ per run | Requires paid tier |
| `POST /optimizations/estimate` | Estimate optimization cost | FREE | Tested, works |
| `POST /backtests/create` | Create backtest | FREE (10/day free tier) | Limited quota |

### ❌ NOT AVAILABLE - Cannot Automate

| Operation | Why Not Available |
|-----------|-------------------|
| Execute Research notebook cells | No API endpoint exists |
| Run `qb.Optimize()` via API | Only works inside Research environment |
| Run `qb.Backtest()` via API | Only works inside Research environment |
| Interactive notebook execution | Requires browser/web interface |

---

## Autonomous Framework Feasibility

### What CAN Be Fully Automated (via API):

1. **Project Management**
   - ✅ Create new projects
   - ✅ Upload strategy files
   - ✅ Compile code
   - ✅ Read project state

2. **Basic Backtesting**
   - ✅ Run single backtests (10/day free)
   - ✅ Read backtest results
   - ✅ Parse performance metrics
   - ✅ Make autonomous decisions based on results

3. **File Operations**
   - ✅ Upload notebooks to research.ipynb
   - ✅ Update strategy parameters
   - ✅ Read/write any project files

4. **State Management**
   - ✅ Track iteration state locally
   - ✅ Log decisions
   - ✅ Manage git commits

### What CANNOT Be Fully Automated:

1. **Parameter Optimization**
   - ❌ API optimization costs money (paid tier only)
   - ✅ Alternative: Upload notebook → user runs in Research (FREE)
   - Decision: **Hybrid approach required**

2. **Walk-Forward Validation**
   - ❌ Cannot execute Research notebooks remotely
   - ✅ Alternative: Upload notebook → user runs manually
   - Decision: **Manual step required**

3. **Advanced Analysis**
   - ❌ Cannot run QuantBook analysis automatically
   - ❌ No API for Monte Carlo sampling
   - Decision: **Notebook-based workflow only**

---

## Autonomous Framework Architectures

### Option A: Fully Automated (LIMITED)

**What's automated:**
- Hypothesis generation
- Strategy code creation
- Single backtest execution
- Basic parameter testing (grid search via multiple backtests)
- Decision making
- Git integration

**Limitations:**
- No true optimization (would need to burn backtest quota)
- No walk-forward validation
- Limited to 10 backtests/day on free tier
- Cannot do Monte Carlo analysis

**Cost:** FREE (within quotas)

**Feasibility:** ⚠️ Possible but constrained by backtest limits

---

### Option B: Hybrid (RECOMMENDED)

**What's automated:**
- Strategy creation and upload
- Initial baseline backtest
- Decision framework (proceed/optimize/abandon)
- Notebook generation and upload
- State tracking and git
- Results parsing (after user runs notebook)

**What requires manual intervention:**
- User runs optimization in Research (1-click, FREE)
- User runs walk-forward notebook (1-click, FREE)
- User provides results back to system

**Workflow:**
```
1. Claude creates strategy → automated
2. Claude uploads to QC → automated
3. Claude runs baseline backtest → automated
4. Claude makes decision → automated
5. IF needs optimization:
   a. Claude uploads notebook → automated
   b. USER runs in Research → MANUAL (1-click, FREE)
   c. Claude reads results → automated
6. Claude updates state → automated
7. Claude commits to git → automated
```

**Cost:** FREE

**Feasibility:** ✅ Highly feasible, best balance

---

### Option C: Paid Tier Automation

**What's automated:**
- Everything from Option A
- True optimization via API
- Multiple optimization runs
- Advanced parameter sweeps

**Requirements:**
- QuantConnect paid subscription ($8-$20/month)
- Optimization costs ($0.50-$5 per run)
- Higher backtest quotas

**Cost:** 💰 $50-$200+/month depending on usage

**Feasibility:** ✅ Fully feasible but expensive

---

## Recommendation for Autonomous Framework

### **Adopt Option B: Hybrid Approach**

**Rationale:**

1. **Cost-Effective**
   - Zero ongoing costs
   - No paid subscription required
   - Unlimited optimizations in Research

2. **Pragmatic**
   - One manual step (run notebook) is acceptable
   - Takes 1 minute of user time
   - Maintains full analytical power

3. **Scalable**
   - Can test multiple hypotheses per day
   - No quota limitations on Research
   - Easy to upgrade to Option C later

### Implementation:

**Autonomous Commands:**
- `/qc-init` - Fully automated
- `/qc-backtest` - Fully automated
- `/qc-optimize` - **Hybrid**: Claude uploads notebook, user runs it
- `/qc-validate` - **Hybrid**: Claude uploads notebook, user runs it
- `/qc-report` - Fully automated

**User Interaction Points:**
1. After `/qc-optimize`: "Notebook uploaded. Please run in Research and return when complete."
2. After `/qc-validate`: "Walk-forward notebook ready. Please run in Research."

**Autonomous Loop:**
```
while iteration < max_iterations:
    # Automated
    hypothesis = generate_hypothesis()
    strategy = create_strategy(hypothesis)
    upload(strategy)
    baseline = run_backtest()

    decision = evaluate(baseline)

    if decision == "optimize":
        # Hybrid - requires user
        notebook = generate_optimization_notebook()
        upload_notebook()
        wait_for_user("Run optimization in Research")
        results = read_results()

    if decision == "validate":
        # Hybrid - requires user
        notebook = generate_walkforward_notebook()
        upload_notebook()
        wait_for_user("Run walk-forward in Research")
        results = read_results()

    # Automated
    git_commit(results)
    log_decision()
    iteration += 1
```

---

## Current Status

### What Works NOW:

- ✅ `upload_research_notebook.py` - Upload notebooks to Research
- ✅ `qc_backtest.py` - Full API client for project/backtest operations
- ✅ `monte_carlo_walkforward_REAL.ipynb` - Complete Monte Carlo notebook
- ✅ API authentication and file operations
- ✅ Backtest creation and result parsing

### What Needs Implementation:

- ⚠️ Update `/qc-optimize` command to use hybrid approach
- ⚠️ Update `/qc-validate` command to use hybrid approach
- ⚠️ Create "wait for user" interaction in commands
- ⚠️ Implement result reading from Research outputs

### Deprecated:

- ❌ `qc_walkforward_wrapper.py` - Calls paid optimization API
- ❌ `qc_optimize_wrapper.py` - Calls paid optimization API (if exists)

---

## Conclusion

**The autonomous framework IS feasible with a hybrid approach.**

**Key Insight:**
By leveraging the Research environment for optimization and walk-forward validation, we get:
- ✅ Full analytical capabilities
- ✅ Zero ongoing costs
- ✅ 90% automation (only 2 manual 1-click steps)
- ✅ Scalable to multiple hypotheses

**Next Steps:**
1. Adopt hybrid architecture
2. Update slash commands for hybrid workflow
3. Test complete end-to-end flow
4. Document user interaction points

**Trade-off:**
- Lose: 10% automation (2 manual clicks)
- Gain: $0 costs, unlimited analysis, full Monte Carlo capability

**Decision: PROCEED with Hybrid Approach** ✅
