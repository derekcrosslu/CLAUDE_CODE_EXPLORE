"""
Enhanced Test Strategy for QuantConnect
Advanced RSI mean-reversion strategy with risk management and multiple confirmations

Features:
- RSI-based mean reversion
- Bollinger Bands for volatility confirmation
- Moving averages for trend filtering
- ATR-based position sizing
- Stop loss and take profit
- Trade logging and performance tracking
"""
from AlgorithmImports import *


class TestStrategy(QCAlgorithm):
    """
    Enhanced RSI Mean-Reversion Strategy (OPTIMIZATION TEST 1 - Very Permissive)

    Entry Logic:
    - Long: RSI < 50 (very relaxed) AND price near lower BB (within 10%)
    - NO 200 SMA filter (removed to enable trades in bull market)

    Exit Logic:
    - Take profit: RSI > 70 (overbought)
    - Stop loss: 3% below entry price
    - Trailing stop: Move stop loss up as trade profits

    Risk Management:
    - Position sizing based on ATR (volatility)
    - Maximum 3% risk per trade
    - Stop loss at 3%
    """

    def initialize(self):
        """Initialize algorithm with enhanced indicators and settings"""
        # Backtest period
        self.set_start_date(2023, 1, 1)
        self.set_end_date(2023, 12, 31)
        self.set_cash(100000)

        # Add equity
        self.spy = self.add_equity("SPY", Resolution.DAILY)

        # OPTIMIZABLE PARAMETERS - using get_parameter for optimization
        rsi_period = self.get_parameter("rsi_period", 14)
        rsi_oversold_threshold = self.get_parameter("rsi_oversold", 30)
        rsi_overbought_threshold = self.get_parameter("rsi_overbought", 70)
        bb_period = self.get_parameter("bb_period", 20)
        bb_std_dev = self.get_parameter("bb_std_dev", 2)
        bb_distance_pct = self.get_parameter("bb_distance_pct", 1.02)
        use_trend_filter = self.get_parameter("use_trend_filter", 1)  # 1=true, 0=false

        # Store parameters for use in on_data
        self.rsi_oversold = rsi_oversold_threshold
        self.rsi_overbought = rsi_overbought_threshold
        self.bb_distance = bb_distance_pct
        self.use_sma_filter = use_trend_filter > 0

        # Core indicators (now parameterized)
        self.rsi = self.rsi(self.spy.symbol, int(rsi_period))
        self.bb = self.bb(self.spy.symbol, int(bb_period), bb_std_dev)
        self.atr = self.atr(self.spy.symbol, 14)

        # Trend filter - only trade in uptrends (if enabled)
        self.sma_200 = self.sma(self.spy.symbol, 200)

        # Additional momentum indicator
        self.macd = self.macd(self.spy.symbol, 12, 26, 9)

        # Strategy state
        self.entry_price = None
        self.stop_loss_price = None
        self.take_profit_price = None
        self.stop_loss_pct = 0.03  # 3% stop loss
        self.take_profit_pct = 0.08  # 8% take profit
        self.trailing_stop_trigger = 0.05  # Start trailing at 5% profit

        # Trade statistics
        self.trades_won = 0
        self.trades_lost = 0
        self.total_trades = 0

        # Warm up period for longest indicator (200 SMA)
        self.set_warm_up(200)

        # Create custom charts
        self._setup_charts()

        self.debug("Enhanced strategy initialized successfully")
        self.debug(f"Initial capital: ${self.portfolio.cash:,.2f}")

    def _setup_charts(self):
        """Setup custom charts for visualization"""
        # Trade signals chart
        trade_plot = Chart("Trade Signals")
        trade_plot.add_series(Series("Buy", SeriesType.SCATTER, 0))
        trade_plot.add_series(Series("Sell", SeriesType.SCATTER, 0))
        trade_plot.add_series(Series("Stop Loss", SeriesType.SCATTER, 0))
        self.add_chart(trade_plot)

        # Performance chart
        perf_plot = Chart("Performance")
        perf_plot.add_series(Series("Win Rate %", SeriesType.LINE, 1))
        self.add_chart(perf_plot)

    def on_data(self, data):
        """Main trading logic with enhanced entry/exit rules"""
        # Skip during warm-up period
        if self.is_warming_up:
            return

        # Validate data availability
        if not data.contains_key(self.spy.symbol):
            return

        # Get data bar (additional safety check)
        bar = data.get(self.spy.symbol)
        if bar is None:
            return

        # Wait for all indicators to be ready
        if not self._indicators_ready():
            return

        # Get current values
        current_price = bar.close
        rsi_value = self.rsi.current.value
        bb_upper = self.bb.upper_band.current.value
        bb_lower = self.bb.lower_band.current.value
        bb_middle = self.bb.middle_band.current.value
        sma_200_value = self.sma_200.current.value

        # Check stop loss and take profit first
        if self._check_exit_conditions(current_price):
            return

        # Update trailing stop if in profit
        self._update_trailing_stop(current_price)

        # ENTRY LOGIC - Only if not invested
        if not self.portfolio.invested:
            # Oversold condition: RSI < threshold (parameterized)
            oversold = rsi_value < self.rsi_oversold

            # Price near lower Bollinger Band (parameterized distance)
            near_lower_bb = current_price < (bb_lower * self.bb_distance)

            # Trend filter: Only trade if above 200 SMA (if enabled via parameter)
            in_uptrend = current_price > sma_200_value if self.use_sma_filter else True

            # Entry signal with parameterized conditions
            if oversold and near_lower_bb and in_uptrend:
                position_size = self._calculate_position_size(current_price)

                if position_size > 0:
                    self.set_holdings(self.spy.symbol, position_size)
                    self.entry_price = current_price
                    self.stop_loss_price = current_price * (1 - self.stop_loss_pct)
                    self.take_profit_price = current_price * (1 + self.take_profit_pct)

                    self.plot("Trade Signals", "Buy", current_price)
                    self.debug(f"BUY SIGNAL - Price: ${current_price:.2f}, RSI: {rsi_value:.2f}, "
                              f"Position: {position_size:.2%}")
                    self.debug(f"Stop Loss: ${self.stop_loss_price:.2f}, "
                              f"Take Profit: ${self.take_profit_price:.2f}")

        # Plot indicators for analysis
        self._plot_indicators(current_price, rsi_value, bb_upper, bb_lower, bb_middle)

    def _indicators_ready(self):
        """Check if all indicators are ready to use"""
        return (self.rsi.is_ready and
                self.bb.is_ready and
                self.atr.is_ready and
                self.sma_200.is_ready and
                self.macd.is_ready)

    def _check_exit_conditions(self, current_price):
        """Check and execute exit conditions (stop loss, take profit, RSI overbought)"""
        if not self.portfolio.invested:
            return False

        rsi_value = self.rsi.current.value
        exit_reason = None

        # Stop loss hit
        if current_price <= self.stop_loss_price:
            exit_reason = "Stop Loss"
            self.plot("Trade Signals", "Stop Loss", current_price)

        # Take profit hit
        elif current_price >= self.take_profit_price:
            exit_reason = "Take Profit"
            self.plot("Trade Signals", "Sell", current_price)

        # RSI overbought - mean reversion exit (parameterized)
        elif rsi_value > self.rsi_overbought:
            exit_reason = "RSI Overbought"
            self.plot("Trade Signals", "Sell", current_price)

        # Execute exit if any condition met
        if exit_reason:
            self.liquidate(self.spy.symbol)
            self._log_trade_exit(exit_reason, current_price)
            return True

        return False

    def _update_trailing_stop(self, current_price):
        """Update stop loss to trailing stop when trade is profitable"""
        if not self.portfolio.invested or self.entry_price is None:
            return

        # Calculate current profit
        profit_pct = (current_price - self.entry_price) / self.entry_price

        # If profit exceeds threshold, activate trailing stop
        if profit_pct > self.trailing_stop_trigger:
            # Set stop to lock in some profit (trail by 2%)
            new_stop = current_price * 0.98

            # Only move stop up, never down
            if new_stop > self.stop_loss_price:
                self.stop_loss_price = new_stop
                self.debug(f"Trailing stop updated to ${new_stop:.2f} "
                          f"(Profit: {profit_pct:.2%})")

    def _calculate_position_size(self, current_price):
        """Calculate position size based on volatility and risk management"""
        if not self.atr.is_ready:
            return 0.5  # Default 50% if ATR not ready

        # Calculate volatility as percentage
        atr_value = self.atr.current.value
        volatility_pct = atr_value / current_price

        # Target 3% portfolio risk
        target_risk = 0.03
        stop_distance = self.stop_loss_pct

        # Position size = (Portfolio Risk) / (Stop Loss %)
        # Adjusted for volatility
        position_size = target_risk / stop_distance

        # Reduce size if volatility is high
        if volatility_pct > 0.02:  # If volatility > 2%
            position_size *= 0.5

        # Cap at 80% maximum allocation
        position_size = min(position_size, 0.8)

        # Floor at 20% minimum
        position_size = max(position_size, 0.2)

        self.debug(f"Position sizing - Volatility: {volatility_pct:.2%}, "
                  f"Size: {position_size:.2%}")

        return position_size

    def _log_trade_exit(self, reason, exit_price):
        """Log trade exit details and update statistics"""
        if self.entry_price is None:
            return

        # Calculate P&L
        pnl_pct = (exit_price - self.entry_price) / self.entry_price
        pnl_dollars = self.portfolio[self.spy.symbol].unrealized_profit

        # Update statistics
        self.total_trades += 1
        if pnl_pct > 0:
            self.trades_won += 1
        else:
            self.trades_lost += 1

        # Calculate win rate
        win_rate = (self.trades_won / self.total_trades * 100) if self.total_trades > 0 else 0

        # Log trade details
        self.debug(f"EXIT ({reason}) - Entry: ${self.entry_price:.2f}, "
                  f"Exit: ${exit_price:.2f}, P&L: {pnl_pct:.2%} (${pnl_dollars:.2f})")
        self.debug(f"Trade Stats - Total: {self.total_trades}, "
                  f"Won: {self.trades_won}, Lost: {self.trades_lost}, "
                  f"Win Rate: {win_rate:.1f}%")

        # Plot win rate
        self.plot("Performance", "Win Rate %", win_rate)

        # Reset trade state
        self.entry_price = None
        self.stop_loss_price = None
        self.take_profit_price = None

    def _plot_indicators(self, price, rsi, bb_upper, bb_lower, bb_middle):
        """Plot indicators for visual analysis"""
        self.plot("Indicators", "Price", price)
        self.plot("Indicators", "BB Upper", bb_upper)
        self.plot("Indicators", "BB Lower", bb_lower)
        self.plot("Indicators", "BB Middle", bb_middle)
        self.plot("RSI", "RSI", rsi)
        self.plot("RSI", "Overbought", 70)
        self.plot("RSI", "Oversold", 50)

    def on_order_event(self, order_event):
        """Called when order status changes"""
        if order_event.status == OrderStatus.FILLED:
            self.debug(f"Order FILLED: {order_event.symbol} - "
                      f"{order_event.fill_quantity} shares @ ${order_event.fill_price:.2f}")

    def on_end_of_algorithm(self):
        """Called at the end of backtest - print final statistics"""
        final_value = self.portfolio.total_portfolio_value
        total_return = (final_value / 100000 - 1)

        self.debug("=" * 50)
        self.debug("BACKTEST COMPLETE")
        self.debug("=" * 50)
        self.debug(f"Initial Capital: $100,000.00")
        self.debug(f"Final Portfolio Value: ${final_value:,.2f}")
        self.debug(f"Total Return: {total_return:.2%}")
        self.debug(f"Total Trades: {self.total_trades}")
        self.debug(f"Winning Trades: {self.trades_won}")
        self.debug(f"Losing Trades: {self.trades_lost}")

        if self.total_trades > 0:
            win_rate = self.trades_won / self.total_trades * 100
            self.debug(f"Win Rate: {win_rate:.1f}%")

        self.debug("=" * 50)
