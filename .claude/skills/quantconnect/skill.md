---
name: QuantConnect
description: QuantConnect Lean Algorithm Framework for strategy development (project)
---

# QuantConnect Lean Algorithm Framework

This skill provides knowledge of the QuantConnect Lean Algorithm Framework for **developing trading strategy code** - algorithms, indicators, orders, and risk management.

## When to Use This Skill

Load this skill when:
- Implementing strategy logic (entry/exit signals)
- Using technical indicators (SMA, RSI, MACD, etc.)
- Placing orders (market, limit, stop)
- Implementing risk management (stop loss, position sizing)
- Debugging common QuantConnect errors
- Understanding data subscriptions and resolution types

**For phase-specific operations, use these skills instead:**
- **quantconnect-backtest**: Running backtests via API (Phase 3)
- **quantconnect-optimization**: Parameter optimization (Phase 4)
- **quantconnect-validation**: Walk-forward validation (Phase 5)

---

## Core Algorithm Structure

Every QuantConnect algorithm inherits from `QCAlgorithm`:

```python
from AlgorithmImports import *

class MyStrategy(QCAlgorithm):
    def Initialize(self):
        """Called once at the start - setup configuration here"""
        # Set backtest period
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2023, 12, 31)
        self.SetCash(100000)

        # Add securities
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol

        # Create indicators
        self.sma = self.SMA(self.symbol, 50, Resolution.Daily)

    def OnData(self, data):
        """Called every time new data arrives"""
        # Check indicator is ready
        if not self.sma.IsReady:
            return

        # Trading logic
        if not self.Portfolio.Invested:
            if data[self.symbol].Close > self.sma.Current.Value:
                self.SetHoldings(self.symbol, 1.0)
        elif data[self.symbol].Close < self.sma.Current.Value:
            self.Liquidate(self.symbol)
```

## Data Subscriptions

### Equity (Stocks)
```python
# Add single equity
self.symbol = self.AddEquity("AAPL", Resolution.Daily).Symbol

# Add with specific properties
self.AddEquity("AAPL", Resolution.Hour, fillForward=True, leverage=2.0)

# Multiple equities
self.symbols = [self.AddEquity(ticker, Resolution.Daily).Symbol
                for ticker in ["AAPL", "MSFT", "GOOGL"]]
```

### Crypto
```python
# Bitcoin
self.btc = self.AddCrypto("BTCUSD", Resolution.Hour).Symbol

# Multiple cryptocurrencies
self.cryptos = [self.AddCrypto(pair, Resolution.Daily).Symbol
                for pair in ["BTCUSD", "ETHUSD"]]
```

### Forex
```python
self.eurusd = self.AddForex("EURUSD", Resolution.Minute).Symbol
```

### Futures
```python
from QuantConnect.Securities.Future import Future

self.AddFuture(Futures.Indices.SP500EMini)
```

### Options
```python
option = self.AddOption("SPY")
option.SetFilter(-2, 2, 0, 30)  # Strike range, expiry range (days)
```

## Resolution Types
- `Resolution.Tick` - Every tick (highest granularity)
- `Resolution.Second` - Second bars
- `Resolution.Minute` - Minute bars
- `Resolution.Hour` - Hourly bars
- `Resolution.Daily` - Daily bars (most common for backtesting)

## Technical Indicators

### Moving Averages
```python
# Simple Moving Average
self.sma = self.SMA(symbol, 20, Resolution.Daily)

# Exponential Moving Average
self.ema = self.EMA(symbol, 20, Resolution.Daily)

# Weighted Moving Average
self.wma = self.WMA(symbol, 20, Resolution.Daily)
```

### Momentum Indicators
```python
# Relative Strength Index
self.rsi = self.RSI(symbol, 14, Resolution.Daily)

# MACD
self.macd = self.MACD(symbol, 12, 26, 9, Resolution.Daily)

# Momentum
self.mom = self.MOM(symbol, 10, Resolution.Daily)

# Rate of Change
self.roc = self.ROC(symbol, 10, Resolution.Daily)

# Stochastic
self.sto = self.STO(symbol, 14, 3, 3, Resolution.Daily)
```

### Volatility Indicators
```python
# Bollinger Bands
self.bb = self.BB(symbol, 20, 2, Resolution.Daily)
# Access: self.bb.UpperBand, self.bb.MiddleBand, self.bb.LowerBand

# Average True Range
self.atr = self.ATR(symbol, 14, Resolution.Daily)

# Standard Deviation
self.std = self.STD(symbol, 20, Resolution.Daily)
```

### Volume Indicators
```python
# On-Balance Volume
self.obv = self.OBV(symbol, Resolution.Daily)

# Accumulation/Distribution
self.ad = self.AD(symbol, Resolution.Daily)
```

### Custom Indicators
```python
# Create custom indicator
from QuantConnect.Indicators import IndicatorBase

class MyIndicator(IndicatorBase):
    def __init__(self, name, period):
        super().__init__(name)
        self.period = period
        self.values = []

    def Update(self, input):
        self.values.append(input.Value)
        if len(self.values) > self.period:
            self.values.pop(0)
        return len(self.values) == self.period
```

### Indicator Ready Check
```python
# ALWAYS check if indicator is ready before using
if not self.sma.IsReady:
    return  # Skip this OnData call

# Use indicator value
current_sma = self.sma.Current.Value
```

## Order Execution

### Market Orders
```python
# Buy 100 shares
self.MarketOrder(symbol, 100)

# Sell 100 shares (or short if not invested)
self.MarketOrder(symbol, -100)
```

### Limit Orders
```python
# Buy at limit price
self.LimitOrder(symbol, 100, limit_price)
```

### Stop Market Orders
```python
# Stop loss
self.StopMarketOrder(symbol, -100, stop_price)
```

### Set Holdings (Percentage of Portfolio)
```python
# Allocate 50% of portfolio to symbol
self.SetHoldings(symbol, 0.5)

# Go 100% long
self.SetHoldings(symbol, 1.0)

# Go 50% short
self.SetHoldings(symbol, -0.5)
```

### Liquidate
```python
# Close position in specific symbol
self.Liquidate(symbol)

# Close ALL positions
self.Liquidate()
```

### Order Targeting
```python
# Target specific dollar value
self.SetHoldings(symbol, 10000)  # $10,000 position

# Calculate shares for risk amount
shares = self.CalculateOrderQuantity(symbol, 0.1)  # 10% of portfolio
self.MarketOrder(symbol, shares)
```

## Portfolio Management

### Check Position Status
```python
# Check if invested in any security
if self.Portfolio.Invested:
    # Have positions

# Check specific symbol
if self.Portfolio[symbol].Invested:
    # Have position in this symbol
    quantity = self.Portfolio[symbol].Quantity
    avg_price = self.Portfolio[symbol].AveragePrice
    unrealized_pnl = self.Portfolio[symbol].UnrealizedProfit
```

### Portfolio Values
```python
# Total portfolio value
total_value = self.Portfolio.TotalPortfolioValue

# Cash available
cash = self.Portfolio.Cash

# Total unrealized profit
unrealized = self.Portfolio.TotalUnrealizedProfit

# Total holdings value
holdings_value = self.Portfolio.TotalHoldingsValue
```

## Risk Management Patterns

### Position Sizing by Volatility
```python
def OnData(self, data):
    if not self.atr.IsReady:
        return

    # Calculate volatility as percentage
    volatility = self.atr.Current.Value / data[self.symbol].Close

    # Risk 1% of portfolio per position
    position_size = 0.01 / volatility

    # Cap at 100% (1.0)
    position_size = min(position_size, 1.0)

    if self.buy_signal:
        self.SetHoldings(self.symbol, position_size)
```

### Stop Loss
```python
def Initialize(self):
    self.entry_price = None
    self.stop_loss_pct = 0.05  # 5% stop loss

def OnData(self, data):
    # Entry
    if self.entry_signal and not self.Portfolio.Invested:
        self.SetHoldings(self.symbol, 1.0)
        self.entry_price = data[self.symbol].Close

    # Stop loss check
    if self.Portfolio.Invested and self.entry_price:
        current_price = data[self.symbol].Close
        if current_price < self.entry_price * (1 - self.stop_loss_pct):
            self.Liquidate(self.symbol)
            self.Debug(f"Stop loss triggered at {current_price}")
```

### Take Profit
```python
def OnData(self, data):
    if self.Portfolio.Invested:
        # Take profit at 10% gain
        pnl_pct = self.Portfolio[self.symbol].UnrealizedProfitPercent
        if pnl_pct > 0.10:
            self.Liquidate(self.symbol)
            self.Debug(f"Take profit at {pnl_pct:.2%}")
```

### Maximum Drawdown Protection
```python
def Initialize(self):
    self.peak_portfolio_value = self.Portfolio.TotalPortfolioValue
    self.max_drawdown = 0.20  # 20% maximum drawdown

def OnData(self, data):
    # Update peak
    current_value = self.Portfolio.TotalPortfolioValue
    if current_value > self.peak_portfolio_value:
        self.peak_portfolio_value = current_value

    # Calculate drawdown
    drawdown = (self.peak_portfolio_value - current_value) / self.peak_portfolio_value

    # Emergency liquidation
    if drawdown > self.max_drawdown:
        self.Liquidate()
        self.Quit(f"Max drawdown {drawdown:.2%} exceeded")
```

### Position Limits
```python
def OnData(self, data):
    # Max 5 positions
    if len(self.Portfolio.Values) >= 5 and not self.Portfolio[symbol].Invested:
        return  # Don't open new positions

    # Max 25% per position
    max_allocation = 0.25
    self.SetHoldings(symbol, min(target_allocation, max_allocation))
```

## Scheduled Events

### Daily Rebalancing
```python
def Initialize(self):
    # Rebalance every day at market open
    self.Schedule.On(
        self.DateRules.EveryDay(self.symbol),
        self.TimeRules.AfterMarketOpen(self.symbol, 30),  # 30 min after open
        self.Rebalance
    )

def Rebalance(self):
    """Called every day at scheduled time"""
    # Your rebalancing logic
    pass
```

### Weekly/Monthly Events
```python
def Initialize(self):
    # Every Monday
    self.Schedule.On(
        self.DateRules.Every(DayOfWeek.Monday),
        self.TimeRules.At(10, 0),  # 10:00 AM
        self.WeeklyRebalance
    )

    # First day of month
    self.Schedule.On(
        self.DateRules.MonthStart(self.symbol),
        self.TimeRules.AfterMarketOpen(self.symbol, 30),
        self.MonthlyRebalance
    )
```

## Logging and Debugging

### Debug Messages
```python
self.Debug(f"Current price: {data[self.symbol].Close}")
self.Debug(f"RSI: {self.rsi.Current.Value:.2f}")
```

### Log Messages
```python
self.Log(f"Trade executed: {quantity} shares at {price}")
```

### Plot Charts
```python
def Initialize(self):
    # Create custom chart
    stockPlot = Chart("Trade Plot")
    stockPlot.AddSeries(Series("Buy", SeriesType.Scatter, 0))
    stockPlot.AddSeries(Series("Sell", SeriesType.Scatter, 0))
    self.AddChart(stockPlot)

def OnData(self, data):
    # Plot indicators
    self.Plot("Indicators", "SMA", self.sma.Current.Value)
    self.Plot("Indicators", "RSI", self.rsi.Current.Value)

    # Plot trades
    if self.buy_signal:
        self.Plot("Trade Plot", "Buy", data[self.symbol].Close)
```

## Common Strategy Patterns

### Momentum Strategy Pattern
```python
def Initialize(self):
    self.SetStartDate(2020, 1, 1)
    self.SetEndDate(2023, 12, 31)
    self.SetCash(100000)

    self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
    self.rsi = self.RSI(self.symbol, 14)
    self.momentum = self.MOM(self.symbol, 10)

def OnData(self, data):
    if not self.rsi.IsReady or not self.momentum.IsReady:
        return

    # Buy on momentum + RSI oversold
    if not self.Portfolio.Invested:
        if self.momentum.Current.Value > 0 and self.rsi.Current.Value < 30:
            self.SetHoldings(self.symbol, 1.0)

    # Sell on RSI overbought
    else:
        if self.rsi.Current.Value > 70:
            self.Liquidate(self.symbol)
```

### Mean Reversion Pattern
```python
def Initialize(self):
    self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
    self.bb = self.BB(self.symbol, 20, 2)

def OnData(self, data):
    if not self.bb.IsReady:
        return

    price = data[self.symbol].Close

    # Buy when price touches lower band (oversold)
    if not self.Portfolio.Invested:
        if price < self.bb.LowerBand.Current.Value:
            self.SetHoldings(self.symbol, 1.0)

    # Sell when price returns to middle band
    else:
        if price > self.bb.MiddleBand.Current.Value:
            self.Liquidate(self.symbol)
```

### Volatility Breakout Pattern
```python
def Initialize(self):
    self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol
    self.bb = self.BB(self.symbol, 20, 2)
    self.atr = self.ATR(self.symbol, 14)

def OnData(self, data):
    if not self.bb.IsReady or not self.atr.IsReady:
        return

    price = data[self.symbol].Close

    # Buy on upside breakout
    if not self.Portfolio.Invested:
        if price > self.bb.UpperBand.Current.Value:
            self.SetHoldings(self.symbol, 1.0)

    # Trailing stop using ATR
    else:
        stop_distance = self.atr.Current.Value * 2
        if price < (self.Portfolio[self.symbol].AveragePrice - stop_distance):
            self.Liquidate(self.symbol)
```

## Multi-Timeframe Analysis

```python
def Initialize(self):
    self.symbol = self.AddEquity("SPY", Resolution.Minute).Symbol

    # Daily SMA for trend
    self.daily_sma = self.SMA(self.symbol, 50, Resolution.Daily)

    # Hourly RSI for entries
    self.hourly_rsi = self.RSI(self.symbol, 14, Resolution.Hour)

def OnData(self, data):
    if not self.daily_sma.IsReady or not self.hourly_rsi.IsReady:
        return

    price = data[self.symbol].Close

    # Only buy if daily trend is up
    if price > self.daily_sma.Current.Value:
        # Use hourly RSI for timing
        if not self.Portfolio.Invested and self.hourly_rsi.Current.Value < 30:
            self.SetHoldings(self.symbol, 1.0)
```

## Data Access

### Current Data
```python
def OnData(self, data):
    # Check if data available
    if not data.ContainsKey(self.symbol):
        return

    # Access price data
    bar = data[self.symbol]
    close = bar.Close
    open_price = bar.Open
    high = bar.High
    low = bar.Low
    volume = bar.Volume
```

### Historical Data
```python
def Initialize(self):
    # Get historical bars
    history = self.History(self.symbol, 100, Resolution.Daily)

    # Access as DataFrame
    close_prices = history['close']

    # Calculate custom metrics
    returns = close_prices.pct_change()
```

## Universe Selection

```python
def Initialize(self):
    # Select top 10 liquid stocks
    self.UniverseSettings.Resolution = Resolution.Daily
    self.AddUniverse(self.CoarseSelectionFunction)

def CoarseSelectionFunction(self, coarse):
    # Filter by dollar volume
    sorted_by_volume = sorted(coarse,
                              key=lambda x: x.DollarVolume,
                              reverse=True)

    # Return top 10
    return [x.Symbol for x in sorted_by_volume[:10]]
```

## Common Errors and Solutions

### Error: Indicator Not Ready
```python
# WRONG
value = self.sma.Current.Value  # May throw error

# RIGHT
if self.sma.IsReady:
    value = self.sma.Current.Value
```

### Error: No Data Available
```python
# WRONG
price = data[self.symbol].Close  # May throw KeyError

# RIGHT
if data.ContainsKey(self.symbol):
    price = data[self.symbol].Close
```

### Error: Insufficient Capital
```python
# WRONG
self.SetHoldings(symbol, 2.0)  # 200% allocation without margin

# RIGHT
# Check leverage or use reasonable allocation
self.SetHoldings(symbol, 1.0)  # 100% max
```

## Best Practices

1. **Always Check Indicator Readiness**
   - Use `if not indicator.IsReady: return` at start of OnData

2. **Validate Data Availability**
   - Check `data.ContainsKey(symbol)` before accessing

3. **Use Proper Position Sizing**
   - Never exceed 100% allocation without leverage setup
   - Consider volatility in position sizing

4. **Implement Risk Management**
   - Always use stop losses
   - Limit maximum drawdown
   - Cap position sizes

5. **Log Important Events**
   - Log entry/exit prices
   - Log why decisions were made
   - Plot indicators for visual debugging

6. **Warm Up Indicators**
   - Use `SetWarmUp()` to pre-fill indicators
   ```python
   def Initialize(self):
       self.SetWarmUp(50)  # Warm up 50 bars
   ```

7. **Test Edge Cases**
   - Market gaps
   - Low liquidity
   - Extreme volatility

## File References

For detailed examples, see:
- `examples/basic_algorithm.py` - Complete minimal working example
- `examples/indicators_usage.py` - All common indicators
- `examples/risk_management.py` - Risk management patterns
- `templates/momentum_template.py` - Momentum strategy template
- `templates/mean_reversion_template.py` - Mean reversion template
- `reference/common_errors.md` - Troubleshooting guide
- `reference/best_practices.md` - Detailed best practices
