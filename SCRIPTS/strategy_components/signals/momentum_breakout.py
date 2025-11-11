"""
Momentum Breakout Signal Component

**Purpose**: Generate buy/sell signals based on price breaking above/below moving average.

**Integration Guide**:

1. In Initialize():
   ```python
   from strategy_components.indicators.add_sma import add_sma
   from strategy_components.signals.momentum_breakout import MomentumBreakoutSignal
   
   # Add SMA indicator
   self.sma = add_sma(self, symbol="SPY", period=20)
   
   # Create signal generator
   self.signal = MomentumBreakoutSignal(volume_confirmation=True)
   
   # Track position
   self.is_long = False
   ```

2. In OnData():
   ```python
   if not self.sma.IsReady:
       return
   
   price = data[self.symbol].Close
   sma_value = self.sma.Current.Value
   volume = data[self.symbol].Volume
   
   # Get signal
   signal = self.signal.get_signal(price, sma_value, volume, self.is_long)
   
   if signal == "BUY":
       self.SetHoldings(self.symbol, 1.0)
       self.is_long = True
   elif signal == "SELL":
       self.Liquidate(self.symbol)
       self.is_long = False
   ```

**Parameters**:
- volume_confirmation: bool - Require volume confirmation (default: False)
- volume_multiplier: float - Volume must be X times average (default: 1.5)

**Returns**: "BUY", "SELL", or None

**Logic**:
- BUY when price crosses above SMA (with optional volume confirmation)
- SELL when price crosses below SMA
"""

class MomentumBreakoutSignal:
    """Generate momentum breakout signals based on SMA crossover."""
    
    def __init__(self, volume_confirmation=False, volume_multiplier=1.5):
        """
        Initialize momentum breakout signal generator.
        
        Args:
            volume_confirmation: Require volume confirmation
            volume_multiplier: Volume threshold multiplier
        """
        self.volume_confirmation = volume_confirmation
        self.volume_multiplier = volume_multiplier
        self.prev_price = None
        self.prev_sma = None
        self.avg_volume = None
        self.volume_history = []
    
    def get_signal(self, price, sma_value, volume=None, is_long=False):
        """
        Get trading signal based on price/SMA crossover.
        
        Args:
            price: Current price
            sma_value: Current SMA value
            volume: Current volume (optional)
            is_long: Boolean indicating if currently long
        
        Returns:
            "BUY", "SELL", or None
        """
        # Track volume for average calculation
        if volume is not None:
            self.volume_history.append(volume)
            if len(self.volume_history) > 20:
                self.volume_history.pop(0)
            self.avg_volume = sum(self.volume_history) / len(self.volume_history)
        
        # Need previous values for crossover detection
        if self.prev_price is None or self.prev_sma is None:
            self.prev_price = price
            self.prev_sma = sma_value
            return None
        
        # Detect crossover
        crossed_above = self.prev_price <= self.prev_sma and price > sma_value
        crossed_below = self.prev_price >= self.prev_sma and price < sma_value
        
        # Volume confirmation
        volume_ok = True
        if self.volume_confirmation and volume is not None and self.avg_volume is not None:
            volume_ok = volume > (self.avg_volume * self.volume_multiplier)
        
        # Generate signals
        signal = None
        
        if not is_long and crossed_above and volume_ok:
            signal = "BUY"
        elif is_long and crossed_below:
            signal = "SELL"
        
        # Update previous values
        self.prev_price = price
        self.prev_sma = sma_value
        
        return signal
