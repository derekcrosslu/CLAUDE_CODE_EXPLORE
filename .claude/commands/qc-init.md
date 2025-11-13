---
description: Initialize a new QuantConnect strategy development session (project)
---

Initialize a new autonomous hypothesis testing session for algorithmic strategy development.

This command implements Phase 1 of the 5-phase autonomous workflow.

## What This Command Does

1. Prompts for hypothesis details (name, description, rationale)
2. Generates unique hypothesis ID (auto-increment based on existing branches)
3. Creates `iteration_state.json` from template (schema v1.0.0)
4. Populates workflow metadata (session_id, timestamps)
5. Sets autonomy mode (default: minimal, requires user approval at each phase)
6. Loads default thresholds from config or uses defaults
7. Creates git branch: `hypotheses/hypothesis-{id}-{name-slug}`
8. Makes initial commit with structured message
9. Sets next_action to `/qc-backtest`

## Usage

```bash
/qc-init
```

You will be prompted for:
- **Hypothesis name**: Short descriptive name (e.g., "RSI Mean Reversion")
- **Hypothesis description**: One-line description of the strategy
- **Hypothesis rationale**: Why you think this will work (market regime, theory, etc.)

## Implementation Steps

When this command is executed, perform these steps:

### Step 1: Gather Hypothesis Information

**⚠️ AUTONOMOUS MODE: DO NOT ASK USER UNLESS BLOCKER**

If command has arguments (e.g., `/qc-init path/to/strategy.py`):
- Extract hypothesis details from code comments/docstrings
- Auto-generate name from filename
- Proceed autonomously

If command has NO arguments:
- **ONLY THEN** ask user for:
  1. **Hypothesis Name** (required)
  2. **Hypothesis Description** (required)
  3. **Hypothesis Rationale** (required)

### Step 2: Generate Hypothesis ID

```bash
# Find highest existing hypothesis ID from git branches
HIGHEST_ID=$(git branch -a | grep 'hypotheses/hypothesis-' | sed 's/.*hypothesis-//; s/-.*//' | sort -n | tail -1)
NEW_ID=$((HIGHEST_ID + 1))
echo "Generated Hypothesis ID: $NEW_ID"
```

### Step 3: Create iteration_state.json

```bash
# Copy template (includes all phase structures: backtest, optimization, validation)
cp PROJECT_SCHEMAS/iteration_state_template.json iteration_state.json

# Populate fields using jq or manual sed/awk
SESSION_ID=$(uuidgen | tr '[:upper:]' '[:lower:]')
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
HYPOTHESIS_NAME="<user input>"
HYPOTHESIS_DESC="<user input>"
HYPOTHESIS_RATIONALE="<user input>"

# Update iteration_state.json with actual values:
# - workflow.session_id = $SESSION_ID
# - workflow.created_at = $TIMESTAMP
# - workflow.updated_at = $TIMESTAMP
# - hypothesis.id = $NEW_ID
# - hypothesis.name = $HYPOTHESIS_NAME
# - hypothesis.description = $HYPOTHESIS_DESC
# - hypothesis.rationale = $HYPOTHESIS_RATIONALE
# - hypothesis.created = $TIMESTAMP
```

### Step 4: Create Git Branch

```bash
# Create branch name (slugify hypothesis name)
BRANCH_NAME="hypotheses/hypothesis-${NEW_ID}-$(echo "$HYPOTHESIS_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | sed 's/[^a-z0-9-]//g')"

# Create and checkout branch
git checkout -b "$BRANCH_NAME"

# Update git.branch in iteration_state.json
# git.branch = $BRANCH_NAME
```

### Step 5: Initial Commit

```bash
# Stage files
git add iteration_state.json

# Commit with structured message
git commit -m "research: Initialize hypothesis - ${HYPOTHESIS_NAME}

Hypothesis: ${HYPOTHESIS_DESC}

Rationale: ${HYPOTHESIS_RATIONALE}

Status: research → implementation
Iteration: 1
Phase: research

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 6: Confirm Success

Display summary:
```
✅ Hypothesis initialized successfully!

Hypothesis ID: {id}
Name: {name}
Branch: {branch_name}

iteration_state.json created with schema v1.0.0
Current phase: research
Next action: /qc-backtest

Ready to implement strategy!
```

## Notes

- The schema includes all phase structures (backtest, optimization, validation)
- Thresholds use defaults unless overridden
- Autonomy mode defaults to "minimal" (user approval at each phase)
- Git integration is automatic and mandatory
- session_id is generated using UUID for uniqueness

## Next Steps

After initialization:
1. Implement the strategy code (Python algorithm)
2. Run `/qc-backtest` to test the hypothesis
