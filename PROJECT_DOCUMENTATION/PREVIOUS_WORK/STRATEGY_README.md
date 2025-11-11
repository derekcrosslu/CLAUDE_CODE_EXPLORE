# QuantConnect Test Strategy

An enhanced RSI mean-reversion trading strategy for QuantConnect with comprehensive risk management.

## Strategy Overview

**TestStrategy** is a professional-grade algorithmic trading strategy that combines multiple technical indicators for robust mean-reversion trading:

- **Core Signal**: RSI-based oversold/overbought detection
- **Confirmation**: Bollinger Bands for volatility analysis
- **Trend Filter**: 200-day SMA to trade only in uptrends
- **Risk Management**: Dynamic position sizing, stop loss, take profit, and trailing stops

## Features

### Technical Indicators
- **RSI (14)**: Primary signal for oversold (<30) and overbought (>70) conditions
- **Bollinger Bands (20, 2)**: Volatility envelope for entry confirmation
- **SMA 200**: Long-term trend filter
- **MACD (12, 26, 9)**: Additional momentum confirmation
- **ATR (14)**: Volatility-based position sizing

### Risk Management
- **Stop Loss**: 3% fixed stop loss on all positions
- **Take Profit**: 8% target profit level
- **Trailing Stop**: Activates at 5% profit, trails by 2%
- **Position Sizing**: Dynamic allocation based on ATR volatility
  - Higher volatility = smaller position size
  - Range: 20% to 80% of portfolio
  - Default risk: 3% of portfolio per trade

### Entry Logic
A position is opened when ALL conditions are met:
1. RSI < 30 (oversold)
2. Price within 2% of lower Bollinger Band
3. Price above 200-day SMA (uptrend confirmation)
4. Not currently invested

### Exit Logic
A position is closed when ANY condition is met:
1. Stop loss hit (price drops 3% from entry)
2. Take profit hit (price rises 8% from entry)
3. RSI > 70 (overbought - mean reversion)
4. Trailing stop triggered (locks in profit)

## File Structure

```
.
├── test_strategy.py          # Main strategy file
├── config/
│   └── config.json            # QuantConnect configuration
├── data/                      # Local data cache (ignored in git)
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore rules
└── STRATEGY_README.md        # This file
```

## Usage

### On QuantConnect Cloud Platform

1. Log in to [QuantConnect](https://www.quantconnect.com)
2. Create a new algorithm project
3. Upload `test_strategy.py`
4. Run backtest with default parameters:
   - Start: 2023-01-01
   - End: 2023-12-31
   - Capital: $100,000

### Local Development (with LEAN)

```bash
# Install dependencies
pip install -r requirements.txt

# Run backtest (requires LEAN installation)
lean backtest "test_strategy"
```

## Configuration

Key parameters can be adjusted in the `initialize()` method:

```python
# Risk management
self.stop_loss_pct = 0.03          # 3% stop loss
self.take_profit_pct = 0.08        # 8% take profit
self.trailing_stop_trigger = 0.05  # Start trailing at 5% profit

# Indicator periods
self.rsi = self.rsi(self.spy.symbol, 14)        # 14-period RSI
self.bb = self.bb(self.spy.symbol, 20, 2)       # 20-period BB, 2 std dev
self.sma_200 = self.sma(self.spy.symbol, 200)   # 200-day trend filter
```

## Performance Metrics

The strategy tracks and logs:
- Total number of trades
- Winning vs losing trades
- Win rate percentage
- Individual trade P&L
- Final portfolio value and total return

Example output:
```
==================================================
BACKTEST COMPLETE
==================================================
Initial Capital: $100,000.00
Final Portfolio Value: $108,450.23
Total Return: 8.45%
Total Trades: 15
Winning Trades: 10
Losing Trades: 5
Win Rate: 66.7%
==================================================
```

## Visualization

The strategy creates custom charts:

1. **Trade Signals**: Buy/sell markers on price chart
2. **Indicators**: Price, Bollinger Bands
3. **RSI**: RSI value with 30/70 reference lines
4. **Performance**: Win rate over time

## Key Advantages

1. **Multiple Confirmations**: Reduces false signals
2. **Trend Alignment**: Only trades in direction of major trend
3. **Volatility-Adjusted Sizing**: Smaller positions in volatile markets
4. **Professional Risk Management**: Protects capital with stops
5. **Trailing Stops**: Locks in profits on winning trades
6. **Comprehensive Logging**: Full transparency on decisions

## Customization Ideas

### Conservative Version
- Increase RSI thresholds (25/75)
- Tighter stop loss (2%)
- Require MACD confirmation
- Reduce maximum position size (50%)

### Aggressive Version
- Relax RSI thresholds (35/65)
- Wider stop loss (5%)
- Increase take profit (10%)
- Allow larger positions (100%)

### Multi-Asset Version
- Add universe selection
- Apply strategy to multiple stocks
- Implement portfolio rebalancing
- Add correlation filters

## Best Practices

1. **Always backtest** strategy changes before live trading
2. **Paper trade** for at least 1 month before going live
3. **Monitor performance** regularly and adjust parameters
4. **Keep position sizes** conservative (< 50% initially)
5. **Use proper risk management** - never risk more than you can afford to lose

## Requirements

- Python 3.8+
- QuantConnect account (cloud) or LEAN Engine (local)
- Basic understanding of technical analysis
- Risk management principles

## Support

- QuantConnect Documentation: https://www.quantconnect.com/docs
- Community Forum: https://www.quantconnect.com/forum
- API Reference: https://www.quantconnect.com/docs/v2

## Disclaimer

This strategy is for educational and testing purposes only. Past performance does not guarantee future results. Always perform thorough backtesting and paper trading before deploying any strategy with real capital. Trading involves substantial risk of loss.

## Version History

- v1.0 (2024): Initial simple RSI strategy
- v2.0 (Current): Enhanced with multiple indicators, risk management, and professional features

## License

Free to use and modify for personal and educational purposes.
