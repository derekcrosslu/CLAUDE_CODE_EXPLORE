"""
Simple Momentum Strategy - Hypothesis 3

Hypothesis: Buy when price crosses above 20-day MA with volume > 1.5x average
Rationale: Moving average identifies trend, volume confirms strength

Entry: Price crosses above SMA(20) AND volume > 1.5x average volume
Exit: Price crosses below SMA(20)
Risk Management: 5% stop loss, max 100% allocation
"""

from AlgorithmImports import *


class SimpleMomentumStrategy(QCAlgorithm):

    def initialize(self):
        """Initialize algorithm parameters and indicators"""
        # Set backtest period (2 years for meaningful results)
        self.set_start_date(2022, 1, 1)
        self.set_end_date(2024, 1, 1)
        self.set_cash(100000)

        # Add SPY as the trading symbol
        self.symbol = self.add_equity("SPY", Resolution.DAILY).symbol

        # Create indicators (use SMA method with capital letters to avoid overwriting)
        self.price_sma = self.SMA(self.symbol, 20, Resolution.DAILY)
        self.volume_sma = self.SMA(self.symbol, 20, Resolution.DAILY, Field.VOLUME)

        # Track entry price for stop loss
        self.entry_price = None
        self.stop_loss_pct = 0.05  # 5% stop loss

        # Track previous price for crossover detection
        self.previous_price = None

        # Warm up indicators
        self.set_warm_up(20)

    def on_data(self, data):
        """Execute strategy logic on each data point"""
        # Check data availability
        if not data.contains_key(self.symbol):
            return

        # Wait for indicators to be ready
        if not self.price_sma.is_ready or not self.volume_sma.is_ready:
            return

        # Skip during warm-up period
        if self.is_warming_up:
            return

        # Get current market data
        bar = data[self.symbol]

        # Additional NoneType check (bar can be None even if key exists)
        if bar is None:
            return

        current_price = bar.close
        current_volume = bar.volume

        # Calculate volume ratio
        avg_volume = self.volume_sma.current.value
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0

        # Get indicator values
        sma_value = self.price_sma.current.value

        # === ENTRY LOGIC ===
        if not self.portfolio.invested:
            # Check for bullish crossover AND volume confirmation
            if self.previous_price is not None:
                # Price crossed above SMA
                crossed_above = (self.previous_price <= sma_value and current_price > sma_value)

                # Volume is elevated (> 1.5x average)
                volume_confirmed = volume_ratio > 1.5

                if crossed_above and volume_confirmed:
                    # Enter long position (100% allocation)
                    self.set_holdings(self.symbol, 1.0)
                    self.entry_price = current_price
                    self.debug(f"BUY: Price={current_price:.2f}, SMA={sma_value:.2f}, Volume Ratio={volume_ratio:.2f}x")

        # === EXIT LOGIC ===
        else:
            # Exit if price crosses below SMA
            if self.previous_price is not None:
                crossed_below = (self.previous_price >= sma_value and current_price < sma_value)

                if crossed_below:
                    self.liquidate(self.symbol)
                    profit_pct = (current_price - self.entry_price) / self.entry_price if self.entry_price else 0
                    self.debug(f"SELL (SMA Cross): Price={current_price:.2f}, SMA={sma_value:.2f}, P&L={profit_pct:.2%}")
                    self.entry_price = None

            # Stop loss check
            if self.entry_price is not None:
                loss_pct = (self.entry_price - current_price) / self.entry_price

                if loss_pct > self.stop_loss_pct:
                    self.liquidate(self.symbol)
                    self.debug(f"SELL (Stop Loss): Price={current_price:.2f}, Loss={loss_pct:.2%}")
                    self.entry_price = None

        # Update previous price for next iteration
        self.previous_price = current_price
