# Monte Carlo Validation Enhancement Plan

**Date**: 2025-11-11
**Status**: IN PROGRESS
**Notebook**: research.ipynb

## Completed ✅

1. **Added Advanced Metrics Functions** (New Cell after Cell 4)
   - `calculate_return_statistics()` - Returns mean, std, skewness, kurtosis, sharpe
   - `calculate_probabilistic_sharpe_ratio()` - PSR with benchmark (threshold: ≥0.95)
   - `calculate_minimum_track_record_length()` - MinTRL calculation
   - `calculate_deflated_sharpe_ratio()` - DSR for multiple testing correction
   - `analyze_mc_distribution()` - Percentiles (p10, p25, median, p75, p90)
   - `calculate_confidence_interval()` - CI calculation
   - `assess_sample_size_adequacy()` - Sample size validation

## Next Steps 🔧

### 2. Modify Monte Carlo Execution Loop (Cell 6 - Now Cell 7)

Need to store additional data in results dict:

```python
# After running strategy, calculate return stats
train_stats = calculate_return_statistics(train_equity)
test_stats = calculate_return_statistics(test_equity)

# Calculate PSR for test period
test_psr = calculate_probabilistic_sharpe_ratio(
    test_sharpe,
    test_stats,
    benchmark_sr=0.0  # Test against SR > 0
)

# Calculate MinTRL
min_trl = calculate_minimum_track_record_length(
    test_sharpe,
    test_stats,
    benchmark_sr=0.0
)

# Store in results
results.append({
    # ... existing fields ...
    'test_psr': float(test_psr),
    'test_skewness': test_stats['skewness'],
    'test_kurtosis': test_stats['kurtosis'],
    'test_observations': test_stats['observations'],
    'min_trl': min_trl,
    'train_skewness': train_stats['skewness'],
    'train_kurtosis': train_stats['kurtosis'],
})
```

### 3. Enhance Analysis Cell (Cell 7 - Now Cell 8)

Add after basic statistics:

```python
# PSR Analysis
test_psrs = [r['test_psr'] for r in results]
psr_dist = analyze_mc_distribution(test_psrs)

print(f"\nProbabilistic Sharpe Ratio Analysis:")
print(f"  Median PSR: {psr_dist['median']:.3f}")
print(f"  10th Percentile PSR: {psr_dist['p10']:.3f}")  # Worst case in 90% scenarios
print(f"  Mean PSR: {psr_dist['mean']:.3f}")
print(f"  Status: {'PASS' if psr_dist['p10'] >= 0.95 else 'MARGINAL' if psr_dist['p10'] >= 0.90 else 'FAIL'}")
print(f"  (Threshold: PSR ≥ 0.95 for statistical significance)")

# Distribution Analysis
test_sharpe_dist = analyze_mc_distribution(df_results['test_sharpe'])
print(f"\nTest Sharpe Distribution:")
print(f"  10th Percentile: {test_sharpe_dist['p10']:.3f}")
print(f"  Median: {test_sharpe_dist['median']:.3f}")
print(f"  90th Percentile: {test_sharpe_dist['p90']:.3f}")
print(f"  Skewness: {test_sharpe_dist['skewness']:.2f}")
print(f"  Kurtosis: {test_sharpe_dist['kurtosis']:.2f}")

# Deflated Sharpe Ratio (if multiple parameter sets tested)
test_sharpes = df_results['test_sharpe'].values
dsr = calculate_deflated_sharpe_ratio(test_sharpes)
print(f"\nDeflated Sharpe Ratio: {dsr:.3f}")
print(f"  (Accounts for {len(test_sharpes)} Monte Carlo trials)")

# MinTRL Analysis
min_trls = [r['min_trl'] for r in results if r['min_trl'] < float('inf')]
if min_trls:
    print(f"\nMinimum Track Record Length:")
    print(f"  Mean: {np.mean(min_trls):.0f} observations")
    print(f"  Actual: {test_stats['observations']} observations")
    print(f"  Status: {'ADEQUATE' if test_stats['observations'] >= np.mean(min_trls) else 'INSUFFICIENT'}")

# Sample Size Adequacy
mean_test_trades = df_results['test_trades'].mean()
sample_assessment = assess_sample_size_adequacy(int(mean_test_trades))
print(f"\nSample Size Assessment:")
print(f"  Average Test Trades: {mean_test_trades:.0f}")
print(f"  Adequacy: {sample_assessment['adequacy']}")
print(f"  Confidence: {sample_assessment['confidence']}")
```

### 4. Enhanced HTML Report (Cell 8 - Now Cell 9)

Add new sections:

```python
# Add PSR metrics card
<div class="metric-card">
    <div class="metric-label">Median Test PSR</div>
    <div class="metric-value">{psr_dist['median']:.3f}</div>
    <div class="metric-subtext">10th percentile: {psr_dist['p10']:.3f}</div>
</div>

# Add PSR to overfitting indicators table
<tr>
    <td>7. Probabilistic Sharpe Ratio</td>
    <td>{psr_dist['median']:.3f} (p10: {psr_dist['p10']:.3f})</td>
    <td>{'SIGNIFICANT' if psr_dist['p10'] >= 0.95 else 'MARGINAL' if psr_dist['p10'] >= 0.90 else 'NOT SIGNIFICANT'}</td>
    <td class="{'status-good' if psr_dist['p10'] >= 0.95 else 'status-warn' if psr_dist['p10'] >= 0.90 else 'status-bad'}">
        {'✓' if psr_dist['p10'] >= 0.95 else '⚠' if psr_dist['p10'] >= 0.90 else '✗'}
    </td>
</tr>

# Add distribution percentiles section
<h2>Distribution Analysis</h2>
<table>
    <tr><th>Metric</th><th>10th %ile</th><th>Median</th><th>90th %ile</th><th>Interpretation</th></tr>
    <tr>
        <td>Test Sharpe</td>
        <td>{test_sharpe_dist['p10']:.3f}</td>
        <td>{test_sharpe_dist['median']:.3f}</td>
        <td>{test_sharpe_dist['p90']:.3f}</td>
        <td>Use 10th percentile for conservative planning</td>
    </tr>
</table>
```

## Key Metrics to Display

### Primary Metrics (Must Have)
1. **PSR** - Probabilistic Sharpe Ratio (median and 10th percentile)
   - Threshold: PSR(p10) ≥ 0.95
2. **Distribution Percentiles** - 10th, 50th, 90th for all key metrics
   - Focus on 10th percentile (worst-case planning)
3. **DSR** - Deflated Sharpe Ratio (if multiple tests)
   - Threshold: DSR ≥ 0.95
4. **MinTRL** - Minimum Track Record Length
   - Compare actual observations vs required
5. **Sample Size Adequacy** - Statistical power assessment
   - Need 100+ trades minimum

### Secondary Metrics (Nice to Have)
- Skewness and kurtosis of returns
- Confidence intervals (95%)
- Trade independence (autocorrelation)

## Testing Checklist

Before uploading to QC:

- [ ] Cell 5 (Advanced Metrics) loads without errors
- [ ] Cell 7 (MC Loop) stores all new fields
- [ ] Cell 8 (Analysis) calculates PSR, DSR, distributions
- [ ] Cell 9 (HTML) displays new metrics
- [ ] All metrics display correctly inline
- [ ] No console truncation issues
- [ ] Sample data (20 runs) completes successfully
- [ ] Scale to 100+ runs for production

## References

- Bailey & López de Prado (2012) - "The Sharpe Ratio Efficient Frontier" (PSR)
- Bailey & López de Prado (2014) - "The Deflated Sharpe Ratio" (DSR, MinTRL)
- Monte Carlo Validation Guide - `/PROJECT_DOCUMENTATION/MONTECARLO_VALIDATION/CLAUDE_MC_VALIDATION_GUIDE.md`

## Notes

- **PSR is THE most important metric** - Focus on getting this right
- Use 10th percentile PSR for parameter selection (not mean)
- DSR only needed if we tested multiple parameter sets
- Keep HTML inline (no file downloads) per QC Research constraints
- Test with 20 runs first, then scale to 1000+

## Status Summary

**Completed**: Advanced metrics functions added
**In Progress**: Need to modify MC loop and analysis cells
**Remaining**: HTML enhancements, testing, upload

**Next Session**: Continue from modifying Cell 6/7 (MC execution loop)
