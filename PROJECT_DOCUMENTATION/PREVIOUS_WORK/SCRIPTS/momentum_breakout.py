"""
Momentum Breakout Strategy
Hypothesis 2: Buy when price breaks above 20-day high with volume surge

Entry Logic:
- Price breaks above 20-day rolling high
- Volume > 1.5x average volume (confirmation)
- Long-only strategy

Testing Period: 2023-01-01 to 2024-12-31
Expected: Momentum strategies should perform well in trending markets
"""

from AlgorithmImports import *


class MomentumBreakoutStrategy(QCAlgorithm):

    def initialize(self):
        """
        Initialize algorithm parameters and data subscriptions
        """
        # Set date range for backtest
        self.set_start_date(2023, 1, 1)
        self.set_end_date(2024, 12, 31)

        # Set starting capital
        self.set_cash(100000)

        # Add SPY as our trading instrument
        self.symbol = self.add_equity("SPY", Resolution.DAILY).symbol

        # Strategy parameters (can be optimized later)
        self.lookback_period = self.get_parameter("lookback_period", 20)
        self.volume_multiplier = self.get_parameter("volume_multiplier", 1.5)
        self.position_size = self.get_parameter("position_size", 0.95)

        # Rolling windows for price and volume
        self.price_window = RollingWindow[float](int(self.lookback_period))
        self.volume_window = RollingWindow[float](int(self.lookback_period))

        # Track if we're in a position
        self.position_active = False

        # Schedule function to run at market close
        self.schedule.on(
            self.date_rules.every_day(self.symbol),
            self.time_rules.before_market_close(self.symbol, 30),
            self.check_signals
        )

        # Warm up period to populate rolling windows
        self.set_warm_up(int(self.lookback_period))

        self.debug(f"Strategy initialized: {self.lookback_period}-day breakout, "
                  f"{self.volume_multiplier}x volume confirmation")


    def on_data(self, data):
        """
        Update rolling windows with daily data
        """
        if not data.contains_key(self.symbol):
            return

        # Get current bar data
        bar = data[self.symbol]

        # Validate bar is not None before accessing attributes
        if bar is None:
            return

        # Update rolling windows
        self.price_window.add(bar.close)
        self.volume_window.add(bar.volume)


    def check_signals(self):
        """
        Check for entry and exit signals
        Called daily before market close
        """
        # Skip if warming up or windows not ready
        if self.is_warming_up or not self.price_window.is_ready or not self.volume_window.is_ready:
            return

        # Get current price and volume
        current_price = self.securities[self.symbol].price
        current_volume = self.securities[self.symbol].volume

        # Calculate indicators from PREVIOUS days (exclude today)
        # price_window[0] is most recent (today), so start from index 1
        high_20 = max([self.price_window[i] for i in range(1, self.price_window.count)])
        avg_volume = sum([self.volume_window[i] for i in range(1, self.volume_window.count)]) / (self.volume_window.count - 1)

        # Entry signal: Breakout above 20-day high with volume confirmation
        breakout = current_price > high_20  # Now comparing to PREVIOUS highs
        volume_surge = current_volume > (avg_volume * self.volume_multiplier)

        # Check if we should enter a position
        if not self.position_active and breakout and volume_surge:
            # Enter long position
            quantity = int((self.portfolio.cash * self.position_size) / current_price)
            if quantity > 0:
                self.market_order(self.symbol, quantity)
                self.position_active = True
                self.debug(f"BUY: Price {current_price:.2f} > 20D High {high_20:.2f}, "
                          f"Volume {current_volume:.0f} > {avg_volume * self.volume_multiplier:.0f}")

        # Exit signal: Simple 10% trailing stop or price below 20-day high
        elif self.position_active:
            holdings = self.portfolio[self.symbol]
            unrealized_profit_pct = holdings.unrealized_profit_percent

            # Exit conditions
            trailing_stop_hit = unrealized_profit_pct < -0.10  # 10% stop loss
            below_breakout = current_price < high_20  # Price fell back below previous 20-day high

            if trailing_stop_hit or below_breakout:
                self.liquidate(self.symbol)
                self.position_active = False
                reason = "Stop Loss" if trailing_stop_hit else "Below 20D High"
                self.debug(f"SELL: {reason}, Price {current_price:.2f}, "
                          f"P/L: {unrealized_profit_pct:.2%}")


    def on_order_event(self, order_event):
        """
        Log order events for debugging
        """
        if order_event.status == OrderStatus.FILLED:
            self.debug(f"Order filled: {order_event.symbol} {order_event.fill_quantity} @ {order_event.fill_price}")
