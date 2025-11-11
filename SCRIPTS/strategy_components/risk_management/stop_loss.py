"""
Stop Loss Risk Management Component

**Purpose**: Protect capital with percentage-based or trailing stop loss.

**Integration Guide**:

1. In Initialize():
   ```python
   from strategy_components.risk_management.stop_loss import StopLossManager
   
   # Create stop loss manager
   self.stop_loss = StopLossManager(
       stop_loss_pct=0.05,  # 5% stop loss
       trailing=False
   )
   
   # Track entry price
   self.entry_price = None
   ```

2. In OnData() - After Entry:
   ```python
   if signal == "BUY":
       self.SetHoldings(self.symbol, 1.0)
       self.is_long = True
       self.entry_price = price
       self.stop_loss.set_entry_price(price)
   ```

3. In OnData() - Check Stop Loss:
   ```python
   if self.is_long:
       current_price = data[self.symbol].Close
       
       if self.stop_loss.should_exit(current_price):
           self.Liquidate(self.symbol)
           self.is_long = False
           self.Debug(f"STOP LOSS: Exit at {current_price}")
   ```

**Parameters**:
- stop_loss_pct: float - Stop loss percentage (e.g., 0.05 = 5%)
- trailing: bool - Use trailing stop loss (default: False)

**Methods**:
- set_entry_price(price): Set entry price for stop calculation
- should_exit(current_price): Check if stop loss triggered
- get_stop_price(): Get current stop loss price

**Types**:
- Fixed: Stop at entry_price * (1 - stop_loss_pct)
- Trailing: Stop moves up with price, never down
"""

class StopLossManager:
    """Manage stop loss for risk management."""
    
    def __init__(self, stop_loss_pct=0.05, trailing=False):
        """
        Initialize stop loss manager.
        
        Args:
            stop_loss_pct: Stop loss percentage (e.g., 0.05 = 5%)
            trailing: Use trailing stop loss
        """
        self.stop_loss_pct = stop_loss_pct
        self.trailing = trailing
        self.entry_price = None
        self.stop_price = None
        self.highest_price = None
    
    def set_entry_price(self, price):
        """
        Set entry price and calculate initial stop.
        
        Args:
            price: Entry price
        """
        self.entry_price = price
        self.stop_price = price * (1 - self.stop_loss_pct)
        self.highest_price = price
    
    def should_exit(self, current_price):
        """
        Check if stop loss triggered.
        
        Args:
            current_price: Current market price
        
        Returns:
            Boolean: True if should exit
        """
        if self.stop_price is None:
            return False
        
        # Update trailing stop
        if self.trailing and current_price > self.highest_price:
            self.highest_price = current_price
            new_stop = self.highest_price * (1 - self.stop_loss_pct)
            # Only move stop up, never down
            if new_stop > self.stop_price:
                self.stop_price = new_stop
        
        # Check if price hit stop
        return current_price <= self.stop_price
    
    def get_stop_price(self):
        """Get current stop loss price."""
        return self.stop_price
    
    def reset(self):
        """Reset stop loss (after exit)."""
        self.entry_price = None
        self.stop_price = None
        self.highest_price = None
