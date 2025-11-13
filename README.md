# QuantConnect Autonomous Strategy Development

**Goal**: Build a lean, self-documenting workflow enabling Claude Code to autonomously develop and validate QuantConnect trading strategies session-after-session.

**Current Phase**: Foundation & Cleanup (Phase 1) - 90% Complete

---

## 🚀 Quick Start (New Session)

### 1. Read Status First
```bash
cat CURRENT_STATUS.md
```
**This is the SINGLE source of truth** for current status and next steps.

### 2. Then Read Next Steps
```bash
cat PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/README.md
```
Quick reference for immediate actions.

### 3. Review Comprehensive Plan
```bash
cat PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/COMPREHENSIVE_NEXT_STEPS.md
```
Complete roadmap with timeline and execution plan.

---

## 📁 Project Organization

### Root Level (Minimal - Progressive Disclosure)
```
/
├── README.md              # This file - Quick orientation
├── CURRENT_STATUS.md      # ⭐ SINGLE SOURCE OF TRUTH
├── requirements.txt
├── .env
└── .gitignore
```

### Key Directories
```
├── .claude/
│   ├── commands/          # Workflow slash commands
│   └── skills/            # Progressive disclosure skills
│
├── SCRIPTS/               # Python CLI tools
├── STRATEGIES/            # Hypothesis directories (H4, H5, H6, etc.)
├── PROJECT_DOCUMENTATION/ # All documentation
│   └── CORE/SETUP/NEXT_STEPS/  # ⭐ START HERE
└── PROJECT_SCHEMAS/       # Templates and schemas
```

---

## 🎯 Current Status Summary

**Completed** (2025-11-13):
- ✅ Root directory cleaned (progressive disclosure enforced)
- ✅ Historical archive restored (PREVIOUS_WORK/ - 190K lines)
- ✅ 70 workflow commits consolidated to main
- ✅ Progressive disclosure pattern established
- ✅ 4 of 8 workflow violations fixed
- ✅ Hypothesis structure standard documented
- ✅ Single source of truth created

**Next Steps** (Immediate):
1. Fix script dependencies (create qc_api.py shared module) - 45 min
2. Update status document - 15 min
3. Progressive disclosure for 6 remaining skills - 10-12 hours

See `CURRENT_STATUS.md` for complete details.

---

## 📖 Core Principles

1. **Progressive Disclosure**: Load only what's needed (85-90% context reduction target)
2. **Phase Independence**: No cross-dependencies between scripts
3. **Single Source of Truth**: CURRENT_STATUS.md is THE reference
4. **Session Continuity**: Clear handoffs between sessions
5. **Hypothesis Isolation**: Each hypothesis fully self-contained

---

## 🔑 Critical Rules

These rules are NEVER violated:

1. **Project ID**: ALWAYS read from iteration_state.json, NEVER as CLI argument
2. **Phase Independence**: Scripts self-contained, use shared qc_api.py module
3. **Progressive Disclosure**: Root ≤10 files, details in subdirectories
4. **Git Workflow**: Every phase transition = git commit
5. **Hypothesis Isolation**: Complete state in hypothesis directory
6. **Single Source**: CURRENT_STATUS.md is authoritative

See `CURRENT_STATUS.md` → "Critical Rules" for details.

---

## 📋 Hypothesis Workflow

Each hypothesis follows a standardized 5-phase workflow:

1. **Phase 1: Initialization** - Create directory, setup files
2. **Phase 2: Implementation** - Code the strategy
3. **Phase 3: Backtest** - Test on QuantConnect, autonomous decision
4. **Phase 4: Optimization** - Parameter tuning (if recommended)
5. **Phase 5: Validation** - Monte Carlo validation with PSR, DSR, WFE

**Hypothesis Directory Structure**: See `PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/HYPOTHESIS_STRUCTURE_STANDARD.md`

**Example**: `STRATEGIES/hypothesis_5_statistical_arbitrage/` (complete reference)

---

## 🛠️ Key Tools

### Slash Commands (Claude Code)
```
/qc-init          Initialize new hypothesis
/qc-backtest      Run backtest with autonomous decision
/qc-optimize      Parameter optimization
/qc-validate      Monte Carlo validation
/qc-status        Check current status
```

### CLI Scripts (Python)
```bash
python SCRIPTS/qc_backtest.py --help
python SCRIPTS/qc_optimize.py --help
python SCRIPTS/qc_validate.py --help
```

All scripts support `--help` and `docs` subcommand for progressive disclosure.

---

## 📊 Progress Tracking

| Phase | Description | Status | % Complete |
|-------|-------------|--------|------------|
| Phase 1 | Foundation & Cleanup | In Progress | 90% |
| Phase 2 | Progressive Disclosure | Planned | 17% |
| Phase 3 | Workflow Validation | Planned | 0% |
| Phase 4 | Documentation Consolidation | Planned | 0% |

**Overall Progress**: 38% (9 of 24 tasks complete)

See `CURRENT_STATUS.md` for detailed breakdown.

---

## 🔗 Essential Documentation

### Status & Planning
- **CURRENT_STATUS.md** - ⭐ Start here (single source of truth)
- `PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/README.md` - Quick reference
- `PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/COMPREHENSIVE_NEXT_STEPS.md` - Full plan

### Standards & Patterns
- `PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/HYPOTHESIS_STRUCTURE_STANDARD.md`
- `PROJECT_DOCUMENTATION/CORE/SETUP/REQUIRED_STEPS/PROGRESSIVE_DISCLOSURE_PATTERN.md`
- `PROJECT_DOCUMENTATION/CORE/SETUP/REQUIRED_STEPS/PROGRESSIVE_DISCLOSURE_QUICKSTART.md`

### Historical Context
- `PROJECT_DOCUMENTATION/PREVIOUS_WORK/` - Archived documentation
- `PROJECT_DOCUMENTATION/PREVIOUS_WORK/backup-workflow-fixes-2025-11-13/` - Complete backup

---

## ⚠️ Important Notes

### For New Claude Code Sessions
1. **Always start** by reading `CURRENT_STATUS.md`
2. **Never read** archived documents in PREVIOUS_WORK/ (outdated)
3. **Update** CURRENT_STATUS.md after major task completion
4. **Follow** the progressive disclosure pattern for new skills

### For Hypothesis Work
1. **Reference**: `HYPOTHESIS_STRUCTURE_STANDARD.md` for required structure
2. **Use**: `iteration_state.json` as single source of truth for project_id
3. **Follow**: Phase progression markers in iteration_state.json
4. **Commit**: At each phase transition with proper format

---

## 🚦 Decision Points

### After Phase 1 Complete
- ✅ Continue to Phase 2 (progressive disclosure)
- ⚠️ If issues: Iterate on foundation
- ❌ If not viable: Reassess approach

### After Phase 2 Complete
- ✅ Continue to Phase 3 (workflow validation)
- Test full H7 cycle end-to-end
- Measure context reduction achieved

### After Phase 3 Complete
- ✅ Continue to Phase 4 (documentation)
- Consolidate to single source of truth
- Prepare for autonomous operation (Phase 3 from original plan)

---

## 📞 Quick Commands

```bash
# Check current status
cat CURRENT_STATUS.md

# View next steps
cat PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/README.md

# List hypotheses
ls -d STRATEGIES/hypothesis_*/

# Check skill sizes (progressive disclosure progress)
wc -l .claude/skills/*/skill.md

# View hypothesis structure standard
cat PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/HYPOTHESIS_STRUCTURE_STANDARD.md
```

---

## 📝 Recent Updates

**2025-11-13**:
- Established single source of truth (CURRENT_STATUS.md)
- Completed root directory cleanup
- Restored complete PREVIOUS_WORK archive
- Created comprehensive planning documents
- Fixed 4 of 8 workflow violations
- Restructured first skill with progressive disclosure

**Next**: Fix script dependencies, then progressive disclosure for remaining skills

---

## 📄 License

Educational and research purposes. Code examples provided as-is.

---

**Last Updated**: 2025-11-13
**Status**: Active Development - Phase 1 (Foundation)
**Maintainer**: Donald Cross
**Single Source of Truth**: `CURRENT_STATUS.md` ⭐
