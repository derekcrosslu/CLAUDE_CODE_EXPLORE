# Comprehensive Next Steps & Timeline

**Date Created**: 2025-11-13
**Purpose**: Provide clear, consistent roadmap integrating progressive disclosure with workflow improvements
**Status**: Active Planning Document

---

## Executive Summary

**Current Situation**:
- ✅ Root directory cleaned (progressive disclosure enforced)
- ✅ Complete PREVIOUS_WORK archive restored (190K lines)
- ✅ Main branch updated with 70 workflow improvement commits
- ✅ Progressive disclosure pattern documented and started (quantconnect-optimization)
- ❌ Remaining workflow violations need fixing
- ❌ 6 skills still monolithic (not using progressive disclosure)
- ❌ Hypothesis directory structure not documented
- ❌ Session continuity still fragile

**Goal**: Establish lean, self-documenting workflow enabling Claude Code to work efficiently session-after-session without confusion or information overload.

**Core Principles**:
1. **Progressive Disclosure**: Load only what's needed (85-90% context reduction)
2. **CLI-First Architecture**: Humans, teams, AND agents can use the same tools
3. **Self-Propagating Documentation**: Patterns that teach themselves across sessions
4. **Phase Independence**: Each phase runs without depending on others
5. **Hypothesis Isolation**: Each hypothesis has complete, self-contained state

---

## Critical Issues Identified

### 1. Documentation Inconsistencies

**Problem**: Multiple sources of truth with conflicting information

**Examples**:
- CURRENT_STATE.md (Nov 9) says "Phase 2 Complete" but doesn't mention progressive disclosure
- IMPLEMENTATION_PROPOSAL.md describes progressive disclosure timeline
- Workflow reports identify 8 violations, 4 already fixed
- Hypothesis directory structure not standardized

**Impact**: Future Claude Code sessions will get confused by contradictory guidance

**Fix**: Create single source of truth (this document + updated status files)

---

### 2. Hypothesis Directory Structure

**Problem**: No documented standard for what each hypothesis directory should contain

**Current State** (observed from H5):
```
STRATEGIES/hypothesis_5_statistical_arbitrage/
├── iteration_state.json          # ✅ Present
├── config.json                    # ✅ Present
├── statistical_arbitrage.py      # ✅ Strategy file
├── research.ipynb                 # ✅ Validation notebook
├── optimization_params*.json      # ✅ Parameter files
├── optimization_results*.json     # ✅ Results
├── mc_validation_results.json     # ✅ Validation results
├── walkforward_config.json        # ✅ Config
├── *.csv files                    # ✅ Data files
├── validation_reports/            # ✅ Reports directory
├── stat_arb_report.md             # ✅ Documentation
└── VALIDATION_ANALYSIS.md         # ✅ Analysis
```

**Missing Standards**:
- No documented "required files" list
- No template for new hypothesis initialization
- No validation checklist
- No clear phase progression markers

**Fix**: Document standard hypothesis structure (Section 5)

---

### 3. Progressive Disclosure Not in Original Timeline

**Problem**: Original CURRENT_STATE.md doesn't mention progressive disclosure, but IMPLEMENTATION_PROPOSAL.md has complete 6-phase plan for it

**Timeline Conflict**:
- Original plan: Phase 3 = "Full Autonomy"
- New plan: Phase 1-6 = Progressive disclosure implementation
- No reconciliation between the two

**Fix**: Merge timelines into unified roadmap (Section 6)

---

## What's Been Completed (Session 2025-11-13)

### ✅ Root Directory Cleanup
- Moved 19 documentation files to PROJECT_DOCUMENTATION/
- Archived 4 old scripts to PREVIOUS_WORK/OLD_SCRIPTS_2025_11_13/
- Deleted 11 obsolete test/config files
- Root reduced from ~40 files to 16 items
- **Commit**: 9275e9e

### ✅ PREVIOUS_WORK Complete Restoration
- Restored 127 files (190,040 lines) from hypothesis-5 branch
- Preserved all historical documentation
- All Monte Carlo notebook iterations recovered
- Complete Lean Engine test data archive
- **Commit**: d2a66f7

### ✅ Workflow Consolidation
- Merged 70 workflow improvement commits from hypothesis branches
- All improvements now on main branch
- Complete git history preserved
- **Commit**: 203b4ca

### ✅ Progressive Disclosure Pattern Started
- Created PROGRESSIVE_DISCLOSURE_PATTERN.md (545 lines)
- Created PROGRESSIVE_DISCLOSURE_QUICKSTART.md (178 lines)
- Restructured quantconnect-optimization skill (582→211 lines, 64% reduction)
- Added CLI `docs` subcommand pattern
- **Commits**: dc437aa, c9bfe77, 2589bc7

### ✅ Workflow Violations Fixed (4 of 8)
- ✅ Violation #1: Template naming (iteration_state_template.json)
- ✅ Violation #2: qc-init.md "minimal" references
- ✅ Violation #6: qc-validate.md project creation timing
- ✅ Root directory progressive disclosure

---

## Remaining Work

### ❌ Violation #4: Script Dependencies (HIGH PRIORITY)
**Issue**: qc_optimize.py and qc_validate.py import from qc_backtest.py (violates phase independence)

**Solution**: Create shared SCRIPTS/qc_api.py module
- Extract QuantConnectAPI class to qc_api.py
- Update qc_backtest.py to import from qc_api.py
- Update qc_optimize.py to import from qc_api.py
- Update qc_validate.py to import from qc_api.py

**Benefit**: True phase independence, cleaner architecture

**Effort**: 30-45 minutes

---

### ❌ Violation #5: Monolithic Skills (HIGH PRIORITY)
**Issue**: 6 skills still using old monolithic approach (3322 total lines)

**Remaining Skills to Restructure**:
| Skill | Current Lines | Target Lines | Effort |
|-------|---------------|--------------|--------|
| backtesting-analysis | 554 | ~200 | 2 hours |
| quantconnect-validation | 463 | ~200 | 2 hours |
| quantconnect-backtest | 458 | ~200 | 2 hours |
| quantconnect | 174 | ~150 | 1 hour |
| project-timeline | 135 | ~100 | 1 hour |
| decision-framework | 122 | ~100 | 1 hour |

**Total Effort**: ~10 hours (2 full sessions)

**Pattern**: Follow PROGRESSIVE_DISCLOSURE_QUICKSTART.md checklist

---

## Recommended Execution Plan

### Phase 1: Immediate Fixes (Session 1 - Today/Tomorrow)
**Duration**: 2-3 hours
**Goal**: Fix remaining critical violations

**Tasks**:
1. ✅ Create this comprehensive next steps document (DONE)
2. **Fix Violation #4: Create qc_api.py module** (45 min)
   - Extract QuantConnectAPI to SCRIPTS/qc_api.py
   - Update all three scripts to import from qc_api
   - Test independence
   - Git commit

3. **Document Hypothesis Directory Structure** (30 min)
   - Create HYPOTHESIS_STRUCTURE_STANDARD.md
   - Define required files
   - Create initialization checklist
   - Document phase progression markers

4. **Update Status Documents** (30 min)
   - Update CURRENT_STATE.md with today's progress
   - Mark violations as fixed
   - Update decision log

**Deliverables**:
- [ ] qc_api.py module created
- [ ] All scripts using shared API client
- [ ] HYPOTHESIS_STRUCTURE_STANDARD.md created
- [ ] CURRENT_STATE.md updated
- [ ] All commits pushed to main

---

### Phase 2: Progressive Disclosure Completion (Sessions 2-3)
**Duration**: 2 sessions (6-8 hours total)
**Goal**: Apply progressive disclosure to all remaining skills

**Session 2A** (3-4 hours):
1. Restructure backtesting-analysis skill
2. Restructure quantconnect-validation skill
3. Restructure quantconnect-backtest skill

**Session 2B** (2-3 hours):
4. Restructure quantconnect skill
5. Restructure project-timeline skill
6. Restructure decision-framework skill

**Pattern for Each Skill**:
1. Create reference/ and examples/ directories
2. Extract detailed content to reference docs
3. Keep primer under 250 lines
4. Add `docs` subcommand to CLI tool
5. Test context reduction
6. Git commit

**Deliverables**:
- [ ] All 6 skills restructured
- [ ] 85-90% context reduction achieved
- [ ] CLI access to all reference docs
- [ ] Progressive disclosure self-propagation verified

---

### Phase 3: Workflow Validation (Session 4)
**Duration**: 1 session (3-4 hours)
**Goal**: Test complete workflow end-to-end

**Tasks**:
1. **Initialize New Hypothesis** (H7)
   - Use /qc-init to create new hypothesis
   - Verify directory structure matches standard
   - Validate iteration_state.json initialization

2. **Run Complete Cycle**
   - /qc-backtest → autonomous decision
   - /qc-optimize → if recommended
   - /qc-validate → Monte Carlo validation
   - /qc-report → final report

3. **Measure Context Usage**
   - Baseline (before progressive disclosure): 3322 lines
   - Target (after progressive disclosure): ~400 lines
   - Document actual savings

4. **Session Continuity Test**
   - Close session
   - Start new session
   - Continue from iteration_state.json
   - Verify no confusion/context issues

**Deliverables**:
- [ ] Complete H7 workflow tested
- [ ] Context reduction metrics documented
- [ ] Session continuity verified
- [ ] Workflow validation report created

---

### Phase 4: Documentation Consolidation (Session 5)
**Duration**: 1 session (2-3 hours)
**Goal**: Single source of truth for all workflow docs

**Tasks**:
1. **Consolidate Status Files**
   - Merge CURRENT_STATE.md with latest progress
   - Update EXECUTIVE_SUMMARY.md
   - Archive outdated versions to PREVIOUS_WORK

2. **Create Workflow Quick Reference**
   - One-page cheat sheet for Claude Code sessions
   - Key commands
   - Directory structure
   - Phase progression
   - Common troubleshooting

3. **Update README.md**
   - Clear project purpose
   - Quick start guide
   - Link to documentation structure
   - Progressive disclosure explanation

**Deliverables**:
- [ ] Single authoritative CURRENT_STATE.md
- [ ] WORKFLOW_QUICK_REFERENCE.md created
- [ ] README.md updated
- [ ] Documentation index created

---

## Hypothesis Directory Structure Standard

### Required Files

**Every hypothesis directory MUST contain**:

```
STRATEGIES/hypothesis_N_description/
├── iteration_state.json          # REQUIRED - Phase state tracking
├── config.json                    # REQUIRED - QC configuration
├── strategy_name.py               # REQUIRED - Main strategy file
├── optimization_params.json       # If Phase 4 reached
├── research.ipynb                 # If Phase 5 reached
└── README.md                      # REQUIRED - Hypothesis description
```

### Optional Files (Phase-Dependent)

**Phase 3 (Backtest)**:
- `backtest_results.json` - Initial backtest results
- `decision_log.md` - Decision history for this hypothesis

**Phase 4 (Optimization)**:
- `optimization_params_*.json` - Parameter grid variations
- `optimization_results_*.json` - Results from each run
- `optimization_summary.json` - Best parameters found

**Phase 5 (Validation)**:
- `mc_validation_results.json` - Monte Carlo results
- `walkforward_config.json` - WF configuration
- `VALIDATION_ANALYSIS.md` - Detailed analysis
- `validation_reports/` - HTML/PDF reports

**Data Files**:
- `*.csv` - Strategy-specific data files
- `*.json` - Additional config/results

### Phase Progression Markers

**iteration_state.json tracks**:
```json
{
  "hypothesis": {
    "id": 7,
    "name": "momentum-regime-filter",
    "status": "in_validation",  // Phase 5
    "current_phase": 5
  },
  "phases": {
    "phase_1_init": {"status": "completed", "date": "2025-11-14"},
    "phase_2_implementation": {"status": "completed"},
    "phase_3_backtest": {"status": "completed", "decision": "proceed_to_optimization"},
    "phase_4_optimization": {"status": "completed", "best_sharpe": 1.8},
    "phase_5_validation": {"status": "in_progress"}
  }
}
```

### Initialization Template

**When running /qc-init**:
1. Create hypothesis directory: `STRATEGIES/hypothesis_N_description/`
2. Copy iteration_state_template.json → iteration_state.json
3. Create config.json with QC API settings
4. Create README.md with hypothesis description
5. Set phase_1_init status to "completed"
6. Git commit: "init: Initialize hypothesis N - description"

---

## Unified Timeline (Merging Original + Progressive Disclosure)

### Week 1-2: Foundation & Phase Independence ✅ MOSTLY COMPLETE
- [x] Phase 1 Validation (original timeline) - API integration working
- [x] Root directory cleanup - Progressive disclosure enforced
- [x] PREVIOUS_WORK restoration - Historical context preserved
- [x] Progressive disclosure pattern documented
- [ ] **Remaining**: Fix script dependencies (Violation #4)
- [ ] **Remaining**: Document hypothesis structure standard

**Status**: 90% complete

---

### Week 3-4: Progressive Disclosure Implementation
- [ ] Apply pattern to 6 remaining skills
- [ ] Achieve 85-90% context reduction target
- [ ] Test CLI-first architecture with all tools
- [ ] Validate session-to-session continuity

**Dependencies**: Week 1-2 completion
**Effort**: 2 full sessions (10-12 hours)

---

### Week 5-6: Full Autonomy (Original Phase 3)
- [ ] /qc-auto-iterate master loop implementation
- [ ] Complete autonomous hypothesis iteration (2-3 per session)
- [ ] Advanced context management automation
- [ ] Cost tracking and limits
- [ ] Systematic failure detection

**Dependencies**: Week 3-4 completion
**Effort**: 2-3 sessions (12-15 hours)

---

### Week 7-8: Production Hardening
- [ ] Multi-hypothesis parallel testing
- [ ] Error recovery mechanisms
- [ ] Performance optimization
- [ ] Documentation finalization
- [ ] Team workflow testing

**Dependencies**: Week 5-6 completion
**Effort**: 2 sessions (8-10 hours)

---

## Success Criteria

### Phase 1 Success (Immediate)
- [x] Root directory has ≤10 essential files ✅
- [x] All documentation in PROJECT_DOCUMENTATION/ ✅
- [x] Complete PREVIOUS_WORK archive restored ✅
- [ ] Script dependencies fixed (qc_api.py created)
- [ ] Hypothesis structure documented

### Phase 2 Success (Progressive Disclosure)
- [ ] All 7 skills under 250 lines (primer only)
- [ ] Reference docs accessible via CLI `docs` command
- [ ] Context usage reduced to ~400 lines (from 3322)
- [ ] New session can continue work without confusion

### Phase 3 Success (Full Autonomy)
- [ ] Complete H7 cycle runs autonomously
- [ ] /qc-auto-iterate processes 2-3 hypotheses per session
- [ ] No manual intervention needed for standard flow
- [ ] Cost limits enforced automatically

### Phase 4 Success (Production)
- [ ] 5+ hypotheses tested successfully
- [ ] Session continuity works reliably
- [ ] Team members can use CLI tools
- [ ] Documentation is self-explanatory

---

## Critical Rules to Preserve (From Previous Sessions)

### 1. Project ID Management
**RULE**: NEVER accept project_id as CLI argument. ALWAYS read from iteration_state.json.

```python
# CORRECT:
state = json.load(open('iteration_state.json'))
project_id = state['project']['project_id']

# WRONG:
@click.option('--project-id', required=True)
```

**Why**: Single source of truth, prevents errors, enables session continuity

---

### 2. Phase Independence
**RULE**: Each script (qc_backtest.py, qc_optimize.py, qc_validate.py) must be self-contained.

**Why**: Removing one script shouldn't break others. Enables modular workflow.

**Implementation**: Shared qc_api.py module (NOT cross-imports)

---

### 3. Progressive Disclosure
**RULE**: Root directory contains ONLY:
- Essential files (README, requirements, .env, .gitignore)
- Top-level directories
- Optional convenience symlinks

**Why**: Reduces cognitive load, enforces information hierarchy

---

### 4. Git Workflow
**RULE**: Every phase transition = git commit

**Format**:
```
<type>: <subject>

<body with metrics>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Why**: Complete audit trail, rollback capability, collaboration support

---

### 5. Hypothesis Isolation
**RULE**: Each hypothesis has complete state in its own directory

**Why**: Parallel experimentation, clean separation, easy cleanup

---

## Files to Create/Update

### Create
- [ ] `PROJECT_DOCUMENTATION/CORE/SETUP/NEXT_STEPS/HYPOTHESIS_STRUCTURE_STANDARD.md`
- [ ] `SCRIPTS/qc_api.py` - Shared QuantConnect API client
- [ ] `PROJECT_DOCUMENTATION/WORKFLOW_QUICK_REFERENCE.md`
- [ ] `PROJECT_SCHEMAS/hypothesis_README_template.md`

### Update
- [ ] `PROJECT_DOCUMENTATION/CORE/SETUP/SESSION_STATUS/CURRENT_STATE.md` - Add today's progress
- [ ] `PROJECT_DOCUMENTATION/CORE/SETUP/SESSION_STATUS/decisions_log.md` - Log today's decisions
- [ ] `README.md` - Quick start and progressive disclosure explanation
- [ ] All 6 remaining skills (progressive disclosure restructure)

### Archive
- [ ] Old CURRENT_STATE.md (Nov 9) → PREVIOUS_WORK/ with context note

---

## Next Immediate Actions (User Decision Required)

### Option A: Fix Script Dependencies First (Recommended)
**Why**: High priority violation, enables true phase independence
**Time**: 45 minutes
**Impact**: Immediate architecture improvement

**Tasks**:
1. Create SCRIPTS/qc_api.py
2. Update 3 scripts to use it
3. Test each script independently
4. Git commit

### Option B: Complete Progressive Disclosure First
**Why**: Bigger context reduction impact
**Time**: 6-8 hours (2 sessions)
**Impact**: Major efficiency gain for future sessions

**Tasks**:
1. Restructure remaining 6 skills
2. Measure context reduction
3. Test session continuity

### Option C: Document Hypothesis Structure First
**Why**: Prevents future confusion, enables standardization
**Time**: 30 minutes
**Impact**: Clarity for all future hypothesis work

**Tasks**:
1. Create HYPOTHESIS_STRUCTURE_STANDARD.md
2. Document required files
3. Create initialization checklist

---

## Recommendation

**Suggested Order**:
1. **Option C** (30 min) - Document hypothesis structure NOW
2. **Option A** (45 min) - Fix script dependencies NEXT
3. **Update status** (15 min) - CURRENT_STATE.md + decisions_log.md
4. **Commit & push** (5 min)
5. **Option B** (Future sessions) - Progressive disclosure completion

**Total Time Today**: ~2 hours
**Deliverables**: 3 critical fixes, clear path forward

---

**Created By**: Claude (2025-11-13 session)
**Status**: Active Planning Document
**Next Review**: After Phase 1 completion
**Priority**: Foundation for all future work - DO NOT SKIP
