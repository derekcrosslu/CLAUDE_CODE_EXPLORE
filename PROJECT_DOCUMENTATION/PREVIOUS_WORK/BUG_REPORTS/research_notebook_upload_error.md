# Research Notebook Upload Error - Root Cause Analysis

**Date**: 2025-11-11
**Status**: ROOT CAUSE IDENTIFIED ✓
**Severity**: MEDIUM - User confusion, created duplicate files

## What Happened

When asked to update `research.ipynb` in project 26140717, I made TWO uploads:

1. **First Upload (16:04:50)**: Created NEW file `monte_carlo_walkforward_stat_arb.ipynb` ❌
2. **Second Upload (16:09:17)**: Correctly updated existing `research.ipynb` ✓

User had to manually delete the duplicate file.

## Root Cause

**I used the WRONG filename in the first upload.**

### What I Did Wrong (First Upload):

```python
# Read from local file
notebook_path = "STRATEGIES/hypothesis_5_statistical_arbitrage/monte_carlo_walkforward_stat_arb.ipynb"
with open(notebook_path, 'r') as f:
    content = f.read()

# WRONG: Used files/create with the LOCAL filename
result = api._request("POST", "files/create", json={
    "projectId": 26140717,
    "name": "monte_carlo_walkforward_stat_arb.ipynb",  # ❌ WRONG FILENAME!
    "content": content
})
```

**Problem**: I used the LOCAL file's name (`monte_carlo_walkforward_stat_arb.ipynb`) instead of the TARGET file's name (`research.ipynb`).

**Result**: Created a new file in the QC project instead of updating the existing one.

### What I Did Correctly (Second Upload):

```python
# Read from same local file
notebook_path = "STRATEGIES/hypothesis_5_statistical_arbitrage/monte_carlo_walkforward_stat_arb.ipynb"
with open(notebook_path, 'r') as f:
    content = f.read()

# CORRECT: Used files/update with the TARGET filename
result = api._request("POST", "files/update", json={
    "projectId": 26140717,
    "name": "research.ipynb",  # ✓ CORRECT FILENAME!
    "content": content
})
```

**Result**: Successfully updated the existing `research.ipynb` file.

## Why This Happened

**Mental Model Error**: I confused the SOURCE file (local) with the DESTINATION file (remote).

- **LOCAL file**: `monte_carlo_walkforward_stat_arb.ipynb` (where I read content FROM)
- **REMOTE file**: `research.ipynb` (where I should upload content TO)

I mistakenly used the source filename as the destination filename.

## What I Should Have Done

### Option 1: Use the helper method

```python
api.upload_file(26140717, "research.ipynb", content)
# OR
api.create_file(26140717, "research.ipynb", content)
```

Both methods:
- Try `files/update` first
- Fall back to `files/create` if file doesn't exist
- Require explicit filename parameter (forces me to think about destination)

### Option 2: Explicit destination mapping

```python
local_file = "STRATEGIES/hypothesis_5_statistical_arbitrage/monte_carlo_walkforward_stat_arb.ipynb"
remote_file = "research.ipynb"  # EXPLICIT destination

with open(local_file, 'r') as f:
    content = f.read()

api.upload_file(26140717, remote_file, content)
```

## Lessons Learned

1. **Separate source and destination concepts**: Don't derive destination filename from source filename
2. **Use helper methods**: `upload_file()` and `create_file()` have better error handling
3. **Explicit is better than implicit**: Always declare destination filename explicitly
4. **Verify before executing**: Should have checked "what file am I updating?" before calling API

## Prevention Strategy - UPDATED SOLUTION ✓

**User's Solution (CORRECT)**: Use `research.ipynb` as the LOCAL filename to match QC platform convention.

### New Convention:
```
STRATEGIES/hypothesis_X_name/
├── research.ipynb          # ✓ Monte Carlo / Research notebooks (matches QC)
├── main.py                 # Strategy implementation
└── ...
```

### Why This Works:
1. **Local filename = Remote filename**: No mental translation needed
2. **Platform consistency**: Matches QuantConnect's research.ipynb convention
3. **Simpler uploads**: Just use the same filename everywhere
4. **No confusion**: Source and destination are the same name

### Updated Upload Pattern:
```python
# Simple and consistent
local_file = "STRATEGIES/hypothesis_5_statistical_arbitrage/research.ipynb"
remote_file = "research.ipynb"  # Same name!

with open(local_file, 'r') as f:
    content = f.read()

api.upload_file(project_id, remote_file, content)
```

## Impact

- ✗ User confusion
- ✗ Created duplicate file (user had to clean up)
- ✓ Eventually fixed with correct upload
- ✓ No data loss or corruption
- ✓ **SOLUTION**: Renamed local file to `research.ipynb` for consistency

---

**Status**: Issue resolved - local file renamed to match QC platform convention
