"""
SMA (Simple Moving Average) Indicator Component

**Purpose**: Add SMA indicator for trend detection and moving average crossovers.

**Integration Guide**:

1. In Initialize():
   ```python
   from strategy_components.indicators.add_sma import add_sma
   
   # Add SMA indicators
   self.sma_fast = add_sma(self, symbol="SPY", period=20, resolution=Resolution.Daily)
   self.sma_slow = add_sma(self, symbol="SPY", period=50, resolution=Resolution.Daily)
   
   # Warm up
   self.SetWarmUp(50, Resolution.Daily)
   ```

2. In OnData():
   ```python
   if not self.sma_fast.IsReady or not self.sma_slow.IsReady:
       return
   
   fast_value = self.sma_fast.Current.Value
   slow_value = self.sma_slow.Current.Value
   
   # Golden cross: fast > slow (bullish)
   # Death cross: fast < slow (bearish)
   ```

**Parameters**:
- symbol: str or Symbol - Equity symbol
- period: int - SMA period
- resolution: Resolution - Data resolution (default: Daily)

**Returns**: SMA indicator object

**Common Periods**:
- 20-day: Short-term trend
- 50-day: Medium-term trend
- 200-day: Long-term trend
"""

from AlgorithmImports import *


def add_sma(algorithm, symbol, period, resolution=Resolution.Daily):
    """
    Add SMA indicator to algorithm.
    
    Args:
        algorithm: QCAlgorithm instance (self)
        symbol: Symbol or string ticker
        period: SMA period
        resolution: Data resolution (default: Daily)
    
    Returns:
        SMA indicator object
    """
    # Convert string to Symbol if needed
    if isinstance(symbol, str):
        symbol = algorithm.Symbol(symbol)
    
    # Create SMA indicator
    sma = algorithm.SMA(symbol, period, resolution)
    
    return sma
