#!/usr/bin/env python3
"""
Upload research.ipynb to QuantConnect Research
"""
import sys
import json
sys.path.append('/Users/donaldcross/ALGOS/Experimentos/Sanboxes/CLAUDE_CODE_EXPLORE/SCRIPTS')

from qc_backtest import QuantConnectAPI

# Initialize API
api = QuantConnectAPI()

# Read the notebook
notebook_path = "research.ipynb"
with open(notebook_path, 'r') as f:
    notebook_content = f.read()

print("="*70)
print("UPLOADING RESEARCH NOTEBOOK TO QUANTCONNECT")
print("="*70)
print()

# Create a new Research project
print("Step 1: Creating Research project...")
project_name = "H5_StatArb_MC_Validation"

# Create project (QC creates algorithm projects, we'll use existing or create new)
# For research notebooks, we typically upload to an existing project or create one
print(f"Project name: {project_name}")
print()

# Option: Upload to existing H5 project (26186305)
project_id = 26186305  # H5_StatArb_Fresh_Init

print(f"Step 2: Uploading research.ipynb to project {project_id}...")
try:
    result = api.upload_file(project_id, "research.ipynb", notebook_content)
    print(f"✅ Upload successful!")
    print(f"   Project ID: {project_id}")
    print(f"   File: research.ipynb")
    print()
    print(f"🌐 Access the notebook at:")
    print(f"   https://www.quantconnect.com/project/{project_id}")
    print()
    print("📝 Next steps:")
    print("   1. Open the project in QC web interface")
    print("   2. Open research.ipynb")
    print("   3. Run all cells to execute Monte Carlo validation")
    print("   4. Review the HTML report generated at the end")
    print()
except Exception as e:
    print(f"❌ Upload failed: {e}")
    print()
    print("Alternative: Manual upload")
    print("   1. Go to https://www.quantconnect.com/project/26186305")
    print("   2. Click 'Add File' → 'Upload'")
    print(f"   3. Select: {notebook_path}")
    sys.exit(1)

print("="*70)
