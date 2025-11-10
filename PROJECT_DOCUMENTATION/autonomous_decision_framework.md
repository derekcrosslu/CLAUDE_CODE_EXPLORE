# Autonomous Decision-Making Framework for QuantConnect Strategy Development

## Overview
This document defines explicit decision rules for autonomous operation. Each decision point includes conditions, options, and deterministic selection criteria.

---

## GLOBAL CONFIGURATION

### Autonomy Levels
```json
{
  "autonomy_mode": "minimal" | "medium" | "full",
  "modes": {
    "minimal": {
      "description": "Human approval at every phase transition",
      "auto_decisions": ["technical_error_fixes", "parameter_generation"],
      "human_gates": ["hypothesis_selection", "implementation_start", "optimization_start", "validation", "deployment"]
    },
    "medium": {
      "description": "Human approval at hypothesis selection and final validation",
      "auto_decisions": ["implementation", "backtesting", "optimization", "iteration_routing"],
      "human_gates": ["hypothesis_selection", "final_validation", "deployment"]
    },
    "full": {
      "description": "Fully autonomous with human review only at completion",
      "auto_decisions": ["all_phases", "all_iterations"],
      "human_gates": ["final_deployment_approval"]
    }
  }
}
```

### Performance Thresholds
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
    },
    "exceptional": {
      "sharpe_ratio": 1.5,
      "max_drawdown": 0.15,
      "min_trades": 100,
      "win_rate": 0.45
    }
  },
  "overfitting_signals": {
    "too_perfect_sharpe": 3.0,
    "too_few_trades": 10,
    "win_rate_too_high": 0.80,
    "max_single_trade_impact": 0.30
  }
}
```

### Iteration Limits
```json
{
  "limits": {
    "max_hypotheses_per_session": 5,
    "max_implementations_per_hypothesis": 3,
    "max_optimization_attempts_per_strategy": 3,
    "max_backtests_per_optimization": 30,
    "max_total_iterations": 15,
    "max_cost_usd": 50,
    "max_context_tokens": 150000
  }
}
```

---

## DECISION TREE: PHASE TRANSITIONS

### Decision Point 1: After Research Phase

**Input**: List of 3-5 hypotheses with scores

**Decision Logic**:
```python
def select_hypothesis(hypotheses, config):
    # Filter invalid hypotheses
    valid = [h for h in hypotheses if h.data_available and h.theoretically_sound]

    if len(valid) == 0:
        return ESCALATE_TO_HUMAN("No valid hypotheses generated")

    # Score hypotheses
    for h in valid:
        h.score = (
            h.novelty * 0.3 +
            h.theoretical_strength * 0.3 +
            h.implementation_simplicity * 0.2 +
            h.data_quality * 0.2
        )

    # Sort by score
    ranked = sorted(valid, key=lambda h: h.score, reverse=True)

    # Decision
    if config.autonomy_mode == "minimal" or config.autonomy_mode == "medium":
        return ASK_USER({
            "question": "Which hypothesis should we implement?",
            "options": [
                {"label": f"H{i+1}: {h.name}", "description": h.rationale}
                for i, h in enumerate(ranked[:4])
            ]
        })
    else:  # full autonomy
        selected = ranked[0]
        LOG_DECISION(f"Selected hypothesis: {selected.name} (score: {selected.score})")
        return PROCEED_TO_IMPLEMENTATION(selected)
```

**Actions**:
- `PROCEED_TO_IMPLEMENTATION(hypothesis)` → Phase 2
- `ASK_USER(question)` → Wait for user input
- `ESCALATE_TO_HUMAN(reason)` → Stop and request guidance

---

### Decision Point 2: After Implementation Phase

**Input**: Implemented algorithm code

**Decision Logic**:
```python
def validate_implementation(code, hypothesis, config):
    # Run static checks
    syntax_valid = run_syntax_check(code)
    has_entry_logic = check_for_pattern(code, "SetHoldings|MarketOrder")
    has_exit_logic = check_for_pattern(code, "Liquidate|stop")
    has_risk_mgmt = check_for_pattern(code, "drawdown|position_size|risk")

    issues = []
    if not syntax_valid:
        issues.append("Syntax errors detected")
    if not has_entry_logic:
        issues.append("No entry logic found")
    if not has_exit_logic:
        issues.append("No exit logic found")
    if not has_risk_mgmt:
        issues.append("No risk management found")

    # Decision
    if len(issues) > 0:
        if attempt_count < 3:
            LOG_DECISION(f"Implementation issues: {issues}. Auto-fixing...")
            return FIX_ISSUES(issues)
        else:
            return ESCALATE_TO_HUMAN(f"Cannot fix issues after 3 attempts: {issues}")
    else:
        LOG_DECISION("Implementation validated. Proceeding to backtest.")
        return PROCEED_TO_BACKTEST(code)
```

**Actions**:
- `PROCEED_TO_BACKTEST(code)` → Phase 3
- `FIX_ISSUES(issues)` → Retry implementation (Phase 2)
- `ESCALATE_TO_HUMAN(reason)` → Stop and request guidance

---

### Decision Point 3: After Backtest Phase

**Input**: Backtest results (metrics, logs, trades)

**Decision Logic**:
```python
def evaluate_backtest(results, thresholds, state, config):
    # Check for technical failures
    if results.status == "error":
        error_type = classify_error(results.error_message)

        if error_type == "data_missing":
            return ESCALATE_TO_HUMAN(f"Data not available: {results.error_message}")
        elif error_type == "runtime_error" and state.fix_attempts < 3:
            LOG_DECISION(f"Runtime error detected. Attempting fix #{state.fix_attempts + 1}")
            return FIX_BUG(results.error_message)
        else:
            return ESCALATE_TO_HUMAN(f"Backtest failed: {results.error_message}")

    # Extract metrics
    sharpe = results.metrics.sharpe_ratio
    drawdown = abs(results.metrics.max_drawdown)
    num_trades = results.metrics.total_trades
    win_rate = results.metrics.win_rate

    # Check for overfitting signals
    if sharpe > thresholds.overfitting_signals.too_perfect_sharpe:
        LOG_DECISION(f"OVERFITTING ALERT: Sharpe {sharpe} is suspiciously high")
        return ESCALATE_TO_HUMAN("Possible overfitting - results too good to be true")

    if num_trades < thresholds.overfitting_signals.too_few_trades:
        LOG_DECISION(f"Too few trades ({num_trades}). Strategy may be overfit.")
        return ABANDON_HYPOTHESIS("Insufficient trade sample size")

    # Performance categorization
    meets_minimum = (
        sharpe >= thresholds.performance_criteria.minimum_viable.sharpe_ratio and
        drawdown <= thresholds.performance_criteria.minimum_viable.max_drawdown and
        num_trades >= thresholds.performance_criteria.minimum_viable.min_trades
    )

    meets_optimization = (
        sharpe >= thresholds.performance_criteria.optimization_worthy.sharpe_ratio and
        drawdown <= thresholds.performance_criteria.optimization_worthy.max_drawdown
    )

    meets_production = (
        sharpe >= thresholds.performance_criteria.production_ready.sharpe_ratio and
        drawdown <= thresholds.performance_criteria.production_ready.max_drawdown and
        num_trades >= thresholds.performance_criteria.production_ready.min_trades
    )

    # Decision logic
    if meets_production:
        LOG_DECISION(f"Excellent performance: Sharpe={sharpe}, DD={drawdown}. Proceeding to validation.")
        return PROCEED_TO_VALIDATION(results)

    elif meets_optimization and state.optimization_attempts < config.limits.max_optimization_attempts_per_strategy:
        LOG_DECISION(f"Good performance (Sharpe={sharpe}), but can optimize. Attempting optimization #{state.optimization_attempts + 1}")
        return PROCEED_TO_OPTIMIZATION(results)

    elif meets_minimum:
        LOG_DECISION(f"Marginal performance (Sharpe={sharpe}). Skipping optimization, proceeding to validation.")
        return PROCEED_TO_VALIDATION(results)

    else:
        LOG_DECISION(f"Poor performance: Sharpe={sharpe}, DD={drawdown}. Abandoning hypothesis.")
        return ABANDON_HYPOTHESIS(f"Performance below minimum thresholds")
```

**Actions**:
- `PROCEED_TO_VALIDATION(results)` → Phase 5
- `PROCEED_TO_OPTIMIZATION(results)` → Phase 4
- `FIX_BUG(error)` → Retry implementation (Phase 2)
- `ABANDON_HYPOTHESIS(reason)` → Select next hypothesis or generate new ones (Phase 1)
- `ESCALATE_TO_HUMAN(reason)` → Stop and request guidance

---

### Decision Point 4: After Optimization Phase

**Input**: Optimization results (all parameter combinations tested)

**Decision Logic**:
```python
def evaluate_optimization(optimization_results, baseline_results, thresholds, state):
    # Find best parameter set
    best = max(optimization_results, key=lambda r: r.sharpe_ratio)

    # Calculate improvement
    improvement = (best.sharpe_ratio - baseline_results.sharpe_ratio) / baseline_results.sharpe_ratio

    # Check for overfitting in optimization
    parameter_sensitivity = calculate_sensitivity(optimization_results)

    if parameter_sensitivity > 0.5:  # High sensitivity = fragile parameters
        LOG_DECISION(f"High parameter sensitivity ({parameter_sensitivity}). Optimization may be overfit.")

        # Use more conservative parameters (median of top 25%)
        top_quartile = sorted(optimization_results, key=lambda r: r.sharpe_ratio, reverse=True)[:len(optimization_results)//4]
        robust_params = calculate_median_parameters(top_quartile)

        LOG_DECISION(f"Using robust parameters (median of top 25%) instead of best.")
        return PROCEED_TO_VALIDATION_WITH_PARAMS(robust_params)

    # Decision based on improvement
    if improvement < 0.05:  # Less than 5% improvement
        LOG_DECISION(f"Optimization yielded minimal improvement ({improvement*100:.1f}%). Proceeding with baseline.")
        return PROCEED_TO_VALIDATION(baseline_results)

    elif improvement > 0.30:  # More than 30% improvement - suspicious
        LOG_DECISION(f"Optimization yielded suspiciously large improvement ({improvement*100:.1f}%). Manual review recommended.")
        return ASK_USER({
            "question": "Optimization improved Sharpe by {:.1f}%. Proceed with optimized parameters?".format(improvement*100),
            "options": [
                {"label": "Yes, use optimized params", "description": f"Sharpe: {best.sharpe_ratio:.2f}"},
                {"label": "No, use baseline params", "description": f"Sharpe: {baseline_results.sharpe_ratio:.2f}"},
                {"label": "Re-optimize with tighter constraints", "description": "Run optimization again"}
            ]
        })

    else:  # Reasonable improvement (5-30%)
        LOG_DECISION(f"Optimization improved performance by {improvement*100:.1f}%. Using optimized parameters.")
        return PROCEED_TO_VALIDATION_WITH_PARAMS(best.parameters)
```

**Actions**:
- `PROCEED_TO_VALIDATION(results)` → Phase 5
- `PROCEED_TO_VALIDATION_WITH_PARAMS(params)` → Phase 5 with new parameters
- `ASK_USER(question)` → Wait for user input
- `ABANDON_HYPOTHESIS(reason)` → Phase 1

---

### Decision Point 5: After Validation Phase

**Input**: Out-of-sample backtest results, in-sample results

**Decision Logic**:
```python
def evaluate_validation(in_sample, out_of_sample, thresholds, state, config):
    # Calculate performance degradation
    sharpe_degradation = (in_sample.sharpe_ratio - out_of_sample.sharpe_ratio) / in_sample.sharpe_ratio

    # Check out-of-sample meets minimum criteria
    oos_meets_minimum = (
        out_of_sample.sharpe_ratio >= thresholds.performance_criteria.minimum_viable.sharpe_ratio and
        abs(out_of_sample.max_drawdown) <= thresholds.performance_criteria.minimum_viable.max_drawdown
    )

    # Decision logic
    if sharpe_degradation > 0.50:  # More than 50% degradation
        LOG_DECISION(f"OVERFITTING DETECTED: Out-of-sample Sharpe degraded by {sharpe_degradation*100:.1f}%")

        if state.optimization_attempts < config.limits.max_optimization_attempts_per_strategy:
            LOG_DECISION("Attempting re-optimization with walk-forward analysis")
            return RETRY_OPTIMIZATION_WALKFORWARD()
        else:
            LOG_DECISION("Max optimization attempts reached. Abandoning hypothesis.")
            return ABANDON_HYPOTHESIS("Strategy does not generalize to out-of-sample data")

    elif sharpe_degradation > 0.30:  # 30-50% degradation
        LOG_DECISION(f"Significant performance degradation ({sharpe_degradation*100:.1f}%), but within acceptable range.")

        if oos_meets_minimum:
            LOG_DECISION("Out-of-sample performance meets minimum criteria. Flagging for human review.")
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
        LOG_DECISION(f"Strategy validates well: {sharpe_degradation*100:.1f}% degradation OOS.")

        if out_of_sample.sharpe_ratio >= thresholds.performance_criteria.production_ready.sharpe_ratio:
            LOG_DECISION("Strategy meets production criteria!")
            return STRATEGY_COMPLETE(out_of_sample)
        else:
            LOG_DECISION("Strategy validated but below production criteria. Documenting for reference.")
            return STRATEGY_VALIDATED_SUBOPTIMAL(out_of_sample)
```

**Actions**:
- `STRATEGY_COMPLETE(results)` → Document and present for deployment
- `STRATEGY_VALIDATED_SUBOPTIMAL(results)` → Document but continue research
- `RETRY_OPTIMIZATION_WALKFORWARD()` → Phase 4 with walk-forward
- `ABANDON_HYPOTHESIS(reason)` → Phase 1
- `ASK_USER(question)` → Wait for user input

---

## ITERATION ROUTING LOGIC

### Master Control Loop

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
            elif decision.action == "ESCALATE_TO_HUMAN":
                return decision

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
            elif decision.action == "ESCALATE_TO_HUMAN":
                return decision

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
            elif decision.action == "ESCALATE_TO_HUMAN":
                return decision

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
            elif decision.action == "ASK_USER":
                return decision

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
            elif decision.action == "ASK_USER":
                return decision

        state.total_iterations += 1
        save_state(state)

def abandon_and_next_hypothesis(state):
    """Handle hypothesis abandonment and routing to next hypothesis"""
    log_hypothesis_outcome(state.current_hypothesis, "ABANDONED", state.backtest_results)

    # Check if we have more hypotheses to try
    if len(state.remaining_hypotheses) > 0:
        state.current_hypothesis = state.remaining_hypotheses.pop(0)
        state.current_phase = "implementation"
        state.fix_attempts = 0
        state.optimization_attempts = 0
        LOG_DECISION(f"Trying next hypothesis: {state.current_hypothesis.name}")
        return state

    # Check if we can generate more hypotheses
    elif state.hypothesis_generation_count < config.limits.max_hypotheses_per_session:
        state.current_phase = "research"
        state.hypothesis_generation_count += 1
        LOG_DECISION(f"All hypotheses exhausted. Generating new set (round #{state.hypothesis_generation_count})")
        return state

    # Exhausted all options
    else:
        LOG_DECISION("Exhausted all hypotheses and generation attempts.")
        return ESCALATE_TO_HUMAN("Unable to find profitable strategy within constraints")
```

---

## SPECIAL CASE HANDLING

### Case 1: Exceptional Performance (Too Good to Be True)

```python
def handle_exceptional_performance(results, thresholds):
    """Detect and handle suspiciously good results"""

    flags = []

    if results.sharpe_ratio > thresholds.overfitting_signals.too_perfect_sharpe:
        flags.append(f"Sharpe ratio ({results.sharpe_ratio:.2f}) exceeds realistic threshold")

    if results.total_trades < thresholds.overfitting_signals.too_few_trades:
        flags.append(f"Trade count ({results.total_trades}) too low for statistical significance")

    if results.win_rate > thresholds.overfitting_signals.win_rate_too_high:
        flags.append(f"Win rate ({results.win_rate:.1%}) unrealistically high")

    # Check if a single trade dominates returns
    if max(results.trade_returns) / results.total_return > thresholds.overfitting_signals.max_single_trade_impact:
        flags.append("Single trade accounts for >30% of total returns")

    if len(flags) > 0:
        LOG_DECISION(f"OVERFITTING RED FLAGS: {flags}")
        return ASK_USER({
            "question": "Strategy shows exceptional performance but with overfitting warning signs. How to proceed?",
            "options": [
                {"label": "Proceed with caution", "description": "Continue to validation with scrutiny"},
                {"label": "Increase sample size", "description": "Extend backtest period"},
                {"label": "Abandon", "description": "Results not trustworthy"}
            ],
            "flags": flags
        })

    return None  # No issues
```

### Case 2: Consistent Failures Across Hypotheses

```python
def detect_systematic_failure(state):
    """Detect if all hypotheses are failing for same reason"""

    if len(state.hypothesis_log) < 3:
        return None  # Not enough data

    recent_failures = [h for h in state.hypothesis_log[-5:] if h.outcome == "ABANDONED"]

    if len(recent_failures) >= 3:
        # Analyze failure reasons
        failure_reasons = [h.failure_reason for h in recent_failures]

        # Group by failure type
        if all("data" in reason.lower() for reason in failure_reasons):
            return ESCALATE_TO_HUMAN("Systematic data availability issues detected across multiple hypotheses")

        elif all("trades" in reason.lower() or "insufficient" in reason.lower() for reason in failure_reasons):
            return ESCALATE_TO_HUMAN("Strategies consistently generating insufficient trades - consider relaxing entry criteria")

        elif all("drawdown" in reason.lower() for reason in failure_reasons):
            return ESCALATE_TO_HUMAN("Risk management issues across strategies - consider different approach or asset class")

    return None  # No systematic issue
```

### Case 3: Context Overflow Imminent

```python
def handle_context_overflow(state, config):
    """Proactive context management before overflow"""

    current_usage = get_context_usage()

    if current_usage > config.limits.max_context_tokens * 0.9:
        LOG_DECISION(f"Context at {current_usage} tokens (90% of limit). Emergency compact.")

        # Archive current state to files
        write_file("iteration_state.json", json.dumps(state))
        write_file("hypotheses_log.md", format_hypothesis_log(state.hypothesis_log))
        write_file("backtest_results.json", json.dumps(state.backtest_results))

        # Execute aggressive compact
        execute_compact()

        # Reload essential state
        LOG_DECISION("State archived to files. Context compacted. Continuing with essential state only.")

    elif current_usage > config.limits.max_context_tokens * 0.7:
        LOG_DECISION(f"Context at {current_usage} tokens (70% of limit). Micro-compact.")
        # Let micro-compact handle automatically
```

---

## LOGGING & AUDITABILITY

### Decision Log Format

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "iteration": 7,
  "phase": "backtest",
  "decision_point": "evaluate_backtest",
  "inputs": {
    "sharpe_ratio": 0.85,
    "max_drawdown": 0.22,
    "total_trades": 67,
    "win_rate": 0.42
  },
  "options_considered": [
    "PROCEED_TO_VALIDATION",
    "PROCEED_TO_OPTIMIZATION",
    "ABANDON_HYPOTHESIS"
  ],
  "decision": "PROCEED_TO_OPTIMIZATION",
  "rationale": "Performance meets optimization threshold (Sharpe 0.85 >= 0.7) and under max optimization attempts (1 < 3)",
  "confidence": 0.8,
  "outcome": "pending"
}
```

### Hypothesis Log Format

```json
{
  "hypothesis_id": "h1_momentum_crypto",
  "name": "Multi-timeframe momentum in BTC/ETH",
  "generated_at": "2025-01-15T09:00:00Z",
  "selected_at": "2025-01-15T09:15:00Z",
  "implementation_attempts": 1,
  "backtest_results": {
    "sharpe": 0.85,
    "drawdown": 0.22,
    "trades": 67
  },
  "optimization_attempts": 1,
  "validation_results": {
    "in_sample_sharpe": 0.92,
    "out_of_sample_sharpe": 0.71,
    "degradation": 0.23
  },
  "outcome": "VALIDATED_SUBOPTIMAL",
  "outcome_timestamp": "2025-01-15T11:30:00Z",
  "total_time_minutes": 150,
  "total_cost_usd": 8.50
}
```

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Build Decision Engine
- [ ] Implement decision functions for each phase
- [ ] Create configuration schema (JSON)
- [ ] Build decision logging system
- [ ] Test decision logic with mock data

### Phase 2: Integrate with Claude Code
- [ ] Create wrapper functions for Bash/Read/Write tools
- [ ] Implement state persistence (JSON files)
- [ ] Build checkpoint automation
- [ ] Test iteration loop with manual steps

### Phase 3: Add Monitoring
- [ ] Create decision log viewer
- [ ] Build cost tracking dashboard
- [ ] Implement context usage monitoring
- [ ] Add systematic failure detection

### Phase 4: Production Hardening
- [ ] Add error recovery for API failures
- [ ] Implement retry logic with exponential backoff
- [ ] Create human escalation notifications
- [ ] Add performance benchmarking

---

## NEXT STEPS

1. **Validate Decision Logic**: Test each decision function with real backtest data
2. **Build State Machine**: Implement master control loop in Python
3. **Create Plugin Commands**: Wrap decision logic in `/qc-auto-iterate` command
4. **Test with Simple Hypothesis**: Run one full cycle manually, observe decision quality
5. **Iterate on Thresholds**: Adjust performance thresholds based on real results
