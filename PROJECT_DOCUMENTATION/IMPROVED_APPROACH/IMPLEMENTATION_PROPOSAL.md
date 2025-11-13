# Implementation Proposal: Beyond MCP Refactoring

**Date**: 2025-11-10
**Purpose**: Phased implementation plan for autonomous framework improvements
**Based On**: 3 improvement reports (decision framework, timeline, strategy development)

---

## Executive Summary

**Goal**: Reduce agent context consumption by 85-90% while improving maintainability and enabling human/team/agent workflows (trifecta).

**Current State**:
- 2088 lines of skills loaded for basic operations
- No progressive disclosure (load everything always)
- Skills-only approach (not usable by humans/teams)

**Target State**:
- ~260 lines for same operations (87% reduction)
- CLI-first architecture (progressive disclosure)
- Human + Team + Agent workflows (trifecta)

**Core Principle**: Build CLI first, minimal skills teach CLI usage, can wrap MCP later if needed.

---

## Improvement Summary

| Component | Current Context | Target Context | Savings | Priority |
|-----------|----------------|----------------|---------|----------|
| **Decision Framework** | 800 lines | 100 lines | 87.5% | **HIGH** |
| **Project Timeline** | 631 lines | 60 lines | 90% | **HIGHEST** |
| **Strategy Components** | 657 lines | 100 lines | 85% | **MEDIUM** |
| **TOTAL** | **2088 lines** | **260 lines** | **87%** | - |

---

## Phased Implementation Plan

### Phase 0: Foundation (Week 0 - Preparation)

**Objective**: Set up infrastructure and validate approach

**Tasks**:
1. ✅ **Create improvement reports** (DONE)
2. ✅ **Research Beyond MCP principles** (DONE)
3. **Create implementation proposal** (THIS DOCUMENT)
4. **Get user approval** on phased plan
5. **Set up testing infrastructure**
   - Benchmark current context usage
   - Create test scenarios for CLI validation
   - Set up comparison framework (before/after metrics)

**Deliverables**:
- [ ] Baseline context measurements
- [ ] Testing framework ready
- [ ] Implementation proposal approved

**Duration**: 1-2 days

---

### Phase 1: Timeline CLI (Week 1) ⭐ **HIGHEST PRIORITY**

**Why First?**
- Highest impact (90% context reduction)
- Used most frequently (every task completion)
- Simplest to implement (jq queries → CLI commands)
- Immediate productivity gain

**Objective**: Replace 631-line project-timeline skill with 60-line CLI primer

#### Tasks

**1.1 Create timeline_cli.py** (2 days)

```bash
# Target commands:
timeline next                    # Get next pending task
timeline status                  # Current week progress
timeline complete TASK_ID        # Mark done + git commit
timeline query [options]         # Custom jq queries
timeline find --status pending   # Find tasks by status
timeline push                    # Git push after complete
```

**Implementation**:
```
SCRIPTS/
└── timeline_cli.py (click-based CLI)
    ├── next() - Query next pending
    ├── status() - Current week status
    ├── complete(task_id) - Mark complete + commit
    ├── query() - Custom jq queries
    └── find() - Search tasks
```

**1.2 Create Minimal Skill** (1 day)

Replace `.claude/skills/project-timeline/skill.md` (631 lines) with minimal version (60 lines):

```markdown
---
name: Project Timeline
description: Systematic checklist execution (CLI-based)
---

# Project Timeline CLI

Manage timeline with: `timeline` (alias for `SCRIPTS/timeline_cli.py`)

## Commands
- `timeline next` - What should I work on?
- `timeline complete TASK_ID` - Mark done + commit
- `timeline status` - Current progress

## Workflow
1. Start session: `timeline next`
2. Do work
3. Complete: `timeline complete w1-test-003`
4. Push: `git push`

## Core Principles
**Priority 1**: Complete framework (all components exist)
**Priority 2**: Validate framework (test robustness)

## Authoritative Docs (When Confused)
- Workflow/decisions: `PROJECT_DOCUMENTATION/autonomous_decision_framework.md`
- Architecture: `PREVIOUS_WORK/PROJECT_DOCUMENTATION/autonomous_workflow_architecture.md`

Use `--help` for details. Do not read source code.
```

**1.3 Integration** (1 day)
- Update current workflow to use `timeline next` instead of loading skill
- Test with hypothesis 4 completion
- Verify git commits formatted correctly
- Measure context savings

**1.4 Testing** (1 day)
- Test all CLI commands
- Verify JSON updates work
- Test git commit workflow
- Compare agent context usage (before/after)

#### Success Criteria
- ✅ CLI works for all timeline operations
- ✅ Context reduced from 631 → 60 lines (90%)
- ✅ Humans can use CLI for manual task tracking
- ✅ Git commits formatted correctly
- ✅ No functionality lost from skill version

#### Risk Mitigation
- **Risk**: Agent doesn't understand CLI commands
  - **Mitigation**: Primer skill teaches exact usage with examples
- **Risk**: jq queries break on JSON structure changes
  - **Mitigation**: Use jq safely with error handling, default values
- **Risk**: Git automation fails
  - **Mitigation**: Add `--no-commit` flag for dry runs

**Duration**: 5 days
**Context Savings**: 571 lines (90%)
**Deliverables**:
- [ ] `SCRIPTS/timeline_cli.py` working
- [ ] Minimal skill (60 lines) replaces old skill (631 lines)
- [ ] Shell alias: `timeline`
- [ ] Integration tested with hypothesis workflow
- [ ] Context measurements show 90% reduction

---

### Phase 2: Decision Framework CLI (Week 2) ⭐ **HIGH PRIORITY**

**Why Second?**
- High impact (87.5% context reduction)
- Critical for autonomous workflow
- Depends on Phase 1 (uses timeline for tracking)
- Enables better hypothesis evaluation

**Objective**: Replace 800-line skills with 100-line CLI primer

#### Tasks

**2.1 Create decision_cli.py** (3 days)

```bash
# Target commands:
decision_cli evaluate-backtest --state iteration_state.json --results backtest.json
decision_cli evaluate-optimization --state iteration_state.json --results optimization.json
decision_cli evaluate-validation --state iteration_state.json --results validation.json
decision_cli route --phase backtest --decision PROCEED_TO_OPTIMIZATION --iteration 1
```

**Refactor from existing** `SCRIPTS/decision_logic.py` (752 lines):
```
SCRIPTS/
└── decision_cli.py (click-based CLI)
    ├── evaluate_backtest() - Phase 3 evaluation only
    ├── evaluate_optimization() - Phase 4 evaluation only
    ├── evaluate_validation() - Phase 5 evaluation only
    └── route() - Phase routing logic
```

**Progressive Disclosure**:
- Phase 3: Only load backtest evaluation logic (~150 lines)
- Phase 4: Only load optimization evaluation logic (~150 lines)
- Phase 5: Only load validation evaluation logic (~150 lines)
- Routing: Only load state machine (~100 lines)

**2.2 Create Minimal Skill** (1 day)

Replace `.claude/skills/decision-framework/skill.md` (500+ lines) with minimal version (~50 lines):

```markdown
# Decision Framework CLI

Evaluate results with: `decision_cli` (alias for `SCRIPTS/decision_cli.py`)

## Commands
- `evaluate-backtest` - Phase 3 decisions
- `evaluate-optimization` - Phase 4 decisions
- `evaluate-validation` - Phase 5 decisions
- `route` - Determine next phase

## Workflow
```bash
# After backtest completes:
decision_cli evaluate-backtest \
  --state iteration_state.json \
  --results PROJECT_LOGS/backtest_result.json

# Route to next phase:
decision_cli route \
  --phase backtest \
  --decision PROCEED_TO_OPTIMIZATION \
  --iteration 1
```

## Thresholds
Read from `iteration_state.json` (single source of truth)

Use `--help` for details.
```

**2.3 Integration** (2 days)
- Update `/qc-backtest` command to use CLI
- Update `/qc-optimize` command to use CLI
- Update `/qc-validate` command to use CLI
- Test with hypothesis 4 backtest

**2.4 Testing** (1 day)
- Test all 3 evaluation commands
- Test routing for all decision paths
- Verify same output as original decision_logic.py
- Measure context savings

#### Success Criteria
- ✅ CLI produces identical decisions to original
- ✅ Context reduced from 800 → 100 lines (87.5%)
- ✅ Humans can run CLI for manual hypothesis evaluation
- ✅ All 8 routing test cases pass
- ✅ Commands integrated into /qc-* commands

#### Risk Mitigation
- **Risk**: CLI output differs from original decision_logic.py
  - **Mitigation**: Comprehensive test suite comparing outputs
- **Risk**: Thresholds not accessible from CLI
  - **Mitigation**: Read from iteration_state.json (single source of truth)
- **Risk**: Complex routing logic hard to debug
  - **Mitigation**: Add `--debug` flag with verbose output

**Duration**: 7 days
**Context Savings**: 700 lines (87.5%)
**Deliverables**:
- [ ] `SCRIPTS/decision_cli.py` working
- [ ] Minimal skill (50 lines) replaces old skills (800 lines)
- [ ] Shell alias: `decision_cli`
- [ ] Integration with /qc-backtest, /qc-optimize, /qc-validate
- [ ] All routing test cases pass

---

### Phase 2.5: Optimization & Validation Wrappers (Week 2.5) ⭐ **HIGH PRIORITY**

**Why Now?**
- Required to complete autonomous workflow (Phases 4-5)
- Decision CLI (Phase 2) evaluates results, but we need wrappers to GENERATE results
- Existing code in PREVIOUS_WORK just needs CLI conversion
- Blocks full autonomous hypothesis testing

**Objective**: Create execution wrappers for optimization and validation operations

**Current Gap**:
```
✅ Phase 1 (research):    /qc-init working
✅ Phase 3 (backtest):    /qc-backtest + qc_backtest.py working
❌ Phase 4 (optimization): /qc-optimize exists but NO qc_optimize.py wrapper!
❌ Phase 5 (validation):   /qc-validate exists but NO qc_validate.py wrapper!
```

**Existing Assets in PREVIOUS_WORK**:
- `qc_optimize_wrapper.py` (12KB, production-ready)
- `qc_walkforward_wrapper.py` (22KB, Monte Carlo validation)

#### Tasks

**2.5.1 Copy & Refactor Optimization Wrapper** (2 days)

**From**: `PREVIOUS_WORK/SCRIPTS/qc_optimize_wrapper.py`
**To**: `SCRIPTS/qc_optimize.py` (CLI-based)

**Current features** (from PREVIOUS_WORK):
- Full QC native optimization API integration
- Prerequisite validation (baseline backtest required)
- Parameter configuration loading
- Cost estimation before execution
- Real-time progress monitoring
- Overfitting detection (>30% improvement = escalate)
- State file management

**Refactor to CLI**:
```bash
# Target commands:
qc_optimize run --config optimization_params.json --state iteration_state.json
qc_optimize status --optimization-id abc123
qc_optimize results --optimization-id abc123 --output results.json
```

**Implementation**:
```python
#!/usr/bin/env python3
"""
QuantConnect Optimization CLI

Usage:
    qc_optimize run --config params.json --state iteration_state.json
    qc_optimize status --optimization-id abc123
    qc_optimize results --optimization-id abc123
"""

import click
from pathlib import Path
from qc_backtest import QuantConnectAPI

@click.group()
def cli():
    """QuantConnect optimization CLI."""
    pass

@cli.command()
@click.option('--config', required=True, help='Optimization config JSON')
@click.option('--state', default='iteration_state.json', help='Iteration state file')
@click.option('--output', default='PROJECT_LOGS/optimization_result.json')
def run(config, state, output):
    """Run parameter optimization."""
    # Load config and state
    # Validate baseline backtest exists
    # Run optimization
    # Save results
    # Update iteration_state.json
    pass

@cli.command()
@click.option('--optimization-id', required=True)
def status(optimization_id):
    """Check optimization status."""
    # Query QC API for status
    # Display progress
    pass

@cli.command()
@click.option('--optimization-id', required=True)
@click.option('--output', default='PROJECT_LOGS/optimization_result.json')
def results(optimization_id, output):
    """Download optimization results."""
    # Fetch results from QC
    # Save to JSON
    # Display summary
    pass
```

**2.5.2 Copy & Refactor Validation Wrapper** (2 days)

**From**: `PREVIOUS_WORK/SCRIPTS/qc_walkforward_wrapper.py`
**To**: `SCRIPTS/qc_validate.py` (CLI-based)

**Current features** (from PREVIOUS_WORK):
- Monte Carlo walk-forward validation
- Random train/test period sampling
- Automated strategy date modification
- Multi-run optimization orchestration
- Out-of-sample backtest validation
- Statistical analysis (mean, std, distribution)
- Parameter stability assessment
- Robustness decision framework

**Refactor to CLI**:
```bash
# Target commands:
qc_validate run --config walkforward_config.json --state iteration_state.json
qc_validate status --validation-id abc123
qc_validate results --validation-id abc123 --output results.json
qc_validate analyze --results results.json  # Statistical analysis
```

**Implementation**:
```python
#!/usr/bin/env python3
"""
QuantConnect Walk-Forward Validation CLI

Usage:
    qc_validate run --config walkforward.json --state iteration_state.json
    qc_validate analyze --results results.json
"""

import click
from pathlib import Path

@click.group()
def cli():
    """QuantConnect walk-forward validation CLI."""
    pass

@cli.command()
@click.option('--config', required=True, help='Walkforward config JSON')
@click.option('--state', default='iteration_state.json')
@click.option('--output', default='PROJECT_LOGS/validation_result.json')
@click.option('--runs', default=10, help='Number of Monte Carlo runs')
def run(config, state, output, runs):
    """Run walk-forward validation."""
    # Load config and state
    # For each Monte Carlo run:
    #   - Split data (train/test)
    #   - Optimize on training period
    #   - Backtest on test period
    #   - Record degradation
    # Statistical analysis
    # Save results
    pass

@cli.command()
@click.option('--results', required=True, help='Validation results JSON')
def analyze(results):
    """Analyze validation results."""
    # Load results
    # Calculate statistics:
    #   - Mean/median degradation
    #   - Standard deviation
    #   - Distribution percentiles
    #   - Parameter stability (consensus)
    # Display summary
    pass
```

**2.5.3 Integration with Commands** (1 day)

Update slash commands:
- `/qc-optimize` → calls `qc_optimize run`
- `/qc-validate` → calls `qc_validate run`

**2.5.4 Integration with Decision CLI** (1 day)

**Workflow**:
```bash
# Phase 3: Backtest
qc_backtest run --strategy strategy.py --output backtest.json
decision_cli evaluate-backtest --results backtest.json
# → Decision: PROCEED_TO_OPTIMIZATION

# Phase 4: Optimization
qc_optimize run --config params.json --state iteration_state.json
decision_cli evaluate-optimization --results optimization.json
# → Decision: PROCEED_TO_VALIDATION (or USE_BASELINE_PARAMS)

# Phase 5: Validation
qc_validate run --config walkforward.json --state iteration_state.json
decision_cli evaluate-validation --results validation.json
# → Decision: DEPLOY or ABANDON
```

**2.5.5 Testing** (1 day)
- Test optimization with sample parameter grid
- Test validation with sample walkforward config
- Verify integration with decision_cli
- Ensure PROJECT_LOGS stores all results

#### Success Criteria
- ✅ `qc_optimize.py` working (run, status, results commands)
- ✅ `qc_validate.py` working (run, analyze commands)
- ✅ Integration with `/qc-optimize` and `/qc-validate` commands
- ✅ Results stored in `PROJECT_LOGS/` (optimization_result.json, validation_result.json)
- ✅ Decision CLI can evaluate optimization and validation results
- ✅ Full Phase 1-5 workflow end-to-end tested

#### Risk Mitigation
- **Risk**: QC optimization API fails
  - **Mitigation**: Error handling, retry logic, fallback to baseline params
- **Risk**: Validation takes too long (Monte Carlo runs)
  - **Mitigation**: Configurable run count (default 10), parallel execution if possible
- **Risk**: Complex config files
  - **Mitigation**: Provide templates (optimization_params_template.json, walkforward_template.json)

**Duration**: 7 days (1 week)
**Enables**: Full autonomous workflow (Phases 1-5 complete)
**Deliverables**:
- [ ] `SCRIPTS/qc_optimize.py` working
- [ ] `SCRIPTS/qc_validate.py` working
- [ ] Shell aliases: `qc_optimize`, `qc_validate`
- [ ] Integration with `/qc-optimize`, `/qc-validate` commands
- [ ] Integration with `decision_cli` (evaluate-optimization, evaluate-validation)
- [ ] Config templates in `PROJECT_SCHEMAS/`
- [ ] All results logged to `PROJECT_LOGS/`

**Critical Note**: This phase is REQUIRED before testing hypotheses that need optimization or validation. Without it, we can only test Phase 1-3 (backtest-only hypotheses).

---

### Phase 3: Strategy Component Library (Week 3-4) **MEDIUM PRIORITY**

**Why Third?**
- Medium impact (85% context reduction)
- Less frequently used than timeline/decisions
- More complex (requires component extraction)
- Enables reusability across hypotheses

**Objective**: Replace 657-line quantconnect skill with 100-line component library

#### Tasks

**3.1 Create Component Library Structure** (2 days)

```
SCRIPTS/strategy_components/
├── README.md (component catalog)
├── indicators/
│   ├── add_rsi.py
│   ├── add_sma.py
│   ├── add_macd.py
│   ├── add_bollinger.py
│   └── add_atr.py
├── signals/
│   ├── mean_reversion.py
│   ├── momentum_breakout.py
│   ├── crossover.py
│   └── rsi_divergence.py
├── risk_management/
│   ├── stop_loss.py
│   ├── trailing_stop.py
│   ├── position_sizing.py
│   └── max_drawdown.py
└── cli.py (component CLI)
```

**3.2 Extract Components from Existing Strategies** (3 days)

From hypothesis 3 and 4:
- RSI indicator setup
- SMA indicator setup
- Mean reversion signal logic
- Momentum signal logic
- Basic stop loss
- Position sizing

Each component self-contained with docstring integration guide.

**3.3 Create strategy_component_cli.py** (2 days)

```bash
# Target commands:
strategy-component list [category]        # List components
strategy-component show COMPONENT         # Show code
strategy-component explain COMPONENT      # Integration guide
strategy-component search KEYWORD         # Search by keyword
```

**3.4 Create Minimal Skill** (1 day)

Replace `.claude/skills/quantconnect/skill.md` (657 lines) with component primer (100 lines):

```markdown
# Strategy Component Library

Build strategies with: `strategy-component`

## Categories
- `indicators/` - RSI, SMA, MACD, Bollinger, ATR
- `signals/` - Mean reversion, momentum, crossover
- `risk_management/` - Stop loss, position sizing

## Workflow
```bash
# Discover components:
strategy-component list indicators

# View component:
strategy-component show add-rsi

# Get integration guide:
strategy-component explain add-rsi
```

## Common Errors
[Keep critical bug section from current skill]

Use `--help` for details.
```

**3.5 Refactor Hypothesis 4 to Modular Architecture** (3 days)

Convert monolithic `rsi_mean_reversion.py` (67 lines) to modular:

```
STRATEGIES/hypothesis_4_rsi_mean_reversion/
├── strategy.py (40 lines - orchestration only)
├── indicators.py (30 lines - RSI setup)
├── signals.py (50 lines - entry/exit logic)
├── risk.py (30 lines - stop loss)
└── config.py (20 lines - parameters)
```

**3.6 Testing** (2 days)
- Test CLI component discovery
- Test modular strategy (same backtest results as monolithic)
- Test component reusability (use RSI in hypothesis 5)
- Measure context savings

#### Success Criteria
- ✅ CLI lists all components correctly
- ✅ Context reduced from 657 → 100 lines (85%)
- ✅ Modular hypothesis 4 produces identical backtest results
- ✅ Components reusable across hypotheses
- ✅ Humans can browse components via CLI

#### Risk Mitigation
- **Risk**: Modular architecture harder to understand
  - **Mitigation**: Each file has clear docstring, main strategy.py orchestrates
- **Risk**: Component library incomplete
  - **Mitigation**: Start with 5 core components, expand as needed
- **Risk**: Backtest results differ after refactoring
  - **Mitigation**: Test against baseline before/after

**Duration**: 13 days (2 weeks)
**Context Savings**: 557 lines (85%)
**Deliverables**:
- [ ] Component library with 15+ components
- [ ] `strategy_component_cli.py` working
- [ ] Hypothesis 4 refactored to modular architecture
- [ ] Minimal skill (100 lines) replaces old skill (657 lines)
- [ ] Components tested for reusability

---

### Phase 4: Kalshi Integration (Week 5-6) **OPTIONAL**

**Why Fourth?**
- Optional enhancement (not core refactoring)
- Depends on Phase 3 (component library)
- Requires external API (Kalshi account)
- High potential impact (40% Sharpe improvement)

**Objective**: Add Kalshi prediction market integration as strategy component

#### Tasks

**4.1 Kalshi API Setup** (1 day)
- Sign up for Kalshi API (free tier)
- Get API credentials
- Test API connection

**4.2 Create kalshi_api_wrapper.py** (2 days)

```python
# SCRIPTS/strategy_components/sentiment/kalshi_api_wrapper.py
from pathlib import Path
import httpx  # Direct HTTP, not SDK (lower dependency footprint)
import json

class KalshiAPI:
    """Kalshi API wrapper with search caching (Beyond MCP pattern)."""

    def __init__(self):
        # Absolute path resolution (works from any directory)
        self.cache_dir = Path(__file__).resolve().parent / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_file = self.cache_dir / "kalshi_markets_cache.json"

        # Build cache on first run (~2-5 minutes), then instant search
        if not self.cache_file.exists():
            self._build_cache()

    def _build_cache(self):
        """Build local cache of all markets (Beyond MCP search pattern)."""
        # Fetch all markets once, store locally
        # Enables instant pandas-based keyword search
        pass

    def get_recession_probability(self): ...
    def get_inflation_probability(self): ...
    def get_fed_cut_probability(self): ...
    def get_sp500_implied_vol(self): ...
```

**Beyond MCP Pattern**:
- Use `httpx` directly (not Kalshi SDK) to minimize dependencies
- Build complete local cache once (~2-5 min), then instant search
- Absolute path resolution (`Path(__file__).resolve()`) works from any directory

**4.3 Create Regime Detector Component** (3 days)

```python
# SCRIPTS/strategy_components/sentiment/kalshi_regime_detector.py
class KalshiRegimeDetector:
    def get_current_regime(self):
        # Returns: RECESSION_RISK, HIGH_VOLATILITY, FED_DOVISH, etc.
        ...
```

**4.4 Integrate with Hypothesis 4** (2 days)

Add regime detection to RSI mean reversion:
```python
regime = self.regime_detector.get_current_regime()

if regime == "RECESSION_RISK":
    self.Liquidate()  # Don't trade
elif regime == "FED_DOVISH":
    position_size = 1.0  # Full position
else:
    position_size = 0.75  # Normal
```

**4.5 Backtest Comparison** (3 days)
- Backtest hypothesis 4 WITHOUT Kalshi (baseline)
- Backtest hypothesis 4 WITH Kalshi (enhanced)
- Compare Sharpe, drawdown, win rate
- Measure alpha contribution

**4.6 Additional Components** (3 days - optional)
- `kalshi_fed_hedge.py` - FOMC event hedging
- `kalshi_vol_forecast.py` - Implied vol from ranges
- `kalshi_sentiment_monitor.py` - Probability shift alerts

#### Success Criteria
- ✅ Kalshi API integration working
- ✅ Regime detector classifies markets correctly
- ✅ Backtest shows improvement (Sharpe +20% minimum)
- ✅ Components reusable across strategies
- ✅ CLI supports Kalshi components

#### Risk Mitigation
- **Risk**: Kalshi API rate limits
  - **Mitigation**: Cache results, query only when needed (daily/weekly)
- **Risk**: No performance improvement
  - **Mitigation**: Acceptable - still learned integration pattern
- **Risk**: API changes break integration
  - **Mitigation**: Version pin, error handling, fallback to defaults

**Duration**: 14 days (2 weeks)
**Expected Impact**: +20-40% Sharpe improvement
**Deliverables**:
- [ ] Kalshi API wrapper working
- [ ] Regime detector component
- [ ] Hypothesis 4 enhanced with Kalshi
- [ ] Backtest comparison report
- [ ] Optional: Fed hedge, vol forecast, sentiment monitor components

---

## Implementation Priority Matrix

| Phase | Priority | Impact | Complexity | Duration | Dependencies |
|-------|----------|--------|------------|----------|--------------|
| **Phase 1: Timeline CLI** | **HIGHEST** | 90% savings | Low | 5 days | None |
| **Phase 2: Decision CLI** | **HIGH** | 87.5% savings | Medium | 7 days | Phase 1 |
| **Phase 2.5: Optimization & Validation Wrappers** | **HIGH** | Enables Phase 4-5 | Medium | 7 days | Phase 2 |
| **Phase 3: Component Library** | **MEDIUM** | 85% savings | High | 13 days | Phase 2.5 |
| **Phase 4: Kalshi Integration** | **OPTIONAL** | +40% Sharpe | Medium | 14 days | Phase 3 |

---

## Recommended Implementation Order

### Option A: Sequential (Safe, Thorough) ⭐ **RECOMMENDED**

**Timeline**: 7-9 weeks total

```
Week 1: Phase 1 (Timeline CLI)
Week 2: Phase 2 (Decision CLI)
Week 2.5: Phase 2.5 (Optimization & Validation Wrappers) - CRITICAL for Phase 4-5
Week 3-4: Phase 3 (Component Library)
Week 5-6: Phase 4 (Kalshi Integration) - OPTIONAL
Week 7-9: Testing, refinement, documentation
```

**Pros**:
- Each phase fully tested before next
- Can stop after any phase if needed
- Clear milestones and deliverables
- Lower risk of breaking existing workflow

**Cons**:
- Slower to realize full benefits
- 6-8 weeks to complete

---

### Option B: Parallel (Fast, Risky)

**Timeline**: 4-5 weeks total

```
Week 1: Phase 1 + start Phase 2
Week 2: Finish Phase 2 + start Phase 2.5
Week 3: Finish Phase 2.5 + start Phase 3
Week 4-5: Finish Phase 3 + start Phase 4
```

**Pros**:
- Faster to full implementation
- Realize benefits sooner

**Cons**:
- Higher risk of integration issues
- Harder to debug problems
- May need rework if dependencies unclear

**Recommendation**: **NOT RECOMMENDED** - Dependencies between phases make parallel risky

---

### Option C: Hybrid (Balanced) ⭐ **ALTERNATIVE**

**Timeline**: 5-6 weeks total

```
Week 1: Phase 1 (Timeline CLI) - Complete & Test
Week 2: Phase 2 (Decision CLI) - Complete & Test
Week 2.5: Phase 2.5 (Optimization & Validation Wrappers) - Complete & Test
Week 3-4: Phase 3 (Component Library) - Complete & Test
Week 5-6: Phase 4 (Kalshi) OR Testing/Refinement
```

**Pros**:
- Balanced speed and safety
- Core refactoring done in 4 weeks
- Kalshi optional in week 5

**Cons**:
- Still sequential, but faster milestones

**Recommendation**: **GOOD ALTERNATIVE** if timeline is priority

---

## Integration with Current Work

### Parallel Track: Hypothesis Testing

**Problem**: Don't want refactoring to block hypothesis testing

**Solution**: Dual-track approach

**Track 1: Refactoring** (background):
- Phase 1-3 improvements on separate branch
- Test in isolation
- Merge when stable

**Track 2: Hypothesis Testing** (main work):
- Continue hypothesis 4, 5, 6 on current system
- Use existing skills (631+800+657 lines)
- Switch to CLI after Phase 1-2 complete

**Merge Strategy**:
```
# Current branch: hypotheses/hypothesis-4-rsi-mean-reversion
# Refactoring branch: feature/beyond-mcp-refactoring

# After Phase 1 complete:
Merge Phase 1 → Use timeline CLI for new hypotheses

# After Phase 2 complete:
Merge Phase 2 → Use decision CLI for evaluations

# After Phase 3 complete:
Merge Phase 3 → Refactor existing hypotheses to modular
```

**Benefits**:
- Hypothesis testing continues unblocked
- Refactoring validated before integration
- Can cherry-pick phases (e.g., just timeline CLI)

---

## Success Metrics

### Context Efficiency

| Metric | Before | After Phase 1 | After Phase 2 | After Phase 3 | Target |
|--------|--------|---------------|---------------|---------------|--------|
| Timeline Operations | 631 lines | 60 lines | 60 lines | 60 lines | 60 lines |
| Decision Operations | 800 lines | 800 lines | 100 lines | 100 lines | 100 lines |
| Strategy Development | 657 lines | 657 lines | 657 lines | 100 lines | 100 lines |
| **TOTAL** | **2088 lines** | **1517 lines** | **817 lines** | **260 lines** | **260 lines** |
| **Reduction** | **0%** | **27%** | **61%** | **87%** | **87%** |

### Workflow Efficiency

**Measure**:
- Time to get next task (before: load 631-line skill, after: `timeline next`)
- Time to mark complete (before: manual jq + commit, after: `timeline complete w1-test-003`)
- Time to evaluate backtest (before: load 800-line skill, after: `decision_cli evaluate-backtest ...`)

**Target**: 50% reduction in time for common operations

### Code Quality

**Measure**:
- Lines of code per strategy (before: 67 monolithic, after: 170 total but modular)
- Component reusability (target: 3+ hypotheses using same components)
- Test coverage (target: 80%+ for CLI tools)

### Human Usability

**Measure**:
- Can human manually run `timeline next`? YES/NO
- Can human manually run `decision_cli evaluate-backtest`? YES/NO
- Can team member understand CLI without reading skills? YES/NO

**Target**: All YES (trifecta achieved)

---

## Risk Assessment

### High Risk

**Risk 1: Agent Confusion with CLI**
- **Probability**: Medium (30%)
- **Impact**: High (blocks autonomous workflow)
- **Mitigation**: Comprehensive primer skills with examples, --help documentation
- **Fallback**: Keep old skills temporarily, A/B test

**Risk 2: Regression in Decision Quality**
- **Probability**: Low (10%)
- **Impact**: Critical (wrong decisions = bad strategies)
- **Mitigation**: Comprehensive test suite, compare outputs before/after
- **Fallback**: Revert to decision_logic.py if CLI differs

### Medium Risk

**Risk 3: Timeline JSON Corruption**
- **Probability**: Medium (20%)
- **Impact**: Medium (lose progress tracking)
- **Mitigation**: Git tracks every change, can rollback; add JSON validation
- **Fallback**: Restore from git history

**Risk 4: Implementation Takes Longer**
- **Probability**: High (50%)
- **Impact**: Medium (delayed benefits)
- **Mitigation**: Phased approach allows stopping after any phase
- **Fallback**: Ship Phase 1+2 only (timeline + decision CLI)

### Low Risk

**Risk 5: Kalshi API Issues**
- **Probability**: Medium (30%)
- **Impact**: Low (optional enhancement only)
- **Mitigation**: Cache results, fallback to defaults, error handling
- **Fallback**: Skip Phase 4 entirely

---

## Resource Requirements

### Development Time

| Phase | Developer Days | Calendar Time |
|-------|---------------|---------------|
| Phase 0: Preparation | 2 days | 2 days |
| Phase 1: Timeline CLI | 5 days | 1 week |
| Phase 2: Decision CLI | 7 days | 1.5 weeks |
| Phase 2.5: Optimization & Validation Wrappers | 7 days | 1 week |
| Phase 3: Component Library | 13 days | 2.5 weeks |
| Phase 4: Kalshi (optional) | 14 days | 2.5 weeks |
| Testing & Documentation | 5 days | 1 week |
| **TOTAL** | **53 days** | **9-11 weeks** |

### External Dependencies

**Required**:
- None (all self-contained)

**Optional** (Phase 4 only):
- Kalshi API account (free tier available)
- Kalshi API credentials

### Testing Requirements

**Unit Tests**:
- Timeline CLI commands (next, complete, status, query)
- Decision CLI commands (evaluate-backtest, evaluate-optimization, route)
- Component library (each component tested independently)

**Integration Tests**:
- End-to-end hypothesis workflow with new CLIs
- Backtest results match before/after refactoring
- Git automation works correctly

**Acceptance Tests**:
- Human can use CLIs without reading skills
- Agent can use CLIs with minimal prompts
- Context usage reduced by 85%+

---

## Rollback Plan

### If Phase 1 Fails

**Revert**:
```bash
git checkout main
# Restore .claude/skills/project-timeline/skill.md (631 lines)
# Continue with old workflow
```

**Impact**: No harm, learned timeline patterns

### If Phase 2 Fails

**Revert**:
```bash
# Keep Phase 1 (timeline CLI working)
# Revert Phase 2 (decision CLI)
# Continue using decision_logic.py with imports
```

**Impact**: Still have 27% context savings from Phase 1

### If Phase 2.5 Fails

**Revert**:
```bash
# Keep Phase 1 + Phase 2 (61% context savings)
# Revert Phase 2.5 (optimization/validation wrappers)
# Continue using manual optimization/validation or skip Phases 4-5
```

**Impact**: Can only test Phase 1-3 hypotheses (backtest-only), but still have 61% context savings

### If Phase 3 Fails

**Revert**:
```bash
# Keep Phase 1 + Phase 2 (61% context savings)
# Revert Phase 3 (component library)
# Continue with monolithic strategies
```

**Impact**: Still have 61% context savings, missing reusability

### If Phase 4 Fails

**Skip entirely** - it's optional enhancement

**Impact**: Core refactoring still successful (87% context savings)

---

## Documentation Plan

### For Each Phase

**Developer Documentation**:
- README for each CLI tool (usage, examples, troubleshooting)
- Inline code comments (docstrings)
- Integration guides (how to use in commands)

**User Documentation**:
- Primer skills (50-100 lines each)
- `--help` text for all CLI commands
- Example workflows (common use cases)

**Migration Documentation**:
- Before/after comparison
- What changed and why
- How to use new CLI vs old skills

---

## Approval Decision Points

### Decision Point 1: After Phase 0

**Question**: Proceed with Phase 1 (Timeline CLI)?

**Criteria**:
- Baseline context measurements complete
- Testing framework ready
- User approves phased plan

**Go/No-Go**:

### Decision Point 2: After Phase 1

**Question**: Proceed with Phase 2 (Decision CLI)?

**Criteria**:
- Timeline CLI working correctly
- Context savings achieved (90%)
- No major issues discovered

**Go/No-Go**:

### Decision Point 3: After Phase 2

**Question**: Proceed with Phase 2.5 (Optimization & Validation Wrappers)?

**Criteria**:
- Decision CLI working correctly
- Cumulative context savings (61%)
- Need full autonomous workflow (Phases 4-5)?

**Go/No-Go**:

### Decision Point 4: After Phase 2.5

**Question**: Proceed with Phase 3 (Component Library)?

**Criteria**:
- Optimization & validation wrappers working
- Full Phase 1-5 workflow tested end-to-end
- No major issues discovered

**Go/No-Go**:

### Decision Point 5: After Phase 3

**Question**: Proceed with Phase 4 (Kalshi) OR Ship?

**Criteria**:
- Component library working
- Context savings achieved (87%)
- Kalshi integration worth effort?

**Options**:
- A) Proceed with Kalshi (2 more weeks)
- B) Ship now (87% savings sufficient)
- C) Defer Kalshi to future enhancement

**Go/No-Go**:

---

## Post-Implementation

### Monitoring

**Track**:
- Context usage per session (before/after)
- Time to complete common tasks
- Agent error rate (confusion with CLIs)
- Human usage of CLIs (adoption rate)

**Goals**:
- Context usage: <300 lines per session (87% reduction)
- Task completion time: 50% faster
- Agent error rate: <5%
- Human CLI usage: >50% of manual operations

### Iteration

**After 2 weeks of use**:
- Gather feedback from Claude Code usage
- Identify CLI pain points
- Refine prompts/help text
- Add missing components

**After 1 month**:
- Assess Kalshi integration value
- Consider additional components
- Evaluate MCP wrapper (if needed at scale)

---

## Recommendation

### Recommended Approach

**Option A: Sequential Implementation** ⭐

**Timeline**: 7-9 weeks

**Phases**:
1. **Week 1**: Phase 1 (Timeline CLI) - 90% context savings on most frequent operation
2. **Week 2**: Phase 2 (Decision CLI) - 87.5% cumulative savings, core workflow optimized
3. **Week 2.5**: Phase 2.5 (Optimization & Validation Wrappers) - CRITICAL for full autonomous workflow
4. **Week 3-4**: Phase 3 (Component Library) - 85% cumulative, enables reusability
5. **Week 5-6**: Phase 4 (Kalshi) OR Testing/Refinement - Optional enhancement
6. **Week 7-9**: Documentation, polish, migration guide

**Rationale**:
- **Highest ROI first** (Timeline CLI = 90% savings, used most)
- **Clear dependencies** (Phase 2 uses Phase 1 patterns)
- **Shippable increments** (can stop after any phase)
- **Lower risk** (validate each phase before next)
- **Learnings compound** (Timeline patterns inform Decision patterns)

### Success Definition

**Minimum Viable** (Phase 1+2 complete):
- ✅ 61% context reduction achieved
- ✅ Timeline and decision operations CLI-based
- ✅ Hypothesis workflow not broken (Phase 1-3 backtest-only)
- ✅ Human usability achieved (trifecta)

**Extended** (Phase 1+2+2.5 complete):
- ✅ 61% context reduction achieved
- ✅ Full autonomous workflow enabled (Phases 1-5)
- ✅ Optimization and validation working
- ✅ Can test hypotheses end-to-end

**Target** (Phase 1+2+2.5+3 complete):
- ✅ 87% context reduction achieved
- ✅ Component library enables reusability
- ✅ Strategy development modular
- ✅ All workflows CLI-based

**Stretch** (Phase 1+2+2.5+3+4 complete):
- ✅ Kalshi integration working
- ✅ +20-40% Sharpe improvement demonstrated
- ✅ Regime detection component proven

---

## Next Steps

**Immediate** (Today):
1. Review this proposal
2. Approve phased plan OR request modifications
3. Set up baseline measurements (Phase 0)

**Week 1**:
1. Implement Phase 1 (Timeline CLI)
2. Test with hypothesis 4 completion
3. Measure context savings

**Decision Point** (End Week 1):
- Go/No-Go for Phase 2?

---

## Appendix: Alternative Approaches Considered

### Alternative 1: Big Bang Refactoring

**Approach**: Implement all phases simultaneously

**Rejected Because**:
- High risk (all or nothing)
- Hard to debug issues
- Long time before any benefits
- No incremental validation

### Alternative 2: MCP Server Approach

**Approach**: Build MCP servers instead of CLIs

**Rejected Because**:
- 10k+ token context consumption per server
- Only works for agents (not humans/teams)
- Beyond MCP research shows CLI-first is better
- Can wrap MCP later if needed (not first)

### Alternative 3: Keep Skills, Optimize Content

**Approach**: Reduce skill line counts without CLI

**Rejected Because**:
- Still loads everything always (no progressive disclosure)
- Doesn't enable human/team workflows (no trifecta)
- Misses 85%+ context savings opportunity
- Doesn't align with Beyond MCP best practices

---

**Prepared By**: Claude Code
**Date**: 2025-11-10
**Status**: DRAFT - Awaiting Approval
**Next Action**: User review and approval to proceed with Phase 0
