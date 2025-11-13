# HELP Directory - Unified JSON Help System

**Purpose**: Centralized, structured, machine-readable help documentation.

## Why JSON?

1. **Easy Retrieval**: Programmatic access to specific sections
2. **Structured**: Consistent format across all tools
3. **Searchable**: Easy to search and filter
4. **Updateable**: `research_help.py` can update dynamically
5. **Version Control**: Clear diffs when content changes
6. **Progressive Disclosure**: Load only needed sections

---

## Directory Structure

```
HELP/
├── README.md                    # This file
├── schema.json                  # JSON schema for help files
├── backtesting_analysis.json    # Backtesting analysis help
├── qc_optimize.json             # Optimization help
├── qc_validate.json             # Validation help
├── qc_backtest.json             # Backtest help
├── decision_framework.json      # Decision framework help
└── ...                          # One JSON file per tool
```

---

## JSON Schema

Each help file follows this structure:

```json
{
  "tool": "backtesting_analysis",
  "version": "2.0.0",
  "description": "Backtesting analysis and overfitting detection",
  "sections": [
    {
      "id": "sharpe_ratio",
      "title": "Sharpe Ratio Deep Dive",
      "content": "Detailed content here...",
      "tags": ["metrics", "sharpe", "risk-adjusted"],
      "priority": 1
    },
    {
      "id": "overfitting_detection",
      "title": "Overfitting Detection",
      "content": "How to detect overfitting...",
      "tags": ["overfitting", "validation"],
      "priority": 1
    }
  ],
  "examples": [
    {
      "title": "Good Backtest Example",
      "description": "Sharpe 0.85, ready for optimization",
      "code": "..."
    }
  ],
  "faqs": [
    {
      "question": "What Sharpe ratio is good?",
      "answer": "0.7-1.0 acceptable, 1.0+ production-ready"
    }
  ],
  "related_tools": ["qc_backtest", "decision_framework"]
}
```

---

## Benefits

### 1. Retrieval by Section

```python
# Get specific section
help_data = load_help("backtesting_analysis")
sharpe_section = help_data.get_section("sharpe_ratio")
```

### 2. Search by Tags

```python
# Find all content tagged "overfitting"
results = search_help(tags=["overfitting"])
```

### 3. Progressive Loading

```python
# Load only high-priority sections
priority_sections = help_data.get_sections(priority=1)
```

### 4. Dynamic Updates

```python
# Add new section
add_help_section(
    tool="backtesting_analysis",
    section_id="new_metric",
    title="New Metric Explanation",
    content="...",
    tags=["metrics"]
)
```

---

## Usage from CLI Tools

CLI tools load help from JSON:

```python
import json
from pathlib import Path

def load_help(tool_name: str) -> dict:
    help_file = Path("HELP") / f"{tool_name}.json"
    with open(help_file) as f:
        return json.load(f)

def format_help_for_display(help_data: dict) -> str:
    """Convert JSON to --help format."""
    output = []
    for section in help_data["sections"]:
        output.append(f"\n{'=' * 80}")
        output.append(section["title"].upper())
        output.append('=' * 80)
        output.append(section["content"])
    return "\n".join(output)

# In ArgumentParser
help_data = load_help("backtesting_analysis")
epilog = format_help_for_display(help_data)
```

---

## Migration Path

1. **Phase 1**: Create JSON files for main tools
   - backtesting_analysis.json
   - qc_optimize.json
   - qc_validate.json

2. **Phase 2**: Update CLI tools to load from JSON
   - Modify ArgumentParser to use JSON
   - Keep backward compatibility

3. **Phase 3**: Update research_help.py
   - Read from JSON files
   - Update JSON directly

4. **Phase 4**: Remove hardcoded epilogs
   - All help content in JSON
   - CLI tools just load and format

---

## Integration with research_help.py

```python
# Search help files
def search_help_json(query: str) -> List[Dict]:
    results = []
    for help_file in Path("HELP").glob("*.json"):
        with open(help_file) as f:
            data = json.load(f)

        # Search sections
        for section in data["sections"]:
            if query.lower() in section["content"].lower():
                results.append({
                    "tool": data["tool"],
                    "section": section["title"],
                    "content": section["content"],
                    "tags": section["tags"]
                })

    return results

# Update help file
def update_help_json(tool: str, section_id: str, content: str):
    help_file = Path("HELP") / f"{tool}.json"
    with open(help_file) as f:
        data = json.load(f)

    # Find section or add new
    for section in data["sections"]:
        if section["id"] == section_id:
            section["content"] = content
            break
    else:
        data["sections"].append({
            "id": section_id,
            "title": section_id.replace("_", " ").title(),
            "content": content,
            "tags": [],
            "priority": 2
        })

    # Save
    with open(help_file, 'w') as f:
        json.dump(data, f, indent=2)
```

---

## Advantages Over Python Epilogs

| Aspect | Python Epilog | JSON Files |
|--------|---------------|------------|
| Retrieval | Parse string | Direct dict access |
| Search | Regex | Structured query |
| Update | String replace | Dict update |
| Version Control | Ugly diffs | Clean diffs |
| Reusability | Copy-paste | Import/reference |
| Validation | None | JSON schema |
| Documentation | In code | Separate files |

---

## Next Steps

1. Create schema.json with JSON schema
2. Convert backtesting_analysis --help to JSON
3. Create helper module for loading/formatting
4. Update research_help.py to use JSON
5. Migrate other tools progressively

---

**Status**: Design phase
**Created**: 2025-11-13
**Author**: Claude (Progressive Disclosure)
