"""
Mean Reversion Signal Component

**Purpose**: Generate buy/sell signals based on RSI mean reversion logic.

**Integration Guide**:

1. In Initialize():
   ```python
   from strategy_components.indicators.add_rsi import add_rsi
   from strategy_components.signals.mean_reversion import MeanReversionSignal
   
   # Add RSI indicator
   self.rsi = add_rsi(self, symbol="SPY", period=14)
   
   # Create signal generator
   self.signal = MeanReversionSignal(
       oversold_threshold=30,
       overbought_threshold=70
   )
   
   # Track position
   self.is_long = False
   ```

2. In OnData():
   ```python
   if not self.rsi.IsReady:
       return
   
   rsi_value = self.rsi.Current.Value
   
   # Get signal
   signal = self.signal.get_signal(rsi_value, self.is_long)
   
   if signal == "BUY":
       self.SetHoldings(self.symbol, 1.0)
       self.is_long = True
   elif signal == "SELL":
       self.Liquidate(self.symbol)
       self.is_long = False
   ```

**Parameters**:
- oversold_threshold: int - RSI level for buy signal (default: 30)
- overbought_threshold: int - RSI level for sell signal (default: 70)

**Returns**: "BUY", "SELL", or None

**Logic**:
- BUY when RSI < oversold_threshold (not already long)
- SELL when RSI > overbought_threshold (currently long)
"""

class MeanReversionSignal:
    """Generate mean reversion signals based on RSI."""
    
    def __init__(self, oversold_threshold=30, overbought_threshold=70):
        """
        Initialize mean reversion signal generator.
        
        Args:
            oversold_threshold: RSI level for oversold (buy signal)
            overbought_threshold: RSI level for overbought (sell signal)
        """
        self.oversold_threshold = oversold_threshold
        self.overbought_threshold = overbought_threshold
    
    def get_signal(self, rsi_value, is_long):
        """
        Get trading signal based on RSI value and current position.
        
        Args:
            rsi_value: Current RSI value
            is_long: Boolean indicating if currently long
        
        Returns:
            "BUY", "SELL", or None
        """
        # Entry signal: RSI oversold (not already long)
        if not is_long and rsi_value < self.oversold_threshold:
            return "BUY"
        
        # Exit signal: RSI overbought (currently long)
        elif is_long and rsi_value > self.overbought_threshold:
            return "SELL"
        
        # No signal
        return None
