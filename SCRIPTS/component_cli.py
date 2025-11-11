#!/usr/bin/env python3
"""
Strategy Component Library CLI

Usage:
    component list [category]           # List all components or by category
    component show COMPONENT            # Show component code
    component explain COMPONENT         # Show integration guide
    component search KEYWORD            # Search components by keyword

Progressive Disclosure Pattern (Beyond MCP):
- Browse components without reading all source files
- Load only what you need
- CLI works for humans, teams, AND agents (trifecta)
"""

import click
import sys
from pathlib import Path
from typing import List, Dict

# Absolute path resolution (Beyond MCP pattern)
SCRIPT_DIR = Path(__file__).resolve().parent
COMPONENT_DIR = SCRIPT_DIR / "strategy_components"


def get_categories() -> List[str]:
    """Get list of component categories."""
    categories = []
    for item in COMPONENT_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('_'):
            categories.append(item.name)
    return sorted(categories)


def get_components(category: str = None) -> Dict[str, List[str]]:
    """Get components, optionally filtered by category."""
    components = {}
    
    categories = [category] if category else get_categories()
    
    for cat in categories:
        cat_path = COMPONENT_DIR / cat
        if not cat_path.exists():
            continue
        
        component_files = []
        for file in cat_path.iterdir():
            if file.suffix == '.py' and not file.name.startswith('_'):
                component_files.append(file.stem)
        
        if component_files:
            components[cat] = sorted(component_files)
    
    return components


def find_component_file(component_name: str) -> Path:
    """Find component file by name (searches all categories)."""
    # Try with underscores (add_rsi)
    for category in get_categories():
        file_path = COMPONENT_DIR / category / f"{component_name}.py"
        if file_path.exists():
            return file_path
    
    # Try with hyphens converted to underscores (add-rsi -> add_rsi)
    component_name_underscore = component_name.replace('-', '_')
    for category in get_categories():
        file_path = COMPONENT_DIR / category / f"{component_name_underscore}.py"
        if file_path.exists():
            return file_path
    
    return None


def extract_docstring(file_path: Path) -> str:
    """Extract module docstring from Python file."""
    with open(file_path) as f:
        lines = f.readlines()
    
    # Find docstring
    in_docstring = False
    docstring_lines = []
    quote_type = None
    
    for line in lines:
        stripped = line.strip()
        
        # Start of docstring
        if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
            in_docstring = True
            quote_type = '"""' if stripped.startswith('"""') else "'''"
            
            # Single-line docstring
            if stripped.endswith(quote_type) and len(stripped) > 6:
                return stripped[3:-3]
            
            # Multi-line docstring start
            docstring_lines.append(stripped[3:])
            continue
        
        # Inside docstring
        if in_docstring:
            # End of docstring
            if stripped.endswith(quote_type):
                docstring_lines.append(stripped[:-3])
                break
            else:
                docstring_lines.append(line.rstrip())
    
    return '\n'.join(docstring_lines)


@click.group()
def cli():
    """Strategy component library CLI.
    
    Browse and integrate reusable strategy components with progressive disclosure.
    """
    pass


@cli.command()
@click.argument('category', required=False)
def list(category: str):
    """List components by category.
    
    Examples:
        component list                # All components
        component list indicators     # Just indicators
        component list signals        # Just signals
    """
    components = get_components(category)
    
    if not components:
        if category:
            click.echo(f"❌ No components found in category: {category}")
        else:
            click.echo("❌ No components found")
        sys.exit(1)
    
    click.echo("📦 Strategy Component Library")
    click.echo("=" * 60)
    
    for cat, comps in components.items():
        click.echo(f"\n📁 {cat}/")
        for comp in comps:
            click.echo(f"   - {comp}")
    
    click.echo(f"\n💡 Use 'component show COMPONENT' to view code")
    click.echo(f"💡 Use 'component explain COMPONENT' for integration guide")


@cli.command()
@click.argument('component_name')
def show(component_name: str):
    """Show component source code.
    
    Examples:
        component show add_rsi
        component show add-rsi        # Hyphen or underscore works
        component show mean_reversion
    """
    file_path = find_component_file(component_name)
    
    if not file_path:
        click.echo(f"❌ Component not found: {component_name}", err=True)
        click.echo(f"\n💡 Use 'component list' to see available components")
        sys.exit(1)
    
    # Read and display file
    with open(file_path) as f:
        code = f.read()
    
    click.echo(f"📄 Component: {file_path.stem}")
    click.echo(f"📁 Category: {file_path.parent.name}")
    click.echo(f"📍 Path: {file_path}")
    click.echo("=" * 60)
    click.echo(code)


@cli.command()
@click.argument('component_name')
def explain(component_name: str):
    """Show integration guide from component docstring.
    
    Examples:
        component explain add_rsi
        component explain mean_reversion
    """
    file_path = find_component_file(component_name)
    
    if not file_path:
        click.echo(f"❌ Component not found: {component_name}", err=True)
        click.echo(f"\n💡 Use 'component list' to see available components")
        sys.exit(1)
    
    # Extract docstring
    docstring = extract_docstring(file_path)
    
    if not docstring:
        click.echo(f"⚠️  No integration guide found for: {component_name}")
        return
    
    click.echo(f"📖 Integration Guide: {file_path.stem}")
    click.echo(f"📁 Category: {file_path.parent.name}")
    click.echo("=" * 60)
    click.echo(docstring)


@cli.command()
@click.argument('keyword')
def search(keyword: str):
    """Search components by keyword in name or docstring.
    
    Examples:
        component search momentum
        component search stop
        component search rsi
    """
    keyword_lower = keyword.lower()
    matches = []
    
    for category in get_categories():
        cat_path = COMPONENT_DIR / category
        for file in cat_path.iterdir():
            if file.suffix == '.py' and not file.name.startswith('_'):
                # Check filename
                if keyword_lower in file.stem.lower():
                    docstring = extract_docstring(file)
                    first_line = docstring.split('\n')[0] if docstring else "No description"
                    matches.append({
                        'name': file.stem,
                        'category': category,
                        'description': first_line
                    })
                    continue
                
                # Check docstring
                docstring = extract_docstring(file)
                if docstring and keyword_lower in docstring.lower():
                    first_line = docstring.split('\n')[0]
                    matches.append({
                        'name': file.stem,
                        'category': category,
                        'description': first_line
                    })
    
    if not matches:
        click.echo(f"❌ No components found matching: {keyword}")
        return
    
    click.echo(f"🔍 Search results for: {keyword}")
    click.echo("=" * 60)
    
    for match in matches:
        click.echo(f"\n📦 {match['name']}")
        click.echo(f"   Category: {match['category']}")
        click.echo(f"   {match['description']}")
    
    click.echo(f"\n💡 Use 'component explain COMPONENT' for integration guide")


if __name__ == '__main__':
    cli()
