#!/usr/bin/env python3
"""
Help Loader - Load and format JSON help files

Unified module for loading structured help documentation from HELP/ directory.

Usage:
    from help_loader import load_help, format_help, search_help

    # Load help data
    help_data = load_help("backtesting_analysis")

    # Format for --help display
    epilog = format_help(help_data)

    # Search across all help files
    results = search_help("overfitting")
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


HELP_DIR = Path(__file__).resolve().parent.parent / "HELP"


def load_help(tool_name: str) -> Dict:
    """Load help data from JSON file.

    Args:
        tool_name: Tool name (e.g., 'backtesting_analysis', 'qc_optimize')

    Returns:
        Dict with help data

    Raises:
        FileNotFoundError: If help file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    help_file = HELP_DIR / f"{tool_name}.json"

    if not help_file.exists():
        raise FileNotFoundError(f"Help file not found: {help_file}")

    with open(help_file) as f:
        return json.load(f)


def format_help(help_data: Dict, priority: Optional[int] = None) -> str:
    """Format help data for CLI display.

    Args:
        help_data: Help data from load_help()
        priority: If specified, only include sections with this priority

    Returns:
        Formatted string for ArgumentParser epilog
    """
    output = []

    # Header
    output.append("=" * 80)
    output.append(f"{help_data['tool'].upper()} - REFERENCE DOCUMENTATION")
    output.append(f"Version: {help_data['version']}")
    output.append("=" * 80)
    output.append("")
    output.append(help_data['description'])
    output.append("")

    # Sections
    sections = help_data.get('sections', [])
    if priority:
        sections = [s for s in sections if s.get('priority') == priority]

    for section in sections:
        output.append("-" * 80)
        output.append(section['title'].upper())
        output.append("-" * 80)
        output.append("")
        output.append(section['content'])
        output.append("")

        # Tags
        if section.get('tags'):
            output.append(f"Tags: {', '.join(section['tags'])}")
            output.append("")

    # Examples
    if help_data.get('examples'):
        output.append("=" * 80)
        output.append("EXAMPLES")
        output.append("=" * 80)
        output.append("")

        for example in help_data['examples']:
            output.append(f"### {example['title']}")
            output.append(example['description'])
            output.append("")
            if example.get('code'):
                output.append("```")
                output.append(example['code'])
                output.append("```")
                output.append("")
            if example.get('output'):
                output.append(f"Output: {example['output']}")
                output.append("")

    # FAQs
    if help_data.get('faqs'):
        output.append("=" * 80)
        output.append("FREQUENTLY ASKED QUESTIONS")
        output.append("=" * 80)
        output.append("")

        for faq in help_data['faqs']:
            output.append(f"Q: {faq['question']}")
            output.append(f"A: {faq['answer']}")
            output.append("")

    # Related tools
    if help_data.get('related_tools'):
        output.append("-" * 80)
        output.append("RELATED TOOLS")
        output.append("-" * 80)
        output.append("")
        for tool in help_data['related_tools']:
            output.append(f"  - python SCRIPTS/{tool}.py --help")
        output.append("")

    # Footer
    output.append("=" * 80)
    if help_data.get('metadata'):
        meta = help_data['metadata']
        output.append(f"Created: {meta.get('created', 'Unknown')}")
        output.append(f"Updated: {meta.get('updated', 'Unknown')}")
    output.append("=" * 80)

    return "\n".join(output)


def get_section(help_data: Dict, section_id: str) -> Optional[Dict]:
    """Get a specific section by ID.

    Args:
        help_data: Help data from load_help()
        section_id: Section ID (e.g., 'sharpe_ratio')

    Returns:
        Section dict or None if not found
    """
    for section in help_data.get('sections', []):
        if section['id'] == section_id:
            return section
    return None


def search_help(query: str, tags: Optional[List[str]] = None) -> List[Dict]:
    """Search across all help files.

    Args:
        query: Search query (case-insensitive)
        tags: Optional list of tags to filter by

    Returns:
        List of matching results with tool, section, and content
    """
    results = []
    query_lower = query.lower()

    # Search all help files
    for help_file in HELP_DIR.glob("*.json"):
        if help_file.name == "schema.json":
            continue

        try:
            with open(help_file) as f:
                data = json.load(f)

            tool_name = data['tool']

            # Search sections
            for section in data.get('sections', []):
                # Tag filter
                if tags:
                    if not any(tag in section.get('tags', []) for tag in tags):
                        continue

                # Content search
                if (query_lower in section['title'].lower() or
                    query_lower in section['content'].lower()):

                    results.append({
                        'tool': tool_name,
                        'section_id': section['id'],
                        'section_title': section['title'],
                        'content': section['content'],
                        'tags': section.get('tags', []),
                        'priority': section.get('priority', 3)
                    })

            # Search FAQs
            for faq in data.get('faqs', []):
                if (query_lower in faq['question'].lower() or
                    query_lower in faq['answer'].lower()):

                    results.append({
                        'tool': tool_name,
                        'type': 'faq',
                        'question': faq['question'],
                        'answer': faq['answer'],
                        'tags': faq.get('tags', [])
                    })

        except Exception as e:
            print(f"Warning: Error reading {help_file}: {e}")
            continue

    return results


def list_all_tools() -> List[str]:
    """List all available tool help files.

    Returns:
        List of tool names
    """
    tools = []
    for help_file in HELP_DIR.glob("*.json"):
        if help_file.name == "schema.json":
            continue
        tools.append(help_file.stem)
    return sorted(tools)


def validate_help_file(tool_name: str) -> bool:
    """Validate help file against schema.

    Args:
        tool_name: Tool name

    Returns:
        True if valid, False otherwise
    """
    try:
        help_data = load_help(tool_name)

        # Basic validation
        required_fields = ['tool', 'version', 'description', 'sections']
        for field in required_fields:
            if field not in help_data:
                print(f"Missing required field: {field}")
                return False

        # Validate sections
        for section in help_data.get('sections', []):
            required = ['id', 'title', 'content', 'priority']
            for field in required:
                if field not in section:
                    print(f"Section missing required field: {field}")
                    return False

        return True

    except Exception as e:
        print(f"Validation error: {e}")
        return False


# CLI interface for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Help Loader Utility")
    parser.add_argument('--tool', help='Tool name to load')
    parser.add_argument('--section', help='Specific section ID')
    parser.add_argument('--search', help='Search query')
    parser.add_argument('--list', action='store_true', help='List all tools')
    parser.add_argument('--validate', help='Validate help file')

    args = parser.parse_args()

    if args.list:
        print("Available tools:")
        for tool in list_all_tools():
            print(f"  - {tool}")

    elif args.validate:
        is_valid = validate_help_file(args.validate)
        print(f"{'✅' if is_valid else '❌'} {args.validate}")

    elif args.search:
        results = search_help(args.search)
        print(f"Found {len(results)} results for '{args.search}':")
        for result in results:
            print(f"\n[{result['tool']}] {result.get('section_title', result.get('question'))}")
            print(f"Tags: {', '.join(result.get('tags', []))}")

    elif args.tool:
        help_data = load_help(args.tool)

        if args.section:
            section = get_section(help_data, args.section)
            if section:
                print(f"=== {section['title']} ===\n")
                print(section['content'])
            else:
                print(f"Section not found: {args.section}")
        else:
            print(format_help(help_data))

    else:
        parser.print_help()
