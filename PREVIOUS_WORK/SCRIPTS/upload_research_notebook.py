#!/usr/bin/env python3
"""
Upload Research Notebook to QuantConnect Project

This script uploads a local .ipynb notebook to the research.ipynb file
in a QuantConnect project using the REST API.

NO OPTIMIZATION API CALLS - NO COSTS
"""

import json
import sys
import argparse
from pathlib import Path
from qc_backtest import QuantConnectAPI


def upload_notebook_to_research(api, project_id, notebook_path):
    """
    Upload a local notebook to research.ipynb in QC project

    Args:
        api: QuantConnectAPI instance
        project_id: QC project ID
        notebook_path: Path to local .ipynb file

    Returns:
        API response
    """
    print(f"📤 Uploading {notebook_path} to project {project_id}")
    print(f"   Target: research.ipynb (default QC research file)")

    # Read local notebook
    notebook_file = Path(notebook_path)
    if not notebook_file.exists():
        raise FileNotFoundError(f"Notebook not found: {notebook_path}")

    # Validate it's a JSON notebook
    with open(notebook_file, 'r') as f:
        try:
            notebook_content = json.load(f)
            # Verify it has notebook structure
            if 'cells' not in notebook_content or 'metadata' not in notebook_content:
                raise ValueError("File is not a valid Jupyter notebook")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in notebook: {e}")

    # Convert back to string for API
    notebook_str = json.dumps(notebook_content, indent=1)

    print(f"   Notebook size: {len(notebook_str)} bytes")
    print(f"   Cells: {len(notebook_content.get('cells', []))}")

    # Update the research.ipynb file in the project
    # Use the files/update endpoint
    result = api.create_file(project_id, "research.ipynb", notebook_str)

    if result.get('success'):
        print(f"✅ Successfully uploaded to research.ipynb in project {project_id}")
        print(f"\n📍 Next steps:")
        print(f"   1. Go to https://www.quantconnect.com/project/{project_id}")
        print(f"   2. Open the Research tab")
        print(f"   3. Run the notebook cells")
        print(f"\n💡 Optimization runs inside Research are FREE")
    else:
        print(f"❌ Upload failed: {result.get('errors')}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Upload local notebook to research.ipynb in QC project (NO COSTS)"
    )
    parser.add_argument("--project-id", type=int, required=True,
                       help="QuantConnect project ID")
    parser.add_argument("--notebook", default="monte_carlo_walkforward_REAL.ipynb",
                       help="Path to local .ipynb file")

    args = parser.parse_args()

    try:
        # Initialize API
        api = QuantConnectAPI()

        # Upload notebook
        result = upload_notebook_to_research(api, args.project_id, args.notebook)

        if not result.get('success'):
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
