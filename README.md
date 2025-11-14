# QuantConnect Autonomous Strategy Development

**Goal**: Build a lean, self-documenting workflow enabling Claude Code to autonomously develop and validate QuantConnect trading strategies session-after-session.

**Critical**: Always use progressive disclosure - check `--help` before loading full docs. Context window is limited!

***Note***: When workflow is broken the priority is to fix the workflow not continue with iteration
---

## 🚀 Start Here (Run This FIRST!)

```bash
./BOOTSTRAP.sh
```

**This script provides everything you need at session start:**
- ✅ Current project status and next steps
- ✅ Available scripts with `--help` for progressive disclosure
- ✅ Available skills and slash commands
- ✅ Critical rules reminder

**Why BOOTSTRAP.sh?**
- Prevents information overload
- Enforces progressive disclosure pattern
- Shows `--help` commands for on-demand docs
- Context-efficient session initialization

**Alternative** (if script unavailable):
```bash
/current-status
# OR
cat PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/CURRENT_STATUS.md
```

---

## 🔑 Critical Rule

**NEVER create status/documentation files at root level.**

Only these files allowed at root:
- README.md (this file - points to real documentation)
- requirements.txt
- .env
- .gitignore

Everything else goes in PROJECT_DOCUMENTATION/

---

**Last Updated**: 2025-11-13
**Session Status**: `PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/CURRENT_STATUS.md`
**Workflow Status**: Use `/qc-status` for active hypothesis tracking
