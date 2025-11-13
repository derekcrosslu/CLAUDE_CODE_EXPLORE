# Progressive Disclosure Rules - IRON CLAD

**Date Created**: 2025-11-13
**Status**: MANDATORY - NEVER VIOLATE
**Purpose**: Ensure consistent reference documentation access pattern

---

## THE ONLY RULE

**ALL reference documentation MUST be accessible ONLY via `--help`.**

**Period. No exceptions. No alternatives.**

---

## What This Means

### ✅ CORRECT Pattern

Every skill has a corresponding CLI tool:

```bash
python SCRIPTS/<tool>.py --help
```

**That's it. That's the only way to access detailed documentation.**

### ❌ FORBIDDEN Patterns

- NO `docs` subcommand
- NO markdown files to read
- NO "Read .claude/skills/<skill>/reference/<file>.md"
- NO "Access detailed docs at..."
- NO alternative access methods

**ONLY `--help`**

---

## Implementation Requirements

### 1. Every Skill Needs a CLI Tool

Each skill in `.claude/skills/<skill-name>/` MUST have:
- Corresponding CLI tool: `SCRIPTS/<tool_name>.py`
- Tool name matches skill (e.g., `backtesting-analysis` → `backtesting_analysis.py`)

### 2. CLI Tool Structure

```python
#!/usr/bin/env python3
"""
<Tool Name>

Usage: python SCRIPTS/<tool>.py --help
"""

import argparse

def main():
    parser = argparse.ArgumentParser(
        description="<Tool description>",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
REFERENCE DOCUMENTATION
=======================

[ALL detailed reference content goes here in --help output]

Section 1: <Topic>
------------------
<Full detailed content>

Section 2: <Topic>
------------------
<Full detailed content>

... (all reference content)
"""
    )

    # Add any functional commands if needed
    parser.add_argument('--version', action='version', version='1.0.0')

    args = parser.parse_args()

    # If tool has functional commands, implement them
    # Otherwise, --help is the only purpose

if __name__ == "__main__":
    main()
```

### 3. Skill Reference Pattern

In skill.md files, reference documentation like this:

```markdown
## Reference Documentation

**Need detailed information?** Use the CLI tool:

```bash
python SCRIPTS/<tool>.py --help
```

**That's the only way to access reference docs.**
```

**NO other instructions. NO markdown file paths. ONLY `--help`.**

---

## Tool Types

### Functional Tools (with commands)

Tools like `qc_optimize.py`, `qc_validate.py`, `qc_backtest.py`:
- Have actual commands (run, status, analyze, etc.)
- ALSO have comprehensive `--help` with all reference content
- `--help` includes BOTH usage AND reference documentation

### Documentation-Only Tools

Tools like `backtesting_analysis.py`, `decision_framework.py`:
- Exist ONLY to provide `--help` documentation
- No functional commands (or minimal like `--version`)
- Entire purpose is comprehensive `--help` output

**Both types use ONLY `--help` for reference documentation.**

---

## Migration Checklist

When restructuring a skill for progressive disclosure:

- [ ] Create `SCRIPTS/<tool>.py` if it doesn't exist
- [ ] Move ALL detailed content to `--help` epilog
- [ ] Ensure `--help` output is comprehensive (200-500 lines is fine)
- [ ] Update skill.md to reference ONLY `python SCRIPTS/<tool>.py --help`
- [ ] Remove ANY mention of:
  - `docs` subcommand
  - markdown files in `reference/` directory
  - alternative access patterns
- [ ] Test: `python SCRIPTS/<tool>.py --help` shows all content
- [ ] Delete `reference/` directories (not needed)

---

## Examples

### ✅ CORRECT Skill Reference

```markdown
## Reference Documentation

**Need detailed Sharpe ratio analysis?**

```bash
python SCRIPTS/backtesting_analysis.py --help
```

**Need overfitting detection patterns?**

```bash
python SCRIPTS/backtesting_analysis.py --help
```

All detailed reference content is in the --help output.
```

### ❌ FORBIDDEN Patterns

```markdown
## Reference Documentation

# WRONG - docs subcommand
python SCRIPTS/qc_optimize.py docs overfitting-detection

# WRONG - markdown files
Read .claude/skills/backtesting-analysis/reference/sharpe_deep_dive.md

# WRONG - multiple access methods
Access via:
- python SCRIPTS/<tool>.py docs <topic>  ← NO
- Read reference/<file>.md                ← NO
```

---

## Why This Rule Exists

1. **Consistency**: One pattern, always works the same way
2. **Discoverability**: `--help` is universal, everyone knows it
3. **Simplicity**: No confusion about where docs are
4. **Maintenance**: All docs in one place (the CLI tool)
5. **Session Continuity**: Claude can always use `--help`, never confused

---

## Enforcement

**This rule is MANDATORY.**

- Code reviews MUST check for violations
- Any skill without `--help`-only pattern is REJECTED
- Any alternative access pattern is REMOVED immediately
- Document this in CURRENT_STATUS.md as Critical Rule

---

## Questions & Clarifications

**Q: What if reference content is too large for --help?**
A: It's not. `--help` can be 500+ lines. If you think it's too large, you haven't made the skill primer concise enough. The primer should be 150-250 lines, `--help` can have all the rest.

**Q: What about functional tools like qc_optimize.py that already have commands?**
A: They STILL use ONLY `--help` for reference docs. The `--help` output includes BOTH command usage AND reference documentation.

**Q: Can I have a `docs` subcommand as an alias to --help?**
A: NO. ONLY `--help`. No aliases, no alternatives, no subcommands for documentation.

**Q: What if the user asks for reference docs?**
A: Tell them: `python SCRIPTS/<tool>.py --help`. That's it.

---

## Automatic Research Fallback (NEW RULE)

**When `--help` doesn't provide sufficient information, automatically trigger research:**

```bash
python SCRIPTS/research_help.py --query "<user question>" --context <tool_name>
```

### How It Works

1. **User asks question**
2. **Check `--help` first** (always primary source)
3. **If `--help` insufficient**, automatically trigger `research_help.py`:
   - Searches PROJECT_DOCUMENTATION/
   - Searches .claude/skills/
   - Identifies relevant CLI tools
   - Generates comprehensive research prompt
   - Uses Claude's research powers to find answer

### Integration Pattern

CLI tools should include fallback:

```python
def handle_help_request(query: str, tool_name: str):
    """Handle user query with automatic research fallback."""

    # First: Show --help
    subprocess.run(['python', f'SCRIPTS/{tool_name}.py', '--help'])

    # If insufficient, trigger research
    subprocess.run([
        'python', 'SCRIPTS/research_help.py',
        '--query', query,
        '--context', tool_name
    ])
```

### Examples

```bash
# User asks: "How do I detect overfitting in optimization?"
# 1. First try: python SCRIPTS/qc_optimize.py --help
# 2. If insufficient: python SCRIPTS/research_help.py --query "detect overfitting optimization" --context qc_optimize

# User asks: "What is PSR metric?"
# 1. First try: python SCRIPTS/backtesting_analysis.py --help
# 2. If insufficient: python SCRIPTS/research_help.py --query "PSR metric" --context backtesting_analysis
```

**This ensures users ALWAYS get answers, even if not in --help.**

### Updating --help Content

When research finds new information that should be added to --help:

```bash
# Add content to a tool's --help
python SCRIPTS/research_help.py --update-help qc_optimize --content "New section content" --section "Advanced Topics"

# This will:
# 1. Backup the original tool (qc_optimize.py.backup)
# 2. Update the epilog with new content
# 3. Preserve existing content
# 4. Verify with: python SCRIPTS/qc_optimize.py --help
```

**Workflow**:
1. Research finds answer not in --help
2. Use --update-help to add it to --help
3. Future users get answer directly from --help
4. Progressive improvement of documentation

---

## Related Files

- `PROGRESSIVE_DISCLOSURE_PATTERN.md` - Overall pattern explanation
- `PROGRESSIVE_DISCLOSURE_QUICKSTART.md` - Quick implementation guide
- `CURRENT_STATUS.md` - Critical Rules section
- `SCRIPTS/research_help.py` - Automatic research fallback tool

---

**Created**: 2025-11-13
**Updated**: 2025-11-13 (Added research fallback rule)
**Status**: ACTIVE - MANDATORY
**Enforcement**: IMMEDIATE
**Violations**: NOT TOLERATED

**ONLY `--help`. Period. With automatic research fallback if needed.**
