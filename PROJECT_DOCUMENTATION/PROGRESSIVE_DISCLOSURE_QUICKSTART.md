# Progressive Disclosure Quick Start

**Self-Propagating Pattern** - Copy this for any skill restructure

---

## 5-Minute Pattern Overview

**Goal**: Organize information hierarchically, preserve everything, reduce context by 50-90%

**Structure**:
```
.claude/skills/<skill-name>/
├── skill.md (~200 lines - PRIMER: essentials only)
├── reference/*.md (DETAILED: load via CLI)
└── examples/* (TEMPLATES: copy-paste ready)
```

**Access**: `<script>.py docs <topic>` → Shows reference content

---

## Copy-Paste Checklist

When restructuring ANY skill:

```markdown
## Phase 1: Setup (5 min)
- [ ] mkdir -p .claude/skills/<skill-name>/reference
- [ ] mkdir -p .claude/skills/<skill-name>/examples
- [ ] Read current skill.md, count lines

## Phase 2: Primer (1 hour)
- [ ] Keep: Critical constraints, CLI commands, quick start, common issues, doc rules
- [ ] Move to reference/: Detailed guides, implementations, exhaustive docs
- [ ] Target: 150-250 lines in primer

## Phase 3: CLI Integration (30 min)
- [ ] Add `docs` subcommand to <script>.py
- [ ] Update `--help` to list reference docs
- [ ] Test: `<script>.py docs` and `<script>.py docs <topic>`

## Phase 4: Verify (15 min)
- [ ] All constraints preserved?
- [ ] All doc rules preserved?
- [ ] CLI access works?
- [ ] Context reduction ≥ 50%?

## Phase 5: Commit
- [ ] git add .claude/skills/<skill-name>/ SCRIPTS/<script>.py
- [ ] git commit with template from PROGRESSIVE_DISCLOSURE_PATTERN.md
```

---

## CLI Integration Template

**Copy this into your Python CLI script:**

```python
@cli.command()
@click.argument('topic', required=False)
def docs(topic: str):
    """Show reference documentation (progressive disclosure).

    Usage:
        <script>.py docs                 # List all
        <script>.py docs <topic>         # Show specific
    """
    from pathlib import Path

    ref_dir = Path(__file__).resolve().parent.parent / '.claude/skills/<skill-name>/reference'

    docs_map = {
        '<topic-1>': '<file-1>.md',
        '<topic-2>': '<file-2>.md',
    }

    if not topic:
        click.echo("📚 Available Reference Documentation:\n")
        for topic_name, filename in docs_map.items():
            doc_path = ref_dir / filename
            status = "✓" if doc_path.exists() else "✗"
            click.echo(f"  {status} {topic_name:25} → {filename}")
        click.echo(f"\n📂 Reference directory: {ref_dir}")
        click.echo(f"\nUsage: <script>.py docs <topic>")
        return

    if topic not in docs_map:
        click.echo(f"❌ Unknown topic: {topic}", err=True)
        sys.exit(1)

    doc_path = ref_dir / docs_map[topic]

    if not doc_path.exists():
        click.echo(f"❌ Documentation not found: {doc_path}", err=True)
        sys.exit(1)

    with open(doc_path, 'r') as f:
        click.echo(f.read())
```

---

## Commit Message Template

```
refactor: Progressive disclosure for <skill-name> skill

PROGRESSIVE DISCLOSURE HIERARCHY CREATED:

Level 1 (Always Loaded): skill.md primer
- <new-lines> lines (was <old-lines> lines)
- <percentage>% context reduction
- Essential information only:
  * Critical constraints
  * CLI commands
  * Quick start
  * Common issues
  * Documentation rules
  * Pointers to Level 2 references

Level 2 (Load On-Demand): reference/ docs
- <topic-1>.md - Description
- <topic-2>.md - Description
- <topic-n>.md - Description
- Load only when implementing specific features

CLI ENHANCEMENT:
- <script>.py --help now shows complete reference doc paths
- <script>.py docs lists all available references
- <script>.py docs <topic> displays full content
- Progressive disclosure unified via CLI

KEY PRESERVATION:
✅ ALL information preserved (no deletion)
✅ Critical constraints intact
✅ Documentation rules enforced
✅ Hierarchical organization by usage frequency

PATTERN:
This follows the self-propagating pattern from:
PROJECT_DOCUMENTATION/PROGRESSIVE_DISCLOSURE_PATTERN.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Reference Implementation

**Study this example**: `.claude/skills/quantconnect-optimization/`

- Before: 582 lines (monolithic)
- After: 211 lines (primer) + 7 reference docs
- CLI: `qc_optimize.py docs` works
- Result: 64% immediate reduction, 90% effective reduction

---

## Skills To Do

| Skill | Lines | Status |
|-------|-------|--------|
| quantconnect-optimization | 582 | ✅ DONE |
| backtesting-analysis | 554 | 🔄 TODO |
| quantconnect-validation | 463 | 🔄 TODO |
| quantconnect-backtest | 458 | 🔄 TODO |

Pick one, follow checklist, 2-3 hours per skill.

---

**For more details**: See `PROGRESSIVE_DISCLOSURE_PATTERN.md`

**Self-propagating**: This pattern persists because it's documented, templated, and exemplified.
