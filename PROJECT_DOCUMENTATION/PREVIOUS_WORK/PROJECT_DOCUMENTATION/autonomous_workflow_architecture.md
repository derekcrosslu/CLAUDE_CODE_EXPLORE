# Autonomous QuantConnect Strategy Development Workflow

## Research Objective
Design an autonomous agentic architecture for Claude Code to iteratively develop profitable QuantConnect trading strategies.

---

## Phase 1: RESEARCH & HYPOTHESIS FORMATION

### Inputs
- Market domain (equity, crypto, forex, futures)
- Initial hypothesis or research direction
- Data availability constraints
- Risk parameters (max drawdown, Sharpe target)

### Autonomous Activities
1. **Market Analysis**
   - Analyze historical price patterns
   - Identify regime changes, volatility clusters
   - Research factor performance (momentum, mean-reversion, volatility)

2. **Literature & Strategy Mining**
   - Search QuantConnect forums/documentation for similar strategies
   - Review academic papers on quantitative factors
   - Analyze existing strategy patterns in codebase

3. **Hypothesis Formulation**
   - Generate 3-5 testable hypotheses
   - Define entry/exit logic conceptually
   - Identify required indicators/data sources

### Decision Point
**Autonomous**: Rank hypotheses by novelty, theoretical soundness, data feasibility
**Human Gate**: Optional review before implementation (configurable)

### Outputs
- Ranked hypothesis list with rationale
- Required data sources and indicators
- Preliminary risk constraints

---

## Phase 2: IMPLEMENTATION

### Inputs
- Selected hypothesis from Phase 1
- QuantConnect Algorithm Framework structure
- Risk management requirements

### Autonomous Activities
1. **Algorithm Scaffolding**
   - Create QCAlgorithm class structure
   - Initialize data subscriptions
   - Set up portfolio construction model

2. **Indicator Implementation**
   - Implement or import required technical indicators
   - Create custom indicators if needed
   - Set up indicator warm-up periods

3. **Signal Generation**
   - Code entry logic based on hypothesis
   - Code exit logic (take-profit, stop-loss, time-based)
   - Implement position sizing rules

4. **Risk Management**
   - Max drawdown controls
   - Position limits per security
   - Portfolio heat constraints

5. **Code Quality**
   - Add logging for debugging
   - Include performance tracking
   - Ensure proper order handling

### Decision Point
**Autonomous**: Self-review code against QuantConnect best practices
**Tool Required**: QuantConnect Skill (Lean framework knowledge)

### Outputs
- Complete algorithm code (main.py)
- Configuration parameters
- Expected behavior description

---

## Phase 3: BACKTESTING

### Inputs
- Implemented algorithm from Phase 2
- Backtest date range
- Initial capital
- Benchmark (SPY, BTC, etc.)

### Autonomous Activities
1. **Execute Backtest**
   - Submit via QuantConnect API
   - Monitor execution status
   - Capture results and logs

2. **Results Analysis**
   - Parse backtest statistics (Sharpe, drawdown, win rate, alpha, beta)
   - Analyze equity curve patterns
   - Review trade log for patterns
   - Check for overfitting signals (too few trades, too perfect results)

3. **Diagnostic Checks**
   - Runtime errors or exceptions
   - Data availability issues
   - Unusual behavior (no trades, constant trading, etc.)

### Decision Point
**Autonomous**:
- If technical errors → return to Phase 2 (fix bugs)
- If performance below threshold → proceed to Phase 4 (optimize) OR return to Phase 1 (new hypothesis)
- If performance meets criteria → validate & document

**Thresholds** (configurable):
- Minimum Sharpe Ratio: 1.0+
- Maximum Drawdown: <20%
- Minimum trades: >50
- Win rate: >40%

### Outputs
- Backtest statistics report
- Equity curve visualization
- Trade log analysis
- Go/no-go decision with rationale

---

## Phase 4: OPTIMIZATION

### Inputs
- Working algorithm with suboptimal performance
- Parameter ranges to test
- Optimization constraints (avoid overfitting)

### Autonomous Activities
1. **Parameter Identification**
   - Extract tunable parameters (lookback periods, thresholds, position sizing)
   - Define sensible ranges for each parameter
   - Prioritize parameters by expected impact

2. **Optimization Strategy**
   - Grid search (for 2-3 parameters)
   - Walk-forward analysis (to avoid overfitting)
   - Out-of-sample validation periods

3. **Execute Optimization**
   - Run parameter combinations via QuantConnect Optimization API
   - Track results across all combinations
   - Monitor for overfitting signals

4. **Results Synthesis**
   - Identify robust parameter sets (perform well across variations)
   - Analyze sensitivity to parameter changes
   - Select optimal parameters with margin of safety

### Decision Point
**Autonomous**:
- If optimization improves performance → validate with out-of-sample backtest
- If no improvement → return to Phase 1 (hypothesis may be flawed)
- If overfitting detected → simplify strategy, reduce parameters

### Outputs
- Optimized parameters
- Performance comparison (before/after)
- Sensitivity analysis
- Overfitting risk assessment

---

## Phase 5: VALIDATION & ITERATION

### Inputs
- Optimized strategy
- Out-of-sample date range

### Autonomous Activities
1. **Out-of-Sample Testing**
   - Run backtest on holdout period
   - Compare performance to in-sample results
   - Check for performance degradation

2. **Robustness Checks**
   - Test on different market regimes (bull, bear, sideways)
   - Test on different assets (if applicable)
   - Monte Carlo simulation of trades

3. **Documentation**
   - Strategy description
   - Parameter settings and rationale
   - Performance statistics
   - Known limitations and risks

### Decision Point
**Autonomous**:
- If out-of-sample validates → COMPLETE (ready for paper trading)
- If performance degrades significantly → return to Phase 4 (re-optimize with different approach)
- If fundamentally flawed → return to Phase 1 (try different hypothesis)

**Human Gate**: Final review before deployment (recommended)

### Outputs
- Validated strategy ready for paper trading
- Complete documentation
- Risk assessment report

---

## AUTONOMOUS ITERATION FRAMEWORK

### Loop Structure
```
while not (strategy_validated OR max_iterations_reached OR human_intervention):
    Phase 1: Research (if hypothesis_count == 0 OR all_hypotheses_failed)
    Phase 2: Implementation
    Phase 3: Backtesting

    if backtest_failed_technically:
        continue to Phase 2 (fix bugs)
    elif backtest_poor_performance:
        if optimization_attempted < max_optimization_attempts:
            Phase 4: Optimization
        else:
            Phase 1: New hypothesis
    elif backtest_meets_criteria:
        Phase 5: Validation
        if validated:
            COMPLETE
        else:
            Phase 1 or 4 (based on failure mode)
```

### Success Criteria (Configurable)
- **Technical**: No runtime errors, sufficient trades
- **Performance**: Sharpe > 1.0, Drawdown < 20%, Win rate > 40%
- **Robustness**: Out-of-sample Sharpe within 30% of in-sample
- **Practical**: >50 trades, not overfitted to single event

### Failure Handling
1. **Technical Failures**: Auto-fix common issues (missing data, indicator errors)
2. **Performance Failures**: Try optimization first, then new hypothesis
3. **Iteration Limit**: After N attempts (e.g., 10), request human input
4. **Cost Limit**: Monitor QuantConnect API usage, pause if exceeding budget

### Human Intervention Points (Configurable)
- **Minimal**: Only on final validation
- **Medium**: After each hypothesis selection
- **High**: After each phase completion

---

## CONTEXT MANAGEMENT STRATEGY

### Challenge
Long-running autonomous tasks can fill context window, causing:
- Performance degradation
- Auto-compact losing important information
- Rate limit issues

### Strategy
1. **Phase-Level Checkpoints**
   - Create checkpoint after each phase completion
   - Allows rewind to any phase if iteration fails

2. **Progressive Context Compression**
   - **Keep Hot**: Current phase code, latest backtest results, current hypothesis
   - **Summarize**: Previous backtest attempts, old hypotheses, fixed bugs
   - **Archive External**: Full trade logs, detailed statistics (store in files)

3. **Micro-Compact Triggers**
   - After each backtest (results → summary)
   - After optimization runs (full results → optimal parameters)
   - After failed implementations (error logs → fix summary)

4. **External State Management**
   - Store iteration state in JSON file
   - Track hypothesis history in markdown
   - Save backtest results to CSV
   - Reference files instead of keeping in context

### File Structure for Context Management
```
strategy_research/
├── iteration_state.json          # Current phase, attempt count, hypotheses tested
├── hypotheses_log.md             # All hypotheses with outcomes
├── backtest_results/
│   ├── hypothesis_1_run_1.json
│   ├── hypothesis_1_run_2.json
│   └── ...
├── strategies/
│   ├── momentum_strategy_v1.py
│   ├── momentum_strategy_v2.py
│   └── ...
└── analysis/
    ├── performance_comparison.md
    └── optimization_results.csv
```

---

## REQUIRED CUSTOMIZATIONS

### 1. QuantConnect Skill
**Purpose**: Teach Claude the Lean Algorithm Framework
**Contents**:
- QCAlgorithm class structure
- Common indicators and their usage
- Data subscription patterns
- Order handling best practices
- Portfolio construction models
- Risk management patterns
- Backtesting API usage

### 2. Strategy Development Plugin
**Purpose**: Automated workflow commands
**Contents**:
- `/qc-new-hypothesis` - Start new hypothesis research
- `/qc-implement` - Implement selected hypothesis
- `/qc-backtest` - Run backtest and analyze
- `/qc-optimize` - Parameter optimization loop
- `/qc-validate` - Out-of-sample validation
- `/qc-status` - Show current iteration state

### 3. Custom QuantConnect Agent (SDK)
**Purpose**: Orchestrate autonomous workflow
**Capabilities**:
- Phase state management
- QuantConnect API integration (submit backtests, optimizations)
- Performance evaluation against criteria
- Autonomous decision-making at each phase gate
- Context management (compress old results)
- Cost tracking and budgeting

### 4. Hooks
**Purpose**: Automatic checkpoints and monitoring
**Examples**:
- `post-backtest-hook`: Auto-save results, create checkpoint
- `pre-optimization-hook`: Verify parameter ranges, estimate cost
- `context-warning-hook`: Trigger micro-compact when context >70%

---

## AUTONOMOUS DECISION-MAKING FRAMEWORK

### Decision Categories

#### 1. Deterministic Decisions (Rule-Based)
- Technical errors → return to implementation
- No trades generated → check data/logic bugs
- Runtime timeout → optimize code or reduce universe

#### 2. Heuristic Decisions (Threshold-Based)
- Sharpe < 0.5 → abandon hypothesis
- Sharpe 0.5-1.0 → attempt optimization
- Sharpe > 1.0 → proceed to validation
- Drawdown > 30% → adjust risk management

#### 3. Analytical Decisions (Model-Based)
- Overfitting detection → analyze trade distribution, parameter sensitivity
- Hypothesis ranking → score based on novelty, theoretical basis, Sharpe potential
- Parameter selection → robust optimization (stable across ranges)

#### 4. Escalation to Human
- All hypotheses failed after N attempts
- Unusual patterns detected (strategy too good to be true)
- Cost budget approaching limit
- Ethical/regulatory concerns

### Decision Logging
Every autonomous decision should log:
- Decision point
- Available options
- Chosen option and rationale
- Confidence level
- Outcome (to improve future decisions)

---

## RISK MANAGEMENT FOR AUTONOMOUS OPERATION

### 1. Cost Control
- Max QuantConnect API calls per session
- Max backtest compute time per iteration
- Alert thresholds (50%, 80%, 95% of budget)

### 2. Quality Control
- Code review before each backtest (syntax, logic)
- Overfitting detection (too-perfect results flag human review)
- Diversity requirement (try different hypothesis types)

### 3. Safety Limits
- Max iterations without human input: 10
- Max optimization runs per hypothesis: 3
- Min trades per backtest for validity: 50
- Max leverage allowed: 2x

### 4. Monitoring & Observability
- Real-time dashboard showing:
  - Current phase and iteration count
  - Hypothesis history with outcomes
  - Best Sharpe ratio achieved so far
  - Context usage %
  - Cost spent vs budget

---

## NEXT STEPS FOR VALIDATION

### Proof of Concept Experiments
1. **Manual Workflow Test**: Execute phases manually with Claude Code to identify friction points
2. **Skill Development**: Create minimal QuantConnect skill and test knowledge transfer
3. **Plugin Prototype**: Build one command (e.g., `/qc-backtest`) and test integration
4. **Decision Framework Test**: Present Claude with backtest results and test autonomous decision quality
5. **Context Management Test**: Run multi-iteration loop and monitor context compression effectiveness

### Success Metrics
- Can complete full cycle (Research → Validation) without human intervention
- Produces strategies meeting minimum criteria (Sharpe > 1.0)
- Stays within cost budget
- Context remains manageable (<150K tokens per full cycle)
- Decisions are auditable and sensible
