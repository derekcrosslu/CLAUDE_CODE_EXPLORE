#!/bin/bash
#
# BOOTSTRAP.sh - Session Initialization Script
#
# PURPOSE: Run this FIRST at the start of every Claude Code session
#
# This script provides:
# 1. Current project status and next steps
# 2. Available scripts with --help for progressive disclosure
# 3. Available skills and slash commands
# 4. Critical rules and constraints
#
# Usage: ./BOOTSTRAP.sh
#

set -e  # Exit on error

echo "=================================================="
echo "🚀 SESSION BOOTSTRAP - QuantConnect Project"
echo "=================================================="
echo ""

# ============================================================================
# 0. README.md
# ============================================================================

echo "README.md"
echo "=================================================="
echo ""

# ============================================================================
# 1. CURRENT STATUS
# ============================================================================

echo "📊 CURRENT STATUS & NEXT STEPS"
echo "=================================================="
echo ""

if [ -f "PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/CURRENT_STATUS.md" ]; then
    # Show first 100 lines of status (enough for overview)
    head -100 PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/CURRENT_STATUS.md
    echo ""
    echo "💡 Full status: cat PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/CURRENT_STATUS.md"
else
    echo "⚠️  CURRENT_STATUS.md not found!"
fi

echo ""
echo "=================================================="
echo ""

# ============================================================================
# 2. AVAILABLE SCRIPTS (with --help for progressive disclosure)
# ============================================================================

echo "📚 AVAILABLE SCRIPTS (Progressive Disclosure)"
echo "=================================================="
echo ""
echo "All scripts support --help for detailed documentation:"
echo ""

# List key scripts
scripts=(
    "SCRIPTS/qc_backtest.py:Phase 3 - Run backtests via QuantConnect API"
    "SCRIPTS/qc_optimize.py:Phase 4 - Parameter optimization"
    "SCRIPTS/qc_validate.py:Phase 5 - Walk-forward validation"
    "SCRIPTS/decision_logic.py:Decision framework and routing logic"
    "SCRIPTS/kalshi:Kalshi prediction market data (Fed, VIX, regime)"
)

for script_info in "${scripts[@]}"; do
    IFS=':' read -r script desc <<< "$script_info"
    if [ -f "$script" ]; then
        echo "✓ $script"
        echo "  Purpose: $desc"
        echo "  Help: python $script --help"
        echo "  Docs: python $script docs  (if supported)"
        echo ""
    else
        echo "✗ $script (not found)"
        echo ""
    fi
done

echo "💡 Run --help on any script to see reference documentation paths"
echo ""

# ============================================================================
# 3. AVAILABLE SKILLS
# ============================================================================

echo "=================================================="
echo "🔧 AVAILABLE SKILLS"
echo "=================================================="
echo ""

if [ -d ".claude/skills" ]; then
    echo "Load skills when needed for specific phases:"
    echo ""
    for skill_dir in .claude/skills/*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            skill_file="$skill_dir/skill.md"
            if [ -f "$skill_file" ]; then
                # Extract description from frontmatter
                desc=$(grep "^description:" "$skill_file" | cut -d':' -f2- | xargs)
                lines=$(wc -l < "$skill_file")
                echo "  - $skill_name ($lines lines)"
                echo "    $desc"
                echo ""
            fi
        fi
    done
else
    echo "⚠️  .claude/skills/ directory not found"
fi

echo ""

# ============================================================================
# 4. SLASH COMMANDS
# ============================================================================

echo "=================================================="
echo "⚡ SLASH COMMANDS"
echo "=================================================="
echo ""

if [ -d ".claude/commands" ]; then
    echo "Available workflow commands:"
    echo ""
    for cmd_file in .claude/commands/*.md; do
        if [ -f "$cmd_file" ]; then
            cmd_name=$(basename "$cmd_file" .md)
            # Try to extract description from first comment line
            first_line=$(head -1 "$cmd_file")
            echo "  /$cmd_name"
            if [[ $first_line == \<!--* ]]; then
                desc=$(echo "$first_line" | sed 's/<!--//;s/-->//')
                echo "    $desc"
            fi
            echo ""
        fi
    done
else
    echo "⚠️  .claude/commands/ directory not found"
fi

echo ""

# ============================================================================
# 5. FILE ORGANIZATION CHECK
# ============================================================================

echo "=================================================="
echo "🔍 FILE ORGANIZATION CHECK"
echo "=================================================="
echo ""

# Check for files at root (except allowed)
ALLOWED_PATTERN='^(README\.md|requirements\.txt|\.env|\.gitignore|BOOTSTRAP\.sh|STRATEGIES|SCRIPTS|PROJECT_DOCUMENTATION|PROJECT_SCHEMAS|PROJECT_LOGS|\.claude|\.git|venv|__pycache__)$'

echo "Checking for root-level violations..."
echo ""

VIOLATIONS=$(ls -1 2>/dev/null | grep -vE "$ALLOWED_PATTERN" || true)

if [ ! -z "$VIOLATIONS" ]; then
    echo "⚠️  WARNING: Files found at root level that may violate organization rules:"
    echo ""
    echo "$VIOLATIONS" | while read -r file; do
        echo "  - $file"
    done
    echo ""
    echo "📦 These should be moved to appropriate directories:"
    echo "   - Hypothesis files → STRATEGIES/hypothesis_X/"
    echo "   - Logs → PROJECT_LOGS/"
    echo "   - Docs → PROJECT_DOCUMENTATION/"
    echo ""
else
    echo "✅ Root directory is clean - no violations found"
    echo ""
fi

# Check for iteration_state.json at root (common mistake)
if [ -f "iteration_state.json" ]; then
    echo "❌ ERROR: iteration_state.json found at root!"
    echo "   This file MUST be in STRATEGIES/hypothesis_X/"
    echo "   Move it immediately to avoid workflow breakage"
    echo ""
fi

# Check for .py files at root (except allowed scripts in SCRIPTS/)
PY_FILES=$(ls -1 *.py 2>/dev/null || true)
if [ ! -z "$PY_FILES" ]; then
    echo "❌ ERROR: Python files found at root:"
    echo ""
    echo "$PY_FILES" | while read -r file; do
        echo "  - $file"
    done
    echo ""
    echo "   Strategy files MUST be in STRATEGIES/hypothesis_X/"
    echo "   Helper scripts MUST be in SCRIPTS/"
    echo ""
fi

# Check for optimization/validation result files at root
RESULT_FILES=$(ls -1 optimization_*.json oos_*.json backtest_result*.json 2>/dev/null || true)
if [ ! -z "$RESULT_FILES" ]; then
    echo "❌ ERROR: Result files found at root:"
    echo ""
    echo "$RESULT_FILES" | while read -r file; do
        echo "  - $file"
    done
    echo ""
    echo "   Result files MUST be in STRATEGIES/hypothesis_X/ or PROJECT_LOGS/"
    echo ""
fi

echo "=================================================="
echo ""

# ============================================================================
# 6. CRITICAL RULES
# ============================================================================

echo "=================================================="
echo "🔑 CRITICAL RULES (NEVER VIOLATE)"
echo "=================================================="
echo ""
echo "1. Root Directory:"
echo "   - ONLY README.md + requirements.txt + .env + .gitignore + BOOTSTRAP.sh + directories"
echo "   - NO status/docs files at root"
echo "   - NO strategy files (.py) at root"
echo "   - NO iteration_state.json at root"
echo ""
echo "2. Progressive Disclosure:"
echo "   - Load skill.md (primer only)"
echo "   - Use script --help for detailed docs"
echo "   - Use script docs <topic> for specific reference"
echo ""
echo "3. Project ID:"
echo "   - ALWAYS read from iteration_state.json"
echo "   - NEVER accept as CLI argument"
echo ""
echo "4. Git Workflow:"
echo "   - Every phase transition = git commit"
echo "   - Structured commit messages with metrics"
echo ""
echo "5. Context Management:"
echo "   - Check --help BEFORE loading full docs"
echo "   - Load reference docs only when needed"
echo "   - Context window is LIMITED - keep it nimble"
echo ""

# ============================================================================
# 7. NEXT ACTIONS
# ============================================================================

echo "=================================================="
echo "🎯 RECOMMENDED NEXT ACTIONS"
echo "=================================================="
echo ""
echo "Based on CURRENT_STATUS.md, your next steps are:"
echo ""

# Find hypothesis directory (if exists)
HYPOTHESIS_DIR=$(find STRATEGIES -maxdepth 1 -name "hypothesis_*" -type d 2>/dev/null | sort | tail -1 || true)

if [ -n "$HYPOTHESIS_DIR" ] && [ -f "${HYPOTHESIS_DIR}/iteration_state.json" ]; then
    current_phase=$(jq -r '.workflow_state.current_phase // .workflow.current_phase // "unknown"' "${HYPOTHESIS_DIR}/iteration_state.json" 2>/dev/null || echo "unknown")
    hypothesis_name=$(jq -r '.current_hypothesis.name // .hypothesis.name // "Unknown"' "${HYPOTHESIS_DIR}/iteration_state.json" 2>/dev/null || echo "Unknown")

    echo "Current Hypothesis: $hypothesis_name"
    echo "Hypothesis Directory: $HYPOTHESIS_DIR"
    echo "Current Phase: $current_phase"
    echo ""

    case "$current_phase" in
        "research")
            echo "→ Define hypothesis in ${HYPOTHESIS_DIR}/iteration_state.json"
            echo "→ Run /qc-init to initialize new hypothesis"
            ;;
        "implementation")
            echo "→ Generate strategy code in ${HYPOTHESIS_DIR}/"
            echo "→ Run /qc-backtest to test hypothesis"
            ;;
        "backtest")
            echo "→ Evaluate backtest results"
            echo "→ Make Phase 3 routing decision"
            ;;
        "optimization")
            echo "→ Run /qc-optimize to improve parameters"
            ;;
        "validation")
            echo "→ Run /qc-validate for walk-forward testing"
            ;;
        *)
            echo "→ Check CURRENT_STATUS.md for specific next steps"
            ;;
    esac
else
    echo "⚠️  No hypothesis directory found"
    echo "→ Run /qc-init to initialize new hypothesis"
    echo "→ Or check CURRENT_STATUS.md for current phase"
fi

echo ""

# ============================================================================
# 8. SUMMARY
# ============================================================================

echo "=================================================="
echo "✅ BOOTSTRAP COMPLETE"
echo "=================================================="
echo ""
echo "You now have:"
echo "  ✓ Current project status"
echo "  ✓ File organization check"
echo "  ✓ Available scripts with --help paths"
echo "  ✓ Available skills and commands"
echo "  ✓ Critical rules reminder"
echo ""
echo "💡 REMEMBER:"
echo "   - Use --help commands for progressive disclosure"
echo "   - Load skills only when needed for specific tasks"
echo "   - Keep context window nimble"
echo "   - ALL hypothesis files go in STRATEGIES/hypothesis_X/"
echo "   - NEVER create files at root (except allowed)"
echo ""
echo "🚀 Ready to continue work!"
echo ""
