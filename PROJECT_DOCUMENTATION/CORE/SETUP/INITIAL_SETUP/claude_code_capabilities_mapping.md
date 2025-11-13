# Claude Code 2.0 Capabilities Mapping to QuantConnect Autonomous Workflow

## Overview
This document maps specific Claude Code 2.0 features to each phase of the autonomous QuantConnect strategy development workflow.

---

## PHASE 1: RESEARCH & HYPOTHESIS FORMATION

### Claude Code Capabilities

#### **Explore Sub-Agent** ⭐ PRIMARY CAPABILITY
- **Use Case**: Rapid codebase exploration for similar strategies
- **How**: "Use Explore sub-agent with very thorough mode to find all mean-reversion strategies in the codebase"
- **Model**: Haiku 4.5 (fast, efficient)
- **Benefit**: Can quickly analyze existing QuantConnect projects for patterns

#### **WebSearch Tool**
- **Use Case**: Research academic papers, trading strategies, market factors
- **How**: Search for "momentum factor academic papers 2024" or "crypto volatility arbitrage strategies"
- **Limitation**: US only currently
- **Benefit**: Stay current with latest quant research

#### **WebFetch Tool**
- **Use Case**: Fetch QuantConnect forum discussions, documentation
- **How**: Fetch and analyze specific strategy threads or API docs
- **Benefit**: Learn from community strategies and best practices

#### **Grep Tool (Content Search)**
- **Use Case**: Search existing strategy codebase for specific patterns
- **How**: `pattern: "def OnData.*symbols.*BTCUSD"` to find Bitcoin strategies
- **Benefit**: Quick needle-in-haystack searches for specific implementations

#### **Model Selection: Sonnet 4.5**
- **Why**: Best for complex reasoning and hypothesis formation
- **Strength**: 30+ hour focus for complex multi-step tasks
- **Tradeoff**: More expensive, slower than Haiku

#### **Interactive Question Tool**
- **Use Case**: Clarify research direction before diving deep
- **Example**: "Which market regime should we target: trending, mean-reverting, or mixed?"
- **Benefit**: Ensures alignment before investing compute

### Supporting Features

- **Checkpoints**: Save state before exploring new research direction
- **Context Management**: `/compact` after completing literature review to summarize findings
- **Plan Mode (Sonnet Plan)**: Plan research approach, execute searches with Haiku

### Workflow Pattern
```
1. User provides market domain and general direction
2. Claude uses Interactive Question Tool to clarify constraints
3. Checkpoint created
4. Explore sub-agent searches existing strategies
5. WebSearch for latest research
6. Sonnet 4.5 synthesizes findings into 3-5 hypotheses
7. Present ranked hypotheses
8. /compact to summarize research before implementation
```

---

## PHASE 2: IMPLEMENTATION

### Claude Code Capabilities

#### **Model Selection: Haiku 4.5** ⭐ PRIMARY CAPABILITY
- **Use Case**: Fast code generation for algorithm implementation
- **Speed**: 2x faster than Sonnet 4
- **Cost**: 1/3 the cost
- **Ideal For**: Straightforward coding tasks with clear specs from Phase 1

#### **Sonnet Plan Mode** ⭐ RECOMMENDED APPROACH
- **How**: Sonnet 4.5 plans implementation → Haiku 4.5 executes code
- **Benefit**: Best of both worlds (smart planning, fast execution)
- **Use Case**: Complex strategy requiring multiple components (data, indicators, signals, risk)

#### **Read/Write/Edit Tools**
- **Use Case**: Create and modify strategy files
- **Pattern**: Read existing template → Edit for new strategy → Write new indicators
- **Benefit**: Precise file operations without bash overhead

#### **Bash Tool**
- **Use Case**: Install dependencies, run linters, execute local tests
- **Example**: `pip install QuantConnect` or `python -m pytest test_strategy.py`
- **Limitation**: Don't use for file operations (use Read/Write/Edit instead)

#### **Glob Tool**
- **Use Case**: Find relevant QuantConnect files by pattern
- **Example**: `pattern: "**/indicators/*.py"` to find indicator implementations
- **Benefit**: Fast pattern matching for boilerplate discovery

#### **Skills (Custom QuantConnect Skill)** ⭐ CRITICAL CUSTOMIZATION
- **Use Case**: Load QuantConnect Lean Framework knowledge on-demand
- **Contents**: Algorithm patterns, indicator usage, order handling
- **Benefit**: Progressive disclosure keeps context clean until needed
- **Access**: Via Skill tool when implementing QuantConnect-specific code

#### **MCP IDE Tools**
- **Use Case**: Get diagnostics while coding
- **Tool**: `mcp__ide__getDiagnostics` for syntax/type errors
- **Benefit**: Catch errors before backtesting

### Supporting Features

- **VS Code Extension**: View/edit files while prompting (ideal for reviewing generated code)
- **Inline Diffs**: Review changes before applying
- **Checkpoints**: Save state before major implementation changes
- **/rewind**: Roll back if implementation goes wrong direction

### Workflow Pattern
```
1. Checkpoint created (pre-implementation)
2. If complex: Enable Plan Mode (Sonnet plans, Haiku executes)
3. Load QuantConnect Skill via Skill tool
4. Glob to find template/similar strategies
5. Read template files
6. Write/Edit strategy files (main.py, indicators, risk management)
7. mcp__ide__getDiagnostics to check for errors
8. Review in VS Code extension (if using IDE)
9. Local syntax validation (python -m py_compile)
10. Checkpoint created (post-implementation)
```

---

## PHASE 3: BACKTESTING

### Claude Code Capabilities

#### **Bash Tool** ⭐ PRIMARY CAPABILITY
- **Use Case**: Execute QuantConnect CLI or API calls
- **Example**: `lean backtest "My Strategy" --start 2020-01-01 --end 2023-12-31`
- **Alternative**: Python script calling QuantConnect API
- **Benefit**: Full control over backtest execution

#### **Background Bash Execution**
- **Use Case**: Long-running backtests
- **Parameter**: `run_in_background: true`
- **Monitoring**: Use BashOutput tool to check progress
- **Benefit**: Continue other work while backtest runs

#### **BashOutput Tool**
- **Use Case**: Monitor running backtests
- **Parameter**: Filter for specific patterns (errors, completion)
- **Benefit**: Check progress without blocking

#### **Read Tool**
- **Use Case**: Parse backtest results (JSON, CSV, logs)
- **Example**: Read backtest_results.json to extract Sharpe, drawdown, trades
- **Benefit**: Structured analysis of results

#### **Model Selection: Sonnet 4.5**
- **Use Case**: Analyze backtest results (pattern recognition)
- **Why**: Better at complex analysis than Haiku
- **Task**: Identify overfitting signals, diagnose poor performance, detect edge cases

#### **Write Tool**
- **Use Case**: Save backtest results for future reference
- **Pattern**: Parse results → Write summary to markdown → Store in backtest_results/
- **Benefit**: Build historical record outside context window

### Supporting Features

- **Checkpoints**: Save before running backtest (in case of errors)
- **/rewind**: Quickly return to pre-backtest state if analysis reveals issues
- **Micro-Compact**: Auto-compress detailed backtest logs (keep summary)
- **Context Management**: Store full results in files, keep only key metrics in context

### Workflow Pattern
```
1. Checkpoint created
2. Execute backtest via Bash (background if long-running)
3. If background: Monitor with BashOutput until completion
4. Read backtest results files (JSON, CSV, logs)
5. Sonnet 4.5 analyzes results:
   - Extract key metrics (Sharpe, drawdown, win rate)
   - Check for errors/anomalies
   - Detect overfitting signals
   - Diagnose poor performance
6. Write analysis summary to file
7. Make autonomous decision:
   - Technical errors → Phase 2 (debugging)
   - Poor performance → Phase 4 (optimization) or Phase 1 (new hypothesis)
   - Meets criteria → Phase 5 (validation)
8. Micro-compact (summarize full results, keep decision)
```

---

## PHASE 4: OPTIMIZATION

### Claude Code Capabilities

#### **Bash Tool (Background Execution)** ⭐ PRIMARY CAPABILITY
- **Use Case**: Run multiple optimization backtests in parallel
- **Pattern**: Launch grid search with multiple background processes
- **Example**: For each parameter combo, run backtest in background
- **Limitation**: QuantConnect API rate limits may apply

#### **BashOutput with Filtering**
- **Use Case**: Monitor multiple optimization runs
- **Filter**: Extract only completion/error messages
- **Benefit**: Track progress across parallel optimizations

#### **Model Selection: Haiku 4.5**
- **Use Case**: Generate parameter combinations
- **Why**: Fast, deterministic task
- **Task**: Create grid of parameter ranges

#### **Model Selection: Sonnet 4.5**
- **Use Case**: Analyze optimization results (complex reasoning)
- **Why**: Better at detecting overfitting, parameter sensitivity
- **Task**: Select robust parameters, assess optimization quality

#### **Read/Write Tools**
- **Use Case**: Track optimization results
- **Pattern**: Write each result to CSV → Read all results → Analyze
- **Benefit**: Structured data for comparison

#### **TodoWrite Tool**
- **Use Case**: Track optimization progress
- **Example**: Create todo for each parameter combination
- **Benefit**: Visibility into long-running optimizations

### Supporting Features

- **Checkpoints**: Save before optimization (easy rollback)
- **Context Management**: Store full optimization results externally, keep only top performers in context
- **Cost Tracking**: Monitor API usage with `/usage` command

### Workflow Pattern
```
1. Checkpoint created
2. Haiku 4.5 generates parameter grid (e.g., 27 combinations)
3. TodoWrite to track optimization runs
4. For each combination:
   - Launch backtest via Bash (background)
   - Mark todo as in_progress
   - Monitor with BashOutput
   - When complete: Read results, Write to CSV, mark todo complete
5. After all runs: Sonnet 4.5 analyzes results
   - Rank by performance
   - Check parameter sensitivity (robust vs fragile)
   - Detect overfitting (isolated peaks)
   - Select optimal parameters with margin of safety
6. Write optimization report
7. /compact to summarize (keep optimal params, summarize 27 runs)
```

---

## PHASE 5: VALIDATION & ITERATION

### Claude Code Capabilities

#### **Model Selection: Sonnet 4.5** ⭐ PRIMARY CAPABILITY
- **Use Case**: Complex decision-making for iteration loops
- **Why**: Best at reasoning about multi-step autonomous workflows
- **Tasks**:
  - Compare in-sample vs out-of-sample performance
  - Decide next iteration action (re-optimize, new hypothesis, complete)
  - Risk assessment and strategy documentation

#### **Bash Tool**
- **Use Case**: Run out-of-sample validation backtest
- **Pattern**: Same as Phase 3 backtesting

#### **Write Tool**
- **Use Case**: Generate strategy documentation
- **Contents**: Strategy description, parameters, performance stats, risks
- **Format**: Markdown for human review

#### **Read Tool**
- **Use Case**: Compare validation results to previous backtest results
- **Pattern**: Read in-sample results → Read out-of-sample results → Compare

#### **Checkpoints**
- **Use Case**: Save validated strategy state
- **Benefit**: Can return to validated version if further experiments fail

#### **Interactive Question Tool**
- **Use Case**: Final human review gate (if configured)
- **Example**: "Strategy validated with Sharpe 1.4. Ready for paper trading?"
- **Options**: [Deploy to paper trading, Run additional tests, Archive and continue research]

### Supporting Features

- **Plan Mode**: Plan documentation structure before writing
- **/usage**: Check total cost of research cycle
- **/context**: Verify context hasn't bloated before final documentation
- **TodoWrite**: Track validation subtasks (out-of-sample, robustness, documentation)

### Workflow Pattern
```
1. Checkpoint created
2. Run out-of-sample backtest (Bash)
3. Read and compare results (in-sample vs out-of-sample)
4. Sonnet 4.5 makes validation decision:
   - Performance degradation > 30% → Re-optimize or new hypothesis
   - Performance stable → Proceed to documentation
5. If validated:
   - Write strategy documentation
   - Write risk assessment
   - Create final checkpoint
6. Interactive Question Tool (if human gate enabled):
   - Present strategy for review
   - Get deployment decision
7. If deployment approved: COMPLETE
8. If not validated: Autonomous decision on next iteration
   - Check iteration count vs limit
   - Decide: Phase 1 (new hypothesis) or Phase 4 (re-optimize)
9. /compact before next iteration
```

---

## CROSS-PHASE CAPABILITIES

### Context Management Strategy

#### **Checkpoints** ⭐ CRITICAL FOR AUTONOMY
- **Frequency**: After each phase completion
- **Use**: Rewind if iteration goes wrong direction
- **Limitation**: Can only go backwards from current checkpoint
- **Complement**: Use Git for permanent version control

#### **Micro-Compact (Automatic)**
- **Trigger**: Large tool results (backtest logs, optimization runs)
- **Action**: Keeps summaries, clears detailed results
- **Benefit**: Extends session length without manual intervention

#### **/compact Command**
- **When**: After completing major research, after optimization
- **Effect**: Clears conversation history, keeps summary
- **Use Case**: Transition between hypotheses while keeping learnings

#### **/clear Command**
- **When**: Starting completely new research direction
- **Effect**: Full reset (no summary)
- **Use Case**: Switch from crypto to equity strategies

#### **External State Files** ⭐ CRITICAL FOR LONG SESSIONS
- **Pattern**: Write iteration state to JSON, results to CSV
- **Benefit**: Context-independent state management
- **Files**:
  - `iteration_state.json`: Current phase, hypothesis count, iteration number
  - `hypotheses_log.md`: All hypotheses tested with outcomes
  - `backtest_results/*.json`: Full backtest outputs
  - `optimization_results.csv`: All parameter combinations tested

#### **/context and /usage Commands**
- **Frequency**: Check before each phase transition
- **Thresholds**: Compact if >70% context, stop if approaching rate limits
- **Benefit**: Proactive context management prevents auto-compact mid-task

### Model Selection Strategy

| Phase | Model | Rationale |
|-------|-------|-----------|
| Research | Sonnet 4.5 | Complex reasoning, hypothesis formation |
| Planning | Sonnet 4.5 | Architecture decisions, task breakdown |
| Implementation | Haiku 4.5 (via Sonnet Plan) | Fast coding with smart planning |
| Backtesting | Sonnet 4.5 | Result analysis, pattern detection |
| Optimization (generation) | Haiku 4.5 | Fast parameter grid creation |
| Optimization (analysis) | Sonnet 4.5 | Overfitting detection, sensitivity analysis |
| Validation | Sonnet 4.5 | Complex decision-making, documentation |
| Iteration Decisions | Sonnet 4.5 | Strategic choices about next steps |

### Autonomous Decision Framework

#### **TodoWrite Tool** ⭐ VISIBILITY & TRACKING
- **Use**: Track progress in long autonomous sessions
- **Pattern**: Create todos for each phase, mark in_progress/completed
- **Benefit**: User visibility into autonomous progress
- **Example**:
  ```
  1. [completed] Research momentum factors
  2. [completed] Implement momentum strategy v1
  3. [completed] Backtest on 2020-2023 data
  4. [in_progress] Optimize lookback period
  5. [pending] Validate on out-of-sample data
  ```

#### **Interactive Question Tool**
- **Minimal Mode**: Only at final validation
- **Medium Mode**: After each hypothesis selection
- **High Mode**: After each phase (user actively guides)
- **Benefit**: Configurable autonomy level

#### **Logging Pattern**
- **Write**: Log all autonomous decisions to `decisions_log.md`
- **Format**: Decision point, options considered, choice made, rationale
- **Benefit**: Auditability, debugging, improvement over time

---

## REQUIRED INTEGRATIONS

### QuantConnect API Integration

**Challenge**: Claude Code needs to interact with QuantConnect programmatically

**Options**:

1. **QuantConnect CLI (lean-cli)**
   - Install: `pip install lean`
   - Usage: `lean backtest "My Project"`
   - Benefits: Simple, CLI-based (works with Bash tool)
   - Limitations: Requires local setup

2. **QuantConnect API (Python SDK)**
   - Install: `pip install quantconnect`
   - Usage: Python script to submit backtests, check status, download results
   - Benefits: Full API access, programmatic control
   - Limitations: Requires API credentials, more complex

3. **Custom Wrapper Script**
   - Create: `qc_backtest.py` that handles API calls
   - Claude calls: `python qc_backtest.py --strategy momentum_v1 --start 2020-01-01`
   - Benefits: Simplified interface, error handling, result parsing
   - **RECOMMENDED APPROACH** ⭐

**Implementation**: Create custom Python wrapper as part of setup

### MCP Server for QuantConnect (Future)

**Potential**: Build custom MCP server for QuantConnect operations
- **Tools**: backtest, optimize, get_results, list_strategies
- **Benefit**: Native Claude Code integration (no Bash scripts)
- **Complexity**: Requires MCP server development
- **Timeline**: Phase 2 of research (after validating workflow)

---

## CAPABILITY GAPS & LIMITATIONS

### Current Limitations

1. **No Native Parallelization**
   - Cannot easily run 10 backtests in true parallel
   - Workaround: Background Bash + BashOutput monitoring
   - Impact: Optimization phase slower than ideal

2. **No Built-in Visualization**
   - Cannot render equity curves, parameter heatmaps
   - Workaround: Generate with matplotlib, save as PNG, describe in text
   - Impact: Analysis relies on text metrics vs visual patterns

3. **Rate Limits**
   - Max plan limits vary (Pro: 20X, Max: 5X or 20X)
   - Long optimizations can hit limits
   - Workaround: Cost tracking, pause/resume logic
   - Impact: May need human intervention mid-optimization

4. **No Persistent Memory Across Sessions**
   - Checkpoints don't survive session restarts
   - Must rely on external files for state
   - Impact: Cannot pause multi-day research and resume seamlessly

5. **QuantConnect API Costs**
   - Backtesting consumes QuantConnect compute credits
   - No built-in budgeting for external API costs
   - Workaround: Manual tracking in iteration_state.json
   - Impact: Could overspend without monitoring

### Gaps Requiring Customization

1. **QuantConnect Skill** (HIGH PRIORITY)
   - Gap: No built-in knowledge of Lean Framework
   - Solution: Create comprehensive skill with Lean patterns
   - Impact: Critical for code quality

2. **Strategy Development Plugin** (HIGH PRIORITY)
   - Gap: No workflow-specific commands
   - Solution: Build plugin with /qc-* commands
   - Impact: Streamlines autonomous operation

3. **Custom Agent (via SDK)** (MEDIUM PRIORITY)
   - Gap: No orchestration for multi-phase workflows
   - Solution: Build QuantConnect agent with state management
   - Impact: Enables fully autonomous operation

4. **Hooks for Automation** (LOW PRIORITY)
   - Gap: Manual checkpoint creation
   - Solution: Post-phase hooks to auto-checkpoint
   - Impact: Reduces manual intervention

---

## RECOMMENDED CAPABILITY STACK

### Minimum Viable Autonomous System
1. ✅ Claude Code 2.0 (Max plan for Opus/Sonnet/Haiku access)
2. ✅ QuantConnect Skill (custom, HIGH priority to build)
3. ✅ Custom wrapper script (`qc_backtest.py`, `qc_optimize.py`)
4. ✅ External state files (iteration_state.json, results CSVs)
5. ✅ Sonnet Plan mode (leverage Sonnet + Haiku)

### Enhanced Autonomous System
1. ✅ Minimum viable stack (above)
2. ✅ Strategy Development Plugin (custom commands)
3. ✅ Post-phase hooks (auto-checkpoint, auto-compact)
4. ✅ Cost tracking dashboard (external monitoring)

### Fully Autonomous System
1. ✅ Enhanced stack (above)
2. ✅ Custom QuantConnect Agent (via SDK)
3. ✅ MCP server for QuantConnect (native integration)
4. ✅ Multi-agent orchestration (parallel hypothesis testing)
5. ✅ Persistent memory (database for cross-session state)

---

## IMMEDIATE NEXT STEPS

### Validation Experiments

1. **Test Sonnet Plan Mode**
   - Task: Implement a simple momentum strategy manually
   - Observe: Quality of planning vs execution split
   - Measure: Speed, cost, code quality

2. **Test Context Management**
   - Task: Run 3 hypothesis iterations (research → backtest)
   - Monitor: Context usage via /context command
   - Practice: /compact at transitions, micro-compact observation

3. **Test Background Execution**
   - Task: Run a long backtest (5+ years of data)
   - Use: Background Bash + BashOutput monitoring
   - Measure: Usability, output capture quality

4. **Build Minimal QuantConnect Skill**
   - Create: skill.md with basic Lean patterns
   - Test: Load skill, implement algorithm, verify knowledge transfer
   - Iterate: Expand skill based on gaps observed

5. **Build Wrapper Script**
   - Create: `qc_backtest.py` that handles backtest submission
   - Interface: Simple CLI (strategy name, date range)
   - Output: Structured JSON with key metrics
   - Test: Call from Claude Code Bash tool

### Success Criteria
- ✅ Can complete 1 full cycle (hypothesis → validation) semi-autonomously
- ✅ Context stays under 100K tokens for full cycle
- ✅ Autonomous decisions are sensible (logged and auditable)
- ✅ Wrapper scripts work reliably from Bash tool
- ✅ Skill successfully teaches Lean Framework patterns
