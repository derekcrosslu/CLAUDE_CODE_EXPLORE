# Order Tags Documentation

## Overview

All orders in the H7 Statistical Arbitrage strategy now include descriptive tags that appear in QuantConnect's order logs and trade logs. These tags provide detailed context about why each order was placed and what conditions triggered it.

## Tag Format

Tags use pipe-delimited format: `TYPE|PAIR|DETAILS`

## Entry Order Tags

### Format
```
ENTRY|{pair_name}|Z={z_score}|HL={half_life}|VIX={vix_allocation}%|{LEG_TYPE}
```

**Note**: Half-life (HL) is only included when ADF or half-life filters are enabled.

### Example Entry Tags
```
ENTRY|PNC_KBE|Z=2.34|HL=12.5|VIX=100%|LONG_LEG
ENTRY|PNC_KBE|Z=2.34|HL=12.5|VIX=100%|SHORT_LEG
ENTRY|ARCC_AMLP|Z=-1.87|HL=18.3|VIX=70%|LONG_LEG
ENTRY|ARCC_AMLP|Z=-1.87|HL=18.3|VIX=70%|SHORT_LEG
```

### Entry Tag Components
- **ENTRY**: Indicates this is an entry order
- **Pair name**: Which pair is being traded (e.g., PNC_KBE)
- **Z-score**: Entry Z-score that triggered the signal
- **Half-life** (optional): Mean reversion half-life in days (only if cointegration filters enabled)
- **VIX allocation**: VIX-adjusted position sizing percentage
- **Leg type**:
  - `LONG_LEG`: Buying this leg
  - `SHORT_LEG`: Shorting this leg

## Exit Order Tags

### Format
```
EXIT|{pair_name}|{exit_reason}|Z={z_score}|HL={half_life}|DAYS={holding_days}
```

**Note**: Half-life (HL) is only included when ADF or half-life filters are enabled.

### Example Exit Tags
```
EXIT|PNC_KBE|MEAN_REVERSION|Z=0.45|HL=11.2|DAYS=7
EXIT|ARCC_AMLP|TIMEOUT|Z=1.23|HL=25.6|DAYS=30
EXIT|RBA_SMFG|STOP_LOSS|Z=4.56|HL=45.3|DAYS=12
EXIT|ENB_WEC|SPREAD_CRITICAL|Z=3.21|HL=15.8|DAYS=5
EXIT|PNC_KBE|BROKEN_COINTEGRATION|Z=2.10|HL=78.4|DAYS=14
```

### Exit Reasons
1. **MEAN_REVERSION**: Primary exit - spread reverted to mean (|Z| < threshold)
2. **TIMEOUT**: Max holding period reached (e.g., 30 days)
3. **STOP_LOSS**: Divergence continued beyond stop loss Z-score
4. **SPREAD_CRITICAL**: Spread deviation filter triggered (if enabled)
5. **BROKEN_COINTEGRATION**: ADF or half-life filter triggered weekly check
6. **VIX_CRISIS**: VIX filter triggered emergency exit (see below)

### Exit Tag Components
- **EXIT**: Indicates this is an exit order
- **Pair name**: Which pair is being closed
- **Exit reason**: Why the position was closed (see above)
- **Z-score**: Current Z-score at exit
- **Half-life** (optional): Mean reversion half-life in days at exit (only if cointegration filters enabled)
- **Days held**: How many days the position was held

## VIX Crisis Exit Tags

### Format
```
EXIT|VIX_CRISIS|VIX={vix_level}|{pair_name}
```

### Example VIX Crisis Tags
```
EXIT|VIX_CRISIS|VIX=32.4|PNC_KBE
EXIT|VIX_CRISIS|VIX=32.4|ARCC_AMLP
EXIT|VIX_CRISIS|VIX=32.4|RBA_SMFG
EXIT|VIX_CRISIS|VIX=32.4|ENB_WEC
```

### VIX Crisis Tag Components
- **EXIT**: Exit order
- **VIX_CRISIS**: Special emergency liquidation trigger
- **VIX level**: Current VIX value that triggered crisis mode
- **Pair name**: Which pair is being liquidated

## How to View Tags in QuantConnect

### 1. Order Events Log
Tags appear in the `OrderEvents` collection:
```python
# In backtest results
for order_event in results.OrderEvents.Values:
    print(f"Time: {order_event.UtcTime}")
    print(f"Symbol: {order_event.Symbol}")
    print(f"Tag: {order_event.Tag}")
```

### 2. Trade Statistics
Tags are included in trade analysis:
```python
# Download orders.csv from backtest
# Tag column shows full tag for each order
```

### 3. Logs
Tags are also visible in algorithm logs when trades execute.

## Tag Analysis Use Cases

### 1. Filter by Exit Reason
```python
# Count exits by reason
exit_reasons = {}
for event in order_events:
    if "EXIT|" in event.Tag:
        parts = event.Tag.split("|")
        reason = parts[2]
        exit_reasons[reason] = exit_reasons.get(reason, 0) + 1

# Output:
# MEAN_REVERSION: 145
# TIMEOUT: 32
# STOP_LOSS: 8
# SPREAD_CRITICAL: 2
```

### 2. VIX Allocation Analysis
```python
# Analyze entry VIX levels
vix_at_entry = []
for event in order_events:
    if "ENTRY|" in event.Tag:
        # Extract VIX=XX% from tag
        vix_match = re.search(r'VIX=(\d+)%', event.Tag)
        if vix_match:
            vix_at_entry.append(int(vix_match.group(1)))

# Analyze distribution of VIX levels at entry
```

### 3. Holding Period by Exit Reason
```python
# Compare holding periods for different exit reasons
holding_by_reason = {}
for event in order_events:
    if "EXIT|" in event.Tag:
        parts = event.Tag.split("|")
        reason = parts[2]
        days_match = re.search(r'DAYS=(\d+)', event.Tag)
        if days_match:
            days = int(days_match.group(1))
            if reason not in holding_by_reason:
                holding_by_reason[reason] = []
            holding_by_reason[reason].append(days)

# Calculate average holding period per exit type
for reason, days_list in holding_by_reason.items():
    avg = sum(days_list) / len(days_list)
    print(f"{reason}: {avg:.1f} days average")
```

### 4. Crisis Event Detection
```python
# Find all VIX crisis events
crisis_events = [e for e in order_events if "VIX_CRISIS" in e.Tag]

# Group by date to find crisis periods
crisis_dates = set(e.UtcTime.date() for e in crisis_events)
print(f"VIX crisis triggered on {len(crisis_dates)} dates")
```

## Tag Advantages

### Debugging
- Instantly see why each order was placed
- Identify filter interactions
- Verify risk management is working

### Performance Analysis
- Compare profitability by exit reason
- Analyze VIX-adjusted entries vs. full-size entries
- Identify which filters are most active

### Risk Management
- Track crisis mode activations
- Monitor spread filter triggers
- Verify cointegration exits

### Backtesting Validation
- Confirm strategy logic is executing correctly
- Verify filter configurations are active
- Cross-reference with debug logs

## Tag Examples by Scenario

### Normal Mean Reversion Trade
```
# Entry
ENTRY|PNC_KBE|Z=2.15|HL=12.3|VIX=100%|LONG_LEG
ENTRY|PNC_KBE|Z=2.15|HL=12.3|VIX=100%|SHORT_LEG

# Exit (7 days later, half-life improved)
EXIT|PNC_KBE|MEAN_REVERSION|Z=0.38|HL=10.5|DAYS=7
EXIT|PNC_KBE|MEAN_REVERSION|Z=0.38|HL=10.5|DAYS=7
```

### Reduced Size Entry (VIX Warning)
```
# Entry with reduced allocation
ENTRY|ARCC_AMLP|Z=-1.92|HL=18.7|VIX=70%|LONG_LEG
ENTRY|ARCC_AMLP|Z=-1.92|HL=18.7|VIX=70%|SHORT_LEG

# Exit via timeout (half-life deteriorated)
EXIT|ARCC_AMLP|TIMEOUT|Z=-0.85|HL=22.4|DAYS=30
EXIT|ARCC_AMLP|TIMEOUT|Z=-0.85|HL=22.4|DAYS=30
```

### Stop Loss Hit
```
# Entry
ENTRY|RBA_SMFG|Z=2.34|HL=15.2|VIX=100%|LONG_LEG
ENTRY|RBA_SMFG|Z=2.34|HL=15.2|VIX=100%|SHORT_LEG

# Exit - spread diverged further (half-life degraded significantly)
EXIT|RBA_SMFG|STOP_LOSS|Z=4.78|HL=42.8|DAYS=12
EXIT|RBA_SMFG|STOP_LOSS|Z=4.78|HL=42.8|DAYS=12
```

### VIX Crisis (March 2020 example)
```
# Multiple pairs liquidated simultaneously
EXIT|VIX_CRISIS|VIX=82.7|PNC_KBE
EXIT|VIX_CRISIS|VIX=82.7|PNC_KBE
EXIT|VIX_CRISIS|VIX=82.7|ARCC_AMLP
EXIT|VIX_CRISIS|VIX=82.7|ARCC_AMLP
EXIT|VIX_CRISIS|VIX=82.7|RBA_SMFG
EXIT|VIX_CRISIS|VIX=82.7|RBA_SMFG
EXIT|VIX_CRISIS|VIX=82.7|ENB_WEC
EXIT|VIX_CRISIS|VIX=82.7|ENB_WEC
```

## Integration with Existing Logs

Tags complement (not replace) the existing debug logs:

**Debug Log:**
```
ENTRY - PNC_KBE | LONG SPREAD | Z=2.34 | VIX allocation=100% | Equity=$102,345.67
```

**Order Tag:**
```
ENTRY|PNC_KBE|Z=2.34|VIX=100%|LONG_LEG
```

Both provide context - logs are human-readable, tags are machine-parseable.

---

**Status**: Implemented in main.py
**Coverage**: All entry, exit, and crisis liquidation orders
**Format**: Pipe-delimited for easy parsing
**Compatibility**: QuantConnect Cloud and Local
