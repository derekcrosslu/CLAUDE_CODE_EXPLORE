---
name: QuantConnect
description: Load QuantConnect Lean Algorithm Framework knowledge for strategy development (project)
---

# QuantConnect Lean Algorithm Framework with API Integration

This skill provides comprehensive knowledge of the QuantConnect Lean Algorithm Framework for developing quantitative trading strategies, **with full API integration capabilities** for uploading strategies, running backtests, and executing optimizations remotely.

## CRITICAL: API Integration Capabilities

**This skill provides the following autonomous capabilities**:

1. ✅ **Upload files to QuantConnect cloud** via `qc_backtest.py`
2. ✅ **Authenticate with QuantConnect API** (credentials in `.env`)
3. ✅ **Run backtests remotely** and wait for completion
4. ✅ **Parse and analyze results** automatically
5. ✅ **Run strategy optimizations** (parameter sweeps)

### Using the QuantConnect API Wrapper

The project includes `qc_backtest.py` which provides a complete Python wrapper for the QuantConnect API.

**Complete Workflow - Upload Strategy and Run Backtest**:

```bash
# Complete workflow: create project, upload code, run backtest
python qc_backtest.py --run --name "TestStrategy_20241109" --file test_strategy.py --output results.json
```

**Available Commands**:

```bash
# List all projects
python qc_backtest.py --list

# Create new project
python qc_backtest.py --create --name "MyStrategy"

# Upload file to existing project
# (use create_file method in Python script)

# Run backtest on existing project
python qc_backtest.py --backtest --project-id 12345

# Check backtest status
python qc_backtest.py --status --project-id 12345 --backtest-id abc123

# Get backtest results (parsed)
python qc_backtest.py --results --project-id 12345 --backtest-id abc123 --output results.json
```

### Python API Integration

**Example: Upload and backtest a strategy programmatically**:

```python
from qc_backtest import QuantConnectAPI, create_project_workflow, parse_backtest_results

# Initialize API (reads credentials from .env)
api = QuantConnectAPI()

# Complete workflow: create project, upload code, run backtest
results = create_project_workflow(
    api,
    name="RSI_MeanReversion_v1",
    code_file="test_strategy.py"
)

# Results include structured metrics
if results["success"]:
    performance = results["performance"]
    print(f"Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {performance['max_drawdown']:.2%}")
    print(f"Total Return: {performance['total_return']:.2%}")
    print(f"Win Rate: {performance['win_rate']:.2%}")

    trading = results["trading"]
    print(f"Total Trades: {trading['total_trades']}")
else:
    print(f"Error: {results['error']}")
```

### Backtest Results Structure

The API returns structured results optimized for decision-making:

```json
{
  "success": true,
  "backtest_id": "abc123",
  "project_id": 12345,
  "name": "Backtest_20241109",
  "status": "Completed",
  "completed": true,
  "performance": {
    "sharpe_ratio": 1.45,
    "sortino_ratio": 1.82,
    "max_drawdown": 0.12,
    "total_return": 0.23,
    "annual_return": 0.15,
    "win_rate": 0.62,
    "loss_rate": 0.38
  },
  "trading": {
    "total_trades": 45,
    "average_win": 0.032,
    "average_loss": -0.018,
    "profit_loss_ratio": 1.78
  },
  "risk": {
    "alpha": 0.08,
    "beta": 0.92,
    "volatility": 0.18
  }
}
```

### Decision Framework Integration

**Use parsed results to make autonomous decisions**:

```python
def evaluate_backtest_results(results):
    """
    Autonomous decision logic for backtest results

    Returns: 'proceed_to_validation', 'proceed_to_optimization',
             'abandon_hypothesis', or 'escalate'
    """
    if not results["success"]:
        return "abandon_hypothesis", f"Backtest failed: {results['error']}"

    perf = results["performance"]
    trading = results["trading"]

    # Overfitting detection
    if perf["sharpe_ratio"] > 3.0:
        return "escalate", "Sharpe too high (>3.0), likely overfitting"

    if trading["total_trades"] < 10:
        return "escalate", "Too few trades (<10), insufficient data"

    if perf["win_rate"] > 0.80:
        return "escalate", "Win rate too high (>80%), likely overfitting"

    # Good performance - proceed to validation
    if perf["sharpe_ratio"] >= 1.0 and perf["max_drawdown"] <= 0.20:
        return "proceed_to_validation", "Good performance, ready for OOS validation"

    # Decent performance - try optimization
    if perf["sharpe_ratio"] >= 0.7:
        return "proceed_to_optimization", "Decent performance, optimize parameters"

    # Poor performance - abandon
    if perf["sharpe_ratio"] < 0.5:
        return "abandon_hypothesis", "Poor performance (Sharpe < 0.5)"

    return "proceed_to_optimization", "Marginal performance, try optimization"


# Use in autonomous workflow
results = create_project_workflow(api, "TestStrategy", "test_strategy.py")
decision, reason = evaluate_backtest_results(results)

print(f"Decision: {decision}")
print(f"Reason: {reason}")
```

### Credentials Configuration

The API wrapper reads credentials from `.env` file:

```bash
# .env file
QUANTCONNECT_USER_ID="your_user_id"
QUANTCONNECT_API_TOKEN="your_api_token"
```

**Get your credentials**:
1. Log in to https://www.quantconnect.com
2. Go to Account → API Access
3. Copy User ID and API Token
4. Save to `.env` file

### Strategy Optimization

**Run parameter optimization** to find the best parameter combinations:

```bash
# Optimize existing project with parameter grid
python qc_backtest.py --optimize --project-id 12345 --params-file optimization_params.json --output optimization_results.json
```

**Parameter file format** (`optimization_params.json`):

```json
[
  {"rsi_period": 10, "rsi_oversold": 25, "rsi_overbought": 75},
  {"rsi_period": 14, "rsi_oversold": 30, "rsi_overbought": 70},
  {"rsi_period": 14, "rsi_oversold": 25, "rsi_overbought": 75},
  {"rsi_period": 20, "rsi_oversold": 30, "rsi_overbought": 70},
  {"rsi_period": 20, "rsi_oversold": 35, "rsi_overbought": 65}
]
```

**Optimization results include**:
- Best parameters by Sharpe ratio
- Top 5 parameter combinations
- Statistics across all runs (mean, min, max Sharpe)
- Complete results for all parameter sets

**Example optimization workflow**:

```python
from qc_backtest import QuantConnectAPI, optimize_strategy, analyze_optimization_results

api = QuantConnectAPI()

# Define parameter grid
parameter_sets = [
    {"rsi_period": 10, "stop_loss_pct": 0.03},
    {"rsi_period": 14, "stop_loss_pct": 0.03},
    {"rsi_period": 14, "stop_loss_pct": 0.05},
    {"rsi_period": 20, "stop_loss_pct": 0.03},
]

# Run optimization
results = optimize_strategy(api, project_id=12345, parameter_sets=parameter_sets)

# Analyze
analysis = analyze_optimization_results(results)

if analysis["success"]:
    print(f"Best Parameters: {analysis['best_parameters']}")
    print(f"Best Sharpe: {analysis['best_sharpe']:.2f}")
    print(f"\nTop 5 Configurations:")
    for config in analysis["top_5"]:
        print(f"  Rank {config['rank']}: Sharpe={config['sharpe']:.2f}, Params={config['parameters']}")
```

**IMPORTANT: Strategy Code Must Be Parameterized**

For optimization to work, your strategy must read parameters from its constructor or configuration:

```python
class TestStrategy(QCAlgorithm):
    def initialize(self):
        # Get parameters (with defaults)
        self.rsi_period = self.get_parameter("rsi_period", 14)
        self.rsi_oversold = self.get_parameter("rsi_oversold", 30)
        self.rsi_overbought = self.get_parameter("rsi_overbought", 70)

        # Use parameterized values
        self.rsi = self.rsi(self.symbol, self.rsi_period)

        # Trading logic uses parameterized thresholds
        if self.rsi.current.value < self.rsi_oversold:
            # Buy signal
```

**Note**: QuantConnect API optimization runs each parameter set as a separate backtest. For large grids, this can take time and consume API rate limits.

---

## IMPORTANT: Image and Screenshot Reading Capability

**YOU MUST READ AND ANALYZE IMAGES/SCREENSHOTS WHEN PROVIDED BY THE USER.**

This is a **native Claude Code capability** - you can read images directly. When a user provides:
- File paths to images (PNG, JPG, etc.)
- Screenshots via Windsurf CLI or other interfaces
- Pasted images in the conversation
- Temporary image files

**YOU MUST**:
- ✅ Read and analyze the image without asking for permission
- ✅ Provide detailed analysis of what you see
- ✅ Answer questions about the image content
- ✅ Extract text, data, patterns from images

**YOU MUST NOT**:
- ❌ Refuse to read images
- ❌ Ask "Can you describe the image instead?"
- ❌ Say "I cannot view images"
- ❌ Redirect to other tools when you can read it directly

**Example Valid Requests**:
```
"Analyze this backtest screenshot: /path/to/results.png"
"What do you see in this equity curve?"
"Read the parameters from this QuantConnect settings screenshot"
"Compare these two optimization heatmaps"
"Extract the Sharpe ratio from this results image"
```

**Your Response**: Immediately read and analyze the image. Provide specific, detailed observations.

This capability is **independent of the autonomous workflow** and is a general Claude Code feature for all tasks including validation, debugging, documentation, and analysis.

---

## CRITICAL: API Naming Convention

**QuantConnect now uses snake_case for ALL methods and variables.**

The examples in this skill use **PascalCase** (old API style) for educational clarity, but **you MUST use snake_case** when writing actual code:

```python
# CORRECT (Current API - use this):
def initialize(self):
    self.set_start_date(2020, 1, 1)
    self.set_cash(100000)
    self.spy = self.add_equity("SPY", Resolution.Daily)
    self.set_holdings(self.spy.symbol, 1.0)

# WRONG (Old API - don't use):
def Initialize(self):  # Wrong
    self.SetStartDate(2020, 1, 1)  # Wrong
    self.SetCash(100000)  # Wrong
```

**See `reference/coding_standards.md` for complete standards.**

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
