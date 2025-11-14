---
description: Run advanced Monte Carlo validation - the final gatekeeper before live trading
---

Run comprehensive Monte Carlo validation with PSR, DSR, CPCV, MACHR, and bootstrap analysis to verify strategy robustness across multiple scenarios before risking real capital.

## ⚠️ CRITICAL: THIS IS THE FINAL GATEKEEPER

**Validation is the LAST step before live trading with real money.**

This is NOT a "quick check" - this is PRODUCTION-READY validation implementing:
- Probabilistic Sharpe Ratio (PSR ≥ 0.95)
- Deflated Sharpe Ratio (DSR - multiple testing correction)
- Combinatorial Purged Cross-Validation (CPCV - 500+ splits)
- Market Condition Historical Randomization (MACHR)
- Bootstrap resampling (1,000-10,000 runs)
- Permutation testing (p < 0.05)
- Monte Carlo drawdown distribution (99th percentile)
- Parameter stability (jitter testing)
- Regime robustness (bull/bear/sideways)

**We take enormous pain to make this robust because it protects real capital.**

---

## ⚠️ CRITICAL RULES (Read Before Executing!)

1. **Work in hypothesis directory**: ALL file operations in `STRATEGIES/hypothesis_X/`
2. **Never at root**: Validation results go in hypothesis directory, NEVER at root
3. **Read iteration_state.json**: Find hypothesis directory and project_id from iteration_state.json
4. **Reuse project_id**: Use SAME project_id from iteration_state.json (created during /qc-backtest)
5. **Save to validation_logs/**: Results go in `STRATEGIES/hypothesis_X/validation_logs/`
6. **Allowed at root**: ONLY README.md, requirements.txt, .env, .gitignore, BOOTSTRAP.sh

**If you create validation files at root, the workflow WILL BREAK!**

---

## Pre-Flight Checks (Run at Start)

**Before executing this command, verify:**

```bash
# Check 1: We're at repository root
if [[ $(basename $(pwd)) != "CLAUDE_CODE_EXPLORE" ]]; then
    echo "⚠️  WARNING: Not at repository root"
    echo "Current: $(pwd)"
    exit 1
fi

# Check 2: Find hypothesis directory
HYPOTHESIS_DIR=$(find STRATEGIES -maxdepth 1 -name "hypothesis_*" -type d | sort | tail -1)
if [ -z "$HYPOTHESIS_DIR" ]; then
    echo "❌ ERROR: No hypothesis directory found!"
    echo "Run /qc-init first"
    exit 1
fi

# Check 3: iteration_state.json exists
if [ ! -f "${HYPOTHESIS_DIR}/iteration_state.json" ]; then
    echo "❌ ERROR: iteration_state.json not found!"
    exit 1
fi

# Check 4: Baseline backtest exists
BASELINE_SHARPE=$(jq -r '.backtest_results.performance.sharpe_ratio // empty' "${HYPOTHESIS_DIR}/iteration_state.json")
if [ -z "$BASELINE_SHARPE" ] || [ "$BASELINE_SHARPE" == "null" ]; then
    echo "❌ ERROR: No baseline backtest found!"
    echo "Run /qc-backtest first"
    exit 1
fi

# Check 5: Strategy file exists
STRATEGY_FILE=$(find "${HYPOTHESIS_DIR}" -name "*.py" -type f | head -1)
if [ -z "$STRATEGY_FILE" ]; then
    echo "❌ ERROR: No strategy file found!"
    exit 1
fi

# Check 6: Project ID exists
PROJECT_ID=$(jq -r '.project.project_id // empty' "${HYPOTHESIS_DIR}/iteration_state.json")
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" == "null" ]; then
    echo "❌ ERROR: No project_id found!"
    echo "Run /qc-backtest first"
    exit 1
fi

# Check 7: Create validation_logs directory
mkdir -p "${HYPOTHESIS_DIR}/validation_logs"

echo "✅ Pre-flight checks passed"
echo "📁 Hypothesis: ${HYPOTHESIS_DIR}"
echo "📊 Baseline Sharpe: ${BASELINE_SHARPE}"
echo "🆔 Project ID: ${PROJECT_ID}"
```

---

## Monte Carlo Validation Suite

### Phase 1: Baseline Metrics Collection

**Extract baseline performance from iteration_state.json:**

```bash
BASELINE_SHARPE=$(jq -r '.backtest_results.performance.sharpe_ratio' "${HYPOTHESIS_DIR}/iteration_state.json")
BASELINE_DRAWDOWN=$(jq -r '.backtest_results.performance.max_drawdown' "${HYPOTHESIS_DIR}/iteration_state.json")
BASELINE_RETURN=$(jq -r '.backtest_results.performance.total_return' "${HYPOTHESIS_DIR}/iteration_state.json")
BASELINE_TRADES=$(jq -r '.backtest_results.performance.total_trades' "${HYPOTHESIS_DIR}/iteration_state.json")
BASELINE_WINRATE=$(jq -r '.backtest_results.performance.win_rate' "${HYPOTHESIS_DIR}/iteration_state.json")

echo "Baseline Metrics:"
echo "  Sharpe: ${BASELINE_SHARPE}"
echo "  Max DD: ${BASELINE_DRAWDOWN}"
echo "  Return: ${BASELINE_RETURN}"
echo "  Trades: ${BASELINE_TRADES}"
echo "  Win Rate: ${BASELINE_WINRATE}"
```

### Phase 2: Run Advanced Monte Carlo Validation

**Execute qc_validate.py with Monte Carlo suite:**

```bash
cd "${HYPOTHESIS_DIR}"

python ../../SCRIPTS/qc_validate.py run \
    --strategy "${STRATEGY_FILE}" \
    --state iteration_state.json \
    --output validation_logs/monte_carlo_results.json \
    --monte-carlo-runs 1000 \
    --bootstrap-runs 5000 \
    --permutation-runs 10000 \
    --machr-runs 500 \
    --cpcv-splits 500
```

**This runs:**
1. **Combinatorial Purged Cross-Validation (CPCV)**
   - 500+ random train/test splits
   - Purging to prevent label overlap
   - Embargoing for serial correlation
   - Generates performance distributions

2. **Probabilistic Sharpe Ratio (PSR)**
   - Accounts for skewness, kurtosis, track record length
   - Threshold: PSR ≥ 0.95 (95% confidence)
   - 10th percentile PSR for worst-case assessment

3. **Deflated Sharpe Ratio (DSR)**
   - Corrects for multiple testing bias
   - Adjusts for number of trials tested
   - Threshold: DSR ≥ 0.95

4. **Minimum Track Record Length (MinTRL)**
   - Required observation count for confidence
   - Calculates if current track record sufficient

5. **Walk-Forward Efficiency (WFE)**
   - OOS returns / IS returns ratio
   - Threshold: WFE ≥ 50-60%
   - Tests generalization ability

6. **Bootstrap Resampling**
   - 5,000 trade sequence resamples
   - Generates alternative equity curves
   - MC drawdown distribution (2-3x larger than backtest)
   - 99th percentile drawdown analysis

7. **Market Condition Historical Randomization (MACHR)**
   - 500+ block-based bootstrapping runs
   - Tests across different regime sequences
   - Regime robustness assessment

8. **Permutation Testing**
   - 10,000 permutations of trade sequence
   - Exact significance without distributional assumptions
   - Threshold: p < 0.05

9. **Parameter Stability (Jitter Testing)**
   - ±5-10% random perturbations
   - Tests fragility vs robustness
   - Plateau width analysis

10. **Regime-Specific Performance**
    - Bull/Bear/Sideways separation
    - Positive in ≥2 of 3 regimes required
    - No single regime > 60% of returns

---

## Monte Carlo Results Analysis

### Extract Results from monte_carlo_results.json

```bash
RESULTS_FILE="${HYPOTHESIS_DIR}/validation_logs/monte_carlo_results.json"

# Probabilistic Sharpe Ratio
PSR=$(jq -r '.monte_carlo.psr.value' "$RESULTS_FILE")
PSR_10TH=$(jq -r '.monte_carlo.psr.percentile_10th' "$RESULTS_FILE")

# Deflated Sharpe Ratio
DSR=$(jq -r '.monte_carlo.dsr.value' "$RESULTS_FILE")

# Minimum Track Record Length
MIN_TRL=$(jq -r '.monte_carlo.min_trl.required_months' "$RESULTS_FILE")
CURRENT_TRL=$(jq -r '.monte_carlo.min_trl.current_months' "$RESULTS_FILE")

# Walk-Forward Efficiency
WFE=$(jq -r '.walk_forward.wfe.overall' "$RESULTS_FILE")
WFE_PROFITABLE_WINDOWS=$(jq -r '.walk_forward.profitable_windows_pct' "$RESULTS_FILE")

# Bootstrap Drawdown Distribution
MC_DD_99TH=$(jq -r '.bootstrap.drawdown.percentile_99th' "$RESULTS_FILE")
MC_DD_RATIO=$(jq -r '.bootstrap.drawdown.ratio_to_backtest' "$RESULTS_FILE")

# Permutation Test
PERM_PVALUE=$(jq -r '.permutation_test.pvalue' "$RESULTS_FILE")

# MACHR Regime Consistency
MACHR_CONSISTENCY=$(jq -r '.machr.consistency_score' "$RESULTS_FILE")
MACHR_CV=$(jq -r '.machr.coefficient_of_variation' "$RESULTS_FILE")

# Parameter Stability
PLATEAU_WIDTH=$(jq -r '.parameter_stability.plateau_width_ratio' "$RESULTS_FILE")
NEIGHBORHOOD_CORR=$(jq -r '.parameter_stability.neighborhood_correlation' "$RESULTS_FILE")

# Regime Performance
BULL_RETURN=$(jq -r '.regime_analysis.bull.return' "$RESULTS_FILE")
BEAR_RETURN=$(jq -r '.regime_analysis.bear.return' "$RESULTS_FILE")
SIDEWAYS_RETURN=$(jq -r '.regime_analysis.sideways.return' "$RESULTS_FILE")
```

---

## Decision Framework - Production-Ready Thresholds

### Tier 1: ROBUST_STRATEGY (Deploy to Production)

All criteria MUST pass:

```bash
DECISION="UNKNOWN"
REASON=""

# Check all thresholds
if (( $(echo "$PSR >= 0.95" | bc -l) )) && \
   (( $(echo "$PSR_10TH >= 0.90" | bc -l) )) && \
   (( $(echo "$DSR >= 0.95" | bc -l) )) && \
   (( $(echo "$WFE >= 0.50" | bc -l) )) && \
   (( $(echo "$WFE_PROFITABLE_WINDOWS >= 0.50" | bc -l) )) && \
   (( $(echo "$PERM_PVALUE < 0.05" | bc -l) )) && \
   (( $(echo "$MC_DD_RATIO < 2.5" | bc -l) )) && \
   (( $(echo "$MACHR_CV < 0.40" | bc -l) )) && \
   (( $(echo "$PLATEAU_WIDTH > 0.20" | bc -l) )) && \
   (( $(echo "$NEIGHBORHOOD_CORR > 0.70" | bc -l) )) && \
   [ "$CURRENT_TRL" -ge "$MIN_TRL" ]; then

    # Check regime robustness
    POSITIVE_REGIMES=0
    (( $(echo "$BULL_RETURN > 0" | bc -l) )) && ((POSITIVE_REGIMES++))
    (( $(echo "$BEAR_RETURN > 0" | bc -l) )) && ((POSITIVE_REGIMES++))
    (( $(echo "$SIDEWAYS_RETURN > 0" | bc -l) )) && ((POSITIVE_REGIMES++))

    if [ "$POSITIVE_REGIMES" -ge 2 ]; then
        DECISION="ROBUST_STRATEGY"
        REASON="Passed all Monte Carlo validation thresholds: PSR=$PSR (≥0.95), DSR=$DSR (≥0.95), WFE=$WFE (≥0.50), Perm p=$PERM_PVALUE (<0.05), MC DD Ratio=$MC_DD_RATIO (<2.5), MACHR CV=$MC_DD_RATIO (<0.40), Plateau Width=$PLATEAU_WIDTH (>0.20), Positive in $POSITIVE_REGIMES/3 regimes. Strategy is production-ready."
    fi
fi
```

### Tier 2: MARGINAL_VALIDATION (Needs Improvement)

Some thresholds fail but not catastrophic:

```bash
if [ "$DECISION" == "UNKNOWN" ]; then
    # Check for marginal cases
    FAILURES=()

    (( $(echo "$PSR < 0.95" | bc -l) )) && FAILURES+=("PSR=$PSR < 0.95")
    (( $(echo "$DSR < 0.95" | bc -l) )) && FAILURES+=("DSR=$DSR < 0.95")
    (( $(echo "$WFE < 0.50" | bc -l) )) && FAILURES+=("WFE=$WFE < 0.50")
    (( $(echo "$PERM_PVALUE >= 0.05" | bc -l) )) && FAILURES+=("Permutation p=$PERM_PVALUE ≥ 0.05")
    (( $(echo "$MC_DD_RATIO >= 2.5" | bc -l) )) && FAILURES+=("MC DD Ratio=$MC_DD_RATIO ≥ 2.5x")
    (( $(echo "$MACHR_CV >= 0.40" | bc -l) )) && FAILURES+=("MACHR CV=$MACHR_CV ≥ 0.40")
    (( $(echo "$PLATEAU_WIDTH <= 0.20" | bc -l) )) && FAILURES+=("Plateau Width=$PLATEAU_WIDTH ≤ 0.20")

    if [ ${#FAILURES[@]} -le 3 ]; then
        DECISION="MARGINAL_VALIDATION"
        REASON="Failed ${#FAILURES[@]} thresholds: ${FAILURES[*]}. Strategy shows promise but needs refinement before production deployment."
    fi
fi
```

### Tier 3: FAILED_VALIDATION (Abandon or Major Rework)

Critical failures - strategy not suitable for production:

```bash
if [ "$DECISION" == "UNKNOWN" ]; then
    CRITICAL_FAILURES=()

    # Critical failure conditions
    (( $(echo "$PSR < 0.80" | bc -l) )) && CRITICAL_FAILURES+=("PSR=$PSR < 0.80 (insufficient confidence)")
    (( $(echo "$WFE < 0.30" | bc -l) )) && CRITICAL_FAILURES+=("WFE=$WFE < 0.30 (severe overfitting)")
    (( $(echo "$MC_DD_RATIO > 3.0" | bc -l) )) && CRITICAL_FAILURES+=("MC DD Ratio=$MC_DD_RATIO > 3.0x (extreme path-dependent risk)")
    (( $(echo "$PERM_PVALUE > 0.10" | bc -l) )) && CRITICAL_FAILURES+=("Permutation p=$PERM_PVALUE > 0.10 (not statistically significant)")
    [ "$POSITIVE_REGIMES" -lt 2 ] && CRITICAL_FAILURES+=("Positive in only $POSITIVE_REGIMES/3 regimes (regime-dependent)")

    DECISION="FAILED_VALIDATION"
    REASON="Critical validation failures: ${CRITICAL_FAILURES[*]}. Strategy is NOT suitable for production. Consider major rework or abandonment."
fi
```

---

## Update iteration_state.json

```bash
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Update validation section
jq --arg decision "$DECISION" \
   --arg reason "$REASON" \
   --arg timestamp "$TIMESTAMP" \
   --argjson psr "$PSR" \
   --argjson dsr "$DSR" \
   --argjson wfe "$WFE" \
   --argjson min_trl "$MIN_TRL" \
   --argjson current_trl "$CURRENT_TRL" \
   --argjson perm_pvalue "$PERM_PVALUE" \
   --argjson mc_dd_99th "$MC_DD_99TH" \
   --argjson machr_consistency "$MACHR_CONSISTENCY" \
   '.validation.status = "completed" |
    .validation.method = "monte_carlo_advanced" |
    .validation.monte_carlo_runs = 1000 |
    .validation.psr = $psr |
    .validation.dsr = $dsr |
    .validation.wfe = $wfe |
    .validation.min_trl = $min_trl |
    .validation.current_trl = $current_trl |
    .validation.permutation_pvalue = $perm_pvalue |
    .validation.mc_drawdown_99th = $mc_dd_99th |
    .validation.machr_consistency = $machr_consistency |
    .validation.decision = $decision |
    .validation.reason = $reason |
    .validation.timestamp = $timestamp |
    .current_phase = "validation_complete" |
    .phases_completed += ["validation"] |
    .metadata.updated_at = $timestamp' \
    "${HYPOTHESIS_DIR}/iteration_state.json" > "${HYPOTHESIS_DIR}/iteration_state.tmp.json"

mv "${HYPOTHESIS_DIR}/iteration_state.tmp.json" "${HYPOTHESIS_DIR}/iteration_state.json"
```

---

## Append to decisions_log

```bash
jq --arg decision "$DECISION" \
   --arg reason "$REASON" \
   --arg timestamp "$TIMESTAMP" \
   --argjson psr "$PSR" \
   --argjson dsr "$DSR" \
   --argjson wfe "$WFE" \
   '.decisions_log += [{
       "phase": "validation",
       "decision": $decision,
       "reason": $reason,
       "timestamp": $timestamp,
       "metrics": {
           "psr": $psr,
           "dsr": $dsr,
           "wfe": $wfe,
           "permutation_pvalue": '$PERM_PVALUE',
           "mc_drawdown_ratio": '$MC_DD_RATIO',
           "machr_cv": '$MACHR_CV'
       }
   }]' "${HYPOTHESIS_DIR}/iteration_state.json" > "${HYPOTHESIS_DIR}/iteration_state.tmp.json"

mv "${HYPOTHESIS_DIR}/iteration_state.tmp.json" "${HYPOTHESIS_DIR}/iteration_state.json"
```

---

## Git Commit with Results

```bash
cd "${HYPOTHESIS_DIR}"

git add iteration_state.json validation_logs/

git commit -m "validate: Monte Carlo validation complete - ${DECISION}

Results:
- PSR: ${PSR} (10th percentile: ${PSR_10TH})
- DSR: ${DSR}
- WFE: ${WFE}
- Permutation p-value: ${PERM_PVALUE}
- MC Drawdown 99th: ${MC_DD_99TH} (${MC_DD_RATIO}x backtest)
- MACHR CV: ${MACHR_CV}
- Plateau Width: ${PLATEAU_WIDTH}
- Neighborhood Correlation: ${NEIGHBORHOOD_CORR}
- MinTRL: ${MIN_TRL} months (current: ${CURRENT_TRL})

Regime Performance:
- Bull: ${BULL_RETURN}
- Bear: ${BEAR_RETURN}
- Sideways: ${SIDEWAYS_RETURN}

Decision: ${DECISION}
Reason: ${REASON}

Phase: validation → complete

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Display Results Summary

```bash
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "MONTE CARLO VALIDATION COMPLETE"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📊 Probabilistic Metrics:"
echo "   PSR:              ${PSR} (threshold: ≥0.95)"
echo "   PSR 10th %ile:    ${PSR_10TH} (worst-case)"
echo "   DSR:              ${DSR} (multiple testing corrected)"
echo ""
echo "📈 Generalization:"
echo "   WFE:              ${WFE} (threshold: ≥0.50)"
echo "   Profitable Windows: ${WFE_PROFITABLE_WINDOWS}% (threshold: ≥50%)"
echo ""
echo "🎲 Statistical Significance:"
echo "   Permutation p:    ${PERM_PVALUE} (threshold: <0.05)"
echo ""
echo "📉 Drawdown Analysis:"
echo "   MC DD 99th:       ${MC_DD_99TH}"
echo "   MC/Backtest Ratio: ${MC_DD_RATIO}x (threshold: <2.5x)"
echo ""
echo "🔄 Regime Robustness:"
echo "   MACHR CV:         ${MACHR_CV} (threshold: <0.40)"
echo "   Bull Return:      ${BULL_RETURN}"
echo "   Bear Return:      ${BEAR_RETURN}"
echo "   Sideways Return:  ${SIDEWAYS_RETURN}"
echo ""
echo "🎯 Parameter Stability:"
echo "   Plateau Width:    ${PLATEAU_WIDTH} (threshold: >0.20)"
echo "   Neighborhood Corr: ${NEIGHBORHOOD_CORR} (threshold: >0.70)"
echo ""
echo "⏱️  Track Record:"
echo "   Required:         ${MIN_TRL} months"
echo "   Current:          ${CURRENT_TRL} months"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ DECISION: ${DECISION}"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "${REASON}"
echo ""

if [ "$DECISION" == "ROBUST_STRATEGY" ]; then
    echo "🚀 Strategy is PRODUCTION-READY for live trading!"
    echo ""
    echo "Next Steps:"
    echo "  1. Review validation_logs/monte_carlo_results.json"
    echo "  2. Set up paper trading with conservative position sizing"
    echo "  3. Monitor performance against Monte Carlo bands"
    echo "  4. Gradually scale to full allocation after 3-6 months"
    echo ""
elif [ "$DECISION" == "MARGINAL_VALIDATION" ]; then
    echo "⚠️  Strategy shows promise but needs improvement"
    echo ""
    echo "Next Steps:"
    echo "  1. Address failed thresholds through optimization"
    echo "  2. Consider parameter adjustments"
    echo "  3. Re-run validation after improvements"
    echo "  4. Do NOT deploy to live trading yet"
    echo ""
else
    echo "❌ Strategy FAILED validation - NOT suitable for production"
    echo ""
    echo "Next Steps:"
    echo "  1. Review validation_logs/monte_carlo_results.json for details"
    echo "  2. Consider major strategy rework or abandonment"
    echo "  3. Analyze which metrics failed and why"
    echo "  4. Start new hypothesis if fundamental issues exist"
    echo ""
fi

echo "Full results: ${HYPOTHESIS_DIR}/validation_logs/monte_carlo_results.json"
echo ""
```

---

## Notes

- **NO "quick" or "standard" levels** - only production-ready validation
- **All metrics required** - PSR, DSR, WFE, MACHR, bootstrap, permutation, parameter stability, regime robustness
- **Thresholds are strict** - this is the final gatekeeper before risking real money
- **Monte Carlo reveals truth** - drawdowns typically 2-3x larger than backtests
- **Execution time**: 30-60 minutes for full suite (1,000+ simulations)
- **Cost**: Higher than basic validation but essential for capital protection

## References

- Complete methodology: `PROJECT_DOCUMENTATION/VALIDATION/MONTECARLO_VALIDATION/CLAUDE_MC_VALIDATION_GUIDE.md`
- Python implementation: `SCRIPTS/qc_validate.py`
- Help system: `python SCRIPTS/qc_validate.py help`

---

**This is the ONLY validation command. There is no "quick" option because validation protects real capital.**
