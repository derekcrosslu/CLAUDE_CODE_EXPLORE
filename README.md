# QuantConnect Autonomous Strategy Development

**Goal**: Build a lean, self-documenting workflow enabling Claude Code to autonomously develop and validate QuantConnect trading strategies session-after-session.

---

## 🚀 Quick Start

### For New Sessions (Claude Code or Human)

```bash
# Read this FIRST - Single source of truth
cat CURRENT_STATUS.md
```

**That's it.** Everything you need is in `CURRENT_STATUS.md`:
- Current phase and progress
- What's been completed
- What needs to be done next
- Project structure
- Critical rules
- Where to find everything

---

## 📋 Core Principles

1. **Progressive Disclosure** - Load only what's needed (85-90% context reduction)
2. **Phase Independence** - No cross-dependencies between scripts
3. **Single Source of Truth** - `CURRENT_STATUS.md` is THE reference
4. **Session Continuity** - Clear handoffs between sessions
5. **Hypothesis Isolation** - Each hypothesis fully self-contained

---

## 🔑 Critical Rules (Never Violate)

1. **Project ID**: ALWAYS read from iteration_state.json, NEVER as CLI argument
2. **Phase Independence**: Scripts self-contained, use shared qc_api.py
3. **Progressive Disclosure**: Root ≤10 files, details in subdirectories
4. **Git Workflow**: Every phase transition = git commit
5. **Hypothesis Isolation**: Complete state in hypothesis directory
6. **Single Source**: `CURRENT_STATUS.md` is authoritative

---

## 📁 Quick Navigation

```
/
├── README.md              # This file
├── CURRENT_STATUS.md      # ⭐ START HERE - Single source of truth
│
├── .claude/skills/        # Progressive disclosure skills
├── SCRIPTS/               # Python CLI tools
├── STRATEGIES/            # Hypothesis directories (H4, H5, H6, etc.)
│
└── PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/
    ├── README.md                          # Quick reference
    ├── COMPREHENSIVE_NEXT_STEPS.md        # Full roadmap
    └── HYPOTHESIS_STRUCTURE_STANDARD.md   # Required structure
```

---

**Status**: Active Development - Phase 1 (Foundation) - 90% Complete

**Next**: Fix script dependencies → Progressive disclosure for 6 skills → End-to-end validation

**Last Updated**: 2025-11-13

⭐ **Always start with `CURRENT_STATUS.md`** ⭐
