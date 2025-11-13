# Required Customizations for QuantConnect Autonomous System

## Overview
This document provides detailed specifications for the three critical customizations needed to enable autonomous QuantConnect strategy development in Claude Code 2.0.

---

## CUSTOMIZATION 1: QuantConnect Skill

### Purpose
Teach Claude the QuantConnect Lean Algorithm Framework on-demand without bloating context.

### Priority
**CRITICAL** - Must be built first before any autonomous operation

### Structure

```
quantconnect-skill/
├── skill.md                    # Main skill definition
├── examples/
│   ├── basic_algorithm.py      # Minimal working example
│   ├── indicators_usage.py     # Common indicators
│   ├── risk_management.py      # Risk patterns
│   └── order_handling.py       # Order execution patterns
├── templates/
│   ├── momentum_template.py
│   ├── mean_reversion_template.py
│   └── volatility_template.py
└── reference/
    ├── common_errors.md        # Troubleshooting guide
    └── best_practices.md       # QC-specific best practices
```

### skill.md Content Specification

```markdown
---
name: QuantConnect
description: Load QuantConnect Lean Algorithm Framework knowledge for strategy development
---

# QuantConnect Lean Algorithm Framework

## Core Algorithm Structure

Every QuantConnect algorithm inherits from QCAlgorithm:

```python
from AlgorithmImports import *

class MyStrategy(QCAlgorithm):
    def Initialize(self):
        # Set dates, cash, resolution
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2023, 12, 31)
        self.SetCash(100000)

        # Add securities
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol

        # Create indicators
        self.sma = self.SMA(self.symbol, 50, Resolution.Daily)

    def OnData(self, data):
        # Trading logic
        if not self.sma.IsReady:
            return

        if not self.Portfolio.Invested:
            if data[self.symbol].Close > self.sma.Current.Value:
                self.SetHoldings(self.symbol, 1.0)
        elif data[self.symbol].Close < self.sma.Current.Value:
            self.Liquidate(self.symbol)
```

## Data Subscriptions

### Equity
```python
self.symbol = self.AddEquity("AAPL", Resolution.Daily).Symbol
```

### Crypto
```python
self.symbol = self.AddCrypto("BTCUSD", Resolution.Hour).Symbol
```

### Forex
```python
self.symbol = self.AddForex("EURUSD", Resolution.Minute).Symbol
```

### Futures
```python
self.symbol = self.AddFuture(Futures.Indices.SP500EMini, Resolution.Minute).Symbol
```

## Common Indicators

### Moving Averages
```python
self.sma = self.SMA(symbol, 20)  # Simple MA
self.ema = self.EMA(symbol, 20)  # Exponential MA
```

### Momentum
```python
self.rsi = self.RSI(symbol, 14)  # RSI
self.macd = self.MACD(symbol, 12, 26, 9)  # MACD
self.mom = self.MOM(symbol, 10)  # Momentum
```

### Volatility
```python
self.bb = self.BB(symbol, 20, 2)  # Bollinger Bands
self.atr = self.ATR(symbol, 14)  # Average True Range
```

### Check if indicator is ready
```python
if not self.sma.IsReady:
    return  # Skip trading until warm-up complete
```

## Order Execution

### Market Orders
```python
# Long 100 shares
self.MarketOrder(symbol, 100)

# Short 50 shares
self.MarketOrder(symbol, -50)
```

### Limit Orders
```python
self.LimitOrder(symbol, 100, limit_price)
```

### Set Holdings (percentage of portfolio)
```python
self.SetHoldings(symbol, 0.5)  # 50% of portfolio
```

### Liquidate
```python
self.Liquidate(symbol)  # Close all positions in symbol
self.Liquidate()  # Close all positions
```

## Risk Management Patterns

### Position Sizing by Volatility
```python
def OnData(self, data):
    volatility = self.atr.Current.Value / data[self.symbol].Close
    position_size = 0.01 / volatility  # Risk 1% per position
    position_size = min(position_size, 1.0)  # Max 100%

    if buy_signal:
        self.SetHoldings(self.symbol, position_size)
```

### Stop Loss
```python
def OnData(self, data):
    if buy_signal:
        self.entry_price = data[self.symbol].Close
        self.SetHoldings(self.symbol, 1.0)
        self.stop_loss_price = self.entry_price * 0.95  # 5% stop

    if self.Portfolio.Invested:
        if data[self.symbol].Close < self.stop_loss_price:
            self.Liquidate(self.symbol)
```

### Maximum Drawdown Protection
```python
def OnData(self, data):
    # Track peak portfolio value
    if self.Portfolio.TotalPortfolioValue > self.peak_value:
        self.peak_value = self.Portfolio.TotalPortfolioValue

    # Calculate current drawdown
    drawdown = (self.peak_value - self.Portfolio.TotalPortfolioValue) / self.peak_value

    # Liquidate if max drawdown exceeded
    if drawdown > 0.20:  # 20% max drawdown
        self.Liquidate()
        self.Quit("Max drawdown exceeded")
```

## Scheduled Events

### Trade at market open
```python
def Initialize(self):
    self.Schedule.On(
        self.DateRules.EveryDay("SPY"),
        self.TimeRules.AfterMarketOpen("SPY", 30),  # 30 min after open
        self.Rebalance
    )

def Rebalance(self):
    # Your rebalancing logic
    pass
```

## Portfolio State

### Check if invested
```python
if self.Portfolio.Invested:
    # Have positions
    pass

if self.Portfolio[symbol].Invested:
    # Have position in specific symbol
    pass
```

### Get position quantity
```python
quantity = self.Portfolio[symbol].Quantity
```

### Get portfolio value
```python
total_value = self.Portfolio.TotalPortfolioValue
cash = self.Portfolio.Cash
```

## Logging and Debugging

```python
self.Debug(f"Price: {data[self.symbol].Close}")
self.Log(f"Trade executed at {self.Time}")
```

## Common Patterns for Strategy Types

### Momentum Strategy Pattern
1. Calculate momentum indicator (RSI, MACD, MOM)
2. Buy when momentum crosses above threshold
3. Sell when momentum crosses below threshold
4. Add stop loss and take profit

### Mean Reversion Pattern
1. Calculate mean (SMA, EMA) and deviation (BB, ATR)
2. Buy when price deviates below mean (oversold)
3. Sell when price returns to mean or above
4. Limit position size to manage risk

### Volatility Breakout Pattern
1. Calculate volatility (ATR, BB)
2. Buy when price breaks above upper band
3. Sell when price falls back into range
4. Use trailing stop to lock profits

## Files to Reference

- `examples/basic_algorithm.py` - Minimal working example
- `examples/indicators_usage.py` - All common indicators
- `examples/risk_management.py` - Risk management patterns
- `templates/momentum_template.py` - Momentum strategy template
- `templates/mean_reversion_template.py` - Mean reversion template
- `reference/common_errors.md` - Troubleshooting guide
- `reference/best_practices.md` - Best practices
```

### Example Files to Include

**examples/basic_algorithm.py**:
```python
from AlgorithmImports import *

class BasicMomentumAlgorithm(QCAlgorithm):
    """Minimal momentum strategy example"""

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2023, 12, 31)
        self.SetCash(100000)

        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.rsi = self.RSI(self.symbol, 14, Resolution.Daily)

    def OnData(self, data):
        if not self.rsi.IsReady:
            return

        if not self.Portfolio.Invested:
            if self.rsi.Current.Value < 30:  # Oversold
                self.SetHoldings(self.symbol, 1.0)
        else:
            if self.rsi.Current.Value > 70:  # Overbought
                self.Liquidate(self.symbol)
```

### Installation Instructions

1. Create directory: `.claude/skills/quantconnect/`
2. Add `skill.md` with content above
3. Add example files in `examples/` subdirectory
4. Test with: Load skill when implementing QuantConnect algorithm

### Usage in Claude Code

When implementing a QuantConnect strategy:
```
Load the QuantConnect skill to access Lean framework knowledge
```

Claude will then have access to all patterns, examples, and best practices.

---

## CUSTOMIZATION 2: QuantConnect Strategy Development Plugin

### Purpose
Provide workflow-specific commands to streamline autonomous operation.

### Priority
**HIGH** - Significantly improves UX and reduces prompt complexity

### Structure

```
quantconnect-plugin/
├── plugin.json                 # Plugin metadata
├── commands/
│   ├── qc-init.md             # Initialize new strategy project
│   ├── qc-backtest.md         # Run backtest and analyze results
│   ├── qc-optimize.md         # Run parameter optimization
│   ├── qc-validate.md         # Run out-of-sample validation
│   ├── qc-status.md           # Show iteration state
│   └── qc-auto-iterate.md     # Autonomous iteration loop
└── hooks/
    ├── post-backtest.sh       # Auto-save results, checkpoint
    └── context-warning.sh     # Trigger compact at 70% usage
```

### plugin.json

```json
{
  "name": "quantconnect-strategy-dev",
  "version": "1.0.0",
  "description": "QuantConnect autonomous strategy development workflow",
  "author": "Your Name",
  "commands": [
    {
      "name": "qc-init",
      "description": "Initialize new QuantConnect strategy research session"
    },
    {
      "name": "qc-backtest",
      "description": "Run backtest and analyze results"
    },
    {
      "name": "qc-optimize",
      "description": "Run parameter optimization"
    },
    {
      "name": "qc-validate",
      "description": "Run out-of-sample validation"
    },
    {
      "name": "qc-status",
      "description": "Show current iteration state and progress"
    },
    {
      "name": "qc-auto-iterate",
      "description": "Start autonomous iteration loop"
    }
  ],
  "hooks": [
    {
      "name": "post-backtest",
      "trigger": "after_tool",
      "tool": "Bash",
      "pattern": "qc_backtest.py",
      "script": "hooks/post-backtest.sh"
    },
    {
      "name": "context-warning",
      "trigger": "context_threshold",
      "threshold": 0.7,
      "script": "hooks/context-warning.sh"
    }
  ]
}
```

### Command Specifications

**commands/qc-init.md**:
```markdown
Initialize a new QuantConnect strategy research session.

Steps:
1. Create project structure:
   - strategy_research/
   - iteration_state.json
   - hypotheses_log.md
   - backtest_results/
   - strategies/
   - analysis/

2. Prompt user for:
   - Market domain (equity, crypto, forex, futures)
   - Initial research direction or hypothesis
   - Risk parameters (max drawdown, target Sharpe)
   - Backtest date range
   - Initial capital

3. Initialize iteration_state.json with config

4. Create first checkpoint

5. Load QuantConnect skill

6. Begin research phase
```

**commands/qc-backtest.md**:
```markdown
Run backtest and analyze results for current strategy.

Parameters:
- strategy_file: Path to strategy Python file
- start_date: Backtest start date (default from config)
- end_date: Backtest end date (default from config)
- initial_capital: Initial capital (default from config)

Steps:
1. Validate strategy file exists and has no syntax errors
2. Execute backtest via qc_backtest.py wrapper
3. Monitor execution (background if long-running)
4. Read results JSON
5. Analyze results:
   - Extract key metrics (Sharpe, drawdown, trades, win rate)
   - Check for overfitting signals
   - Diagnose errors or anomalies
6. Write analysis to backtest_results/{timestamp}.json
7. Make autonomous decision (proceed to optimization/validation, fix bugs, or abandon)
8. Update iteration_state.json
9. Create checkpoint
```

**commands/qc-auto-iterate.md**:
```markdown
Start autonomous strategy development iteration loop.

This command enables fully autonomous operation according to the decision framework.

Configuration:
- Read autonomy_mode from iteration_state.json (minimal/medium/full)
- Read performance thresholds and limits

Steps:
1. Load current state from iteration_state.json
2. Resume from current phase
3. Execute master control loop (from autonomous_decision_framework.md)
4. At each decision point:
   - Apply decision logic
   - Log decision and rationale
   - Execute chosen action
5. Continue until:
   - Strategy validated and complete
   - Iteration limit reached
   - Cost budget exceeded
   - Human intervention required
6. Present final results and recommendations
```

**commands/qc-status.md**:
```markdown
Show current iteration state and progress.

Display:
- Current phase
- Current hypothesis (name and description)
- Iteration count (current/max)
- Hypotheses tested (count and outcomes)
- Best Sharpe ratio achieved so far
- Cost spent vs budget
- Context usage percentage
- Recent decisions (last 3)

Example output:
```
QuantConnect Strategy Research Status
=====================================
Phase: Optimization (attempt 2/3)
Hypothesis: Multi-timeframe momentum (BTC/ETH)
Iteration: 7 / 15

Progress:
  Hypotheses tested: 2
  - H1 (Mean reversion): ABANDONED (poor performance)
  - H2 (Momentum): IN PROGRESS

Performance:
  Best Sharpe so far: 0.85 (H2, baseline)
  Current optimization improving to: 0.92 (pending validation)

Resources:
  Cost: $12.50 / $50.00 (25%)
  Context: 72,000 / 150,000 tokens (48%)

Recent Decisions:
  [2025-01-15 11:23] Backtest met optimization threshold → PROCEED_TO_OPTIMIZATION
  [2025-01-15 10:15] Implementation validated → PROCEED_TO_BACKTEST
  [2025-01-15 09:45] Selected hypothesis H2 (score: 0.82)
```
```

### Hook Scripts

**hooks/post-backtest.sh**:
```bash
#!/bin/bash
# Automatically triggered after backtest completion

# Save checkpoint
echo "Creating post-backtest checkpoint..."

# Log to decisions log
echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Post-backtest checkpoint created" >> strategy_research/decisions_log.md

# Check context usage and trigger compact if needed
CONTEXT_USAGE=$(claude context --json | jq '.usage_percent')
if (( $(echo "$CONTEXT_USAGE > 70" | bc -l) )); then
    echo "Context usage at ${CONTEXT_USAGE}% - triggering compact"
    # Compact will be suggested to user
fi
```

### Installation

```bash
# Clone plugin repo (or create locally)
git clone https://github.com/yourusername/quantconnect-claude-plugin

# Install via Claude Code
/plugin install /path/to/quantconnect-plugin
```

---

## CUSTOMIZATION 3: QuantConnect Agent (via Claude Agent SDK)

### Purpose
Orchestrate fully autonomous multi-phase strategy development with state management.

### Priority
**MEDIUM** - Enhances autonomy but can start with plugins/commands

### Architecture

```
quantconnect-agent/
├── agent.py                    # Main agent orchestrator
├── config.json                 # Agent configuration
├── phases/
│   ├── research.py            # Research phase logic
│   ├── implementation.py      # Implementation phase logic
│   ├── backtest.py            # Backtest phase logic
│   ├── optimization.py        # Optimization phase logic
│   └── validation.py          # Validation phase logic
├── decision_engine/
│   ├── evaluator.py           # Decision evaluation logic
│   ├── thresholds.py          # Performance thresholds
│   └── router.py              # Phase routing logic
├── integrations/
│   ├── quantconnect_api.py    # QC API wrapper
│   └── claude_code.py         # Claude Code tool wrappers
├── state/
│   ├── manager.py             # State persistence
│   └── checkpoint.py          # Checkpoint management
└── utils/
    ├── logging.py             # Decision logging
    ├── monitoring.py          # Cost/context monitoring
    └── reporting.py           # Results reporting
```

### agent.py (Main Orchestrator)

```python
from claude_code_sdk import Agent, Tool
from phases import ResearchPhase, ImplementationPhase, BacktestPhase, OptimizationPhase, ValidationPhase
from decision_engine import DecisionEvaluator, PhaseRouter
from state import StateManager
from integrations import QuantConnectAPI, ClaudeCodeTools

class QuantConnectStrategyAgent(Agent):
    """Autonomous QuantConnect strategy development agent"""

    def __init__(self, config_path: str):
        super().__init__(name="quantconnect-strategy-agent")

        # Load configuration
        self.config = self.load_config(config_path)

        # Initialize components
        self.state_manager = StateManager(self.config)
        self.qc_api = QuantConnectAPI(self.config.qc_api_key)
        self.claude_tools = ClaudeCodeTools()
        self.decision_evaluator = DecisionEvaluator(self.config.thresholds)
        self.phase_router = PhaseRouter(self.config)

        # Initialize phases
        self.phases = {
            "research": ResearchPhase(self.claude_tools, self.config),
            "implementation": ImplementationPhase(self.claude_tools, self.config),
            "backtest": BacktestPhase(self.qc_api, self.claude_tools, self.config),
            "optimization": OptimizationPhase(self.qc_api, self.claude_tools, self.config),
            "validation": ValidationPhase(self.qc_api, self.claude_tools, self.config)
        }

    async def run(self, initial_prompt: str):
        """Main autonomous iteration loop"""

        # Initialize state
        state = self.state_manager.initialize(initial_prompt)

        while not state.is_complete:
            # Check global limits
            if self.check_limits(state):
                break

            # Execute current phase
            current_phase = self.phases[state.current_phase]
            result = await current_phase.execute(state)

            # Evaluate results and make decision
            decision = self.decision_evaluator.evaluate(
                phase=state.current_phase,
                result=result,
                state=state
            )

            # Log decision
            self.log_decision(decision, state)

            # Route to next phase
            state = self.phase_router.route(decision, state)

            # Save state
            self.state_manager.save(state)

            # Create checkpoint
            await self.claude_tools.create_checkpoint(state.current_phase)

        # Present final results
        return self.generate_report(state)

    def check_limits(self, state) -> bool:
        """Check if any global limits exceeded"""
        if state.total_iterations >= self.config.limits.max_iterations:
            self.escalate_to_human("Max iterations reached")
            return True

        if state.total_cost >= self.config.limits.max_cost:
            self.escalate_to_human("Cost budget exceeded")
            return True

        return False
```

### Key Methods in Phases

**phases/backtest.py** (example):
```python
class BacktestPhase:
    async def execute(self, state):
        """Execute backtest phase"""

        # Validate code
        validation_result = self.validate_code(state.current_code)
        if not validation_result.valid:
            return BacktestResult(
                status="error",
                error_message=validation_result.errors,
                needs_debugging=True
            )

        # Submit backtest to QuantConnect
        backtest_id = await self.qc_api.submit_backtest(
            code=state.current_code,
            start_date=self.config.backtest_start,
            end_date=self.config.backtest_end
        )

        # Monitor progress
        while True:
            status = await self.qc_api.get_backtest_status(backtest_id)
            if status.completed:
                break
            await asyncio.sleep(10)

        # Download results
        results = await self.qc_api.get_backtest_results(backtest_id)

        # Analyze results
        analysis = self.analyze_results(results)

        return BacktestResult(
            status="success",
            metrics=results.metrics,
            analysis=analysis,
            results_file=self.save_results(results, state)
        )
```

### Usage

```python
# Initialize agent
agent = QuantConnectStrategyAgent("config.json")

# Start autonomous research
result = await agent.run(
    initial_prompt="Develop a profitable crypto momentum strategy targeting BTC and ETH"
)

# Agent runs fully autonomously until completion or escalation
print(result.summary)
```

### Integration with Claude Code

The agent uses Claude Code tools internally:
- `ClaudeCodeTools.read_file()` → wraps Read tool
- `ClaudeCodeTools.write_file()` → wraps Write tool
- `ClaudeCodeTools.execute_bash()` → wraps Bash tool
- `ClaudeCodeTools.create_checkpoint()` → creates checkpoint
- `ClaudeCodeTools.load_skill()` → loads QuantConnect skill

### Benefits Over Plugin Approach

1. **Full Python Control**: Complex logic in Python vs markdown prompts
2. **Async Operations**: Parallel backtests, concurrent optimizations
3. **State Persistence**: Database or structured state management
4. **Error Recovery**: Programmatic retry logic, exponential backoff
5. **Monitoring**: Real-time dashboards, cost tracking, alerts
6. **Testing**: Unit tests for decision logic
7. **Reusability**: Import as library in other projects

---

## IMPLEMENTATION ROADMAP

### Phase 1: Minimal Viable System (Week 1-2)
**Goal**: Validate workflow with manual operation

- [x] Design workflow architecture
- [x] Map Claude Code capabilities
- [x] Define decision framework
- [ ] Build QuantConnect Skill (skill.md + examples)
- [ ] Create qc_backtest.py wrapper script
- [ ] Test one full manual cycle (research → validation)
- [ ] Document learnings and friction points

**Deliverables**:
- Working QuantConnect Skill
- Wrapper script for backtesting
- Manual workflow documentation

### Phase 2: Semi-Autonomous System (Week 3-4)
**Goal**: Automate individual phases

- [ ] Build QuantConnect Plugin
  - [ ] /qc-init command
  - [ ] /qc-backtest command
  - [ ] /qc-status command
- [ ] Create iteration_state.json schema
- [ ] Implement decision logging
- [ ] Add post-backtest hook
- [ ] Test semi-autonomous operation (manual phase transitions)

**Deliverables**:
- Working plugin with commands
- State management files
- Decision logging system

### Phase 3: Fully Autonomous System (Week 5-8)
**Goal**: Full autonomous multi-iteration operation

- [ ] Build /qc-auto-iterate command (master loop)
- [ ] Implement all decision functions from framework
- [ ] Add context management automation
- [ ] Create cost tracking and alerts
- [ ] Build systematic failure detection
- [ ] Test 5+ hypothesis iterations autonomously

**Deliverables**:
- Fully autonomous plugin
- Monitoring dashboard
- Complete decision framework implementation

### Phase 4: Agent SDK Implementation (Week 9-12)
**Goal**: Production-grade autonomous system

- [ ] Build QuantConnect Agent using SDK
- [ ] Migrate decision logic to Python
- [ ] Add async backtest execution
- [ ] Build real-time monitoring
- [ ] Implement database state persistence
- [ ] Create agent unit tests
- [ ] Performance benchmarking

**Deliverables**:
- Production QuantConnect Agent
- Monitoring dashboard
- Test suite
- Performance benchmarks

---

## TESTING STRATEGY

### Unit Tests
- Decision functions with mock backtest data
- State management (save/load)
- Threshold evaluation
- Overfitting detection

### Integration Tests
- Full phase execution (research → implementation)
- State persistence across iterations
- Context management triggers
- Checkpoint/rewind functionality

### End-to-End Tests
- Complete autonomous cycle (1 hypothesis)
- Multi-hypothesis iterations (3-5 hypotheses)
- Cost limit enforcement
- Context overflow handling
- Systematic failure detection

### Performance Benchmarks
- Time to complete full cycle
- Cost per hypothesis tested
- Context usage per phase
- Decision quality (manual review)

---

## SUCCESS METRICS

### Technical Metrics
- ✅ Can complete full cycle without errors
- ✅ Autonomous decisions match human judgment >80%
- ✅ Context stays under 150K tokens per full cycle
- ✅ Cost under $50 per validated strategy
- ✅ Time to validated strategy <4 hours

### Quality Metrics
- ✅ Generated strategies meet minimum criteria (Sharpe >1.0)
- ✅ Out-of-sample validation <30% degradation
- ✅ No false positives (overfitted strategies marked valid)
- ✅ Decision rationales are clear and auditable

### Operational Metrics
- ✅ Zero unhandled exceptions
- ✅ All state persisted correctly
- ✅ Checkpoints enable reliable rewind
- ✅ Hooks trigger correctly
- ✅ Monitoring shows real-time progress

---

## NEXT IMMEDIATE ACTIONS

1. **Build QuantConnect Skill** (2-3 hours)
   - Create skill.md with Lean framework knowledge
   - Add 3-4 example files
   - Test skill loading and knowledge transfer

2. **Create Wrapper Script** (1-2 hours)
   - Build qc_backtest.py
   - Test with sample strategy
   - Validate JSON output format

3. **Manual Workflow Test** (3-4 hours)
   - Pick simple hypothesis (e.g., RSI mean reversion)
   - Manually execute all phases
   - Document friction points and improvements
   - Validate decision framework thresholds

4. **Build /qc-init Command** (2 hours)
   - Create plugin structure
   - Implement initialization logic
   - Test project setup automation

5. **Build /qc-backtest Command** (3 hours)
   - Integrate wrapper script
   - Add result analysis logic
   - Test autonomous decision-making
