# Quick Reference: Critical Violations Found

## Status Overview

**Total Violations Found**: 8  
**Critical**: 2 (fix immediately)  
**High**: 3 (fix this week)  
**Medium**: 3 (address soon)

---

## VIOLATION #1: Template Naming Confusion (CRITICAL)

**File**: `PROJECT_SCHEMAS/iteration_state_template_full.json`

**Problem**: 
- Name says "full" which implies "minimal" version exists
- But only ONE template exists (user requirement met, but confusing)

**Where it breaks documentation**:
- qc-init.md line 3: "Creates from **minimal template**"
- qc-init.md line 63: "Copy **full template**"
- Contradiction causes confusion about schema versioning

**Fix** (5 minutes):
```bash
# Rename file
mv PROJECT_SCHEMAS/iteration_state_template_full.json \
   PROJECT_SCHEMAS/iteration_state_template.json

# Update qc-init.md line 64:
# FROM: cp PROJECT_SCHEMAS/iteration_state_template_full.json
# TO:   cp PROJECT_SCHEMAS/iteration_state_template.json
```

---

## VIOLATION #2: "Minimal" Template Mentioned But Doesn't Exist (CRITICAL)

**File**: `.claude/commands/qc-init.md`

**Problem**: 
- Line 3: "Creates `iteration_state.json` from **minimal template**"
- Line 13: "Creates `iteration_state.json` from **minimal template**"
- Line 137: "The **minimal schema** is ~30 lines"
- Actual file is 76 lines, not 30 lines

**Why it matters**: 
- Users expect two templates (minimal/full)
- Only one actually exists
- Creates false expectations about schema complexity

**Fix** (15 minutes):
```markdown
# Line 3: Change FROM
"Creates `iteration_state.json` from minimal template (schema v1.0.0)"
# TO
"Creates `iteration_state.json` from template (schema v1.0.0)"

# Line 13: Same change

# Line 137: Change FROM
"The minimal schema is ~30 lines (sufficient for Phase 1-3)"
# TO
"The schema is ~76 lines (sufficient for all phases 1-5)"
```

---

## VIOLATION #3: No Progressive Disclosure for Strategy Templates (HIGH)

**Files**: 
- `.claude/skills/quantconnect/templates/mean_reversion_template.py` (202 lines)
- `.claude/skills/quantconnect/templates/momentum_template.py` (170 lines)

**Problem**: 
- Loading 202-line file just to change one RSI parameter (3 lines)
- 70% of work involves modifying indicators only
- Should load 15-20 line component, not 202-line template

**Progressive Disclosure Gap**:
- **Current**: Load mean_reversion_template.py (202 lines) → copy → modify 3 lines
- **Should be**: Load add_rsi.py (15 lines) → copy → modify

**Timeline**: 1-2 weeks (Phase 3 from IMPLEMENTATION_PROPOSAL.md)

---

## VIOLATION #4: Script Dependencies Violate Phase Independence (HIGH)

**Files**:
- `SCRIPTS/qc_optimize.py` - imports from qc_backtest.py
- `SCRIPTS/qc_validate.py` - imports from qc_backtest.py

**Problem**:
```python
# qc_optimize.py line 28
from qc_backtest import QuantConnectAPI  # VIOLATION

# Should have its own:
class QuantConnectAPI:
    """Independent API client for optimization"""
```

**Why it matters**: 
- Each phase should run independently
- Removing qc_backtest.py breaks qc_optimize.py and qc_validate.py
- Violates "phase independence" principle from WORKFLOW_CONSISTENCY_VERIFICATION.md

**Fix** (1-2 days):
- Add QuantConnectAPI class to qc_optimize.py
- Add QuantConnectAPI class to qc_validate.py
- Remove import from qc_backtest

---

## VIOLATION #5: Monolithic Skills (3322 lines total) (HIGH)

**All Skill Files**:
| Skill | Lines | When Needed |
|-------|-------|-------------|
| quantconnect-optimization | 582 | Only Phase 4 |
| quantconnect-validation | 463 | Only Phase 5 |
| backtesting-analysis | 554 | Only Phase 3 |
| quantconnect-backtest | 458 | Phase 2-3 |
| quantconnect | 174 | Phase 2 |
| decision-framework | 122 | After each phase |
| project-timeline | 135 | Phase tracking |
| **TOTAL** | **3322** | **Always loaded** |

**Problem**: 
- All skills loaded even if only using Phase 3 (backtest)
- Should load only ~150 lines per phase
- Goal: 85-90% context reduction (IMPLEMENTATION_PROPOSAL.md)

**Fix** (1 week):
- Create minimal skill primers (60-100 lines each)
- Replace monolithic skills with phase-specific loading
- Target: 300-400 lines total, not 3322

---

## VIOLATION #6: qc-validate.md Has Incorrect Project Reference (HIGH)

**File**: `.claude/commands/qc-validate.md`

**Problem**:
- Line 9: "Do NOT create a new project for validation"
- Line 117: "Validation runs on the SAME project created during **/qc-init**"
- **WRONG**: Project created in **/qc-backtest**, not /qc-init

**Correct Workflow**:
```
/qc-init     → Creates iteration_state.json (project_id = null)
/qc-backtest → Creates QC project, saves project_id
/qc-validate → Uses project_id from iteration_state.json
```

**Fix** (10 minutes):
```markdown
# Line 9: Change TO
"Uses project created during /qc-backtest"

# Line 117: Change FROM
"Validation runs on the SAME project created during /qc-init"
# TO
"Validation runs on the SAME project created during /qc-backtest"
```

---

## VIOLATION #7: Documentation Lacks Phase-Based Guidance (MEDIUM)

**Problem**: 
- Skills don't show which sections apply to which phases
- Users must read 458-582 lines to find relevant section
- No "Phase 3: Use this section" structure

**Example** (quantconnect-backtest/skill.md):
- 458 lines covering everything
- No sections like:
  - "## For Phase 2 (Implementation)"
  - "## For Phase 3 (Backtest Analysis)"

**Fix** (3-5 days):
- Restructure skill.md files by phase
- Add section headers for each phase
- Mark required vs. optional content per phase

---

## VIOLATION #8: Strategy Template Duplication (MEDIUM)

**Files**:
- `mean_reversion_template.py`: Contains 3 implementations
  - MeanReversionTemplate (basic)
  - RSIMeanReversion (RSI-only variant)
  - BollingerSqueeze (squeeze variant)

**Problem**: 
- Unclear which to use for new strategy
- Three different entry/exit patterns in one file
- Should be 3 separate templates

**Fix** (1 day):
```
mean_reversion_template.py → Simple mean reversion
rsi_mean_reversion_template.py → RSI variant
bollinger_squeeze_template.py → Squeeze variant
```

---

## Fix Priority Order

### Today (1-2 hours)
1. Rename `iteration_state_template_full.json` → `iteration_state_template.json`
2. Update qc-init.md lines 3, 13, 63, 137 (remove "minimal/full")
3. Fix qc-validate.md lines 9, 117 (fix project timing)

### This Week (3-5 days)
1. Fix qc_optimize.py and qc_validate.py dependencies
2. Create minimal skill primers
3. Delete redundant qc-walkforward.md
4. Add phase-based documentation structure

### Next 2 Weeks (Progressive Disclosure Implementation)
1. Break templates into components
2. Create strategy_component_cli.py
3. Implement phase-based skill loading
4. Achieve 85% context reduction goal

---

## Files to Create/Delete

### CREATE
- `PROJECT_DOCUMENTATION/TEMPLATE_USAGE.md` - Explain single template
- `PROJECT_DOCUMENTATION/PROGRESSIVE_DISCLOSURE_GUIDE.md` - Explain approach
- `SCRIPTS/strategy_components/indicators/add_rsi.py` (and others)
- `SCRIPTS/strategy_component_cli.py` - Component discovery CLI

### DELETE
- `.claude/commands/qc-walkforward.md` - Redundant with qc-validate

### RENAME
- `PROJECT_SCHEMAS/iteration_state_template_full.json` → `iteration_state_template.json`

### MODIFY
- `.claude/commands/qc-init.md` (remove minimal/full terminology)
- `.claude/commands/qc-validate.md` (fix project creation timing)
- `.claude/commands/qc-optimize.md` (fix script reference)
- All skill .md files (add phase-based structure)
- `SCRIPTS/qc_optimize.py` (add own API client)
- `SCRIPTS/qc_validate.py` (add own API client)

---

## Alignment with User Requirements

**User stated**: "ONLY ONE iteration_state template (no minimal/full split)"

**Current state**: ✅ Compliant (only 1 file exists)  
**But documentation**: ❌ Violates (mentions "minimal" version that doesn't exist)  
**Status**: **NEEDS IMMEDIATE FIX** (terminology confusion)

---

**Full analysis available in**:  
`PROJECT_DOCUMENTATION/WORKFLOW_CONSISTENCY_AND_PROGRESSIVE_DISCLOSURE_REPORT.md`

**Report generated**: 2025-11-13
