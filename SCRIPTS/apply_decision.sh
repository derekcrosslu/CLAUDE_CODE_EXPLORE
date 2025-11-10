#!/bin/bash

# Extract metrics from backtest result
SHARPE=$(cat backtest_result.json | jq -r '.performance.sharpe_ratio')
MAX_DRAWDOWN=$(cat backtest_result.json | jq -r '.performance.max_drawdown')
TOTAL_RETURN=$(cat backtest_result.json | jq -r '.performance.total_return')
TOTAL_TRADES=$(cat backtest_result.json | jq -r '.trading.total_trades')
WIN_RATE=$(cat backtest_result.json | jq -r '.performance.win_rate')
BACKTEST_ID=$(cat backtest_result.json | jq -r '.backtest_id')
PROJECT_ID=$(cat backtest_result.json | jq -r '.project_id')
PROJECT_URL="https://www.quantconnect.com/project/${PROJECT_ID}"

# Decision logic (4-tier framework)
DECISION="UNKNOWN"
REASON=""

# Check overfitting signals first
if (( $(echo "$SHARPE > 3.0" | bc -l 2>/dev/null || echo 0) )); then
    DECISION="ESCALATE_TO_HUMAN"
    REASON="Sharpe ratio too perfect ($SHARPE > 3.0), possible overfitting"
elif (( TOTAL_TRADES < 20 && TOTAL_TRADES > 0 )); then
    DECISION="ESCALATE_TO_HUMAN"
    REASON="Too few trades ($TOTAL_TRADES < 20), unreliable statistics"
elif (( $(echo "$WIN_RATE > 0.75" | bc -l 2>/dev/null || echo 0) )); then
    DECISION="ESCALATE_TO_HUMAN"
    REASON="Win rate suspiciously high ($WIN_RATE > 0.75)"
    
# Check minimum viable
elif (( $(echo "$SHARPE < 0.5" | bc -l 2>/dev/null || echo 1) )); then
    DECISION="ABANDON_HYPOTHESIS"
    REASON="Sharpe ratio below minimum viable ($SHARPE < 0.5)"
elif (( $(echo "$MAX_DRAWDOWN > 0.40" | bc -l 2>/dev/null || echo 0) )); then
    DECISION="ABANDON_HYPOTHESIS"
    REASON="Max drawdown too high ($MAX_DRAWDOWN > 0.40)"
elif (( TOTAL_TRADES < 30 )); then
    DECISION="ABANDON_HYPOTHESIS"
    REASON="Insufficient trades for statistical significance ($TOTAL_TRADES < 30)"
    
# Check production ready (can skip optimization)
elif (( $(echo "$SHARPE >= 1.0" | bc -l 2>/dev/null || echo 0) )) && \
     (( $(echo "$MAX_DRAWDOWN <= 0.30" | bc -l 2>/dev/null || echo 1) )) && \
     (( TOTAL_TRADES >= 100 )); then
    DECISION="PROCEED_TO_VALIDATION"
    REASON="Strong baseline performance (Sharpe $SHARPE, DD $MAX_DRAWDOWN), ready for validation"
    
# Check optimization worthy
elif (( $(echo "$SHARPE >= 0.7" | bc -l 2>/dev/null || echo 0) )) && \
     (( $(echo "$MAX_DRAWDOWN <= 0.35" | bc -l 2>/dev/null || echo 1) )) && \
     (( TOTAL_TRADES >= 50 )); then
    DECISION="PROCEED_TO_OPTIMIZATION"
    REASON="Decent performance (Sharpe $SHARPE), worth optimizing parameters"
    
# Marginal case - try optimization
elif (( $(echo "$SHARPE >= 0.5" | bc -l 2>/dev/null || echo 0) )); then
    DECISION="PROCEED_TO_OPTIMIZATION"
    REASON="Marginal performance (Sharpe $SHARPE), attempting optimization"
    
else
    DECISION="ABANDON_HYPOTHESIS"
    REASON="Performance does not meet criteria"
fi

echo "Decision: $DECISION"
echo "Reason: $REASON"
echo "Sharpe: $SHARPE"
echo "Trades: $TOTAL_TRADES"
echo "Return: $TOTAL_RETURN"
echo "Drawdown: $MAX_DRAWDOWN"
echo "Backtest ID: $BACKTEST_ID"
echo "Project ID: $PROJECT_ID"
echo "Project URL: $PROJECT_URL"

# Export for use in updating iteration_state.json
echo "$DECISION" > /tmp/decision.txt
echo "$REASON" > /tmp/decision_reason.txt
