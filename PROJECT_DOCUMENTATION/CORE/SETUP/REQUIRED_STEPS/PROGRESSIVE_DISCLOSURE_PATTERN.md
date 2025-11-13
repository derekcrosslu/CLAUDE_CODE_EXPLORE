# Progressive Disclosure Pattern: Skill Restructuring Guide

**Date**: 2025-11-13
**Status**: FOUNDATIONAL PATTERN - Apply to all future skills
**Goal**: 85-90% context reduction while preserving ALL information

---

## Executive Summary

This document establishes the **progressive disclosure pattern** for skill file restructuring. This pattern ensures:

1. **ALL information preserved** - Nothing is deleted, only reorganized
2. **Hierarchical access** - Load what you need, when you need it
3. **CLI-first interface** - Unified access via `--help` and `docs` subcommand
4. **Self-evident structure** - Future sessions can apply pattern without rereading full docs

---

## Core Principle

> **"Load only what's relevant at each phase; minimize context consumption by 85-90%"**
> — IMPLEMENTATION_PROPOSAL.md

**Key Rule**: Information is ORGANIZED, not REMOVED.

---

## Three-Level Hierarchy

### Level 1: Skill Primer (Always Loaded)
**Target**: 150-250 lines
**File**: `.claude/skills/<skill-name>/skill.md`

**Must Include**:
- Critical constraints (rules that MUST be followed)
- CLI commands for accessing the skill functionality
- Quick start guide (minimal example)
- Common issues (top 3-5 problems)
- Documentation rules (PROJECT_LOGS/, naming conventions, etc.)
- Pointers to Level 2 references (via CLI `docs` command)
- Authorization: "Use `<script>.py --help`, not source code"

**Must NOT Include**:
- Detailed implementation code
- Exhaustive troubleshooting guides
- Multiple examples
- Step-by-step tutorials
- Verbose explanations

### Level 2: Reference Documentation (Load On-Demand)
**Location**: `.claude/skills/<skill-name>/reference/*.md`

**Accessed Via**: `<script>.py docs <topic>`

**Contains**:
- Detailed implementation guides
- Complete troubleshooting documentation
- Decision logic and thresholds
- Methodology explanations
- Advanced configurations
- Best practices

**Organized by topic** - one file per logical grouping.

### Level 3: Examples (Load When Needed)
**Location**: `.claude/skills/<skill-name>/examples/*`

**Contains**:
- Specific use cases
- Copy-paste templates
- Complete workflow examples
- JSON configuration samples

---

## CLI Integration Pattern

Every CLI script must have:

### 1. Enhanced `--help` Output

```python
@click.group()
def cli():
    """<Brief description>

    <Phase info>

    \b
    REFERENCE DOCUMENTATION (Progressive Disclosure):
      .claude/skills/<skill-name>/reference/
        ├── <topic-1>.md - Description
        ├── <topic-2>.md - Description
        ├── <topic-3>.md - Description
        └── <topic-n>.md - Description

    Load reference docs on-demand when needed.
    """
    pass
```

**The `\b` marker** prevents Click from reformatting the documentation tree structure.

### 2. `docs` Subcommand

```python
@cli.command()
@click.argument('topic', required=False)
def docs(topic: str):
    """Show reference documentation (progressive disclosure).

    Usage:
        <script>.py docs                 # List all available docs
        <script>.py docs <topic>         # Show specific doc

    Available topics:
        <topic-1>    - Description
        <topic-2>    - Description
        <topic-n>    - Description
    """
    import os
    from pathlib import Path

    # Reference documentation directory
    ref_dir = Path(SCRIPT_DIR).parent / '.claude/skills/<skill-name>/reference'

    # Map topics to files
    docs_map = {
        '<topic-1>': '<file-1>.md',
        '<topic-2>': '<file-2>.md',
    }

    if not topic:
        # List all available docs
        click.echo("📚 Available Reference Documentation:\n")
        for topic_name, filename in docs_map.items():
            doc_path = ref_dir / filename
            status = "✓" if doc_path.exists() else "✗"
            click.echo(f"  {status} {topic_name:25} → {filename}")

        click.echo(f"\n📂 Reference directory: {ref_dir}")
        click.echo("\nUsage: <script>.py docs <topic>")
        return

    # Show specific doc
    if topic not in docs_map:
        click.echo(f"❌ Unknown topic: {topic}", err=True)
        click.echo(f"\nAvailable topics: {', '.join(docs_map.keys())}", err=True)
        sys.exit(1)

    doc_path = ref_dir / docs_map[topic]

    if not doc_path.exists():
        click.echo(f"❌ Documentation not found: {doc_path}", err=True)
        sys.exit(1)

    # Display the doc
    with open(doc_path, 'r') as f:
        content = f.read()

    click.echo(content)
```

---

## Example: quantconnect-optimization Restructure

### Before (Monolithic)
```
.claude/skills/quantconnect-optimization/
└── skill.md (582 lines - everything in one file)
```

**Problem**: 582 lines loaded every time, even when only need 20 lines.

### After (Progressive Disclosure)
```
.claude/skills/quantconnect-optimization/
├── skill.md (211 lines - primer only)
├── reference/
│   ├── manual_optimization.md
│   ├── decision_criteria.md
│   ├── parameter_grid_setup.md
│   ├── overfitting_detection.md
│   ├── common_errors.md
│   └── cost_estimation.md
└── examples/
    ├── grid_search_momentum.json
    └── complete_workflow.md
```

**Access Pattern**:
1. Load `skill.md` (211 lines) → Get essentials
2. Run `qc_optimize.py --help` → See commands + reference list
3. Run `qc_optimize.py docs` → List all available docs
4. Run `qc_optimize.py docs manual-optimization` → Get detailed guide

**Result**: 64% immediate context reduction (582→211 lines)

---

## Restructuring Checklist

Use this checklist when restructuring ANY skill:

### Phase 1: Analysis (30 min)
- [ ] Read current skill.md file
- [ ] Identify critical constraints (must keep in primer)
- [ ] Identify documentation rules (must keep in primer)
- [ ] Identify reference material (move to reference/)
- [ ] Identify examples (move to examples/)
- [ ] List all topics for reference docs

### Phase 2: Create Directory Structure (5 min)
```bash
mkdir -p .claude/skills/<skill-name>/reference
mkdir -p .claude/skills/<skill-name>/examples
```

### Phase 3: Create Level 1 Primer (1-2 hours)
- [ ] Create new skill.md with template below
- [ ] Include critical constraints
- [ ] Include CLI commands section
- [ ] Include quick start (minimal example)
- [ ] Include common issues (top 3-5)
- [ ] Include documentation rules
- [ ] List all reference docs with descriptions
- [ ] Target: 150-250 lines

### Phase 4: Create Level 2 References (2-3 hours)
- [ ] Extract detailed content from original skill.md
- [ ] Create reference/<topic>.md for each topic
- [ ] Preserve ALL information (no deletion)
- [ ] Organize by logical grouping
- [ ] Add "Level 2 Reference" header to each

### Phase 5: CLI Integration (1 hour)
- [ ] Add enhanced --help with reference doc tree
- [ ] Add `docs` subcommand to CLI script
- [ ] Test `<script>.py docs` lists all docs
- [ ] Test `<script>.py docs <topic>` displays content

### Phase 6: Verification (30 min)
- [ ] Count lines: Before vs After
- [ ] Calculate context reduction percentage
- [ ] Verify ALL critical constraints preserved
- [ ] Verify documentation rules preserved
- [ ] Test CLI access to all references
- [ ] Update skill.md to reference CLI access

### Phase 7: Commit (15 min)
- [ ] Stage all changes
- [ ] Write commit message with pattern template
- [ ] Include before/after line counts
- [ ] Include context reduction percentage

**Total Time**: 5-7 hours per skill (first time)
**Future Time**: 2-3 hours per skill (pattern established)

---

## Skill Primer Template

```markdown
---
name: <Skill Name>
description: <One-line description> (project)
---

# <Skill Name> (Phase X)

**Progressive Disclosure**: This primer loads essential information. Detailed guides in `reference/` (load on-demand).

---

## When to Use

Load when <trigger condition>.

---

## ⚠️ CRITICAL CONSTRAINTS

**List all rules that MUST be followed**

### Why This Matters

1. **Reason 1**
2. **Reason 2**
3. **Reason 3**

### Correct Workflow

```<language>
# ✅ CORRECT example
```

### Wrong Examples (DO NOT DO)

```<language>
# ❌ WRONG example 1
# ❌ WRONG example 2
```

**See `reference/<topic>.md` for complete details.**

---

## CLI Command

```bash
# Using <script>.py CLI (progressive disclosure pattern)
<script>.py <command> <options>
```

**⚠️ IMPORTANT: Access all information via CLI:**
- `<script>.py --help` - All commands and reference doc paths
- `<script>.py docs` - List all available reference docs
- `<script>.py docs <topic>` - View specific reference doc
- Do NOT read source code or skill files directly

---

## Quick Start

### 1. Step One

Brief description + minimal example

### 2. Step Two

Brief description + minimal example

### 3. Step Three

Brief description + minimal example

---

## Common Issues

### 1. Issue One
**Fix**: Solution

### 2. Issue Two
**Fix**: Solution

### 3. Issue Three
**Fix**: Solution

---

## Documentation Rules (CRITICAL)

**List all documentation standards here**

**Naming conventions**: <patterns>

**See `PROJECT_LOGS/README.md` for complete logging standards.**

---

## Progressive Disclosure: Reference Documentation

**Load these on-demand when you need detailed information:**

### <Category 1>
- `reference/<topic-1>.md` - Description
- `reference/<topic-2>.md` - Description

### <Category 2>
- `reference/<topic-3>.md` - Description
- `reference/<topic-4>.md` - Description

### <Category 3>
- `reference/<topic-5>.md` - Description

### Examples
- `examples/<example-1>` - Description
- `examples/<example-2>` - Description

---

## Authoritative Documentation

**When confused about <X>:**
- `PROJECT_DOCUMENTATION/<doc-1>.md`
- `PROJECT_DOCUMENTATION/<doc-2>.md`

**When confused about <Y>:**
- `PROJECT_SCHEMAS/<schema-1>`

---

## Related Skills

- **<skill-1>** - Description
- **<skill-2>** - Description
- **<skill-3>** - Description

---

## Summary

**This primer covers:**
- ✅ Critical constraints
- ✅ CLI commands
- ✅ Quick start
- ✅ Common issues
- ✅ Documentation rules
- ✅ Pointers to reference docs

**Context usage:**
- **Before**: <N> lines (monolithic)
- **After**: <M> lines (primer) + reference docs (load on-demand)
- **Savings**: <X>% immediate context reduction

**Key rule**: <Most critical constraint>

---

**Version**: 2.0.0 (Progressive Disclosure)
**Last Updated**: <Date>
**Status**: Production Ready
```

---

## Skills Requiring Restructure

| Skill | Current Lines | Target Lines | Priority | Status |
|-------|---------------|--------------|----------|--------|
| quantconnect-optimization | 582 | ~200 | HIGH | ✅ DONE (211 lines, 64% reduction) |
| backtesting-analysis | 554 | ~200 | HIGH | 🔄 TODO |
| quantconnect-validation | 463 | ~200 | HIGH | 🔄 TODO |
| quantconnect-backtest | 458 | ~200 | HIGH | 🔄 TODO |
| quantconnect | 174 | ~150 | MEDIUM | 🔄 TODO |
| project-timeline | 135 | ~100 | HIGH | 🔄 TODO (per IMPLEMENTATION_PROPOSAL) |
| decision-framework | 122 | ~100 | HIGH | 🔄 TODO (per IMPLEMENTATION_PROPOSAL) |

**Total Before**: 2488 lines
**Total Target**: ~1250 lines
**Expected Savings**: ~50% (but with hierarchical access, effective savings 85-90%)

---

## Gradual Migration Strategy

This pattern is designed for **gradual but persistent** adoption:

### Week 1 (DONE)
- ✅ Establish pattern with quantconnect-optimization
- ✅ Create this documentation
- ✅ Test CLI `docs` subcommand

### Week 2-3 (Next Steps)
- Apply pattern to 3 largest skills:
  - backtesting-analysis (554 lines)
  - quantconnect-validation (463 lines)
  - quantconnect-backtest (458 lines)

### Week 4-5 (Remaining Skills)
- Apply pattern to remaining 3 skills
- Verify all skills follow pattern
- Measure aggregate context savings

### Week 6+ (Maintenance)
- All NEW skills MUST follow this pattern
- Reference this doc when creating new skills
- Update pattern if improvements discovered

---

## Future Session Guidance

**For Claude in future sessions:**

1. **Check if skill needs restructuring**: Look at line count
   - If skill.md > 250 lines → Restructure using this pattern

2. **Apply pattern systematically**:
   - Read this document first
   - Follow the checklist exactly
   - Use the template for skill.md primer
   - Use the CLI integration pattern for scripts

3. **Preserve ALL information**:
   - Never delete content from original skill
   - Move to reference/ if not in primer
   - Verify all constraints and rules preserved

4. **Test CLI access**:
   - Verify `<script>.py --help` lists references
   - Verify `<script>.py docs` works
   - Verify `<script>.py docs <topic>` displays content

5. **Measure and document**:
   - Record line count before/after
   - Calculate context reduction percentage
   - Update skills table in this document

---

## Pattern Persistence

This pattern will persist across sessions because:

1. **Self-documenting**: This file explains WHY and HOW
2. **Template-based**: Copy template, fill in blanks
3. **Checklist-driven**: Follow steps mechanically
4. **Example-based**: quantconnect-optimization is reference implementation
5. **Enforced by CLI**: `docs` subcommand is standard
6. **Documented in standards**: Added to documentation_standards.md

---

## Success Criteria

A skill is properly restructured when:

- ✅ Primer < 250 lines
- ✅ ALL information from original preserved
- ✅ Critical constraints in primer
- ✅ Documentation rules in primer
- ✅ CLI script has `docs` subcommand
- ✅ `--help` lists reference docs
- ✅ Context reduction ≥ 50%
- ✅ Related CLI script updated

---

## References

- **Pattern Origin**: PROJECT_DOCUMENTATION/IMPROVED_APPROACH/IMPLEMENTATION_PROPOSAL.md
- **Workflow Reports**: PROJECT_DOCUMENTATION/WORKFLOW_CONSISTENCY_AND_PROGRESSIVE_DISCLOSURE_REPORT.md
- **Example Implementation**: .claude/skills/quantconnect-optimization/
- **Documentation Standards**: PROJECT_DOCUMENTATION/documentation_standards.md

---

**Version**: 1.0.0
**Last Updated**: November 13, 2025
**Status**: FOUNDATIONAL - Apply to all skills going forward
**Owner**: Project maintainers + Claude (future sessions)
