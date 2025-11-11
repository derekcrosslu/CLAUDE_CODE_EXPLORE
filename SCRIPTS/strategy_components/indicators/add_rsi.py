"""
RSI (Relative Strength Index) Indicator Component

**Purpose**: Add RSI indicator to detect overbought/oversold conditions.

**Integration Guide**:

1. In Initialize():
   ```python
   from strategy_components.indicators.add_rsi import add_rsi
   
   # Add RSI indicator
   self.rsi = add_rsi(self, symbol="SPY", period=14, resolution=Resolution.Daily)
   
   # Warm up
   self.SetWarmUp(14, Resolution.Daily)
   ```

2. In OnData():
   ```python
   if not self.rsi.IsReady:
       return
   
   rsi_value = self.rsi.Current.Value
   
   # Oversold: RSI < 30
   # Overbought: RSI > 70
   ```

**Parameters**:
- symbol: str or Symbol - Equity symbol
- period: int - RSI period (default: 14)
- resolution: Resolution - Data resolution (default: Daily)

**Returns**: RSI indicator object

**Common Values**:
- RSI < 30: Oversold (potential buy)
- RSI > 70: Overbought (potential sell)
- RSI 30-70: Neutral
"""

from AlgorithmImports import *


def add_rsi(algorithm, symbol, period=14, resolution=Resolution.Daily):
    """
    Add RSI indicator to algorithm.
    
    Args:
        algorithm: QCAlgorithm instance (self)
        symbol: Symbol or string ticker
        period: RSI period (default: 14)
        resolution: Data resolution (default: Daily)
    
    Returns:
        RSI indicator object
    """
    # Convert string to Symbol if needed
    if isinstance(symbol, str):
        symbol = algorithm.Symbol(symbol)
    
    # Create RSI indicator
    rsi = algorithm.RSI(symbol, period, resolution)
    
    return rsi
