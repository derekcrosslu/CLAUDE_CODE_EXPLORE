# Monte Carlo Walk-Forward - Correct Usage

## ⚠️ IMPORTANT: Cost-Free Workflow

The **CORRECT** way to run Monte Carlo walk-forward validation:

### Step 1: Upload Notebook (FREE)
```bash
python3 upload_research_notebook.py \
  --project-id 26129044 \
  --notebook monte_carlo_walkforward_REAL.ipynb
```

This uploads your notebook to the `research.ipynb` file in your project.

**Cost: $0** (File management API is free)

### Step 2: Run in QC Research (FREE)
1. Go to https://www.quantconnect.com/project/26129044
2. Click the **Research** tab
3. The notebook will be loaded automatically
4. Click "Run All Cells" or run cells individually

**Cost: $0** (Optimization inside Research environment is free)

---

## ❌ What NOT to Do

**DO NOT USE** `qc_walkforward_wrapper.py`

That script calls `/optimizations/create` API endpoint which:
- ❌ Costs money ($0.50-$5+ per optimization)
- ❌ Requires paid tier
- ❌ Uses API quota

---

## Why This Approach Works

### API Optimization (PAID) vs Research Optimization (FREE)

| Method | API Endpoint | Cost | When to Use |
|--------|-------------|------|-------------|
| **API Optimization** | `/optimizations/create` | 💰 $0.50+ per run | Automated workflows, CI/CD |
| **Research Optimization** | `qb.Optimize()` in notebook | ✅ FREE | Manual testing, exploration |

### The Workflow

```
Local Machine                QC Cloud
     │                           │
     │  1. Upload notebook       │
     │  ────────────────────────>│
     │     (research.ipynb)      │
     │                           │
     │                      2. Open Research
     │                           │
     │                      3. Run qb.Optimize()
     │                           │ (FREE!)
     │                           │
     │  4. View results          │
     │  <────────────────────────│
```

---

## Files in This Project

| File | Purpose | Use It? |
|------|---------|---------|
| `upload_research_notebook.py` | Upload notebook to QC | ✅ YES |
| `monte_carlo_walkforward_REAL.ipynb` | Monte Carlo notebook | ✅ YES |
| `qc_walkforward_wrapper.py` | Old API wrapper | ❌ DEPRECATED |
| `qc_backtest.py` | API client library | ✅ YES (internal) |

---

## Complete Example

### Configure the Notebook

Edit `monte_carlo_walkforward_REAL.ipynb` Cell 2:

```python
config = {
    'project_id': 26129044,
    'total_period': {
        'start': datetime(2023, 1, 1),
        'end': datetime(2024, 12, 31)
    },
    'train_test_split': 0.60,
    'monte_carlo_runs': 10,
    'parameters': {
        'lookback_period': {'min': 15, 'max': 25, 'step': 5},
        'volume_multiplier': {'min': 1.3, 'max': 1.7, 'step': 0.2}
    }
}
```

### Upload to QC

```bash
python3 upload_research_notebook.py --project-id 26129044
```

### Run in QC Research

Navigate to: https://www.quantconnect.com/project/26129044

Click **Research** → **Run All Cells**

### View Results

The notebook will output:
- Aggregate statistics
- Parameter stability analysis
- Robustness decision (ROBUST/CAUTION/ABANDON)
- 4 visualization plots
- JSON results file

---

## Troubleshooting

### Upload fails with "file too large"
- Notebook size limit: 128KB
- Remove unnecessary cells or outputs

### "Project not found"
- Verify project ID is correct
- Check you have access to the project

### Optimization times out
- Reduce `monte_carlo_runs` (start with 3)
- Narrow parameter ranges
- Use smaller date range

---

## Summary

✅ **DO**: Upload notebook → Run in Research (FREE)

❌ **DON'T**: Use API wrapper with optimization calls (PAID)

The Monte Carlo framework is designed to run entirely within the QC Research environment where optimization is free.
