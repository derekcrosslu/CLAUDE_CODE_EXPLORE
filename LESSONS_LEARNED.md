# Lessons Learned - QuantConnect Strategy Development

## Critical Bugs Encountered and Fixed

### Bug #1: NoneType AttributeError in on_data()

**Date**: 2025-11-10
**Hypothesis**: Momentum Breakout Strategy (H2)

**Error**:
```
Runtime Error: 'NoneType' object has no attribute 'close'
at on_data
    self.price_window.add(bar.close)
in main.py: line 70
```

**Root Cause**:
Even when `data.contains_key(symbol)` returns True, the data object `data[symbol]` can still be None.

**Incorrect Code**:
```python
def on_data(self, data):
    if not data.contains_key(self.symbol):
        return

    bar = data[self.symbol]  # ❌ Can be None!
    self.price_window.add(bar.close)  # ERROR
```

**Correct Code**:
```python
def on_data(self, data):
    if not data.contains_key(self.symbol):
        return

    bar = data[self.symbol]

    # CRITICAL: Always validate bar is not None
    if bar is None:
        return

    self.price_window.add(bar.close)  # Safe
```

**Lesson**: **ALWAYS add explicit None check after retrieving data objects from QuantConnect API**

---

### Bug #2: Impossible Breakout Condition (Off-by-One Logic Error)

**Date**: 2025-11-10
**Hypothesis**: Momentum Breakout Strategy (H2)
**Impact**: Zero trades generated

**Error**:
Strategy generated 0 trades despite 2-year backtest period in trending market.

**Root Cause**:
Calculating the 20-day high from a rolling window that **includes today's price**, then comparing today's price to that high. This creates an impossible condition:

- If today is a new high: `current_price == high_20` (not greater)
- If today is not a new high: `current_price < high_20`
- **Result**: `current_price > high_20` is NEVER true

**Incorrect Code**:
```python
# on_data() adds today's price to window
self.price_window.add(bar.close)

# check_signals() calculates high including today
high_20 = max([self.price_window[i] for i in range(self.price_window.count)])
breakout = current_price > high_20  # ❌ IMPOSSIBLE - current price is IN the window!
```

**Correct Code**:
```python
# on_data() adds today's price to window
self.price_window.add(bar.close)  # price_window[0] = today

# check_signals() calculates high from PREVIOUS days only
# Start from index 1 to exclude today (index 0)
high_20 = max([self.price_window[i] for i in range(1, self.price_window.count)])
breakout = current_price > high_20  # ✅ Comparing to PREVIOUS 20-day high
```

**Also Updated**:
```python
# Volume average should also exclude today for consistency
avg_volume = sum([self.volume_window[i] for i in range(1, self.volume_window.count)]) / (self.volume_window.count - 1)
```

**Lesson**: **When using rolling windows that include current data, always exclude the current observation when calculating reference values for comparison**

---

## Best Practices for QuantConnect Strategies

### 1. Data Validation
```python
def on_data(self, data):
    # Check 1: Key exists
    if not data.contains_key(self.symbol):
        return

    # Check 2: Data object is not None
    bar = data[self.symbol]
    if bar is None:
        return

    # Now safe to use bar.close, bar.volume, etc.
```

### 2. Rolling Window Usage for Breakouts
```python
# When detecting breakouts, exclude current observation
def check_signals(self):
    current_price = self.securities[self.symbol].price

    # Calculate reference from PREVIOUS periods only
    # price_window[0] = today, so start from index 1
    previous_high = max([self.price_window[i] for i in range(1, self.price_window.count)])

    # Compare current to previous
    breakout = current_price > previous_high  # Correct
```

### 3. Indicator Calculation Pattern
```python
# WRONG: Include current observation in reference calculation
current_value = self.window[0]
reference = max([self.window[i] for i in range(self.window.count)])  # ❌ Includes current!
signal = current_value > reference  # Never true for new highs

# RIGHT: Exclude current observation from reference
current_value = self.window[0]
reference = max([self.window[i] for i in range(1, self.window.count)])  # ✅ Previous only
signal = current_value > reference  # Correct breakout detection
```

### 4. Testing Checklist
Before running backtest:
- [ ] Added None checks after all data retrievals?
- [ ] Rolling windows exclude current observation for comparisons?
- [ ] Entry conditions are logically possible?
- [ ] Warm-up period covers indicator lookback?
- [ ] Position sizing validates quantity > 0?
- [ ] Debug statements included for trade entry/exit?

---

## Strategy-Specific Notes

### Momentum Breakout Strategy
- **Window Size**: 20 days for high detection
- **Volume Multiplier**: 1.5x for surge confirmation
- **Entry**: Price > previous 20-day high AND volume > 1.5x average
- **Exit**: 10% stop loss OR price < previous 20-day high
- **Fixed**: Exclude current day from high/volume calculations

### Mean Reversion Strategy (H1 - Abandoned)
- **Issue**: 0 trades in 2023 (strong bull market)
- **Root Cause**: Strategy type incompatible with market regime
- **Lesson**: Match strategy type to expected market conditions

---

## Git Workflow

After fixing bugs:
1. Update strategy file
2. Document fix in this file
3. Commit with clear message:
```bash
git add momentum_breakout.py LESSONS_LEARNED.md
git commit -m "fix: Correct breakout logic to exclude current price from reference high

- Bug: Comparing current price to high that includes current price
- Fix: Calculate high from previous 20 days only (exclude today)
- Result: Enables proper breakout detection

This prevented all trades from generating (0 trades in 2-year period)"
```

---

**Last Updated**: 2025-11-10
**Hypothesis**: 2 (Momentum Breakout Strategy)
**Bugs Fixed**: 2
