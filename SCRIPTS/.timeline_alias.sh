#!/bin/bash
# Timeline CLI alias for autonomous framework development
# Source this file in your ~/.zshrc or ~/.bashrc:
#   source /Users/donaldcross/ALGOS/Experimentos/Sanboxes/CLAUDE_CODE_EXPLORE/.timeline_alias.sh

# Get the directory of this script (absolute path resolution)
TIMELINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create alias using venv python
alias timeline="${TIMELINE_DIR}/venv/bin/python ${TIMELINE_DIR}/SCRIPTS/timeline_cli.py"

# Example usage:
#   timeline next
#   timeline status
#   timeline complete w1-test-003
#   timeline find --status pending
