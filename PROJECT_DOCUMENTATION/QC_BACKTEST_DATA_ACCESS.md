# QuantConnect Backtest Data Access

**Purpose**: Document working methods for accessing backtest data in QC Research notebooks

**Date**: 2025-11-14
**Status**: VERIFIED - Working methods confirmed via table.ipynb analysis

---

## Problem Context

QC Research environment has limitations with API methods:
- `api.list_backtests()` - May fail with NullReferenceException
- `qb.ReadBacktest()` - Doesn't exist in QuantBook
- Direct API calls unreliable in Research environment

**Solution**: Use documented API methods with proper error handling

---

## Working API Methods

### 1. Read Backtest Results

```python
from QuantConnect.Api import Api

# Initialize API (credentials from QC environment)
api = Api()
api.Initialize(user_id, token, organization_id)

# Read backtest - WORKS
backtest = api.read_backtest(project_id, backtest_id)

# Access result data
result = getattr(backtest, "result", {}) or {}
```

**Returns**: Complete backtest results including:
- Equity curve (nested in charts/series structure)
- Closed trades (TotalPerformance/ClosedTrades path)
- Statistics
- Charts data

---

### 2. Extract Equity Curve

**Pattern verified from** `/Users/donaldcross/ALGOS/Experimentos/Sanboxes/QC_PAD/PROFIT1_ORIGIN/table.ipynb:cell-1`

```python
def read_equity_curve(project_id, backtest_id):
    """
    Extract equity curve from QC backtest results.

    Returns:
        pd.DataFrame with columns: TimeTS, Equity
    """
    bt = api.read_backtest(project_id, backtest_id)
    res = getattr(bt, "result", {}) or {}

    # Walk nested structure to find equity series
    def _walk_series(o, name_hint=None):
        # yields (lower_name, values_list)
        if isinstance(o, dict):
            vals = o.get("Values") or o.get("values")
            if isinstance(vals, list) and len(vals)>0 and all(isinstance(v, (dict,)) for v in vals):
                nm = (o.get("Name") or o.get("name") or name_hint or "")
                yield (nm.lower(), vals)
            # handle QC chart container shapes
            ser = o.get("Series") or o.get("series")
            if isinstance(ser, dict):
                for v in ser.values():
                    yield from _walk_series(v, o.get("Name") or o.get("name"))
            if isinstance(ser, list):
                for v in ser:
                    yield from _walk_series(v, o.get("Name") or o.get("name"))
            for k,v in o.items():
                if k not in ("Series","series","Values","values","Name","name"):
                    yield from _walk_series(v, k)
        elif isinstance(o, list):
            for it in o:
                yield from _walk_series(it, name_hint)

    cands = list(_walk_series(res))
    chosen = None

    # Find equity series (prefer "equity" or "portfolio value")
    for nm, vals in cands:
        if "equity" in nm or ("portfolio" in nm and "value" in nm):
            chosen = vals
            break

    # Fallback: use longest series
    if chosen is None and cands:
        chosen = max(cands, key=lambda t: len(t[1]))[1]

    # Parse data points
    rows = []
    for p in chosen or []:
        x = p.get("x") or p.get("time") or p.get("Time")
        y = p.get("y") or p.get("value") or p.get("Value")
        if x is None or y is None:
            continue
        # Convert timestamp (milliseconds since epoch)
        ts = datetime.fromtimestamp(x/1000.0, tz=timezone.utc) if isinstance(x,(int,float)) else pd.to_datetime(x, utc=True)
        rows.append((ts, float(y)))

    return pd.DataFrame(rows, columns=["TimeTS","Equity"]).sort_values("TimeTS")
```

**Usage**:
```python
equity_df = read_equity_curve(project_id, backtest_id)
# Returns: DataFrame with timestamp and equity value for each data point
```

---

### 3. Read Order History

```python
def fetch_orders(project_id, backtest_id):
    """
    Fetch all orders from backtest (paginated).

    Returns:
        pd.DataFrame with order details
    """
    start, size, out = 0, 100, []

    while True:
        resp = api.read_backtest_orders(project_id, backtest_id, start, start+size)
        batch = getattr(resp, "orders", resp) or []
        if not batch:
            break
        out.extend(batch)
        if len(batch) < size:
            break
        start += size

    # Parse orders into DataFrame
    rows = []
    for x in out:
        o = getattr(x, "order", x)
        sym = getattr(getattr(o, "symbol", ""), "value", str(getattr(o, "symbol", "")))
        t = pd.to_datetime(getattr(o, "time", None), utc=True)
        px = float(getattr(o, "price", 0) or 0)
        qty = int(getattr(o, "quantity", 0) or 0)
        # ... extract other fields ...
        rows.append(dict(TimeTS=t, Symbol=sym, Price=px, Quantity=qty))

    return pd.DataFrame(rows).sort_values("TimeTS")
```

---

### 4. Extract Closed Trades

```python
def closed_trades_df(project_id, backtest_id):
    """
    Extract closed trades from backtest results.

    Returns:
        pd.DataFrame with Symbol, ExitTime, NetProfit, Key
    """
    bt = api.read_backtest(project_id, backtest_id)
    res = getattr(bt, "result", {}) or {}

    # Try known paths
    paths = [
        ["TotalPerformance", "ClosedTrades"],
        ["TradeBuilder", "ClosedTrades"],
        ["tradeBuilder", "closedTrades"],
        ["ClosedTrades"]
    ]

    items = None
    for path in paths:
        cur = res
        ok = True
        for k in path:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok:
            items = cur
            break

    # Parse trades
    rows = []
    for tr in items or []:
        sym = tr.get("Symbol") or tr.get("symbol") or {}
        if isinstance(sym, dict):
            sym = sym.get("Value") or sym.get("value") or str(sym)
        exit_time = tr.get("ExitTime") or tr.get("exitTime") or tr.get("CloseTime") or tr.get("closeTime")
        pnl = tr.get("ProfitLoss") or tr.get("profitLoss") or tr.get("Profit") or tr.get("profit")
        fees = tr.get("TotalFees") or tr.get("totalFees") or 0

        if exit_time is None or pnl is None:
            continue

        rows.append(dict(
            Symbol=sym,
            ExitTime=pd.to_datetime(exit_time, utc=True),
            NetProfit=float(pnl)-float(fees or 0)
        ))

    return pd.DataFrame(rows).sort_values("ExitTime") if rows else pd.DataFrame(columns=["Symbol","ExitTime","NetProfit"])
```

---

## Monte Carlo Validation Workflow

**For Hypothesis 7 Statistical Arbitrage validation:**

### Step 1: Extract Equity Curve

```python
from QuantConnect.Api import Api
from datetime import datetime, timezone
import pandas as pd
import numpy as np

# Initialize API
api = Api()
project_id = qb.project_id

# Use known backtest ID
backtest_id = '67dd62a13c9acfba69bb3493'

# Extract equity curve
equity_df = read_equity_curve(project_id, backtest_id)

print(f'Loaded {len(equity_df)} equity data points')
print(f'Date range: {equity_df["TimeTS"].min()} to {equity_df["TimeTS"].max()}')
```

### Step 2: Calculate Returns

```python
# Calculate returns from equity curve
returns = equity_df['Equity'].pct_change().dropna()

# Verify data quality
print(f'Total returns: {len(returns)}')
print(f'Mean return: {returns.mean():.6f}')
print(f'Std return: {returns.std():.6f}')
```

### Step 3: Run Monte Carlo Validation

Use returns data for:
- **PSR (Probabilistic Sharpe Ratio)**: Calculate with skew/kurtosis adjustments
- **DSR (Deflated Sharpe Ratio)**: Correct for multiple testing
- **MinTRL (Minimum Track Record Length)**: Required observations
- **Bootstrap Resampling**: 1,000 runs with replacement
- **Permutation Testing**: Statistical significance (p < 0.05)

All metrics use REAL equity curve data, not synthetic.

---

## Error Handling

**Always use try/except with fallbacks:**

```python
try:
    # Attempt API call
    equity_df = read_equity_curve(project_id, backtest_id)

    if equity_df.empty:
        raise ValueError("No equity data found")

    # Proceed with validation
    returns = equity_df['Equity'].pct_change().dropna()

except Exception as e:
    print(f'Error extracting equity curve: {e}')
    print('Manual fallback required - check backtest ID and data availability')
    raise
```

---

## API Initialization in Research

**QC Research notebooks have credentials in environment:**

```python
from QuantConnect.Api import Api

# API credentials should be available in QC environment
# If not, initialize explicitly:
uid = "YOUR_USER_ID"
tok = "YOUR_TOKEN"
org = "YOUR_ORG_ID"

api = Api()
api.Initialize(int(uid), tok, org)
```

**Best Practice**: Let QC environment handle credentials when possible.

---

## References

**Source Notebook**: `/Users/donaldcross/ALGOS/Experimentos/Sanboxes/QC_PAD/PROFIT1_ORIGIN/table.ipynb`

**Verified Methods**:
- `api.read_backtest(project_id, backtest_id)` - cell-1, cell-2
- `api.read_backtest_orders(project_id, backtest_id, start, end)` - cell-1, cell-2
- Equity curve extraction pattern - cell-1 `read_equity_curve()` function
- Closed trades extraction - cell-1 `closed_trades_df()` function

**QC Documentation**: https://www.quantconnect.com/docs/v2/research-environment

---

## Next Steps for H7 Validation

1. Update `research.ipynb` to use `read_equity_curve()` pattern
2. Extract equity curve from backtest ID: `67dd62a13c9acfba69bb3493`
3. Calculate returns from real equity data
4. Run Monte Carlo validation with proper data
5. Collect results via `qc_validate collect-results`

---

**Status**: Ready for implementation
**Validation**: Pattern confirmed working in production notebook
