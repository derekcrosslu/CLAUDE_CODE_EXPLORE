#!/usr/bin/env python3
"""Debug script to test QC optimization API responses"""

import json
from qc_backtest import QuantConnectAPI

# Initialize API
api = QuantConnectAPI()

# Load parameters
with open("optimization_params.json") as f:
    params_config = json.load(f)

parameters = params_config["parameters"]
project_id = 26120873

print("=== Testing Estimate Optimization ===")
estimate_result = api.estimate_optimization(
    project_id=project_id,
    parameters=parameters,
    node_type="O2-8",
    parallel_nodes=2
)
print(json.dumps(estimate_result, indent=2))

print("\n=== Testing Create Optimization ===")
create_result = api.create_optimization(
    project_id=project_id,
    name="Debug_Test",
    target="TotalPerformance.PortfolioStatistics.SharpeRatio",
    parameters=parameters,
    target_to="max",
    node_type="O2-8",
    parallel_nodes=2
)
print(json.dumps(create_result, indent=2))
