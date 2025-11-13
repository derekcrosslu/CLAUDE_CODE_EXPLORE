# PROJECT_LOGS

This folder stores all logs generated during autonomous strategy development.

## Log Organization

### Backtest Logs
Store backtest results and output logs:
- `backtest_result_hypothesis_{id}_iteration_{n}.json` - Backtest performance metrics
- `backtest_output_hypothesis_{id}_iteration_{n}.log` - Backtest execution logs
- `backtest_errors_hypothesis_{id}_iteration_{n}.log` - Error logs from failed backtests

### Optimization Logs
Store optimization results:
- `optimization_result_hypothesis_{id}_iteration_{n}.json` - Optimization results
- `optimization_output_hypothesis_{id}_iteration_{n}.log` - Optimization execution logs

### Validation Logs
Store walk-forward validation results:
- `validation_result_hypothesis_{id}_iteration_{n}.json` - Validation metrics
- `validation_output_hypothesis_{id}_iteration_{n}.log` - Validation execution logs

### API Logs
Store QuantConnect API interaction logs:
- `qc_api_{operation}_{timestamp}.log` - API request/response logs

## Naming Convention

Use descriptive filenames that include:
1. **Operation type**: backtest, optimization, validation, api
2. **Hypothesis ID**: hypothesis_4
3. **Iteration number**: iteration_1
4. **Timestamp**: ISO 8601 format (YYYY-MM-DDTHH-MM-SS)
5. **Extension**: .json for structured data, .log for text logs

## Example Filenames

```
PROJECT_LOGS/
├── backtest_result_hypothesis_4_iteration_1_2025-11-10T19-30-00Z.json
├── backtest_output_hypothesis_4_iteration_1_2025-11-10T19-30-00Z.log
├── optimization_result_hypothesis_4_iteration_2_2025-11-10T20-00-00Z.json
├── validation_result_hypothesis_4_iteration_3_2025-11-10T21-00-00Z.json
└── qc_api_upload_2025-11-10T19-25-00Z.log
```

## Log Retention

- Keep all logs for analysis and debugging
- Logs are version-controlled via git (except large binary files)
- Clean up old logs only when hypothesis is abandoned or deployed

## Usage in Commands

Commands should write logs to PROJECT_LOGS:

```python
# In /qc-backtest command
log_file = f"PROJECT_LOGS/backtest_output_hypothesis_{hypothesis_id}_iteration_{iteration}.log"

# In qc_backtest.py wrapper
result_file = f"PROJECT_LOGS/backtest_result_hypothesis_{hypothesis_id}_iteration_{iteration}.json"
```

## Do NOT Store Here

- Strategy code (use STRATEGIES/)
- Research notebooks (use RESEARCH_NOTEBOOKS/)
- State files (use STRATEGIES/hypothesis_N/iteration_state.json)
- Documentation (use PROJECT_DOCUMENTATION/)
- Timeline tracking (use project_timeline.json)

**This folder is for execution logs and results ONLY.**
