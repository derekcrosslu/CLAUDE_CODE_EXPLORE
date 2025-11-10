# iteration_state.json Authoritative Schema

**Date**: November 10, 2025
**Status**: Definitive schema for autonomous workflow
**Purpose**: Single source of truth for autonomous decision-making

---

## Schema Philosophy

**iteration_state.json is NOT a documentation file**

It is the **central state machine** that enables autonomous operation:

- ✅ Runtime state (phase, iteration, results)
- ✅ Decision inputs (metrics, thresholds, history)
- ✅ Command coordination (what to run next)
- ❌ Documentation (explanations, guides, lessons)
- ❌ Code (wrappers, scripts)

**Principle**: Keep it minimal, machine-readable, and authoritative.

---

## Schema Versioning

```json
{
  "schema_version": "1.0.0",
  "schema_updated": "2025-11-10T14:00:00Z"
}
```

All iteration_state.json files MUST include schema_version.

**Version History**:
- `1.0.0`: Initial authoritative schema (this document)

---

## Complete Schema Definition

### Top-Level Structure

```json
{
  "schema_version": "1.0.0",
  "workflow": {
    "autonomy_mode": "minimal" | "medium" | "full",
    "current_phase": "research" | "implementation" | "backtest" | "optimization" | "validation" | "complete" | "abandoned",
    "iteration": 1,
    "session_id": "hypothesis_{id}_{name_slug}",
    "created_at": "2025-11-10T14:00:00Z",
    "updated_at": "2025-11-10T14:05:00Z"
  },
  "hypothesis": {
    "id": 1,
    "name": "RSI Mean Reversion",
    "description": "Buy when RSI < 30, sell when RSI > 70",
    "rationale": "Mean reversion in oversold/overbought conditions",
    "status": "active" | "abandoned" | "validated" | "deployed",
    "created": "2025-11-10T14:00:00Z"
  },
  "project": {
    "project_id": 12345678,
    "project_name": "RSIMeanReversion_2023_2024",
    "strategy_file": "rsi_mean_reversion.py",
    "language": "Python",
    "qc_url": "https://www.quantconnect.com/project/12345678"
  },
  "thresholds": {
    "minimum_viable": {
      "sharpe_ratio": 0.5,
      "max_drawdown": 0.40,
      "min_trades": 30
    },
    "optimization_worthy": {
      "sharpe_ratio": 0.7,
      "max_drawdown": 0.35,
      "min_trades": 50
    },
    "production_ready": {
      "sharpe_ratio": 1.0,
      "max_drawdown": 0.30,
      "min_trades": 100,
      "win_rate": 0.40
    },
    "exceptional": {
      "sharpe_ratio": 1.5,
      "max_drawdown": 0.15,
      "min_trades": 100,
      "win_rate": 0.45
    },
    "overfitting_signals": {
      "too_perfect_sharpe": 3.0,
      "too_few_trades": 20,
      "win_rate_too_high": 0.75,
      "max_single_trade_impact": 0.30
    }
  },
  "limits": {
    "max_iterations_per_hypothesis": 3,
    "max_optimization_attempts": 3,
    "max_backtests_per_optimization": 30,
    "max_context_tokens": 150000
  },
  "phase_results": {
    "research": {
      "completed": true,
      "timestamp": "2025-11-10T14:00:00Z"
    },
    "implementation": {
      "completed": true,
      "timestamp": "2025-11-10T14:02:00Z",
      "validation_issues": [],
      "attempt": 1
    },
    "backtest": {
      "completed": true,
      "timestamp": "2025-11-10T14:05:00Z",
      "backtest_id": "abc123def456",
      "performance": {
        "sharpe_ratio": 0.85,
        "max_drawdown": 0.22,
        "total_return": 0.156,
        "total_trades": 67,
        "win_rate": 0.42,
        "loss_rate": 0.58,
        "net_profit": 0.156
      },
      "decision": "proceed_to_optimization",
      "decision_reason": "Performance meets optimization threshold (Sharpe 0.85 >= 0.7)"
    },
    "optimization": {
      "completed": false,
      "attempt": 0,
      "optimization_id": null,
      "baseline_sharpe": 0.85,
      "optimized_sharpe": null,
      "improvement_pct": null,
      "best_parameters": null,
      "overfitting_detected": false
    },
    "validation": {
      "completed": false,
      "oos_backtest_id": null,
      "oos_performance": null,
      "degradation_pct": null,
      "robustness_score": null,
      "decision": null
    }
  },
  "decisions_log": [
    {
      "timestamp": "2025-11-10T14:05:00Z",
      "iteration": 1,
      "phase": "backtest",
      "decision_point": "evaluate_backtest",
      "inputs": {
        "sharpe_ratio": 0.85,
        "max_drawdown": 0.22,
        "total_trades": 67
      },
      "options_considered": [
        "PROCEED_TO_VALIDATION",
        "PROCEED_TO_OPTIMIZATION",
        "ABANDON_HYPOTHESIS"
      ],
      "decision": "PROCEED_TO_OPTIMIZATION",
      "rationale": "Performance meets optimization threshold (Sharpe 0.85 >= 0.7) and under max optimization attempts (0 < 3)",
      "confidence": 0.8,
      "outcome": "pending"
    }
  ],
  "hypothesis_history": [
    {
      "id": 0,
      "name": "Previous Hypothesis",
      "status": "abandoned",
      "abandon_reason": "Sharpe ratio -9.462, poor risk-adjusted returns",
      "final_phase": "backtest",
      "timestamp": "2025-11-10T12:00:00Z"
    }
  ],
  "cost_tracking": {
    "api_calls": 12,
    "backtests_run": 3,
    "optimizations_run": 0,
    "validations_run": 0,
    "estimated_cost_usd": 0.0
  },
  "git": {
    "branch": "hypotheses/hypothesis-1-rsi-mean-reversion",
    "commits": [
      {
        "hash": "abc123",
        "phase": "backtest",
        "message": "backtest: Complete iteration 1 - PROCEED_TO_OPTIMIZATION"
      }
    ],
    "tags": []
  },
  "next_action": {
    "command": "/qc-optimize",
    "reason": "Backtest performance warrants optimization (Sharpe 0.85 >= 0.7)",
    "wait_for_user": false
  }
}
```

---

## Minimal Schema (Phase 1-3 Only)

For initial MVP, only these sections are REQUIRED:

```json
{
  "schema_version": "1.0.0",
  "workflow": {
    "autonomy_mode": "minimal",
    "current_phase": "research",
    "iteration": 1,
    "session_id": "hypothesis_1_test",
    "created_at": "2025-11-10T14:00:00Z",
    "updated_at": "2025-11-10T14:00:00Z"
  },
  "hypothesis": {
    "id": 1,
    "name": "Test Hypothesis",
    "description": "Test strategy",
    "status": "active"
  },
  "project": {
    "project_id": null,
    "strategy_file": null
  },
  "thresholds": {
    "minimum_viable": {
      "sharpe_ratio": 0.5,
      "max_drawdown": 0.40,
      "min_trades": 30
    }
  },
  "limits": {
    "max_iterations_per_hypothesis": 3
  },
  "phase_results": {},
  "decisions_log": [],
  "cost_tracking": {
    "api_calls": 0,
    "backtests_run": 0
  }
}
```

**Size**: ~30 lines (vs 264 lines in previous version)

---

## Command Ownership Map

### /qc-init (Phase 1: Research)

**CREATES**:
```json
{
  "schema_version": "1.0.0",
  "workflow": {...},
  "hypothesis": {...},
  "project": {
    "project_id": null,  // Will be filled by /qc-backtest
    "strategy_file": "hypothesis_name.py"
  },
  "thresholds": {...},  // Load from config
  "limits": {...},       // Load from config
  "phase_results": {},
  "decisions_log": [],
  "hypothesis_history": [],
  "cost_tracking": {
    "api_calls": 0,
    "backtests_run": 0
  },
  "git": {
    "branch": "hypotheses/hypothesis-{id}-{name}",
    "commits": [],
    "tags": []
  },
  "next_action": {
    "command": "/qc-backtest",
    "reason": "Hypothesis initialized, ready for implementation and backtest"
  }
}
```

**UPDATES**:
- `workflow.updated_at`
- `decisions_log` (append initialization decision)

**GIT**:
- Create branch `hypotheses/hypothesis-{id}-{name}`
- Commit: `research: Initialize hypothesis - {name}`

---

### /qc-backtest (Phase 2 & 3: Implementation + Backtest)

**UPDATES**:
```json
{
  "workflow": {
    "current_phase": "backtest" | "abandoned",
    "updated_at": "..."
  },
  "project": {
    "project_id": 12345678,      // NEW
    "project_name": "...",       // NEW
    "qc_url": "..."              // NEW
  },
  "phase_results": {
    "implementation": {          // NEW
      "completed": true,
      "timestamp": "...",
      "validation_issues": [],
      "attempt": 1
    },
    "backtest": {                // NEW
      "completed": true,
      "timestamp": "...",
      "backtest_id": "...",
      "performance": {...},
      "decision": "proceed_to_optimization" | "abandon_hypothesis" | "proceed_to_validation",
      "decision_reason": "..."
    }
  },
  "decisions_log": [...],       // APPEND decision
  "cost_tracking": {
    "api_calls": +3,              // INCREMENT
    "backtests_run": +1           // INCREMENT
  },
  "git": {
    "commits": [...]              // APPEND commit hash
  },
  "next_action": {
    "command": "/qc-optimize" | "/qc-validate" | null,
    "reason": "...",
    "wait_for_user": false | true
  }
}
```

**GIT**:
- Commit: `backtest: Complete iteration {N} - {DECISION}`
- Message includes metrics (Sharpe, drawdown, trades)

---

### /qc-optimize (Phase 4: Optimization)

**UPDATES**:
```json
{
  "workflow": {
    "current_phase": "optimization",
    "iteration": +1,              // INCREMENT if retrying
    "updated_at": "..."
  },
  "phase_results": {
    "optimization": {             // NEW/UPDATE
      "completed": true,
      "attempt": +1,              // INCREMENT
      "optimization_id": "...",
      "baseline_sharpe": 0.85,
      "optimized_sharpe": 1.12,
      "improvement_pct": 31.8,
      "best_parameters": {...},
      "overfitting_detected": true | false
    }
  },
  "decisions_log": [...],        // APPEND decision
  "cost_tracking": {
    "api_calls": +N,              // INCREMENT
    "optimizations_run": +1,      // INCREMENT
    "backtests_run": +M,          // INCREMENT (optimization runs many backtests)
    "estimated_cost_usd": +X      // INCREMENT
  },
  "git": {
    "commits": [...]              // APPEND commit
  },
  "next_action": {
    "command": "/qc-validate" | "/qc-backtest" | "escalate_to_human",
    "reason": "...",
    "wait_for_user": false | true
  }
}
```

**GIT**:
- Commit: `optimize: Iteration {N} - {DECISION}`
- If overfitting detected: Commit includes escalation message

---

### /qc-validate (Phase 5: Validation)

**UPDATES**:
```json
{
  "workflow": {
    "current_phase": "validation" | "complete",
    "updated_at": "..."
  },
  "phase_results": {
    "validation": {               // NEW
      "completed": true,
      "timestamp": "...",
      "oos_backtest_id": "...",
      "oos_performance": {...},
      "degradation_pct": 12.5,
      "robustness_score": 0.87,
      "decision": "deploy_strategy" | "abandon_hypothesis" | "return_to_optimization"
    }
  },
  "hypothesis": {
    "status": "validated" | "abandoned"  // UPDATE
  },
  "decisions_log": [...],        // APPEND decision
  "cost_tracking": {
    "api_calls": +N,              // INCREMENT
    "validations_run": +1,        // INCREMENT
    "backtests_run": +M           // INCREMENT
  },
  "git": {
    "commits": [...],             // APPEND commit
    "tags": ["validated-v1.0"]   // ADD tag if DEPLOY
  },
  "next_action": {
    "command": null,
    "reason": "Strategy complete - validated for deployment",
    "wait_for_user": true
  }
}
```

**GIT**:
- Commit: `validate: Complete validation - {DECISION}`
- If DEPLOY: Tag commit with `validated-{hypothesis_id}`

---

## Decision Log Schema

Every decision must be logged in this exact format:

```json
{
  "timestamp": "2025-11-10T14:05:00Z",
  "iteration": 1,
  "phase": "backtest" | "optimization" | "validation",
  "decision_point": "evaluate_backtest" | "evaluate_optimization" | "evaluate_validation",
  "inputs": {
    // All metrics that influenced the decision
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
  "rationale": "Performance meets optimization threshold (Sharpe 0.85 >= 0.7) and under max optimization attempts (0 < 3)",
  "confidence": 0.8,
  "outcome": "pending" | "success" | "failure",
  "outcome_notes": null  // Filled after next phase completes
}
```

**Purpose**: Provides complete audit trail for autonomous decisions.

---

## Hypothesis History Schema

When abandoning a hypothesis, append to history:

```json
{
  "id": 1,
  "name": "RSI Mean Reversion",
  "status": "abandoned",
  "abandon_reason": "Sharpe ratio -9.462, poor risk-adjusted returns",
  "final_phase": "backtest",
  "metrics": {
    "sharpe_ratio": -9.462,
    "max_drawdown": 0.003,
    "total_trades": 6
  },
  "iterations_completed": 1,
  "timestamp": "2025-11-10T12:00:00Z"
}
```

**Purpose**: Learning from failed hypotheses, avoid repeating mistakes.

---

## State Transitions

### Phase Transitions

```
research → implementation → backtest → optimization → validation → complete
                                    ↓
                               abandoned (can occur at any phase)
```

### Iteration Loop

```
backtest (iteration 1)
    ↓
optimization (iteration 1)
    ↓
backtest (iteration 2) ← if parameters changed
    ↓
optimization (iteration 2)
    ↓
... (max 3 iterations)
    ↓
validation (final)
```

### Decision Points

| Phase | Decision Point | Possible Actions |
|-------|---------------|------------------|
| Research | select_hypothesis | PROCEED_TO_IMPLEMENTATION, ASK_USER |
| Implementation | validate_implementation | PROCEED_TO_BACKTEST, FIX_ISSUES, ESCALATE_TO_HUMAN |
| Backtest | evaluate_backtest | PROCEED_TO_OPTIMIZATION, PROCEED_TO_VALIDATION, ABANDON_HYPOTHESIS |
| Optimization | evaluate_optimization | PROCEED_TO_VALIDATION, USE_BASELINE_PARAMS, ITERATE_AGAIN, ESCALATE_TO_HUMAN |
| Validation | evaluate_validation | DEPLOY_STRATEGY, ABANDON_HYPOTHESIS, RETURN_TO_OPTIMIZATION |

---

## Autonomy Mode Effects

### Minimal Mode

**Human gates**:
- Hypothesis selection
- Implementation start
- Optimization start
- Validation
- Deployment

**Auto decisions**:
- Technical error fixes
- Parameter generation

**iteration_state.json behavior**:
- `next_action.wait_for_user` = `true` at all phase transitions

---

### Medium Mode

**Human gates**:
- Hypothesis selection
- Final validation
- Deployment

**Auto decisions**:
- Implementation
- Backtesting
- Optimization
- Iteration routing

**iteration_state.json behavior**:
- `next_action.wait_for_user` = `true` only at hypothesis selection and validation

---

### Full Mode

**Human gates**:
- Final deployment approval

**Auto decisions**:
- All phases
- All iterations

**iteration_state.json behavior**:
- `next_action.wait_for_user` = `false` always (except final deployment)
- Master control loop runs until strategy complete or abandoned

---

## What Does NOT Belong in iteration_state.json

### Documentation

❌ Explanations of how framework works
❌ Usage guides
❌ Implementation notes
❌ Best practices

**Why**: Use separate .md files (LESSONS_LEARNED.md, MONTECARLO_WALKFORWARD_GUIDE.md)

---

### Code

❌ Python wrapper implementations
❌ Notebook code
❌ Strategy code

**Why**: Use separate .py/.ipynb files (qc_optimize_wrapper.py, monte_carlo_walkforward.ipynb)

---

### Configuration Details

❌ Complete parameter grids
❌ Walkforward configuration
❌ Detailed threshold explanations

**Why**: Use separate config files (optimization_params.json, walkforward_config.json)

---

### Temporary Debug Info

❌ Print statements
❌ Intermediate calculations
❌ Verbose API responses

**Why**: Use logging, decisions_log is for final decisions only

---

## Validation Rules

### Schema Validation

```python
def validate_iteration_state(state):
    required_fields = [
        "schema_version",
        "workflow",
        "hypothesis",
        "project",
        "thresholds",
        "limits",
        "phase_results",
        "decisions_log",
        "cost_tracking"
    ]

    for field in required_fields:
        if field not in state:
            raise ValueError(f"Missing required field: {field}")

    if state["schema_version"] != "1.0.0":
        raise ValueError(f"Unsupported schema version: {state['schema_version']}")

    if state["workflow"]["current_phase"] not in ["research", "implementation", "backtest", "optimization", "validation", "complete", "abandoned"]:
        raise ValueError(f"Invalid phase: {state['workflow']['current_phase']}")

    return True
```

---

## Migration from Previous Schema

### Previous → New Schema Mapping

| Previous Field | New Field | Notes |
|---------------|-----------|-------|
| `current_hypothesis` | `hypothesis` | Renamed for clarity |
| `current_phase` | `workflow.current_phase` | Nested under workflow |
| `phases_completed` | (removed) | Redundant, use phase_results.*.completed |
| `backtest_results` | `phase_results.backtest` | Nested properly |
| `optimization` | `phase_results.optimization` | Nested properly |
| `validation` | `phase_results.validation` | Nested properly |
| `iteration_count` | `workflow.iteration` | Renamed for clarity |
| `max_iterations` | `limits.max_iterations_per_hypothesis` | Moved to limits |
| `metadata` | `workflow` | Integrated into workflow |
| `git_integration` | `git` | Renamed for brevity |
| `walkforward_framework` | (removed) | Use separate documentation file |
| `operational_wrappers` | (removed) | Use separate documentation file |
| `lessons_learned` | (removed) | Use LESSONS_LEARNED.md |

---

## Template Files

### Minimal Template (Phase 1-3 MVP)

**File**: `iteration_state_template_minimal.json`

```json
{
  "schema_version": "1.0.0",
  "workflow": {
    "autonomy_mode": "minimal",
    "current_phase": "research",
    "iteration": 1,
    "session_id": "",
    "created_at": "",
    "updated_at": ""
  },
  "hypothesis": {
    "id": 0,
    "name": "",
    "description": "",
    "rationale": "",
    "status": "active",
    "created": ""
  },
  "project": {
    "project_id": null,
    "project_name": null,
    "strategy_file": null,
    "language": "Python",
    "qc_url": null
  },
  "thresholds": {
    "minimum_viable": {
      "sharpe_ratio": 0.5,
      "max_drawdown": 0.40,
      "min_trades": 30
    }
  },
  "limits": {
    "max_iterations_per_hypothesis": 3
  },
  "phase_results": {},
  "decisions_log": [],
  "hypothesis_history": [],
  "cost_tracking": {
    "api_calls": 0,
    "backtests_run": 0
  },
  "git": {
    "branch": "",
    "commits": [],
    "tags": []
  },
  "next_action": {
    "command": "/qc-backtest",
    "reason": "Hypothesis initialized",
    "wait_for_user": true
  }
}
```

---

### Full Template (All Phases)

**File**: `iteration_state_template_full.json`

Use the complete schema shown at the top of this document.

---

## Summary

### Key Principles

1. **Single source of truth**: iteration_state.json is authoritative for workflow state
2. **Machine-readable**: JSON format, strict schema validation
3. **Minimal**: No documentation, code, or verbose explanations
4. **Versioned**: schema_version tracks changes
5. **Command-driven**: Each slash command knows what to create/update
6. **Audit trail**: decisions_log captures all autonomous decisions
7. **Git-integrated**: Tracks branch, commits, tags

### Schema Sizes

- **Minimal (Phase 1-3)**: ~30 lines
- **Full (All phases)**: ~150 lines (vs 264 in previous version)

### What Changed

- ✅ Added schema versioning
- ✅ Nested workflow metadata
- ✅ Separated phase results clearly
- ✅ Defined command ownership
- ✅ Removed documentation sections
- ✅ Added validation rules
- ✅ Created migration guide

---

**Status**: Authoritative schema defined ✅
**Next**: Implement in /qc-init command
**Validation**: Test with 3 hypotheses (Week 1 goal)

---

**Last Updated**: November 10, 2025
**Author**: Autonomous Framework Development
**Related**: autonomous_framework_architecture.md, gaps_report.md
