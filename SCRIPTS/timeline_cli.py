#!/usr/bin/env python3
"""
Timeline management CLI for autonomous framework development.

Usage:
    timeline next                    # Get next pending task
    timeline status                  # Current week status
    timeline complete TASK_ID        # Mark complete + git commit
    timeline find [options]          # Find tasks by criteria
    timeline query FILTER            # Custom jq-style queries

Progressive Disclosure Pattern (Beyond MCP):
- Load only what you need (next task, not entire timeline)
- CLI works for humans, teams, AND agents (trifecta)
- 90% context reduction vs 631-line skill
"""

import click
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any

# Absolute path resolution (Beyond MCP pattern - works from any directory)
TIMELINE_FILE = Path(__file__).resolve().parent.parent / "_project_timeline.json"


def load_timeline() -> Dict[str, Any]:
    """Load timeline JSON with error handling."""
    try:
        with open(TIMELINE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        click.echo(f"❌ Error: {TIMELINE_FILE} not found", err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"❌ Error: Invalid JSON in {TIMELINE_FILE}: {e}", err=True)
        sys.exit(1)


def save_timeline(timeline: Dict[str, Any]) -> None:
    """Save timeline JSON with error handling."""
    try:
        with open(TIMELINE_FILE, 'w') as f:
            json.dump(timeline, f, indent=2)
    except Exception as e:
        click.echo(f"❌ Error saving timeline: {e}", err=True)
        sys.exit(1)


def get_git_commit_hash() -> str:
    """Get current git commit short hash."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def utc_now() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


@click.group()
def cli():
    """Project timeline management CLI.

    Manage autonomous framework development timeline with progressive disclosure.
    Load only what you need - not the entire 631-line skill!
    """
    pass


@cli.command()
@click.option('--week', type=int, help='Filter by week number')
@click.option('--section', help='Filter by section name')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def next(week: Optional[int], section: Optional[str], output_json: bool):
    """Get next pending task.

    Progressive disclosure: Only load the NEXT task, not entire timeline.

    Examples:
        timeline next                 # Next pending task (any week)
        timeline next --week 1        # Next pending task in week 1
        timeline next --section test  # Next pending in test section
        timeline next --json          # Output as JSON
    """
    timeline = load_timeline()

    # Find first pending task
    for week_data in timeline['weeks']:
        # Filter by week if specified
        if week and week_data['week'] != week:
            continue

        for section_data in week_data['sections']:
            # Filter by section if specified
            if section and section.lower() not in section_data['name'].lower():
                continue

            for item in section_data['items']:
                if item['status'] == 'pending':
                    # Found next pending task
                    result = {
                        'id': item['id'],
                        'task': item['task'],
                        'week': week_data['week'],
                        'week_title': week_data['title'],
                        'section': section_data['name'],
                        'section_id': section_data['id']
                    }

                    if output_json:
                        click.echo(json.dumps(result, indent=2))
                    else:
                        click.echo(f"📋 Next Pending Task:")
                        click.echo(f"   ID:      {result['id']}")
                        click.echo(f"   Task:    {result['task']}")
                        click.echo(f"   Week:    {result['week']} - {result['week_title']}")
                        click.echo(f"   Section: {result['section']}")

                    return

    # No pending tasks found
    if output_json:
        click.echo('{}')
    else:
        click.echo("✅ No pending tasks found! All work complete.")


@cli.command()
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def status(output_json: bool):
    """Show current week status and progress.

    Examples:
        timeline status        # Human-readable status
        timeline status --json # JSON output
    """
    timeline = load_timeline()
    current = timeline.get('current_status', {})

    if output_json:
        click.echo(json.dumps(current, indent=2))
    else:
        click.echo(f"📊 Project Status:")
        click.echo(f"   Week:     {current.get('week', 'N/A')}")
        click.echo(f"   Phase:    {current.get('phase', 'N/A')}")
        click.echo(f"   Progress: {current.get('progress', 'N/A')}")
        click.echo(f"   Updated:  {current.get('updated_at', 'N/A')}")


@cli.command()
@click.argument('task_id')
@click.option('--no-commit', is_flag=True, help='Skip git commit')
@click.option('--message', '-m', help='Custom commit message')
def complete(task_id: str, no_commit: bool, message: Optional[str]):
    """Mark task complete and create git commit.

    Examples:
        timeline complete w1-test-003              # Mark complete + auto commit
        timeline complete w1-test-003 --no-commit  # Mark complete (no commit)
        timeline complete w1-test-003 -m "Custom"  # Custom commit message
    """
    timeline = load_timeline()

    # Find task
    task_found = False
    task_name = None
    week_num = None
    section_name = None

    for week_data in timeline['weeks']:
        for section_data in week_data['sections']:
            for item in section_data['items']:
                if item['id'] == task_id:
                    # Update task
                    item['status'] = 'completed'
                    item['completed_at'] = utc_now()
                    item['git_commit'] = get_git_commit_hash()

                    task_name = item['task']
                    week_num = week_data['week']
                    section_name = section_data['name']
                    task_found = True
                    break
            if task_found:
                break
        if task_found:
            break

    if not task_found:
        click.echo(f"❌ Error: Task {task_id} not found", err=True)
        sys.exit(1)

    # Save timeline
    save_timeline(timeline)
    click.echo(f"✅ Marked {task_id} complete: {task_name}")

    # Create git commit (unless --no-commit)
    if not no_commit:
        # Prepare commit message
        if message:
            commit_msg = message
        else:
            commit_msg = f"""docs: Mark {task_id} complete

{task_name}

Week {week_num} - {section_name}

✅ Task complete

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"""

        try:
            # Stage timeline file
            subprocess.run(['git', 'add', str(TIMELINE_FILE)], check=True)

            # Create commit
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)

            click.echo(f"✅ Git commit created")
        except subprocess.CalledProcessError as e:
            click.echo(f"⚠️  Warning: Git commit failed: {e}", err=True)


@cli.command()
@click.option('--status', type=click.Choice(['pending', 'completed', 'all']), default='all', help='Filter by status')
@click.option('--week', type=int, help='Filter by week number')
@click.option('--section', help='Filter by section name (partial match)')
@click.option('--limit', type=int, help='Limit number of results')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def find(status: str, week: Optional[int], section: Optional[str], limit: Optional[int], output_json: bool):
    """Find tasks by criteria.

    Examples:
        timeline find --status pending           # All pending tasks
        timeline find --week 1                   # All week 1 tasks
        timeline find --section test             # All tasks in test sections
        timeline find --status completed --week 1 # Completed week 1 tasks
        timeline find --limit 5                  # First 5 tasks
        timeline find --json                     # JSON output
    """
    timeline = load_timeline()
    results = []

    for week_data in timeline['weeks']:
        # Filter by week
        if week and week_data['week'] != week:
            continue

        for section_data in week_data['sections']:
            # Filter by section
            if section and section.lower() not in section_data['name'].lower():
                continue

            for item in section_data['items']:
                # Filter by status
                if status != 'all' and item['status'] != status:
                    continue

                # Add to results
                result = {
                    'id': item['id'],
                    'task': item['task'],
                    'status': item['status'],
                    'week': week_data['week'],
                    'section': section_data['name']
                }

                # Add completion info if completed
                if item['status'] == 'completed':
                    result['completed_at'] = item.get('completed_at', 'N/A')
                    result['git_commit'] = item.get('git_commit', 'N/A')

                results.append(result)

                # Check limit
                if limit and len(results) >= limit:
                    break
            if limit and len(results) >= limit:
                break
        if limit and len(results) >= limit:
            break

    # Output results
    if output_json:
        click.echo(json.dumps(results, indent=2))
    else:
        if not results:
            click.echo("No tasks found matching criteria.")
        else:
            click.echo(f"Found {len(results)} task(s):\n")
            for r in results:
                status_icon = "✅" if r['status'] == 'completed' else "📋"
                click.echo(f"{status_icon} {r['id']}: {r['task']}")
                click.echo(f"   Week {r['week']} - {r['section']} - {r['status']}")
                if r['status'] == 'completed':
                    click.echo(f"   Completed: {r.get('completed_at', 'N/A')} (commit: {r.get('git_commit', 'N/A')})")
                click.echo()


@cli.command()
@click.argument('jq_filter')
def query(jq_filter: str):
    """Run custom jq-style query on timeline.

    Examples:
        timeline query '.current_status.week'
        timeline query '.weeks[0].title'
        timeline query '[.weeks[].sections[].items[] | select(.status == "pending")] | length'

    Note: Requires jq to be installed.
    """
    try:
        # Use jq for complex queries
        result = subprocess.run(
            ['jq', jq_filter, str(TIMELINE_FILE)],
            capture_output=True,
            text=True,
            check=True
        )
        click.echo(result.stdout)
    except FileNotFoundError:
        click.echo("❌ Error: jq not installed. Install with: brew install jq", err=True)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Error: Invalid jq filter: {e.stderr}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
