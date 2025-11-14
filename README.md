# QuantConnect Autonomous Strategy Development

**Goal**: Build a lean, self-documenting workflow enabling Claude Code to autonomously develop and validate QuantConnect trading strategies session-after-session.

**Note 1**: This is a work in progress. We need to build redundancy so claude code does not get lost and can work autonomously without user intervention.

**Note 2**: Never load into context script or files without checking first --help. Context window is veruy limited and keeping it nimble is key to acomplish your session tasks and project goals.

---

## 🚀 Start Here

```bash
/qc-status
```

**Check current workflow status, phase, and next steps.**

This displays:
- Current hypothesis and phase
- Progress (iteration, backtests, cost)
- Recent decisions
- Next recommended actions

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
**Workflow Status**: Use `/qc-status` command
**State File**: `iteration_state.json` (managed by workflow)
