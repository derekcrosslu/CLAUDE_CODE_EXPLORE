# Autonomous Framework Architecture

**Purpose**: Design an autonomous system for developing, testing, and validating quantitative trading strategies on QuantConnect with minimal human intervention.

---

## Core Problem

Developing profitable trading strategies requires iterating through multiple hypotheses, each requiring:
1. Strategy implementation
2. Backtesting
3. Parameter optimization
4. Out-of-sample validation
5. Decision-making at each phase (proceed, abandon, refine)

**Human bottleneck**: Each phase requires manual analysis, decision-making, and workflow orchestration.

**Goal**: Automate the entire workflow with autonomous decision-making at each phase.

---

## Proposed Solution: 5-Phase Autonomous Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                   AUTONOMOUS LOOP                            │
│                                                              │
│  1. RESEARCH                                                │
│     ├─ Generate hypothesis                                  │
│     ├─ Initialize state (iteration_state.json)              │
│     └─ Decision: Hypothesis viable? → Phase 2 or ABANDON    │
│                                                              │
│  2. IMPLEMENTATION                                          │
│     ├─ Code strategy using QuantConnect Lean Framework      │
│     ├─ Upload to QuantConnect                               │
│     └─ Decision: Code compiles? → Phase 3 or FIX            │
│                                                              │
│  3. BACKTEST                                                │
│     ├─ Run backtest on historical data                      │
│     ├─ Parse results (Sharpe, trades, drawdown, etc.)       │
│     └─ Decision: Performance acceptable? → Phase 4 or ABANDON│
│                                                              │
│  4. OPTIMIZATION                                            │
│     ├─ Parameter sweep on training period                   │
│     ├─ Find optimal parameters                              │
│     └─ Decision: Improved? Overfitting? → Phase 5 or REVIEW │
│                                                              │
│  5. VALIDATION                                              │
│     ├─ Out-of-sample testing (walk-forward)                 │
│     ├─ Monte Carlo robustness testing                       │
│     └─ Decision: Robust? → DEPLOY or ABANDON                │
│                                                              │
│  ↓ LOOP: If ABANDON → Generate new hypothesis (Phase 1)     │
│  ↓ If DEPLOY → Tag, document, move to live trading          │
└─────────────────────────────────────────────────────────────┘
```

---

## Central State Machine: iteration_state.json

**Purpose**: Single source of truth for the entire autonomous workflow.

**Core Concept**: Every command reads current state, performs action, updates state, makes autonomous decision about next step.

### Minimal Schema (Initialization by /qc-init)

```json
{
  "current_hypothesis": {
    "id": 1,
    "name": "Strategy Name",
    "description": "Strategy description",
    "created": "ISO8601 timestamp",
    "status": "research|implementation|backtest|optimization|validation|abandoned|deployed"
  },
  "project": {
    "project_id": null,
    "project_name": null,
    "strategy_file": null
  },
  "current_phase": "research",
  "phases_completed": [],
  "backtest_results": null,
  "optimization": null,
  "validation": null,
  "iteration_count": 0,
  "max_iterations": 3,
  "decisions_log": [],
  "next_steps": []
}
```

### Schema Evolution Through Phases

Each phase **reads** the current state, **performs** its action, **writes** results back, and **decides** next action.

**Phase 3 (Backtest) adds**:
```json
"backtest_results": {
  "backtest_id": "...",
  "completed": true,
  "performance": {
    "sharpe_ratio": 1.2,
    "total_trades": 45,
    "win_rate": 0.58,
    ...
  },
  "decision": "proceed_to_optimization|abandon_hypothesis|escalate",
  "reason": "..."
}
```

**Phase 4 (Optimization) adds**:
```json
"optimization": {
  "status": "completed",
  "best_parameters": {...},
  "improvement_pct": 15.2,
  "decision": "proceed_to_validation|use_baseline|escalate",
  "reason": "..."
}
```

**Phase 5 (Validation) adds**:
```json
"validation": {
  "status": "completed",
  "robustness_score": 0.85,
  "degradation_pct": 12,
  "decision": "deploy_strategy|abandon_strategy|proceed_with_caution",
  "reason": "..."
}
```

---

## Autonomous Decision Framework

**Source**: PREVIOUS_WORK/PROJECT_DOCUMENTATION/autonomous_decision_framework.md

This is the CORE of autonomous operation - explicit routing logic at each phase.

### Global Configuration

#### Performance Thresholds
```json
{
  "performance_criteria": {
    "minimum_viable": {
      "sharpe_ratio": 0.5,
      "max_drawdown": 0.35,
      "min_trades": 20,
      "win_rate": 0.35
    },
    "optimization_worthy": {
      "sharpe_ratio": 0.7,
      "max_drawdown": 0.30,
      "min_trades": 30,
      "win_rate": 0.38
    },
    "production_ready": {
      "sharpe_ratio": 1.0,
      "max_drawdown": 0.20,
      "min_trades": 50,
      "win_rate": 0.40
    }
  },
  "overfitting_signals": {
    "too_perfect_sharpe": 3.0,
    "too_few_trades": 10,
    "win_rate_too_high": 0.80
  }
}
```

#### Iteration Limits
```json
{
  "limits": {
    "max_hypotheses_per_session": 5,
    "max_implementations_per_hypothesis": 3,
    "max_optimization_attempts_per_strategy": 3,
    "max_total_iterations": 15,
    "max_cost_usd": 50,
    "max_context_tokens": 150000
  }
}
```

### Phase 3: Backtest Decision Logic

```python
def evaluate_backtest(results, thresholds, state, config):
    # Check for technical failures
    if results.status == "error":
        error_type = classify_error(results.error_message)

        if error_type == "runtime_error" and state.fix_attempts < 3:
            return FIX_BUG(results.error_message)
        else:
            return ESCALATE_TO_HUMAN(f"Backtest failed: {results.error_message}")

    # Extract metrics
    sharpe = results.metrics.sharpe_ratio
    drawdown = abs(results.metrics.max_drawdown)
    num_trades = results.metrics.total_trades

    # Overfitting detection
    if sharpe > thresholds.overfitting_signals.too_perfect_sharpe:
        return ESCALATE_TO_HUMAN("Possible overfitting - results too good to be true")

    if num_trades < thresholds.overfitting_signals.too_few_trades:
        return ABANDON_HYPOTHESIS("Insufficient trade sample size")

    # Performance categorization
    meets_production = (
        sharpe >= thresholds.performance_criteria.production_ready.sharpe_ratio and
        drawdown <= thresholds.performance_criteria.production_ready.max_drawdown and
        num_trades >= thresholds.performance_criteria.production_ready.min_trades
    )

    meets_optimization = (
        sharpe >= thresholds.performance_criteria.optimization_worthy.sharpe_ratio and
        drawdown <= thresholds.performance_criteria.optimization_worthy.max_drawdown
    )

    meets_minimum = (
        sharpe >= thresholds.performance_criteria.minimum_viable.sharpe_ratio and
        drawdown <= thresholds.performance_criteria.minimum_viable.max_drawdown and
        num_trades >= thresholds.performance_criteria.minimum_viable.min_trades
    )

    # Decision routing
    if meets_production:
        return PROCEED_TO_VALIDATION(results)  # Skip optimization, already excellent

    elif meets_optimization and state.optimization_attempts < config.limits.max_optimization_attempts_per_strategy:
        return PROCEED_TO_OPTIMIZATION(results)  # Can improve further

    elif meets_minimum:
        return PROCEED_TO_VALIDATION(results)  # Marginal but acceptable

    else:
        return ABANDON_HYPOTHESIS(f"Performance below minimum thresholds")
```

**Actions**:
- `PROCEED_TO_VALIDATION(results)` → Phase 5
- `PROCEED_TO_OPTIMIZATION(results)` → Phase 4
- `FIX_BUG(error)` → Retry implementation (Phase 2)
- `ABANDON_HYPOTHESIS(reason)` → Next hypothesis or generate new (Phase 1)
- `ESCALATE_TO_HUMAN(reason)` → Stop and request guidance

### Phase 4: Optimization Decision Logic

```python
def evaluate_optimization(optimization_results, baseline_results, thresholds, state):
    # Find best parameter set
    best = max(optimization_results, key=lambda r: r.sharpe_ratio)

    # Calculate improvement
    improvement = (best.sharpe_ratio - baseline_results.sharpe_ratio) / baseline_results.sharpe_ratio

    # Check parameter sensitivity (fragility)
    parameter_sensitivity = calculate_sensitivity(optimization_results)

    if parameter_sensitivity > 0.5:  # High sensitivity = overfitting risk
        # Use robust parameters (median of top 25%)
        top_quartile = sorted(optimization_results, key=lambda r: r.sharpe_ratio, reverse=True)[:len(optimization_results)//4]
        robust_params = calculate_median_parameters(top_quartile)
        return PROCEED_TO_VALIDATION_WITH_PARAMS(robust_params)

    # Decision based on improvement magnitude
    if improvement < 0.05:  # Less than 5% improvement
        return PROCEED_TO_VALIDATION(baseline_results)  # Use baseline

    elif improvement > 0.30:  # More than 30% improvement - suspicious
        return ASK_USER({
            "question": f"Optimization improved Sharpe by {improvement*100:.1f}%. Proceed?",
            "options": [
                {"label": "Yes, use optimized params", "description": f"Sharpe: {best.sharpe_ratio:.2f}"},
                {"label": "No, use baseline params", "description": f"Sharpe: {baseline_results.sharpe_ratio:.2f}"},
                {"label": "Re-optimize with tighter constraints", "description": "Try again"}
            ]
        })

    else:  # Reasonable improvement (5-30%)
        return PROCEED_TO_VALIDATION_WITH_PARAMS(best.parameters)
```

**Actions**:
- `PROCEED_TO_VALIDATION(results)` → Phase 5 with baseline params
- `PROCEED_TO_VALIDATION_WITH_PARAMS(params)` → Phase 5 with optimized params
- `ASK_USER(question)` → Wait for user input
- `ABANDON_HYPOTHESIS(reason)` → Phase 1

### Phase 5: Validation Decision Logic

```python
def evaluate_validation(in_sample, out_of_sample, thresholds, state, config):
    # Calculate performance degradation
    sharpe_degradation = (in_sample.sharpe_ratio - out_of_sample.sharpe_ratio) / in_sample.sharpe_ratio

    # Check out-of-sample meets minimum criteria
    oos_meets_minimum = (
        out_of_sample.sharpe_ratio >= thresholds.performance_criteria.minimum_viable.sharpe_ratio and
        abs(out_of_sample.max_drawdown) <= thresholds.performance_criteria.minimum_viable.max_drawdown
    )

    # Decision logic based on degradation
    if sharpe_degradation > 0.50:  # More than 50% degradation - severe overfitting
        if state.optimization_attempts < config.limits.max_optimization_attempts_per_strategy:
            return RETRY_OPTIMIZATION_WALKFORWARD()
        else:
            return ABANDON_HYPOTHESIS("Strategy does not generalize to out-of-sample data")

    elif sharpe_degradation > 0.30:  # 30-50% degradation - concerning
        if oos_meets_minimum:
            return ASK_USER({
                "question": f"Strategy shows {sharpe_degradation*100:.1f}% degradation OOS. Proceed?",
                "options": [
                    {"label": "Accept strategy", "description": f"OOS Sharpe: {out_of_sample.sharpe_ratio:.2f}"},
                    {"label": "Re-optimize", "description": "Try walk-forward optimization"},
                    {"label": "Abandon", "description": "Try different hypothesis"}
                ]
            })
        else:
            return ABANDON_HYPOTHESIS("Out-of-sample performance below minimum criteria")

    else:  # Less than 30% degradation - good generalization
        if out_of_sample.sharpe_ratio >= thresholds.performance_criteria.production_ready.sharpe_ratio:
            return STRATEGY_COMPLETE(out_of_sample)  # Success!
        else:
            return STRATEGY_VALIDATED_SUBOPTIMAL(out_of_sample)  # Document but keep searching
```

**Actions**:
- `STRATEGY_COMPLETE(results)` → Document and present for deployment
- `STRATEGY_VALIDATED_SUBOPTIMAL(results)` → Document but continue research
- `RETRY_OPTIMIZATION_WALKFORWARD()` → Phase 4 with walk-forward
- `ABANDON_HYPOTHESIS(reason)` → Phase 1
- `ASK_USER(question)` → Wait for user input

### Master Routing Loop

This is the autonomous engine that orchestrates the entire workflow:

```python
def autonomous_strategy_development(initial_config):
    state = initialize_state(initial_config)

    while True:
        # Check global limits
        if state.total_iterations >= config.limits.max_total_iterations:
            return ESCALATE_TO_HUMAN("Reached maximum iteration limit")

        if state.total_cost >= config.limits.max_cost_usd:
            return ESCALATE_TO_HUMAN("Reached cost budget limit")

        if state.context_tokens >= config.limits.max_context_tokens:
            execute_compact()

        # Route to current phase
        if state.current_phase == "research":
            hypotheses = execute_research_phase(state)
            decision = select_hypothesis(hypotheses, config)

            if decision.action == "PROCEED_TO_IMPLEMENTATION":
                state.current_hypothesis = decision.hypothesis
                state.current_phase = "implementation"
                checkpoint_create()

        elif state.current_phase == "implementation":
            code = execute_implementation_phase(state.current_hypothesis)
            decision = validate_implementation(code, state.current_hypothesis, config)

            if decision.action == "PROCEED_TO_BACKTEST":
                state.current_code = code
                state.current_phase = "backtest"
                checkpoint_create()
            elif decision.action == "FIX_ISSUES":
                state.fix_attempts += 1
                continue  # Retry implementation

        elif state.current_phase == "backtest":
            results = execute_backtest_phase(state.current_code)
            decision = evaluate_backtest(results, config.thresholds, state, config)

            if decision.action == "PROCEED_TO_VALIDATION":
                state.backtest_results = results
                state.current_phase = "validation"
                checkpoint_create()
            elif decision.action == "PROCEED_TO_OPTIMIZATION":
                state.backtest_results = results
                state.current_phase = "optimization"
                checkpoint_create()
            elif decision.action == "FIX_BUG":
                state.current_phase = "implementation"
                state.fix_attempts += 1
            elif decision.action == "ABANDON_HYPOTHESIS":
                state = abandon_and_next_hypothesis(state)

        elif state.current_phase == "optimization":
            opt_results = execute_optimization_phase(state.current_code, state.backtest_results)
            decision = evaluate_optimization(opt_results, state.backtest_results, config.thresholds, state)

            if decision.action == "PROCEED_TO_VALIDATION" or decision.action == "PROCEED_TO_VALIDATION_WITH_PARAMS":
                if decision.action == "PROCEED_TO_VALIDATION_WITH_PARAMS":
                    state.current_code = update_parameters(state.current_code, decision.parameters)
                state.current_phase = "validation"
                state.optimization_attempts += 1
                checkpoint_create()
            elif decision.action == "ABANDON_HYPOTHESIS":
                state = abandon_and_next_hypothesis(state)

        elif state.current_phase == "validation":
            oos_results = execute_validation_phase(state.current_code)
            decision = evaluate_validation(state.backtest_results, oos_results, config.thresholds, state, config)

            if decision.action == "STRATEGY_COMPLETE":
                document_strategy(state, oos_results)
                return PRESENT_STRATEGY_FOR_DEPLOYMENT(oos_results)
            elif decision.action == "STRATEGY_VALIDATED_SUBOPTIMAL":
                document_strategy(state, oos_results)
                state = abandon_and_next_hypothesis(state)
            elif decision.action == "RETRY_OPTIMIZATION_WALKFORWARD":
                state.current_phase = "optimization"
            elif decision.action == "ABANDON_HYPOTHESIS":
                state = abandon_and_next_hypothesis(state)

        state.total_iterations += 1
        save_state(state)

def abandon_and_next_hypothesis(state):
    """Handle hypothesis abandonment and routing to next hypothesis"""
    log_hypothesis_outcome(state.current_hypothesis, "ABANDONED", state.backtest_results)

    # Check if we have more hypotheses queued
    if len(state.remaining_hypotheses) > 0:
        state.current_hypothesis = state.remaining_hypotheses.pop(0)
        state.current_phase = "implementation"
        state.fix_attempts = 0
        state.optimization_attempts = 0
        return state

    # Generate new hypotheses
    elif state.hypothesis_generation_count < config.limits.max_hypotheses_per_session:
        state.current_phase = "research"
        state.hypothesis_generation_count += 1
        return state

    # Exhausted all options
    else:
        return ESCALATE_TO_HUMAN("Unable to find profitable strategy within constraints")
```

### Special Case Handling

#### Overfitting Detection
```python
def handle_exceptional_performance(results, thresholds):
    """Detect suspiciously good results"""
    flags = []

    if results.sharpe_ratio > thresholds.overfitting_signals.too_perfect_sharpe:
        flags.append(f"Sharpe ratio ({results.sharpe_ratio:.2f}) exceeds realistic threshold")

    if results.total_trades < thresholds.overfitting_signals.too_few_trades:
        flags.append(f"Trade count ({results.total_trades}) too low for statistical significance")

    if results.win_rate > thresholds.overfitting_signals.win_rate_too_high:
        flags.append(f"Win rate ({results.win_rate:.1%}) unrealistically high")

    if len(flags) > 0:
        return ASK_USER({
            "question": "Strategy shows exceptional performance with overfitting warnings. Proceed?",
            "flags": flags
        })
```

#### Systematic Failure Detection
```python
def detect_systematic_failure(state):
    """Detect if all hypotheses fail for same reason"""
    if len(state.hypothesis_log) < 3:
        return None

    recent_failures = [h for h in state.hypothesis_log[-5:] if h.outcome == "ABANDONED"]

    if len(recent_failures) >= 3:
        failure_reasons = [h.failure_reason for h in recent_failures]

        if all("trades" in reason.lower() for reason in failure_reasons):
            return ESCALATE_TO_HUMAN("Strategies consistently generating insufficient trades")
        elif all("drawdown" in reason.lower() for reason in failure_reasons):
            return ESCALATE_TO_HUMAN("Risk management issues across strategies")
```

---

## Integration Components

### 1. Slash Commands (Claude Code)

Commands that orchestrate the workflow:

- **/qc-init**: Initialize hypothesis, create iteration_state.json, git branch
- **/qc-backtest**: Run backtest, update state, make decision
- **/qc-optimize**: Run optimization, update state, make decision
- **/qc-validate**: Run validation, update state, make decision
- **/qc-status**: Show current state
- **/qc-report**: Generate complete report

Each command:
1. Reads iteration_state.json
2. Calls appropriate wrapper (qc_backtest.py, etc.)
3. Writes results to iteration_state.json
4. Applies decision framework
5. Updates next_steps
6. Commits to git with structured message

### 2. Python Wrappers (API Integration)

Scripts that interface with QuantConnect API:

- **qc_backtest.py**: Create project, upload code, run backtest, parse results
- **qc_optimize_wrapper.py**: Run parameter optimization via API
- **qc_validate_wrapper.py**: Run walk-forward validation

Each wrapper:
- Uses QuantConnect REST API with HMAC authentication
- Returns structured JSON results
- No decision-making (that's in slash commands)

### 3. Skills (Knowledge Base)

Claude skills that provide domain knowledge:

- **QuantConnect Skill**: How to code Lean strategies
- **Backtesting Analysis Skill**: How to interpret backtest results
- **Optimization Skill**: Parameter optimization theory
- **Validation Skill**: Walk-forward and Monte Carlo methods

---

## Critical Research Questions (Unresolved)

### 1. Phase 5 Implementation Approach

**Question**: How should walk-forward validation be implemented?

**Option A: External API Calls** (qc_walkforward_wrapper.py)
- Uses api.create_optimization() for each training period
- Uses api.create_backtest() for each test period
- Requires paid QC tier
- Expensive ($3-5 per hypothesis)

**Option B: Research Notebook with QuantBook**
- Upload notebook to QC Research
- Use qb.History() for data
- Pure Python strategy simulation
- Free tier compatible
- Requires manual "Run All" (not 100% autonomous)

**Status**: Unclear which approach is correct. Need to research:
- Does qb.Optimize() and qb.Backtest() exist in QuantBook?
- Can Research notebooks run strategies without full API?
- What's the cost/autonomy trade-off?

### 2. Skills Integration with Autonomous Decisions

**Question**: How should Claude use skills to make autonomous decisions?

**Current Gap**: Skills provide knowledge, but how does Claude apply them in decision framework?

**Example**:
- Backtest shows Sharpe=1.5, Trades=8, Win Rate=45%
- Should Claude autonomously decide this is "acceptable" or "abandon"?
- What if there's a subtle overfitting pattern that requires domain knowledge?

**Research Needed**:
- Can skills contain decision thresholds?
- Should thresholds be in iteration_state.json?
- How to balance rigid rules vs flexible analysis?

### 3. Monte Carlo Validation Methodology

**Question**: What's the correct statistical approach for robustness testing?

**Options**:
1. Random time periods (Monte Carlo temporal)
2. Bootstrapping from actual trades
3. Synthetic data generation (GARCH + Jump-Diffusion)
4. Combination of above

**Status**: Research exists on synthetic data generation, but unclear:
- Should synthetic data match specific backtest or general market properties?
- How to validate synthetic data is realistic?
- What robustness score threshold indicates "deployable"?

---

## Success Criteria

### For the Framework (Not Individual Strategies)

1. **Autonomous Operation**: Can run through all 5 phases with <10% human intervention
2. **Correct Decisions**: Abandons truly bad strategies, advances good ones
3. **Cost Efficiency**: <$20 per hypothesis tested
4. **Speed**: <4 hours per hypothesis (backtest through validation)
5. **Reproducibility**: Same hypothesis → same decision (deterministic)
6. **Audit Trail**: Complete git log + decisions_log.md for every decision

### Key Metrics

- **Hypotheses tested**: Target 10+ to validate framework
- **False positives**: Strategies that passed validation but failed in live (should be <10%)
- **False negatives**: Strategies abandoned that were actually good (acceptable if high threshold)
- **Cost per viable strategy**: Total cost / strategies deployed

---

## Non-Goals

This project is NOT about:
- Finding the "holy grail" strategy
- Live trading execution
- Real-time data streaming
- Order management systems
- Production infrastructure

This project IS about:
- Autonomous hypothesis testing
- Decision-making frameworks
- Research workflow automation
- Validation methodology

---

## Architecture Principles

1. **State-Driven**: iteration_state.json is the single source of truth
2. **Idempotent**: Running same command twice should be safe
3. **Transparent**: Every decision logged with reasoning
4. **Fail-Safe**: Errors should pause, not corrupt state
5. **Reversible**: Git allows rollback to any hypothesis
6. **Modular**: Each phase can be run independently for testing

---

## Open Questions

1. What is the complete schema for iteration_state.json?
2. Which sections are written by /qc-init vs /qc-backtest vs wrappers?
3. How do skills integrate with autonomous decisions?
4. What is the correct Phase 5 validation approach (API vs QuantBook)?
5. What decision thresholds should be configurable vs hard-coded?
6. How to handle rate limits, API failures, data issues?
7. What's the minimum viable framework to test with one hypothesis?

---

**Status**: Architecture defined, implementation approach unclear
**Next**: Write gaps_report.md to identify what research is needed vs what can be implemented directly
