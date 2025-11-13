#!/usr/bin/env python3
"""
Research Help - Automatic Research Fallback

This script is automatically triggered when --help doesn't provide sufficient
information. It uses Claude's research capabilities to find answers.

Usage:
    python SCRIPTS/research_help.py --query "What is walk-forward validation?"
    python SCRIPTS/research_help.py --query "How do I optimize parameters in QuantConnect?" --context qc_optimize

Progressive Disclosure Pattern:
- First try: python SCRIPTS/<tool>.py --help
- If insufficient: This script triggers automatically
- Searches project docs, web, and external resources
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional, List, Dict

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent


def search_project_docs(query: str) -> List[Dict[str, str]]:
    """Search PROJECT_DOCUMENTATION for relevant files."""
    results = []
    doc_dir = PROJECT_ROOT / "PROJECT_DOCUMENTATION"

    if not doc_dir.exists():
        return results

    # Search all markdown files
    for md_file in doc_dir.rglob("*.md"):
        try:
            content = md_file.read_text()
            # Simple keyword matching (could be enhanced with better search)
            if any(keyword.lower() in content.lower() for keyword in query.split()):
                results.append({
                    "file": str(md_file.relative_to(PROJECT_ROOT)),
                    "relevance": "high" if query.lower() in content.lower() else "medium",
                    "snippet": extract_snippet(content, query)
                })
        except Exception:
            continue

    return results


def extract_snippet(content: str, query: str, context_lines: int = 3) -> str:
    """Extract a snippet around the query match."""
    lines = content.split('\n')
    query_lower = query.lower()

    for i, line in enumerate(lines):
        if query_lower in line.lower():
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            snippet = '\n'.join(lines[start:end])
            return snippet[:300] + "..." if len(snippet) > 300 else snippet

    # If no direct match, return first 300 chars
    return content[:300] + "..."


def search_skills(query: str) -> List[Dict[str, str]]:
    """Search .claude/skills for relevant skills."""
    results = []
    skills_dir = PROJECT_ROOT / ".claude" / "skills"

    if not skills_dir.exists():
        return results

    for skill_file in skills_dir.rglob("skill.md"):
        try:
            content = skill_file.read_text()
            if any(keyword.lower() in content.lower() for keyword in query.split()):
                skill_name = skill_file.parent.name
                results.append({
                    "skill": skill_name,
                    "file": str(skill_file.relative_to(PROJECT_ROOT)),
                    "snippet": extract_snippet(content, query)
                })
        except Exception:
            continue

    return results


def search_cli_tools(context: Optional[str] = None) -> List[str]:
    """Find relevant CLI tools based on context."""
    tools = []
    scripts_dir = PROJECT_ROOT / "SCRIPTS"

    if not scripts_dir.exists():
        return tools

    # Get all Python scripts
    for script in scripts_dir.glob("*.py"):
        if script.name == "research_help.py":
            continue

        # If context provided, filter by relevance
        if context and context.lower() in script.name.lower():
            tools.insert(0, script.name)  # Prioritize
        else:
            tools.append(script.name)

    return tools


def generate_research_prompt(query: str, context: Optional[str],
                            project_results: List[Dict],
                            skill_results: List[Dict],
                            cli_tools: List[str]) -> str:
    """Generate a comprehensive research prompt for Claude."""

    prompt = f"""RESEARCH REQUEST: {query}

CONTEXT:
{'- Tool context: ' + context if context else '- No specific tool context'}

SEARCH RESULTS FROM PROJECT:

"""

    if project_results:
        prompt += "## PROJECT_DOCUMENTATION Matches:\n\n"
        for result in project_results[:3]:  # Top 3
            prompt += f"### {result['file']}\n```\n{result['snippet']}\n```\n\n"
    else:
        prompt += "## No matches in PROJECT_DOCUMENTATION\n\n"

    if skill_results:
        prompt += "## SKILL Matches:\n\n"
        for result in skill_results[:2]:  # Top 2
            prompt += f"### {result['skill']} ({result['file']})\n```\n{result['snippet']}\n```\n\n"
    else:
        prompt += "## No matches in skills\n\n"

    if cli_tools:
        prompt += f"## Available CLI Tools:\n{', '.join(cli_tools[:5])}\n\n"

    prompt += """
RESEARCH INSTRUCTIONS:

1. Analyze the search results above
2. If found in project docs/skills:
   - Provide direct answer with file references
   - Suggest relevant --help commands to run

3. If NOT found in project:
   - Use WebSearch to find authoritative sources
   - Summarize findings
   - Suggest how to integrate into project

4. Always provide:
   - Direct answer to query
   - Relevant file paths (if applicable)
   - Suggested next steps
   - Related CLI commands to try

QUERY: {query}
"""

    return prompt


def update_help_content(tool_name: str, new_content: str, section: Optional[str] = None) -> bool:
    """Update --help content in a CLI tool.

    Args:
        tool_name: Name of the tool (e.g., 'qc_optimize', 'backtesting_analysis')
        new_content: New content to add to --help
        section: Optional section name to update (adds to epilog if None)

    Returns:
        True if successful, False otherwise
    """
    tool_path = SCRIPT_DIR / f"{tool_name}.py"

    if not tool_path.exists():
        print(f"❌ Tool not found: {tool_path}")
        return False

    try:
        content = tool_path.read_text()

        # Find epilog section in ArgumentParser
        epilog_pattern = re.compile(
            r'(epilog\s*=\s*""")(.*?)(""")',
            re.DOTALL
        )

        match = epilog_pattern.search(content)
        if not match:
            print(f"❌ No epilog found in {tool_name}.py")
            print("💡 TIP: --help content should be in epilog parameter of ArgumentParser")
            return False

        current_epilog = match.group(2)

        # Add new content
        if section:
            # Add to specific section
            section_marker = f"\n{'-' * 80}\n{section.upper()}\n{'-' * 80}\n"
            if section_marker in current_epilog:
                # Section exists, append to it
                section_end = current_epilog.find('\n' + '-' * 80, current_epilog.find(section_marker) + len(section_marker))
                if section_end == -1:
                    section_end = len(current_epilog)
                new_epilog = (
                    current_epilog[:section_end] +
                    f"\n{new_content}\n" +
                    current_epilog[section_end:]
                )
            else:
                # Section doesn't exist, create it
                new_epilog = current_epilog + f"\n{section_marker}{new_content}\n"
        else:
            # Append to end of epilog
            new_epilog = current_epilog + f"\n\n{new_content}\n"

        # Replace epilog
        new_file_content = content[:match.start(2)] + new_epilog + content[match.end(2):]

        # Backup original
        backup_path = tool_path.with_suffix('.py.backup')
        tool_path.rename(backup_path)

        # Write updated content
        tool_path.write_text(new_file_content)

        print(f"✅ Updated {tool_name}.py --help content")
        print(f"📁 Backup saved to: {backup_path.name}")
        return True

    except Exception as e:
        print(f"❌ Error updating {tool_name}.py: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Research Help - Automatic fallback when --help is insufficient",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:

    # Research a specific topic
    python SCRIPTS/research_help.py --query "What is Sharpe ratio overfitting?"

    # Research with tool context
    python SCRIPTS/research_help.py --query "How to validate strategies?" --context qc_validate

    # Research with output to file
    python SCRIPTS/research_help.py --query "Walk-forward methodology" --output research_result.md

    # Update --help content in a tool
    python SCRIPTS/research_help.py --update-help qc_optimize --content "New section content" --section "Advanced Topics"

AUTOMATIC TRIGGERING:

This script should be automatically triggered when:
1. User asks a question
2. --help doesn't have the answer
3. Project docs don't have clear guidance

The script will:
- Search PROJECT_DOCUMENTATION/
- Search .claude/skills/
- Search SCRIPTS/ for relevant tools
- Generate comprehensive research prompt
- Optionally search web if no local results

INTEGRATION:

Add to CLI tools:
```python
if not found_in_help:
    subprocess.run([
        'python', 'SCRIPTS/research_help.py',
        '--query', user_query,
        '--context', tool_name
    ])
```
"""
    )

    parser.add_argument('--query', help='Research query')
    parser.add_argument('--context', help='Tool context (e.g., qc_optimize, qc_validate)')
    parser.add_argument('--output', help='Output file for research results')
    parser.add_argument('--format', choices=['text', 'json', 'markdown'],
                       default='markdown', help='Output format')

    # Update help content mode
    parser.add_argument('--update-help', metavar='TOOL',
                       help='Update --help content in specified tool (e.g., qc_optimize)')
    parser.add_argument('--content', help='Content to add to --help (required with --update-help)')
    parser.add_argument('--section', help='Section name to update (optional with --update-help)')

    args = parser.parse_args()

    # Mode 1: Update help content
    if args.update_help:
        if not args.content:
            parser.error("--content is required when using --update-help")

        print(f"📝 Updating --help content for {args.update_help}...")
        print("=" * 60)

        success = update_help_content(args.update_help, args.content, args.section)

        if success:
            print()
            print("✅ Update complete!")
            print(f"🔍 Verify with: python SCRIPTS/{args.update_help}.py --help")
        else:
            print()
            print("❌ Update failed")
            sys.exit(1)

        return

    # Mode 2: Research query (original functionality)
    if not args.query:
        parser.error("--query is required for research mode")

    print("🔍 RESEARCH HELP - Searching for information...")
    print("=" * 60)
    print(f"Query: {args.query}")
    if args.context:
        print(f"Context: {args.context}")
    print("=" * 60)
    print()

    # Search project resources
    print("📚 Searching PROJECT_DOCUMENTATION...")
    project_results = search_project_docs(args.query)
    print(f"   Found {len(project_results)} relevant documents")

    print("🎯 Searching skills...")
    skill_results = search_skills(args.query)
    print(f"   Found {len(skill_results)} relevant skills")

    print("🔧 Finding CLI tools...")
    cli_tools = search_cli_tools(args.context)
    print(f"   Found {len(cli_tools)} CLI tools")
    print()

    # Generate research prompt
    research_prompt = generate_research_prompt(
        args.query,
        args.context,
        project_results,
        skill_results,
        cli_tools
    )

    # Output results
    if args.format == 'json':
        result = {
            "query": args.query,
            "context": args.context,
            "project_docs": project_results,
            "skills": skill_results,
            "cli_tools": cli_tools,
            "research_prompt": research_prompt
        }
        output = json.dumps(result, indent=2)
    else:
        output = research_prompt

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output)
        print(f"✅ Research results saved to: {args.output}")
    else:
        print("=" * 60)
        print("RESEARCH PROMPT (Copy to Claude):")
        print("=" * 60)
        print()
        print(output)
        print()
        print("=" * 60)
        print("💡 TIP: Copy the above prompt and send to Claude for comprehensive research")
        print("=" * 60)


if __name__ == "__main__":
    main()
