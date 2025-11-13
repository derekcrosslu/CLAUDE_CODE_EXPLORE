# Root Directory Cleanup - TODO

**Date Created**: 2025-11-13
**Date Completed**: 2025-11-13
**Priority**: MEDIUM
**Status**: ✅ COMPLETED
**Actual Time**: 15 minutes
**Commit**: 9275e9e

---

## Problem

Root directory is polluted with ~40 files that violate progressive disclosure principles:
- Documentation files (should be in PROJECT_DOCUMENTATION/)
- Old script versions (duplicates of SCRIPTS/ files)
- Test files and obsolete configs
- Symlinks/aliases in wrong location

---

## Progressive Disclosure Violation

**Rule**: Root directory should contain ONLY:
- README.md
- requirements.txt
- .env
- .gitignore
- Potentially: LICENSE, CONTRIBUTING.md

**Current State**: 40+ files in root (massive pollution)

---

## Audit Results (2025-11-13)

### Duplicates Found

| Root File | SCRIPTS/ Version | Status |
|-----------|------------------|--------|
| qc_backtest.py (770 lines) | SCRIPTS/qc_backtest.py (859 lines) | SCRIPTS is NEWER ✅ |
| qc_optimize_wrapper.py (12K) | SCRIPTS/qc_optimize.py (13K) | SCRIPTS is NEWER ✅ |
| qc_walkforward_wrapper.py (21K) | SCRIPTS/qc_validate.py (34K) | SCRIPTS is NEWER ✅ |

**Action**: Delete root versions, keep SCRIPTS/ versions

### Documentation Files to Move

Move to `PROJECT_DOCUMENTATION/CORE/`:
- agent_based_architecture.md (60K)
- autonomous_decision_framework.md (26K)
- autonomous_workflow_architecture.md (13K)
- claude_code_capabilities_mapping.md (21K)
- context_management_playbook.md (22K)
- GIT_WORKFLOW_STRATEGY.md (14K)
- MCP_INTEGRATION.md (7K)
- MCP_TOOLS_VERIFIED.md (5K)
- required_customizations.md (25K)

Move to `PROJECT_DOCUMENTATION/STRATEGIES/`:
- STRATEGY_README.md (6K)
- WALKFORWARD_README.md (7K)

Move to `PROJECT_DOCUMENTATION/SETUP/`:
- SETUP_GUIDE.md (4K)
- QC_OPTIMIZATION_LIMITATION.md (8K)

Move to `PROJECT_DOCUMENTATION/SESSION_STATUS/`:
- SESSION_OBJECTIVE.md (3K)
- EXECUTIVE_SUMMARY.md (19K)
- CURRENT_STATE.md (11K)
- PHASE1_VALIDATION_COMPLETE.md (11K)
- WEEK1_PROGRESS.md (7K)
- decisions_log.md (15K)

### Files to Delete (Obsolete/Test)

**Test files**:
- test_api.py
- test_opt_debug.py
- test_strategy.py

**Old configs/results**:
- backtest_full_results.json
- backtest_results.json
- baseline_backtest_20251109_190550.json
- phase1_validation_results.json
- optimization_params.json
- walkforward_config.json
- qc_guide.json
- iteration_state.json (belongs in hypothesis dirs only)

**Old notebook**:
- monte_carlo_walkforward.ipynb (move to PREVIOUS_WORK if needed)

### Symlinks/Aliases to Review

Current root level:
- component (symlink to SCRIPTS/component?)
- qc_optimize (symlink to SCRIPTS/qc_optimize?)
- qc_validate (symlink to SCRIPTS/qc_validate?)
- .timeline_alias.sh

**Decision needed**: Keep symlinks in root for convenience OR move to SCRIPTS/ only?

---

## Cleanup Plan

### Phase 1: Create Target Directories (5 min)

```bash
mkdir -p PROJECT_DOCUMENTATION/CORE
mkdir -p PROJECT_DOCUMENTATION/STRATEGIES
mkdir -p PROJECT_DOCUMENTATION/SETUP
mkdir -p PROJECT_DOCUMENTATION/SESSION_STATUS
```

### Phase 2: Move Documentation (15 min)

```bash
# Core architecture docs
mv agent_based_architecture.md PROJECT_DOCUMENTATION/CORE/
mv autonomous_decision_framework.md PROJECT_DOCUMENTATION/CORE/
mv autonomous_workflow_architecture.md PROJECT_DOCUMENTATION/CORE/
mv claude_code_capabilities_mapping.md PROJECT_DOCUMENTATION/CORE/
mv context_management_playbook.md PROJECT_DOCUMENTATION/CORE/
mv GIT_WORKFLOW_STRATEGY.md PROJECT_DOCUMENTATION/CORE/
mv MCP_INTEGRATION.md PROJECT_DOCUMENTATION/CORE/
mv MCP_TOOLS_VERIFIED.md PROJECT_DOCUMENTATION/CORE/
mv required_customizations.md PROJECT_DOCUMENTATION/CORE/

# Strategy docs
mv STRATEGY_README.md PROJECT_DOCUMENTATION/STRATEGIES/
mv WALKFORWARD_README.md PROJECT_DOCUMENTATION/STRATEGIES/

# Setup docs
mv SETUP_GUIDE.md PROJECT_DOCUMENTATION/SETUP/
mv QC_OPTIMIZATION_LIMITATION.md PROJECT_DOCUMENTATION/SETUP/

# Session status docs
mv SESSION_OBJECTIVE.md PROJECT_DOCUMENTATION/SESSION_STATUS/
mv EXECUTIVE_SUMMARY.md PROJECT_DOCUMENTATION/SESSION_STATUS/
mv CURRENT_STATE.md PROJECT_DOCUMENTATION/SESSION_STATUS/
mv PHASE1_VALIDATION_COMPLETE.md PROJECT_DOCUMENTATION/SESSION_STATUS/
mv WEEK1_PROGRESS.md PROJECT_DOCUMENTATION/SESSION_STATUS/
mv decisions_log.md PROJECT_DOCUMENTATION/SESSION_STATUS/
```

### Phase 3: Archive Old Scripts (10 min)

```bash
mkdir -p PREVIOUS_WORK/OLD_SCRIPTS_2025_11_13

# Move old duplicates
mv qc_backtest.py PREVIOUS_WORK/OLD_SCRIPTS_2025_11_13/
mv qc_optimize_wrapper.py PREVIOUS_WORK/OLD_SCRIPTS_2025_11_13/
mv qc_walkforward_wrapper.py PREVIOUS_WORK/OLD_SCRIPTS_2025_11_13/

# Move old notebook
mv monte_carlo_walkforward.ipynb PREVIOUS_WORK/OLD_SCRIPTS_2025_11_13/
```

### Phase 4: Delete Obsolete Files (5 min)

```bash
# Test files
rm test_api.py test_opt_debug.py test_strategy.py

# Old results/configs
rm backtest_full_results.json backtest_results.json
rm baseline_backtest_20251109_190550.json phase1_validation_results.json
rm optimization_params.json walkforward_config.json qc_guide.json
rm iteration_state.json
```

### Phase 5: Review Symlinks (10 min)

**Option A**: Keep convenience symlinks in root
```bash
# Verify they work
./component --help
./qc_optimize --help
./qc_validate --help
```

**Option B**: Remove symlinks, use SCRIPTS/ only
```bash
rm component qc_optimize qc_validate .timeline_alias.sh
# Update documentation to reference SCRIPTS/ directly
```

**Decision**: TBD in cleanup session

### Phase 6: Verify & Commit (15 min)

```bash
# Verify root is clean
ls -la | grep -v "^\." | wc -l  # Should be ~8-10 files max

# Verify all files accessible
ls PROJECT_DOCUMENTATION/CORE/
ls PROJECT_DOCUMENTATION/STRATEGIES/
ls PROJECT_DOCUMENTATION/SETUP/
ls PROJECT_DOCUMENTATION/SESSION_STATUS/

# Git commit
git add -A
git commit -m "chore: Clean root directory per progressive disclosure rules

Moved 19 documentation files to PROJECT_DOCUMENTATION/
Archived 4 old script versions to PREVIOUS_WORK/
Deleted 13 obsolete test/config files

Root directory now contains only:
- README.md, requirements.txt, .env, .gitignore
- Symlinks (optional, TBD)

Aligns with progressive disclosure principle:
'Root should be minimal, details in subdirectories'
"
```

---

## Root Directory Target State

**After cleanup** (8-10 files):
```
/
├── .env
├── .gitignore
├── README.md
├── requirements.txt
├── .claude/           (skill files)
├── PROJECT_DOCUMENTATION/
├── PROJECT_SCHEMAS/
├── SCRIPTS/
├── STRATEGIES/
└── [optional symlinks: component, qc_optimize, qc_validate]
```

---

## Risks & Mitigations

### Risk 1: Deleting needed files
**Mitigation**: Archive (don't delete) old scripts to PREVIOUS_WORK/

### Risk 2: Breaking references
**Mitigation**: Search for imports before moving:
```bash
grep -r "import autonomous_workflow_architecture" .
grep -r "from autonomous_decision_framework" .
```

### Risk 3: Git conflicts
**Mitigation**: Do cleanup on main branch after all work merged

---

## Success Criteria

- ✅ Root directory has ≤10 files
- ✅ All documentation in PROJECT_DOCUMENTATION/
- ✅ No duplicate scripts (root vs SCRIPTS/)
- ✅ No test files or old configs in root
- ✅ Git history preserved (moves, not deletions)
- ✅ All functionality still works

---

## Future Session Checklist

When ready to execute cleanup:

- [ ] Ensure on main branch, all work committed
- [ ] Run Phase 1: Create directories
- [ ] Run Phase 2: Move documentation
- [ ] Run Phase 3: Archive old scripts
- [ ] Run Phase 4: Delete obsolete files
- [ ] Run Phase 5: Review symlinks (decide keep/remove)
- [ ] Run Phase 6: Verify and commit
- [ ] Test: Ensure workflows still work
- [ ] Push to remote

**Estimated time**: 1 hour (manual execution)

---

## Related Documentation

- **Progressive Disclosure Pattern**: `PROJECT_DOCUMENTATION/PROGRESSIVE_DISCLOSURE_PATTERN.md`
- **Documentation Standards**: `PROJECT_DOCUMENTATION/documentation_standards.md` (if exists)
- **Workflow Reports**: `PROJECT_DOCUMENTATION/WORKFLOW_CONSISTENCY_AND_PROGRESSIVE_DISCLOSURE_REPORT.md`

---

**Created By**: Claude (2025-11-13 session)
**Status**: Ready for execution in future session
**Priority**: Clean root = better progressive disclosure compliance
