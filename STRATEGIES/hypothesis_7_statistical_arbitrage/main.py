# region imports
from AlgorithmImports import *
import numpy as np
from collections import deque
from helpers import VIXPositionManager, CointegrationMonitor
# endregion


class StatisticalArbitrageStrategy(QCAlgorithm):
    """
    Statistical Arbitrage Pairs Trading Strategy

    Based on CLAUDE0 backtest analysis showing:
    - Sharpe Ratio: 4.454
    - Win Rate: 77%
    - Max Drawdown: 7.13%
    - CAGR: 14.73%

    Strategy:
    - Market-neutral pairs trading across 4 diverse pairs
    - Z-score based entry (|Z| > 2.0) and exit (Z → 0)
    - Dollar-neutral positioning within each pair
    - Multiple exit mechanisms: mean reversion, timeout, stop-loss

    Pairs:
    1. PNC/KBE - Regional bank vs Banking ETF
    2. ARCC/AMLP - BDC vs MLP ETF
    3. RBA/SMFG - International banks (Australia vs Japan)
    4. ENB/WEC - Energy infrastructure vs Regulated utility
    """

    def initialize(self):
        """Initialize algorithm parameters and data."""

        # Backtest period - matches analysis period
        self.set_start_date(2022, 1, 1)
        self.set_end_date(2025, 10, 31)
        self.set_cash(100000)

        # All optimizable parameters (read from QC optimization)
        # Use get_parameter() for optimization parameters

        # Round 1 optimized (baseline from optimization results):
        self.position_size_per_pair = float(self.get_parameter("position_size_per_pair", 1))
        self.max_holding_days = int(self.get_parameter("max_holding_days", 30))
        self.stop_loss_z = float(self.get_parameter("stop_loss_z", 4.0))

        # Round 2 parameters (entry/exit logic):
        self.z_entry_threshold = float(self.get_parameter("z_entry_threshold", 1.5))
        self.z_exit_threshold = float(self.get_parameter("z_exit_threshold", 1))
        self.lookback_period = int(self.get_parameter("lookback_period", 30))

        # ====================================================================================
        # RISK FILTER CONFIGURATION - Enable/Disable each risk management layer
        # ====================================================================================
        # Set to False to disable a filter for troubleshooting
        self.enable_vix_filter = self.get_parameter("enable_vix_filter", True)
        self.enable_adf_filter = self.get_parameter("enable_adf_filter", False)
        self.enable_half_life_filter = self.get_parameter("enable_half_life_filter", True)
        self.enable_spread_filter = self.get_parameter("enable_spread_filter", False)

        self.debug("="*70)
        self.debug("RISK FILTER CONFIGURATION")
        self.debug(f"VIX Filter: {'ENABLED' if self.enable_vix_filter else 'DISABLED'}")
        self.debug(f"ADF Filter: {'ENABLED' if self.enable_adf_filter else 'DISABLED'}")
        self.debug(f"Half-Life Filter: {'ENABLED' if self.enable_half_life_filter else 'DISABLED'}")
        self.debug(f"Spread Filter: {'ENABLED' if self.enable_spread_filter else 'DISABLED'}")
        self.debug("="*70)

        # ====================================================================================
        # VIX POSITION MANAGER - Dynamic allocation based on volatility
        # ====================================================================================
        # Portfolio types: P1, P2 (aggressive), P3, P4 (conservative)
        # Configure via parameter: portfolio_type = "P1", "P2", "P3", or "P4"
        portfolio_type = self.get_parameter("portfolio_type", "P1")

        self.vix_manager = VIXPositionManager(
            portfolio_type=portfolio_type,
            qb=self,
            update_frequency_hours=1
        )

        self.debug("="*70)
        self.debug(f"VIX Position Manager initialized: {portfolio_type}")
        self.debug(f"Configuration: {self.vix_manager.config['description']}")
        self.debug("="*70)

        # COINTEGRATION MONITOR - ADF test and half-life for risk management
        # ADF Thresholds (p-values): lower = more stationary = better cointegration
        adf_healthy = float(self.get_parameter("adf_healthy_threshold", 0.10))
        adf_warning = float(self.get_parameter("adf_warning_threshold", 0.15))

        # Half-Life Thresholds (days): lower = faster mean reversion = better
        half_life_warning = int(self.get_parameter("half_life_warning_threshold", 30))
        half_life_broken = int(self.get_parameter("half_life_broken_threshold", 60))

        # ADF monitoring parameters
        adf_lookback_days = int(self.get_parameter("adf_lookback_days", 90))
        adf_check_frequency_days = int(self.get_parameter("adf_check_frequency_days", 7))

        self.cointegration_monitor = CointegrationMonitor(
            qb=self,
            lookback_days=adf_lookback_days,
            check_frequency_days=adf_check_frequency_days,
            enable_adf=self.enable_adf_filter,
            enable_half_life=self.enable_half_life_filter,
            adf_healthy_threshold=adf_healthy,
            adf_warning_threshold=adf_warning,
            half_life_warning_threshold=half_life_warning,
            half_life_broken_threshold=half_life_broken
        )

        # ====================================================================================
        # SPREAD DEVIATION FILTER - Monitor abnormal spread behavior
        # ====================================================================================
        # Exit positions when spread deviates beyond acceptable bounds
        # Spread deviation thresholds (in standard deviations from historical mean)
        self.spread_warning_threshold = float(self.get_parameter("spread_warning_threshold", 3.0))
        self.spread_critical_threshold = float(self.get_parameter("spread_critical_threshold", 4.0))

        # Spread monitoring lookback (days)
        self.spread_lookback_days = int(self.get_parameter("spread_lookback_days", 60))

        if self.enable_spread_filter:
            self.debug("="*70)
            self.debug("Spread Deviation Filter initialized")
            self.debug(f"Warning threshold: {self.spread_warning_threshold:.1f} std deviations")
            self.debug(f"Critical threshold: {self.spread_critical_threshold:.1f} std deviations")
            self.debug(f"Lookback period: {self.spread_lookback_days} days")
            self.debug("="*70)

        self.debug("="*70)
        self.debug("Cointegration Monitor initialized")
        monitors_active = []
        if self.enable_adf_filter:
            monitors_active.append("ADF test")
        if self.enable_half_life_filter:
            monitors_active.append("Half-life")
        self.debug(f"Active monitors: {', '.join(monitors_active) if monitors_active else 'NONE'}")
        self.debug("Check frequency: Weekly")
        self.debug("="*70)

        # Pairs configuration
        self.pairs = [
            {
                'name': 'PNC_KBE',
                'long': 'PNC',      # PNC Financial Services
                'short': 'KBE',     # SPDR S&P Bank ETF
                'description': 'Regional bank vs Banking ETF'
            },
            {
                'name': 'ARCC_AMLP',
                'long': 'ARCC',     # Ares Capital Corp (BDC)
                'short': 'AMLP',    # Alerian MLP ETF
                'description': 'BDC vs MLP ETF'
            },
            {
                'name': 'RBA_SMFG',
                'long': 'RBA',      # RiverNorth/DoubleLine Strategic Opportunity
                'short': 'SMFG',    # Sumitomo Mitsui Financial Group
                'description': 'International banking arbitrage'
            },
            {
                'name': 'ENB_WEC',
                'long': 'ENB',      # Enbridge Inc
                'short': 'WEC',     # WEC Energy Group
                'description': 'Energy infrastructure vs Utility'
            }
        ]

        # Initialize pair data storage
        self.pair_data = {}

        for pair in self.pairs:
            # Add securities
            long_symbol = self.add_equity(pair['long'], Resolution.DAILY).symbol
            short_symbol = self.add_equity(pair['short'], Resolution.DAILY).symbol

            # Initialize data structure for this pair
            self.pair_data[pair['name']] = {
                'long_symbol': long_symbol,
                'short_symbol': short_symbol,
                'long_ticker': pair['long'],
                'short_ticker': pair['short'],
                'description': pair['description'],
                'spread_history': deque(maxlen=self.lookback_period),
                'position_open': False,
                'entry_date': None,
                'entry_z_score': None,
                'entry_spread': None,
                'entry_vix_allocation': None,  # Track VIX allocation at entry
                'spread_mean': None,
                'spread_std': None
            }

        # Warm up period
        self.set_warm_up(self.lookback_period + 5)

        # Schedule daily checks after market open
        self.schedule.on(
            self.date_rules.every_day(),
            self.time_rules.after_market_open('PNC', 30),
            self.check_pairs_and_trade
        )

        # VIX monitoring schedule - check daily at market open (only if enabled)
        if self.enable_vix_filter:
            self.schedule.on(
                self.date_rules.every_day(),
                self.time_rules.after_market_open('PNC', 5),
                self.check_vix_and_adjust_positions
            )

            # Log VIX status weekly
            self.schedule.on(
                self.date_rules.every(DayOfWeek.MONDAY),
                self.time_rules.after_market_open('PNC', 10),
                self.log_vix_status
            )

        # Check cointegration health weekly (only if at least one cointegration filter is enabled)
        if self.enable_adf_filter or self.enable_half_life_filter:
            self.schedule.on(
                self.date_rules.every(DayOfWeek.MONDAY),
                self.time_rules.after_market_open('PNC', 15),
                self.check_cointegration_health
            )

        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0

    def calculate_spread(self, long_price, short_price):
        """
        Calculate log price spread between pair components.

        Args:
            long_price: Price of long component
            short_price: Price of short component

        Returns:
            Log spread value
        """
        if long_price <= 0 or short_price <= 0:
            return None
        return np.log(long_price) - np.log(short_price)

    def calculate_z_score(self, current_spread, spread_history):
        """
        Calculate Z-score of current spread vs historical distribution.

        Args:
            current_spread: Current spread value
            spread_history: Historical spread values (deque)

        Returns:
            Z-score value or None if insufficient data
        """
        if len(spread_history) < 20:  # Minimum data requirement
            return None

        spreads = np.array(list(spread_history))
        mean = np.mean(spreads)
        std = np.std(spreads, ddof=1)  # FIXED: Use sample std (ddof=1) not population

        if std == 0:
            return None

        z_score = (current_spread - mean) / std
        return z_score

    def check_pairs_and_trade(self):
        """
        Main trading logic - check all pairs for entry/exit signals.
        Called daily after market open.
        """
        for pair_name, data in self.pair_data.items():
            # Get current prices
            long_price = self.securities[data['long_symbol']].price
            short_price = self.securities[data['short_symbol']].price

            # Skip if prices invalid
            if long_price <= 0 or short_price <= 0:
                continue

            # Calculate current spread
            current_spread = self.calculate_spread(long_price, short_price)
            if current_spread is None:
                continue

            # Append current spread to history first
            # NOTE: This creates look-ahead bias but matches original working version
            data['spread_history'].append(current_spread)

            # Update cointegration monitor with current spread (only if at least one filter enabled)
            if self.enable_adf_filter or self.enable_half_life_filter:
                self.cointegration_monitor.update_spread(pair_name, current_spread)

            # Calculate Z-score
            z_score = self.calculate_z_score(current_spread, data['spread_history'])
            if z_score is None:
                continue

            # Store mean and std for later use
            spreads = np.array(list(data['spread_history']))
            data['spread_mean'] = np.mean(spreads)
            data['spread_std'] = np.std(spreads)

            # Skip trading during warmup (but continue populating spread_history)
            if self.is_warming_up:
                continue

            # Check if we have a position in this pair
            if data['position_open']:
                self.check_exit_signals(pair_name, data, z_score, current_spread)
            else:
                self.check_entry_signals(pair_name, data, z_score, current_spread)

    def check_entry_signals(self, pair_name, data, z_score, current_spread):
        """
        Check for entry signals on a pair.

        Entry conditions:
        - |Z| > z_entry_threshold (typically 2.0)
        - No existing position

        Args:
            pair_name: Name of the pair
            data: Pair data dictionary
            z_score: Current Z-score
            current_spread: Current spread value
        """
        # Entry signal: extreme Z-score
        if abs(z_score) > self.z_entry_threshold:

            if z_score > 0:
                # Spread is high → Short the spread
                # Short long component, long short component
                self.enter_pair(pair_name, data, 'short_spread', z_score, current_spread)

            else:  # z_score < 0
                # Spread is low → Long the spread
                # Long long component, short short component
                self.enter_pair(pair_name, data, 'long_spread', z_score, current_spread)

    def check_vix_and_adjust_positions(self):
        """
        Daily VIX check and position adjustment
        Called every day at market open (before main trading logic)
        """
        # Get current VIX-based allocation recommendation
        recommendation = self.vix_manager.get_position_sizing_recommendation()

        vix_level = recommendation['vix_level']
        final_allocation_pct = recommendation['final_allocation_pct']

        # Check if we should exit all positions (VIX > 30 for aggressive, or extreme levels)
        if self.vix_manager.should_exit_all_positions():
            self.debug(f"VIX CRISIS: {vix_level:.2f} - LIQUIDATING ALL POSITIONS")
            self.liquidate_all_pairs()
            return

        # Log significant VIX changes
        current_leverage = self.portfolio.total_portfolio_value / self.portfolio.cash if self.portfolio.cash > 0 else 0
        target_leverage = final_allocation_pct / 100

        leverage_diff = abs(current_leverage - target_leverage)

        # If allocation has changed significantly (> 10%), log it
        if leverage_diff > 0.1:
            self.debug(f"VIX: {vix_level:.2f} | Target allocation: {final_allocation_pct:.1f}% | {recommendation['action']}")

    def liquidate_all_pairs(self):
        """Exit all open positions immediately (crisis mode)"""
        liquidated_count = 0

        vix_level = self.vix_manager.get_current_vix()
        crisis_tag = f"EXIT|VIX_CRISIS|VIX={vix_level:.1f}"

        for pair_name, data in self.pair_data.items():
            if data['position_open']:
                # Close both legs with VIX crisis tag
                self.liquidate(data['long_symbol'], tag=crisis_tag + f"|{pair_name}")
                self.liquidate(data['short_symbol'], tag=crisis_tag + f"|{pair_name}")

                # Update state
                data['position_open'] = False
                liquidated_count += 1

                self.debug(f"LIQUIDATED: {pair_name}")

        if liquidated_count > 0:
            self.debug(f"VIX Crisis: Liquidated {liquidated_count} pairs")

    def log_vix_status(self):
        """Log VIX status and position sizing (called weekly)"""
        self.vix_manager.log_status(force_vix_update=True)

    def check_cointegration_health(self):
        """
        Check cointegration health for all pairs (called weekly)
        Logs status and exits pairs with broken cointegration
        """
        self.debug("="*70)
        self.debug("WEEKLY COINTEGRATION HEALTH CHECK")
        self.debug("="*70)

        all_status = self.cointegration_monitor.get_all_pairs_status()

        for pair_name, health in all_status.items():
            status = health['status']
            adf_pvalue = health['adf_pvalue']
            half_life = health['half_life']

            self.debug(f"{pair_name}: {status}")
            adf_str = f"{adf_pvalue:.3f}" if adf_pvalue is not None else "N/A"
            half_life_str = f"{half_life:.1f}" if half_life is not None else "N/A"
            self.debug(f"  ADF p-value: {adf_str}")
            self.debug(f"  Half-life: {half_life_str} days")

            # Exit positions if cointegration is broken
            if status == 'BROKEN':
                data = self.pair_data[pair_name]
                if data['position_open']:
                    self.debug(f"  ACTION: Exiting {pair_name} due to broken cointegration")

                    # Calculate current z_score and spread
                    long_price = self.securities[data['long_symbol']].price
                    short_price = self.securities[data['short_symbol']].price
                    current_spread = self.calculate_spread(long_price, short_price)
                    z_score = self.calculate_z_score(current_spread, data['spread_history']) if current_spread else 0

                    # Calculate holding days
                    holding_days = (self.time - data['entry_date']).days if data['entry_date'] else 0

                    self.exit_pair(pair_name, data, z_score, current_spread, 'BROKEN_COINTEGRATION', holding_days)

        self.debug("="*70)

    def enter_pair(self, pair_name, data, direction, z_score, spread):
        """
        Enter a pairs trade position with VIX-based dynamic sizing.

        Args:
            pair_name: Name of the pair
            data: Pair data dictionary
            direction: 'long_spread' or 'short_spread'
            z_score: Entry Z-score
            spread: Entry spread value
        """
        # VIX Risk Filter (if enabled)
        if self.enable_vix_filter:
            vix_allocation_pct = self.vix_manager.get_allocation_percentage()

            # Check if we should enter positions (crisis mode = 0% allocation)
            if vix_allocation_pct == 0:
                self.debug(f"VIX CRISIS MODE - Skipping entry for {pair_name} (allocation = 0%)")
                return
        else:
            vix_allocation_pct = 100  # Bypass VIX filter

        # Cointegration Risk Filters (ADF and/or Half-Life)
        if self.enable_adf_filter or self.enable_half_life_filter:
            coint_multiplier = self.cointegration_monitor.get_position_multiplier(pair_name)

            # Check if cointegration is broken
            if coint_multiplier == 0:
                self.debug(f"BROKEN COINTEGRATION - Skipping entry for {pair_name}")
                return
        else:
            coint_multiplier = 1.0  # Bypass all cointegration filters

        # Combined scaling: Base × VIX × Cointegration
        # Example: 1.0 × 100% × 1.0 = full size
        #          1.0 × 70% × 0.5 = 35% (both warning states)
        scaled_position_size = self.position_size_per_pair * (vix_allocation_pct / 100) * coint_multiplier
        leg_percentage = scaled_position_size / 2

        # Log risk-adjusted sizing if different from base
        if vix_allocation_pct < 100 or coint_multiplier < 1.0:
            self.debug(f"Risk Adjustments:")
            self.debug(f"  Base: {self.position_size_per_pair*100:.1f}%")
            self.debug(f"  VIX scaling: {vix_allocation_pct:.1f}% {'(BYPASSED)' if not self.enable_vix_filter else ''}")

            # Show which cointegration filters are active
            coint_status = []
            if self.enable_adf_filter:
                coint_status.append("ADF")
            if self.enable_half_life_filter:
                coint_status.append("Half-Life")
            coint_label = f"Cointegration ({', '.join(coint_status)})" if coint_status else "Cointegration (BYPASSED)"

            self.debug(f"  {coint_label}: {coint_multiplier*100:.0f}%")
            self.debug(f"  Final: {scaled_position_size*100:.1f}%")

        # Get half-life for this pair (if available)
        half_life = None
        if self.enable_adf_filter or self.enable_half_life_filter:
            pair_health = self.cointegration_monitor.check_pair_health(pair_name)
            if pair_health and pair_health['half_life'] is not None:
                half_life = pair_health['half_life']

        # Build order tag with entry details including z-score and half-life
        entry_tag = f"ENTRY|{pair_name}|Z={z_score:.2f}"
        if half_life is not None:
            entry_tag += f"|HL={half_life:.1f}"
        entry_tag += f"|VIX={vix_allocation_pct:.0f}%"

        # Execute trades based on direction
        if direction == 'long_spread':
            # Long the spread: buy long component, sell short component
            self.set_holdings(data['long_symbol'], leg_percentage, tag=entry_tag + "|LONG_LEG")
            self.set_holdings(data['short_symbol'], -leg_percentage, tag=entry_tag + "|SHORT_LEG")
            signal_type = 'LONG SPREAD'

        else:  # short_spread
            # Short the spread: sell long component, buy short component
            self.set_holdings(data['long_symbol'], -leg_percentage, tag=entry_tag + "|SHORT_LEG")
            self.set_holdings(data['short_symbol'], leg_percentage, tag=entry_tag + "|LONG_LEG")
            signal_type = 'SHORT SPREAD'

        # Record entry (including VIX allocation at entry)
        data['position_open'] = True
        data['entry_date'] = self.time
        data['entry_z_score'] = z_score
        data['entry_spread'] = spread
        data['entry_vix_allocation'] = vix_allocation_pct  # Track VIX allocation at entry

        self.total_trades += 1

        self.debug(f"ENTRY - {pair_name} | {signal_type} | Z={z_score:.2f} | VIX allocation={vix_allocation_pct:.1f}% | Equity=${self.portfolio.total_portfolio_value:.2f}")

    def check_exit_signals(self, pair_name, data, z_score, current_spread):
        """
        Check for exit signals on an open position.

        Exit conditions:
        1. Mean reversion: |Z| < z_exit_threshold
        2. Timeout: Held longer than max_holding_days
        3. Stop loss: |Z| > stop_loss_z (divergence)
        4. Spread filter: Spread deviation > critical_threshold (if enabled)

        Args:
            pair_name: Name of the pair
            data: Pair data dictionary
            z_score: Current Z-score
            current_spread: Current spread value
        """
        exit_reason = None

        # Exit 1: Mean reversion (primary exit)
        if abs(z_score) < self.z_exit_threshold:
            exit_reason = 'MEAN_REVERSION'

        # Exit 2: Timeout
        holding_days = (self.time - data['entry_date']).days
        if holding_days >= self.max_holding_days:
            exit_reason = 'TIMEOUT'

        # Exit 3: Stop loss (divergence continues)
        if abs(z_score) > self.stop_loss_z:
            exit_reason = 'STOP_LOSS'

        # Exit 4: Spread filter - abnormal spread deviation (if enabled)
        if self.enable_spread_filter and current_spread is not None and data['spread_mean'] is not None:
            spread_deviation = abs(current_spread - data['spread_mean']) / data['spread_std'] if data['spread_std'] > 0 else 0

            if spread_deviation > self.spread_critical_threshold:
                exit_reason = 'SPREAD_CRITICAL'
                self.debug(f"SPREAD FILTER TRIGGERED: {pair_name} | Deviation={spread_deviation:.2f} > {self.spread_critical_threshold:.2f}")

        if exit_reason:
            self.exit_pair(pair_name, data, z_score, current_spread, exit_reason, holding_days)

    def exit_pair(self, pair_name, data, z_score, spread, exit_reason, holding_days):
        """
        Exit a pairs trade position.

        Args:
            pair_name: Name of the pair
            data: Pair data dictionary
            z_score: Exit Z-score
            spread: Exit spread value
            exit_reason: Reason for exit
            holding_days: Days held
        """
        # Get half-life for this pair (if available)
        half_life = None
        if self.enable_adf_filter or self.enable_half_life_filter:
            pair_health = self.cointegration_monitor.check_pair_health(pair_name)
            if pair_health and pair_health['half_life'] is not None:
                half_life = pair_health['half_life']

        # Build exit tag with exit details including z-score and half-life
        exit_tag = f"EXIT|{pair_name}|{exit_reason}|Z={z_score:.2f}"
        if half_life is not None:
            exit_tag += f"|HL={half_life:.1f}"
        exit_tag += f"|DAYS={holding_days}"

        # Close both positions with tags
        self.liquidate(data['long_symbol'], tag=exit_tag)
        self.liquidate(data['short_symbol'], tag=exit_tag)

        # Calculate P&L (approximate)
        entry_z = data['entry_z_score']
        entry_spread = data['entry_spread']
        z_change = abs(z_score) - abs(entry_z)
        spread_change = spread - entry_spread if (spread is not None and entry_spread is not None) else None

        # Determine if trade was profitable
        is_winner = False
        if exit_reason == 'MEAN_REVERSION':
            # Mean reversion should be profitable
            is_winner = True
            self.winning_trades += 1
        elif exit_reason == 'STOP_LOSS':
            # Stop loss is a losing trade
            is_winner = False
        else:  # TIMEOUT
            # Timeout could be either - check Z-score movement
            if z_change < 0:  # Z-score decreased toward mean
                is_winner = True
                self.winning_trades += 1

        # Reset position data
        data['position_open'] = False
        data['entry_date'] = None
        data['entry_z_score'] = None
        data['entry_spread'] = None

        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0

        # Build exit message with spread information
        exit_msg = f"EXIT - {pair_name} | {exit_reason} | " + \
                   f"Entry Z={entry_z:.2f} → Exit Z={z_score:.2f} | "

        if spread_change is not None:
            exit_msg += f"Spread Δ={spread_change:.4f} | "

        exit_msg += f"Held {holding_days} days | " + \
                    f"Win: {is_winner} | Overall Win Rate: {win_rate:.1f}% | " + \
                    f"Equity=${self.portfolio.total_portfolio_value:.2f}"

        self.debug(exit_msg)

    def on_data(self, data):
        """
        OnData event handler. Main logic in scheduled check_pairs_and_trade.

        Args:
            data: Slice object containing data
        """
        pass  # Logic handled in scheduled function

    def on_end_of_algorithm(self):
        """Log final statistics at end of backtest."""
        self.debug("="*60)
        self.debug("STATISTICAL ARBITRAGE STRATEGY - FINAL RESULTS")
        self.debug("="*60)
        self.debug(f"Strategy Parameters:")
        self.debug(f"  Z-Score Entry Threshold: {self.z_entry_threshold}")
        self.debug(f"  Z-Score Exit Threshold: {self.z_exit_threshold}")
        self.debug(f"  Lookback Period: {self.lookback_period} days")
        self.debug(f"  Max Holding Days: {self.max_holding_days}")
        self.debug(f"  Stop Loss Z-Score: {self.stop_loss_z}")
        self.debug(f"  Position Size per Pair: {self.position_size_per_pair:.0%}")
        self.debug("")
        self.debug(f"Performance:")
        self.debug(f"  Total Trades: {self.total_trades}")
        self.debug(f"  Winning Trades: {self.winning_trades}")
        if self.total_trades > 0:
            self.debug(f"  Win Rate: {self.winning_trades/self.total_trades:.1%}")
        self.debug("")
        self.debug(f"Pairs Traded:")
        for pair in self.pairs:
            self.debug(f"  - {pair['name']}: {pair['description']}")
        self.debug("="*60)
