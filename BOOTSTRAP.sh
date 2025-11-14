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
# 5. CRITICAL RULES
# ============================================================================

echo "=================================================="
echo "🔑 CRITICAL RULES (NEVER VIOLATE)"
echo "=================================================="
echo ""
echo "1. Root Directory:"
echo "   - ONLY README.md + requirements.txt + .env + .gitignore + BOOTSTRAP.sh + directories"
echo "   - NO status/docs files at root"
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
# 6. NEXT ACTIONS
# ============================================================================

echo "=================================================="
echo "🎯 RECOMMENDED NEXT ACTIONS"
echo "=================================================="
echo ""
echo "Based on CURRENT_STATUS.md, your next steps are:"
echo ""

if [ -f "iteration_state.json" ]; then
    current_phase=$(jq -r '.workflow.current_phase // "unknown"' iteration_state.json 2>/dev/null || echo "unknown")
    echo "Current Phase: $current_phase"
    echo ""

    case "$current_phase" in
        "research")
            echo "→ Define hypothesis in iteration_state.json"
            echo "→ Run /qc-init to initialize new hypothesis"
            ;;
        "implementation")
            echo "→ Generate strategy code"
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
    echo "⚠️  iteration_state.json not found"
    echo "→ Check CURRENT_STATUS.md for initialization steps"
fi

echo ""

# ============================================================================
# 7. SUMMARY
# ============================================================================

echo "=================================================="
echo "✅ BOOTSTRAP COMPLETE"
echo "=================================================="
echo ""
echo "You now have:"
echo "  ✓ Current project status"
echo "  ✓ Available scripts with --help paths"
echo "  ✓ Available skills and commands"
echo "  ✓ Critical rules reminder"
echo ""
echo "💡 REMEMBER:"
echo "   - Use --help commands for progressive disclosure"
echo "   - Load skills only when needed for specific tasks"
echo "   - Keep context window nimble"
echo ""
echo "🚀 Ready to continue work!"
echo ""
