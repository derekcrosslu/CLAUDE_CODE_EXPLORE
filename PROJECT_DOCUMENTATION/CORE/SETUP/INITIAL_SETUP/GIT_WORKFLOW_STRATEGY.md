# Git Workflow Strategy - Autonomous QuantConnect Development

**Purpose**: Git is a VITAL component of the autonomous workflow, providing version control, audit trail, rollback capability, and collaboration support.

---

## Why Git is Critical

### 1. **Audit Trail**
- Every decision, backtest, and optimization is committed with context
- Full history of strategy evolution
- Regulatory compliance for live trading
- Reproducibility of results

### 2. **Rollback Capability**
- Revert to previous working strategy
- Undo failed optimizations
- Return to validated baseline
- Recover from mistakes

### 3. **Experimentation Safety**
- Try aggressive optimizations with confidence
- Branch for each hypothesis
- Merge only validated strategies
- Keep main branch clean (validated only)

### 4. **Collaboration & Review**
- Share strategies with team
- Code review before deployment
- Document decision rationale in commits
- Track who changed what and why

### 5. **Continuous Integration**
- Automated testing on commit
- Pre-commit hooks for validation
- Automatic backtest triggering
- Deploy validated strategies automatically

---

## Git Branch Strategy

### Branch Structure

```
main
├─ validated-strategies/     (only validated, deployable strategies)
├─ optimization/             (parameter optimization experiments)
└─ hypotheses/
    ├─ hypothesis-001-rsi-mean-reversion
    ├─ hypothesis-002-macd-momentum
    └─ hypothesis-003-bollinger-breakout
```

### Branch Rules

**`main` branch**:
- ✅ Only validated strategies (OOS tested)
- ✅ Ready for deployment consideration
- ✅ Protected - requires approval to merge
- ✅ Tagged with version numbers (v1.0.0, v1.1.0, etc.)

**`validated-strategies/` branches**:
- Strategies that passed validation
- Not yet merged to main (pending review/approval)
- Tagged with validation date

**`optimization/` branches**:
- Parameter optimization experiments
- Merged back to hypothesis branch with results
- Deleted after merge

**`hypotheses/hypothesis-XXX-name` branches**:
- One branch per hypothesis
- All development happens here
- Commits at each phase transition
- Merged to validated-strategies/ if successful

---

## Commit Strategy - Automated by Workflow

### Phase-Based Commits

Each phase transition triggers an automatic commit:

#### 1. **After Research (Hypothesis Creation)**

```bash
# Triggered by: /qc-init
git checkout -b hypotheses/hypothesis-001-rsi-mean-reversion
git add iteration_state.json
git commit -m "research: Initialize hypothesis - RSI Mean Reversion

Hypothesis: RSI mean reversion with Bollinger Band confirmation
Entry: RSI < 30 AND price near BB lower
Exit: RSI > 70 OR stop loss

Phase: research → implementation
Iteration: 1

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### 2. **After Implementation**

```bash
# Triggered by: Strategy file created/modified
git add test_strategy.py iteration_state.json
git commit -m "implement: Create RSI mean reversion strategy

Implementation:
- RSI(14) with 30/70 thresholds
- Bollinger Bands(20, 2) confirmation
- 200 SMA trend filter
- 3% stop loss, 8% take profit
- ATR-based position sizing

Phase: implementation → backtest
Iteration: 1
File: test_strategy.py

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### 3. **After Backtest**

```bash
# Triggered by: /qc-backtest
git add backtest_results.json iteration_state.json decisions_log.md
git commit -m "backtest: Complete initial backtest

Results:
- Sharpe: 0.00
- Drawdown: 0%
- Return: 0%
- Trades: 0

Decision: ESCALATE
Reason: Too few trades (0 < 10), insufficient data

Next Action: Relax entry conditions
Phase: backtest → modification
Iteration: 1
Backtest ID: 691852b80fe50a0015e01c1737a2e654

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### 4. **After Optimization**

```bash
# Triggered by: /qc-optimize
git add optimization_results.json iteration_state.json test_strategy.py
git commit -m "optimize: Parameter optimization complete

Parameters Tested: 27 combinations
- rsi_period: 10, 14, 20
- rsi_oversold: 25, 30, 35
- rsi_overbought: 65, 70, 75

Best Parameters:
- rsi_period: 14
- rsi_oversold: 30
- rsi_overbought: 70

Best Sharpe: 1.45 (vs baseline 0.82)
Improvement: 78%
Parameter Sensitivity: 0.32 (LOW ✅)

Decision: PROCEED_TO_VALIDATION
Phase: optimization → validation
Iteration: 2

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### 5. **After Validation**

```bash
# Triggered by: /qc-validate
git add oos_results.json iteration_state.json decisions_log.md
git commit -m "validate: Out-of-sample validation PASSED

In-Sample (2023):
- Sharpe: 1.45
- Drawdown: 12%
- Trades: 45

Out-of-Sample (2024):
- Sharpe: 1.28
- Drawdown: 15%
- Trades: 38

Degradation: 11.7% (ACCEPTABLE ✅)

Decision: STRATEGY_COMPLETE
Status: Ready for deployment consideration
Phase: validation → complete
Iteration: 2

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

# Create tag for validated strategy
git tag -a v1.0.0-rsi-mean-reversion -m "Validated strategy - RSI Mean Reversion
Sharpe: 1.28 (OOS)
Validated: 2025-11-09"
```

#### 6. **Merge to Validated Strategies**

```bash
# After validation passes
git checkout -b validated-strategies/rsi-mean-reversion
git merge hypotheses/hypothesis-001-rsi-mean-reversion
git push origin validated-strategies/rsi-mean-reversion

# Create pull request for main branch
# (Requires human review before merging to main)
```

---

## Commit Message Format

### Standard Format

```
<phase>: <brief description>

<detailed information>
- Key metrics
- Parameters
- Results

Decision: <autonomous decision>
Reason: <decision rationale>
Phase: <from> → <to>
Iteration: <number>
[Backtest ID: <id>]
[Project ID: <id>]

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Phase Prefixes

- `research:` - Hypothesis creation
- `implement:` - Strategy implementation
- `backtest:` - Backtest execution
- `optimize:` - Parameter optimization
- `validate:` - Out-of-sample validation
- `fix:` - Bug fixes
- `refactor:` - Code improvements
- `docs:` - Documentation updates

---

## Git Integration with Slash Commands

### Automatic Commits

Every slash command commits state automatically:

| Command | Commits | Branch Action |
|---------|---------|---------------|
| `/qc-init` | iteration_state.json | Create hypothesis branch |
| `/qc-backtest` | backtest_results.json, iteration_state.json, decisions_log.md | Commit to current branch |
| `/qc-optimize` | optimization_results.json, test_strategy.py, iteration_state.json | Commit to current branch |
| `/qc-validate` | oos_results.json, iteration_state.json | Commit + tag if passed |
| `/qc-report` | strategy_report.md | Commit report |

### Manual Git Commands

Available for user control:

```bash
# Check status
git status

# View commit history
git log --oneline --graph

# Compare versions
git diff v1.0.0 v1.1.0

# Rollback to previous version
git checkout <commit-hash>

# Create experimental branch
git checkout -b experiment/aggressive-params
```

---

## Git Hooks for Validation

### Pre-Commit Hook

Automatically validates before each commit:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate iteration_state.json format
python -m json.tool iteration_state.json > /dev/null || exit 1

# Check for secrets in .env
if git diff --cached --name-only | grep -q ".env"; then
    echo "ERROR: Do not commit .env file"
    exit 1
fi

# Ensure test_strategy.py has no syntax errors
if [ -f test_strategy.py ]; then
    python -m py_compile test_strategy.py || exit 1
fi

echo "✅ Pre-commit validation passed"
```

### Post-Commit Hook

Automatically updates tracking after commit:

```bash
#!/bin/bash
# .git/hooks/post-commit

# Update iteration_state.json with latest commit hash
COMMIT_HASH=$(git rev-parse HEAD)
COMMIT_MSG=$(git log -1 --pretty=%B)

# Log commit to decisions_log.md
echo "Committed: $COMMIT_HASH - $COMMIT_MSG" >> git_history.log
```

---

## Rollback Scenarios

### Scenario 1: Bad Optimization

```bash
# Optimization made strategy worse
# Rollback to pre-optimization state

# Find commit before optimization
git log --oneline | grep "optimize:"

# Rollback
git reset --hard <commit-before-optimization>

# Or create new branch to try different params
git checkout -b optimization/alternative-params <commit-before-optimization>
```

### Scenario 2: Failed Validation

```bash
# Validation failed (high OOS degradation)
# Rollback to baseline strategy

git checkout <baseline-commit>
git checkout -b hypotheses/hypothesis-001-rsi-mean-reversion-v2
```

### Scenario 3: Bug Found After Deployment

```bash
# Critical bug found in live trading
# Immediately revert to previous version

git checkout main
git revert <problematic-commit>
git push origin main --force

# Or rollback to last known good version
git checkout v1.0.0
```

---

## Git Tags for Strategy Versions

### Tagging Strategy

```bash
# After successful validation
git tag -a v1.0.0 -m "Initial validated version
Sharpe: 1.28 (OOS)
Validated: 2025-11-09
Ready for paper trading"

# After optimization improvement
git tag -a v1.1.0 -m "Optimized parameters
Sharpe: 1.45 (OOS)
Improvement: 13% vs v1.0.0"

# After bug fix
git tag -a v1.0.1 -m "Fix: Stop loss calculation error"

# Push tags
git push origin --tags
```

### Tag Naming Convention

- `v1.0.0` - Major version (new strategy)
- `v1.1.0` - Minor version (optimization, improvement)
- `v1.0.1` - Patch version (bug fix)
- `v1.0.0-beta` - Pre-validation testing
- `v1.0.0-paper` - Paper trading phase

---

## Cost Tracking with Git

### Git as Cost Audit Trail

Each commit includes cost information:

```bash
git commit -m "backtest: Test alternative parameters

Results: Sharpe 0.95
Cost This Backtest: $0.00 (Free tier)
Total Session Cost: $0.00
API Calls: 8
Backtests Run: 3"
```

### Query Costs from Git History

```bash
# Total backtests run
git log --all --grep="backtest:" --oneline | wc -l

# Total optimizations
git log --all --grep="optimize:" --oneline | wc -l

# Extract cost data
git log --all --grep="Cost:" --pretty=format:"%s" | grep "Cost:"
```

---

## Collaboration Workflow

### Multi-Person Team

```bash
# Person A: Research & Implementation
git checkout -b hypotheses/hypothesis-005-volatility-breakout
# ... implement strategy ...
git commit -m "implement: Volatility breakout strategy"
git push origin hypotheses/hypothesis-005-volatility-breakout

# Person B: Review & Backtest
git checkout hypotheses/hypothesis-005-volatility-breakout
/qc-backtest
git commit -m "backtest: Initial results - Sharpe 1.2"
git push

# Person A: Optimize
git pull
/qc-optimize
git commit -m "optimize: Best params found"

# Person C: Validate
git pull
/qc-validate
git commit -m "validate: OOS passed, Sharpe 1.15"

# Merge to validated strategies
git checkout -b validated-strategies/volatility-breakout
git merge hypotheses/hypothesis-005-volatility-breakout
```

---

## Integration with iteration_state.json

### Git Metadata in State File

```json
{
  "git": {
    "current_branch": "hypotheses/hypothesis-001-rsi-mean-reversion",
    "latest_commit": "a1b2c3d4",
    "commits_this_iteration": 4,
    "tags": ["v1.0.0-beta"],
    "uncommitted_changes": false
  },

  "commit_history": [
    {
      "phase": "research",
      "commit": "a1b2c3d4",
      "timestamp": "2025-11-09T22:30:00Z",
      "message": "research: Initialize hypothesis"
    },
    {
      "phase": "implementation",
      "commit": "e5f6g7h8",
      "timestamp": "2025-11-09T22:35:00Z",
      "message": "implement: Create strategy"
    },
    {
      "phase": "backtest",
      "commit": "i9j0k1l2",
      "timestamp": "2025-11-09T22:45:00Z",
      "message": "backtest: Complete initial backtest"
    },
    {
      "phase": "validation",
      "commit": "m3n4o5p6",
      "timestamp": "2025-11-09T23:00:00Z",
      "message": "validate: OOS validation PASSED"
    }
  ]
}
```

---

## Best Practices

### DO:
- ✅ Commit after every phase transition
- ✅ Use descriptive commit messages with metrics
- ✅ Tag validated strategies
- ✅ Keep commits atomic (one logical change)
- ✅ Push regularly to remote
- ✅ Use branches for experiments
- ✅ Review diffs before committing

### DON'T:
- ❌ Commit .env files (credentials)
- ❌ Commit large data files (use .gitignore)
- ❌ Force push to main branch
- ❌ Commit without testing
- ❌ Mix multiple changes in one commit
- ❌ Commit directly to main (use branches)

---

## Emergency Recovery

### Lost Work Recovery

```bash
# Find lost commits (even after reset)
git reflog

# Recover specific commit
git checkout <commit-hash>

# Create branch from recovered commit
git checkout -b recovery/lost-work <commit-hash>
```

### Corrupted Repository

```bash
# Clone fresh copy
git clone <remote-url> recovery/
cd recovery/

# Cherry-pick recent work
git cherry-pick <commit1> <commit2> <commit3>
```

---

## Summary: Git is VITAL Because...

1. **Audit Trail**: Every decision documented and traceable
2. **Rollback**: Instantly undo failed experiments
3. **Collaboration**: Team can work on different hypotheses simultaneously
4. **Safety**: Branch strategy prevents contamination of validated code
5. **Compliance**: Required for regulatory audit in live trading
6. **Reproducibility**: Exact state of strategy at any point in time
7. **Cost Tracking**: Historical record of all API calls and backtests
8. **Knowledge Base**: Git history becomes strategy development encyclopedia

**Without git, the autonomous workflow lacks persistence, safety, and accountability.**

---

## Next: Implement Git Integration in Commands

See updated slash commands:
- `/qc-init` → Creates branch + initial commit
- `/qc-backtest` → Commits results automatically
- `/qc-optimize` → Commits best parameters
- `/qc-validate` → Commits + tags if validated
- `/qc-status` → Shows git status + branch info
