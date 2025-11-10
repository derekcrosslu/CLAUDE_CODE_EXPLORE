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

## API & Architecture Lessons (Nov 10, 2025)

### Lesson #3: Always Verify API Methods Exist Before Building

**Date**: 2025-11-10
**Context**: Monte Carlo Walk-Forward Implementation

**Assumption (WRONG)**:
Based on examples and forum posts, assumed these methods existed:
- `qb.Optimize()` - To run optimizations from research notebooks
- `qb.Backtest()` - To run backtests from research notebooks

**Reality**:
These methods DO NOT EXIST in QuantConnect's QuantBook API.

**What Actually Exists**:
```python
# From within Research notebooks (api variable is auto-available):
from QuantConnect.Api import Api
api = Api()  # Already authenticated

# Create jobs (then wait for completion)
optimization = api.create_optimization(...)  # Costs $3-5
backtest = api.create_backtest(...)  # FREE

# Read results
opt_results = api.read_optimization(optimization_id)
backtest_results = api.read_backtest(project_id, backtest_id)
```

**Impact**:
- Entire Monte Carlo notebook built with wrong methods
- 8 hours of research required to discover correct approach
- Notebook requires complete rewrite

**Lesson**: **Test API methods against real environment before building workflows. Don't rely solely on documentation or forum posts - verify with actual API calls.**

---

### Lesson #4: "Local" Doesn't Mean "Free"

**Date**: 2025-11-10
**Context**: Cost analysis for LEAN CLI

**Assumption (WRONG)**:
"Running LEAN locally = no costs" (compared to cloud API costs)

**Reality**:
Local LEAN CLI costs $2,000-4,000/year:
- Researcher subscription: $720/year (required)
- Security Master: $600/year (required for US Equities)
- Data downloads: $600-2,500/year (per-file charges)

**Comparison**:
- Local LEAN: $2,000-4,000/year
- Cloud API: $0-720/year
- **Cloud is 2-6x CHEAPER**

**Lesson**: **Infrastructure has costs. Always research actual pricing before recommending "local" solutions. Cloud services often include data, making them cheaper than self-hosted.**

---

### Lesson #5: Perfect is the Enemy of Good (90% vs 100% Autonomy)

**Date**: 2025-11-10
**Context**: Architecture decision

**Trade-off Analysis**:
- **100% Autonomous**: Use API optimization → Costs $3-5 per hypothesis
- **90% Autonomous**: User clicks "Run All" once → Costs $0

**Decision**: Accept 90% autonomy
- Manual step takes 1 minute
- Saves $3-5 per hypothesis
- Framework still highly effective

**Lesson**: **Don't over-engineer for 100% autonomy if 90% achieves the goal at a fraction of the cost. Consider cost/benefit carefully.**

---

### Lesson #6: API Limitations Shape Architecture

**Date**: 2025-11-10
**Context**: Research notebook execution

**Discovery**:
QuantConnect provides:
- ✅ Full READ/WRITE access to notebook files via API
- ✅ Can upload and download .ipynb files
- ✅ Can read cell outputs after execution
- ❌ NO remote execution capability
- ❌ NO "Run All" trigger via API

**Architectural Impact**:
Can't build fully autonomous notebook execution. Must adopt hybrid approach:
1. Upload notebook via API (automated)
2. User runs notebook in Research UI (manual)
3. Read results via API (automated)

**Lesson**: **API limitations constrain architecture. Design around what's possible, not what's ideal. Hybrid approaches are often the pragmatic solution.**

---

### Lesson #7: Emoji Characters Break QC API

**Date**: 2025-11-10
**Context**: Notebook upload

**Error**:
```
API Error: File not saved. The file contents of 'research.ipynb'
contains invalid characters near 🔍
```

**Cause**: QC API rejects emoji characters in file uploads

**Fix**: Remove all emojis, use text equivalents:
- ✅ → [OK]
- ❌ → [ERROR]
- ⚠️ → [WARNING]
- 🔍 → (remove or use "SEARCH")

**Lesson**: **Enterprise APIs often have character encoding restrictions. Avoid emojis in programmatically-uploaded files. Stick to ASCII or basic Unicode.**

---

### Lesson #8: One Question Can Reveal Major Flaws

**Date**: 2025-11-10
**Context**: User asked "Did you include data costs?"

**What Happened**:
- I had recommended "free local LEAN" approach
- One question revealed I hadn't researched data costs
- Data costs made "free" solution actually the MOST expensive option

**Impact**:
- Complete architecture reversal (local → cloud)
- 8 hours of corrective research
- Multiple documentation updates

**Lesson**: **Welcome challenging questions. They expose blind spots and prevent expensive mistakes. Always research ALL cost components before making recommendations.**

---

### Lesson #9: OptimizationParameter is NOT for API Calls

**Date**: 2025-11-10
**Context**: Monte Carlo notebook execution error

**Error**:
```
NameError: name 'OptimizationParameter' is not defined
at format_optimization_params()
```

**Root Cause**:
`OptimizationParameter` is a LEAN algorithm framework class, NOT part of the Research/API framework.

**Wrong Code**:
```python
# ❌ This is WRONG for API calls
from QuantConnect.Optimizer import OptimizationParameter

def format_optimization_params(params_config):
    opt_params = []
    for name, config in params_config.items():
        param = OptimizationParameter(  # ❌ NOT available in Research
            name,
            config['min'],
            config['max'],
            config['step']
        )
        opt_params.append(param)
    return opt_params
```

**Correct Code**:
```python
# ✅ Use plain dictionaries for API calls
def format_optimization_params(params_config):
    opt_params = []
    for name, config in params_config.items():
        param = {  # ✅ Plain dictionary
            'key': name,
            'min': config['min'],
            'max': config['max'],
            'step': config['step']
        }
        opt_params.append(param)
    return opt_params
```

**API Usage**:
```python
# When calling api.create_optimization():
response = requests.post(url, json={
    "projectId": project_id,
    "parameters[0][key]": "lookback_period",
    "parameters[0][min]": 15,
    "parameters[0][max]": 25,
    "parameters[0][step]": 5
})
```

**Lesson**: **Don't import framework classes for API calls. APIs use plain JSON/dictionaries, not framework-specific objects. Test imports in target environment before assuming availability.**

---

## Updated Best Practices

### Architecture & Design
1. **Test API methods exist** before building on them
2. **Research ALL costs** (not just subscription fees)
3. **Consider hybrid approaches** when pure automation is too expensive
4. **Design around API limitations**, not ideal scenarios
5. **90% solution at $0 often beats 100% solution at $$**

### Development Process
1. **Validate assumptions** with real API calls
2. **Research pricing thoroughly** before recommending solutions
3. **Welcome skeptical questions** - they catch errors
4. **Document wrong assumptions** to avoid repeating
5. **Update docs immediately** when errors are discovered

### Cost Management
1. **Compare total cost of ownership** (subscription + data + usage)
2. **Cloud services often include data** (cheaper than local)
3. **Manual gates can save money** if they're infrequent
4. **Budget for API usage** before building workflows

---

**Last Updated**: 2025-11-10 17:00:00
**Hypothesis**: 2 (Momentum Breakout Strategy)
**Bugs Fixed**: 2 (code) + 7 (architecture/API assumptions)
