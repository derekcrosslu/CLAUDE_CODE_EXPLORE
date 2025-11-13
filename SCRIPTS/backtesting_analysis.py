#!/usr/bin/env python3
"""
Backtesting Analysis - Reference Documentation

This tool provides comprehensive reference documentation for interpreting
backtest results and detecting overfitting.

Usage:
    python SCRIPTS/backtesting_analysis.py --help

Note: All help content loaded from HELP/backtesting_analysis.json
"""

import argparse
import sys
from pathlib import Path

# Add SCRIPTS to path for imports
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from help_loader import load_help, format_help

def main():
    # Load help from JSON
    try:
        help_data = load_help("backtesting_analysis")
        epilog = format_help(help_data)
    except Exception as e:
        epilog = f"Error loading help: {e}\nCheck HELP/backtesting_analysis.json"

    parser = argparse.ArgumentParser(
        description="Backtesting Analysis Reference Documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog
    )

    parser.add_argument('--version', action='version', version='2.0.0')
    parser.add_argument('--section', help='Show specific section by ID')
    parser.add_argument('--search', help='Search help content')
    parser.add_argument('--list-sections', action='store_true',
                       help='List all available sections')

    args = parser.parse_args()

    # Section-specific display
    if args.list_sections:
        print("Available sections:")
        for section in help_data.get('sections', []):
            priority_marker = "★" * section.get('priority', 3)
            print(f"  {priority_marker} {section['id']}: {section['title']}")
            if section.get('tags'):
                print(f"     Tags: {', '.join(section['tags'])}")
        sys.exit(0)

    if args.section:
        from help_loader import get_section
        section = get_section(help_data, args.section)
        if section:
            print(f"\n{'=' * 80}")
            print(f"{section['title'].upper()}")
            print('=' * 80)
            print()
            print(section['content'])
            print()
            if section.get('tags'):
                print(f"Tags: {', '.join(section['tags'])}")
        else:
            print(f"❌ Section not found: {args.section}")
            print("\nUse --list-sections to see available sections")
            sys.exit(1)
        sys.exit(0)

    if args.search:
        from help_loader import search_help
        results = search_help(args.search)

        # Filter to this tool only
        results = [r for r in results if r.get('tool') == 'backtesting_analysis']

        if results:
            print(f"\n{'=' * 80}")
            print(f"Search results for '{args.search}' ({len(results)} found)")
            print('=' * 80)
            for result in results:
                if result.get('section_title'):
                    print(f"\n### {result['section_title']}")
                    print(f"Section ID: {result['section_id']}")
                    print(f"Tags: {', '.join(result.get('tags', []))}")
                elif result.get('question'):
                    print(f"\n### FAQ: {result['question']}")
                    print(f"A: {result['answer']}")
            print()
        else:
            print(f"\n❌ No results found for '{args.search}'")
            print("Try searching with different keywords or use --help to see all content")
        sys.exit(0)

    # If no args, argparse will show --help automatically

if __name__ == "__main__":
    main()
