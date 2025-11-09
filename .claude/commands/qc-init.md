---
description: Initialize a new QuantConnect strategy development session
---

Initialize a new autonomous strategy development session with QuantConnect.

This command will:
1. Create a new hypothesis entry
2. Initialize iteration_state.json
3. Set up project structure
4. Create decisions_log.md
5. **Create git branch for hypothesis**
6. **Commit initial state to git**

**Usage**:
```
/qc-init
```

You will be prompted for:
- Hypothesis name
- Hypothesis description
- Strategy file path (optional, if already exists)
- Project name (optional, will reuse existing if found)

**What happens next**:
- iteration_state.json is created/updated with new hypothesis
- decisions_log.md is initialized
- QuantConnect project is checked (created if needed)
- Status is set to "research" phase

**Example**:
```
/qc-init
> Hypothesis name: MACD Momentum Strategy
> Description: Buy on MACD crossover with volume confirmation
> Strategy file: momentum_strategy.py
> Project name: MACD_Momentum_v1
```

**Output**:
- ✅ Hypothesis initialized
- 📊 iteration_state.json created
- 📝 decisions_log.md ready
- 🌿 Git branch created: hypotheses/hypothesis-XXX-<name>
- 💾 Initial commit made
- 🚀 Ready for implementation phase

---

## Git Integration (AUTOMATIC)

After creating state files, **automatically execute these git commands**:

```bash
# Get hypothesis ID and name from iteration_state.json
HYPOTHESIS_ID=$(cat iteration_state.json | grep '"id"' | head -1 | sed 's/[^0-9]*//g')
HYPOTHESIS_NAME=$(cat iteration_state.json | grep '"name"' | head -1 | sed 's/.*: "//;s/",//' | tr ' ' '-' | tr '[:upper:]' '[:lower:]')

# Create hypothesis branch
git checkout -b hypotheses/hypothesis-${HYPOTHESIS_ID}-${HYPOTHESIS_NAME}

# Add files
git add iteration_state.json decisions_log.md

# Commit with structured message
git commit -m "$(cat <<'EOF'
research: Initialize hypothesis - $(cat iteration_state.json | grep '"name"' | head -1 | sed 's/.*: "//;s/",//')

Hypothesis: $(cat iteration_state.json | grep '"description"' | head -1 | sed 's/.*: "//;s/",//')

Status: research → implementation
Iteration: 1
Phase: research

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# Confirm
echo "✅ Git branch created: $(git branch --show-current)"
echo "✅ Initial commit: $(git log -1 --oneline)"
```

**Important**: This git integration happens **automatically** - you don't need to run these commands manually.
