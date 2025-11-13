# region imports
from AlgorithmImports import *
import numpy as np
from collections import deque
# endregion


class RegimeDiversifiedStatArb(QCAlgorithm):
    """
    Regime-Diversified Statistical Arbitrage Strategy
    
    Combines 2023-2025 champion pairs (QT regime) with 2015-2022 ZIRP pairs
    for robust performance across different market regimes.
    
    KEY FEATURES:
    - Automatic regime detection (QT vs ZIRP vs Transitional)
    - Dynamic pair activation based on regime
    - Regime-specific parameters (Z-scores, lookback, holding periods)
    - Portfolio allocation adjusts to regime (70% QT / 40% ZIRP / 50% Transition)
    
    QT CHAMPION PAIRS (High Dispersion 2023-2025):
    - PNC/KBE, ARCC/AMLP, RBA/SMFG, ENB/WEC
    
    ZIRP PAIRS (Low Dispersion 2015-2022):
    - BSX/HOV (Medical devices vs Homebuilder)
    - PSEC/KIM (BDC vs Shopping REIT)
    - CHTR/THO (Cable vs RV manufacturer)
    """

    def initialize(self):
        """Initialize algorithm with regime-aware configuration."""
        
        # Backtest period - full regime cycle
        self.set_start_date(2015, 1, 1)
        # self.set_end_date(2022, 11, 11)
        self.set_cash(100000)
        
        # =================================================================
        # PAIRS CONFIGURATION
        # =================================================================
        
        # QT/High Dispersion Champion Pairs (2023-2025)
        self.qt_champion_pairs = [
            {
                'name': 'PNC_KBE',
                'long': 'PNC',
                'short': 'KBE',
                'description': 'Regional bank vs Banking ETF',
                'regime': 'QT',
                'weight': 0.60
            },
            {
                'name': 'ARCC_AMLP',
                'long': 'ARCC',
                'short': 'AMLP',
                'description': 'BDC vs MLP ETF',
                'regime': 'QT',
                 'weight': 0.10
            },
            {
                'name': 'RBA_SMFG',
                'long': 'RBA',
                'short': 'SMFG',
                'description': 'International banking',
                'regime': 'QT',
                 'weight': 0.10
            },
            {
                'name': 'ENB_WEC',
                'long': 'ENB',
                'short': 'WEC',
                'description': 'Energy infra vs Utility',
                'regime': 'QT',
                 'weight': 0.10
            }
        ]
        
        # ZIRP/Low Dispersion Pairs (2015-2022)
        self.zirp_pairs = [

            {
                'name': 'PSEC_KIM',
                'long': 'PSEC',
                'short': 'KIM',
                'description': 'BDC vs Shopping REIT - TIER 1',
                'regime': 'ZIRP',
                'weight': 0.20
            },
            {
                'name': 'CAKE_URBN',
                'long': 'CAKE',
                'short': 'URBN',
                'description': '',
                'regime': 'ZIRP',
                'weight': 0.40
            },
            {
                'name': 'QRVO-EWY',
                'long': 'QRVO',
                'short': 'EWY',
                'description': '',
                'regime': 'ZIRP',
                'weight': 0.20
            },
            {
                'name': 'CRON-ITRI',
                'long': 'CRON',
                'short': 'ITRI',
                'description': '',
                'regime': 'ZIRP',
                'weight': 0.20
            },
        ]
        
        # =================================================================
        # REGIME-SPECIFIC PARAMETERS
        # =================================================================
        
        # QT Regime (High Dispersion, Rising Rates)
        self.qt_params = {
            'z_entry': 1.5,
            'z_exit': 1,
            'stop_loss_z': 4.0,
            'lookback': 30,
            'max_holding_days': 20
        }
        
        # ZIRP Regime (Low Dispersion, Low Rates)
        self.zirp_params = {
            'z_entry': 2.0,
            'z_exit': 0.75,
            'stop_loss_z': 3.5,
            'lookback': 60,
            'max_holding_days': 45
        }
        
        # Transitional Regime (Blended)
        self.transition_params = {
            'z_entry': 2.0,
            'z_exit': 0.2,
            'stop_loss_z': 4.0,
            'lookback': 45,
            'max_holding_days': 10
        }
        
        # =================================================================
        # INITIALIZE SECURITIES AND REGIME INDICATORS
        # =================================================================
        
        # Initialize pair data storage
        self.pair_data = {}
        all_pairs = self.qt_champion_pairs + self.zirp_pairs
        
        for pair in all_pairs:
            # Add securities
            long_symbol = self.add_equity(pair['long'], Resolution.DAILY).symbol
            short_symbol = self.add_equity(pair['short'], Resolution.DAILY).symbol
            
            # Initialize data structure
            self.pair_data[pair['name']] = {
                'long_symbol': long_symbol,
                'short_symbol': short_symbol,
                'long_ticker': pair['long'],
                'short_ticker': pair['short'],
                'description': pair['description'],
                'regime': pair['regime'],
                'spread_history': deque(maxlen=60),  # Max lookback
                'position_open': False,
                'entry_date': None,
                'entry_z_score': None,
                'entry_spread': None,
                'spread_mean': None,
                'spread_std': None,
                'active': False  # Will be set based on regime
            }
        
        # Initialize regime detection
        self.initialize_regime_detection()
        
        # Warm up period
        self.set_warm_up(60)
        
        # Schedule trading
        self.schedule.on(
            self.date_rules.every_day(),
            self.time_rules.after_market_open('PNC', 30),
            self.check_pairs_and_trade
        )
        
        # Schedule regime update (weekly)
        self.schedule.on(
            self.date_rules.week_start(),
            self.time_rules.after_market_open('PNC', 0),
            self.log_regime_status
        )
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.regime_trades = {'QT': 0, 'ZIRP': 0, 'TRANSITIONAL': 0}

        # Debug plotting - add indicator charts
        self._initialize_debug_charts()

        # Initialize Z-SCORE
        self.z_score = 0

        # Initialize Holding days
        self.holding_days = 0

        # Initialize Entry Signal
        self.entry_signal = 0
        
    def initialize_regime_detection(self):
        """
        Initialize regime detection using available QC data.
        """
        
        # VIX for volatility
        try:
            self.vix = self.add_data(CBOE, "VIX", Resolution.DAILY).symbol
        except:
            self.debug("VIX data not available, using SPY volatility proxy")
            self.vix = None
        
        # Sector ETFs for correlation
        self.sector_etfs = {}
        sector_tickers = ['XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLU']
        for ticker in sector_tickers:
            try:
                self.sector_etfs[ticker] = self.add_equity(ticker, Resolution.DAILY).symbol
            except:
                self.debug(f"Could not add sector ETF: {ticker}")
        
        # Treasury ETFs for rate proxy
        self.tlt = self.add_equity('TLT', Resolution.DAILY).symbol
        self.tlt_sma = self.sma('TLT', 252, Resolution.DAILY)
        
        # Volatility ETF
        try:
            self.vxx = self.add_equity('VXX', Resolution.DAILY).symbol
        except:
            self.vxx = None
        
        # Historical data
        self.sector_history = {ticker: deque(maxlen=60) for ticker in self.sector_etfs.keys()}
        self.vix_history = deque(maxlen=252)
        self.regime_history = deque(maxlen=20)
        
        # Regime state
        self.current_regime = "TRANSITIONAL"
        self.regime_score = 50
        self.last_regime = None
        
    def calculate_regime_score(self):
        """
        Calculate regime score (0-100).

        Score interpretation:
        - 0-35: ZIRP regime (low dispersion, low rates)
        - 35-65: Transitional
        - 65-100: QT regime (high dispersion, high rates)

        Indicators:
        1. VIX level (20%)
        2. Sector correlation (25%)
        3. Rate environment (25%)
        4. Volatility term structure (15%)
        5. Market dispersion (15%)
        """

        score = 50

        # Reset components for tracking
        self.vix_component = 0
        self.corr_component = 0
        self.rate_component = 0
        self.term_component = 0
        self.disp_component = 0

        # 1. VIX Level (20% weight)
        if self.vix and len(self.vix_history) > 20:
            current_vix = self.securities[self.vix].price
            avg_vix = np.mean(list(self.vix_history)[-60:]) if len(self.vix_history) >= 60 else current_vix

            if avg_vix > 22:
                self.vix_component = 4
            elif avg_vix > 18:
                self.vix_component = 2
            elif avg_vix < 13:
                self.vix_component = -4
            elif avg_vix < 15:
                self.vix_component = -2

            score += self.vix_component
        
        # 2. Sector Correlation (25% weight)
        if all(len(hist) >= 30 for hist in self.sector_history.values()):
            correlations = []
            sector_names = list(self.sector_etfs.keys())

            for i in range(len(sector_names)):
                for j in range(i+1, len(sector_names)):
                    s1 = list(self.sector_history[sector_names[i]])[-30:]
                    s2 = list(self.sector_history[sector_names[j]])[-30:]
                    if len(s1) >= 30 and len(s2) >= 30:
                        corr = np.corrcoef(s1, s2)[0, 1]
                        if not np.isnan(corr):
                            correlations.append(corr)

            if correlations:
                avg_corr = np.mean(correlations)

                if avg_corr < 0.40:
                    self.corr_component = 6.25
                elif avg_corr < 0.50:
                    self.corr_component = 3.75
                elif avg_corr > 0.65:
                    self.corr_component = -6.25
                elif avg_corr > 0.55:
                    self.corr_component = -3.75

                score += self.corr_component
        
        # 3. Rate Environment (25% weight)
        if self.tlt_sma.is_ready:
            tlt_price = self.securities[self.tlt].price
            tlt_sma = self.tlt_sma.current.value

            if tlt_price < tlt_sma * 0.95:
                self.rate_component = 5
            elif tlt_price < tlt_sma:
                self.rate_component = 2.5
            elif tlt_price > tlt_sma * 1.05:
                self.rate_component = -5
            elif tlt_price > tlt_sma:
                self.rate_component = -2.5

            score += self.rate_component
        
        # 4. Volatility Term Structure (15% weight)
        if self.vxx and self.vix:
            try:
                vxx_price = self.securities[self.vxx].price
                vix_price = self.securities[self.vix].price

                if vxx_price > 0 and vix_price > 0:
                    vxx_ratio = vxx_price / 20
                    term_structure = vxx_ratio / vix_price

                    if term_structure > 1.15:
                        self.term_component = 3
                    elif term_structure > 1.05:
                        self.term_component = 1.5
                    elif term_structure < 0.85:
                        self.term_component = -3
                    elif term_structure < 0.95:
                        self.term_component = -1.5

                    score += self.term_component
            except:
                pass
        
        # 5. Market Dispersion (15% weight)
        if all(len(hist) >= 20 for hist in self.sector_history.values()):
            recent_returns = []
            for sector_hist in self.sector_history.values():
                prices = list(sector_hist)[-20:]
                if len(prices) >= 20:
                    ret = (prices[-1] - prices[-20]) / prices[-20]
                    recent_returns.append(ret)

            if len(recent_returns) >= 4:
                dispersion = np.std(recent_returns)

                if dispersion > 0.10:
                    self.disp_component = 3
                elif dispersion > 0.07:
                    self.disp_component = 1.5
                elif dispersion < 0.03:
                    self.disp_component = -3
                elif dispersion < 0.05:
                    self.disp_component = -1.5

                score += self.disp_component
        
        return max(0, min(100, score))
    
    def update_regime(self):
        """Update regime with hysteresis to prevent whipsawing."""
        
        new_score = self.calculate_regime_score()
        self.regime_history.append(new_score)
        
        # Smooth with 10-day average
        if len(self.regime_history) >= 10:
            self.regime_score = np.mean(list(self.regime_history)[-10:])
        else:
            self.regime_score = new_score
        
        # Update regime with hysteresis (5-point buffer)
        if self.current_regime == "QT":
            # if self.regime_score < 55:
            if self.regime_score < 35:
                self.current_regime = "TRANSITIONAL"
        elif self.current_regime == "ZIRP":
            if self.regime_score > 45:
                self.current_regime = "TRANSITIONAL"
        elif self.current_regime == "TRANSITIONAL":
            # if self.regime_score >= 65:
            if self.regime_score >= 65:
                self.current_regime = "QT"
            elif self.regime_score <= 35:
                self.current_regime = "ZIRP"
        
        # Log regime changes
        if self.last_regime != self.current_regime:
            self.debug(f"{'='*60}")
            self.debug(f"REGIME CHANGE: {self.last_regime or 'INIT'} → {self.current_regime}")
            self.debug(f"Regime Score: {self.regime_score:.1f}")
            self.debug(f"Date: {self.time}")
            self.debug(f"{'='*60}")
            self.last_regime = self.current_regime
    
    def get_active_configuration(self):
        """
        Get active pairs, parameters, and allocation based on regime.
        """
        
        if self.current_regime == "QT":
            # High dispersion - use champions
            pairs = self.qt_champion_pairs
            params = self.qt_params
            allocation = 0.70
            
        elif self.current_regime == "ZIRP":
            # Low dispersion - use ZIRP pairs
            pairs = self.zirp_pairs
            params = self.zirp_params
            allocation = 0.40
            
        else:  # TRANSITIONAL
            # Use both with reduced sizing
            pairs = self.qt_champion_pairs + self.zirp_pairs
            params = self.transition_params
            allocation = 0.50
        
        return pairs, params, allocation
    
    def check_pairs_and_trade(self):
        """Main trading logic with regime awareness."""
        
        # Update historical data for regime detection
        if self.vix and self.securities[self.vix].price > 0:
            self.vix_history.append(self.securities[self.vix].price)
        
        for ticker, symbol in self.sector_etfs.items():
            if self.securities[symbol].price > 0:
                self.sector_history[ticker].append(self.securities[symbol].price)
        
        # Update regime
        if not self.is_warming_up:
            self.update_regime()
        
        # Get active configuration
        active_pairs, params, regime_allocation = self.get_active_configuration()
        
        # Calculate position size
        num_pairs = len(active_pairs)
        position_size_per_pair = regime_allocation / num_pairs if num_pairs > 0 else 0
        
        # Process each pair
        for pair_config in active_pairs:
            pair_name = pair_config['name']
            data = self.pair_data[pair_name]
            
            # Mark pair as active/inactive
            data['active'] = True
            
            # Get prices
            long_price = self.securities[data['long_symbol']].price
            short_price = self.securities[data['short_symbol']].price
            
            if long_price <= 0 or short_price <= 0:
                continue
            
            # Calculate spread
            current_spread = self.calculate_spread(long_price, short_price)
            if current_spread is None:
                continue
            
            data['spread_history'].append(current_spread)
            
            # Calculate Z-score with appropriate lookback
            lookback = min(params['lookback'], len(data['spread_history']))
            recent_spreads = list(data['spread_history'])[-lookback:]
            z_score = self.calculate_z_score_from_list(current_spread, recent_spreads)
            self.z_score = z_score
            
            if z_score is None or self.is_warming_up:
                continue
            
            # Store statistics
            data['spread_mean'] = np.mean(recent_spreads)
            data['spread_std'] = np.std(recent_spreads, ddof=1)
            
            # Trading logic
            if data['position_open']:
                self.check_exit_signals(
                    pair_name, data, z_score, current_spread, params
                )
            else:
                self.check_entry_signals(
                    pair_name, data, z_score, current_spread, 
                    params, position_size_per_pair
                )
        
        # Mark inactive pairs
        for pair_name, data in self.pair_data.items():
            if pair_name not in [p['name'] for p in active_pairs]:
                data['active'] = False
                # Close positions in inactive pairs
                if data['position_open']:
                    self.debug(f"Closing {pair_name} - no longer active in {self.current_regime} regime")
                    self.exit_pair(pair_name, data, 0, 0, 'REGIME_SWITCH', 0)

        # Plot debug indicators
        if not self.is_warming_up:
            self._plot_debug_indicators()
    
    def calculate_spread(self, long_price, short_price):
        """Calculate log price spread."""
        if long_price <= 0 or short_price <= 0:
            return None
        return np.log(long_price) - np.log(short_price)
    
    def calculate_z_score_from_list(self, current_spread, spread_list):
        """Calculate Z-score from spread list."""
        if len(spread_list) < 20:
            return None
        
        mean = np.mean(spread_list)
        std = np.std(spread_list, ddof=1)
        
        if std == 0:
            return None
        
        return (current_spread - mean) / std
    
    def check_entry_signals(self, pair_name, data, z_score, spread, params, position_size):
        """Check for entry signals."""
        
        if abs(z_score) > params['z_entry']:
            direction = 'short_spread' if z_score > 0 else 'long_spread'
            self.enter_pair(pair_name, data, direction, z_score, spread, position_size)
    
    def enter_pair(self, pair_name, data, direction, z_score, spread, position_size):
        """Enter a pairs trade."""
        
        leg_size = position_size / 2
        
        if direction == 'long_spread':
            self.set_holdings(data['long_symbol'], leg_size)
            self.set_holdings(data['short_symbol'], -leg_size)
            signal = 'LONG SPREAD'
        else:
            self.set_holdings(data['long_symbol'], -leg_size)
            self.set_holdings(data['short_symbol'], leg_size)
            signal = 'SHORT SPREAD'
        
        data['position_open'] = True
        data['entry_date'] = self.time
        data['entry_z_score'] = z_score
        data['entry_spread'] = spread
        
        self.total_trades += 1
        self.regime_trades[self.current_regime] += 1
        
        self.debug(f"ENTRY - {pair_name} [{self.current_regime}] | {signal} | Z={z_score:.2f}")
        self.entry_signal = 1
    
    def check_exit_signals(self, pair_name, data, z_score, spread, params):
        """Check for exit signals."""
        
        exit_reason = None
        
        # Mean reversion
        if abs(z_score) < params['z_exit']:
            exit_reason = 'MEAN_REVERSION'
        
        # Timeout
        holding_days = (self.time - data['entry_date']).days
        self.holding_days = holding_days
        if holding_days >= params['max_holding_days']:
            exit_reason = 'TIMEOUT'
        
        # Stop loss
        if abs(z_score) > params['stop_loss_z']:
            exit_reason = 'STOP_LOSS'
        
        if exit_reason:
            self.exit_pair(pair_name, data, z_score, spread, exit_reason, holding_days)
    
    def exit_pair(self, pair_name, data, z_score, spread, exit_reason, holding_days):
        """Exit a pairs trade."""
        
        self.liquidate(data['long_symbol'])
        self.liquidate(data['short_symbol'])
        
        entry_z = data['entry_z_score']
        z_change = abs(z_score) - abs(entry_z) if entry_z else 0
        
        is_winner = False
        if exit_reason == 'MEAN_REVERSION':
            is_winner = True
            self.winning_trades += 1
        elif exit_reason != 'STOP_LOSS':
            if z_change < 0:
                is_winner = True
                self.winning_trades += 1
        
        data['position_open'] = False
        data['entry_date'] = None
        data['entry_z_score'] = None
        data['entry_spread'] = None
        
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        self.debug(f"EXIT - {pair_name} [{self.current_regime}] | {exit_reason} | " +
                  f"Z: {entry_z:.2f}→{z_score:.2f} | {holding_days}d | " +
                  f"Win: {is_winner} | WR: {win_rate:.1f}%")

        self.entry_signal = 0
    
    def log_regime_status(self):
        """Log regime status weekly."""
        if not self.is_warming_up:
            self.debug(f"{'='*60}")
            self.debug(f"REGIME STATUS - {self.time.strftime('%Y-%m-%d')}")
            self.debug(f"Current Regime: {self.current_regime} (Score: {self.regime_score:.1f})")
            self.debug(f"Total Trades: {self.total_trades} | Win Rate: {(self.winning_trades/self.total_trades*100) if self.total_trades > 0 else 0:.1f}%")
            self.debug(f"Regime Trades: QT={self.regime_trades['QT']} | ZIRP={self.regime_trades['ZIRP']} | TRANS={self.regime_trades['TRANSITIONAL']}")
            self.debug(f"{'='*60}")
    
    def on_data(self, data):
        """OnData event handler."""
        pass
    
    def on_end_of_algorithm(self):
        """Log final statistics."""
        self.debug("="*60)
        self.debug("REGIME-DIVERSIFIED STAT ARB - FINAL RESULTS")
        self.debug("="*60)
        self.debug(f"Total Trades: {self.total_trades}")
        self.debug(f"Winning Trades: {self.winning_trades}")
        if self.total_trades > 0:
            self.debug(f"Overall Win Rate: {self.winning_trades/self.total_trades:.1%}")
        self.debug(f"")
        self.debug(f"Trades by Regime:")
        self.debug(f"  QT: {self.regime_trades['QT']}")
        self.debug(f"  ZIRP: {self.regime_trades['ZIRP']}")
        self.debug(f"  TRANSITIONAL: {self.regime_trades['TRANSITIONAL']}")
        self.debug(f"")
        self.debug(f"Final Regime: {self.current_regime} (Score: {self.regime_score:.1f})")
        self.debug("="*60)

    def _initialize_debug_charts(self):
        """Initialize debug plotting charts."""
        # Chart 1: Regime Score
        regime_chart = Chart("Regime Score")
        regime_chart.add_series(Series("Score", SeriesType.LINE, 0))
        regime_chart.add_series(Series("QT Threshold (65)", SeriesType.LINE, 0))
        regime_chart.add_series(Series("ZIRP Threshold (35)", SeriesType.LINE, 0))
        self.add_chart(regime_chart)

        # Chart 2: Active Pairs Status
        pair_chart = Chart("Active Pairs")
        for pair in self.qt_champion_pairs:
            pair_chart.add_series(Series(pair['name'], SeriesType.BAR, 0))
        for pair in self.zirp_pairs:
            pair_chart.add_series(Series(pair['name'], SeriesType.BAR, 0))
        self.add_chart(pair_chart)

        # Chart 3: Indicator Components Breakdown
        comp_chart = Chart("Score Components")
        comp_chart.add_series(Series("VIX Component", SeriesType.LINE, 0))
        comp_chart.add_series(Series("Correlation Component", SeriesType.LINE, 0))
        comp_chart.add_series(Series("Rate Component", SeriesType.LINE, 0))
        comp_chart.add_series(Series("Term Struct Component", SeriesType.LINE, 0))
        comp_chart.add_series(Series("Dispersion Component", SeriesType.LINE, 0))
        self.add_chart(comp_chart)

        # Initialize component tracking
        self.vix_component = 0
        self.corr_component = 0
        self.rate_component = 0
        self.term_component = 0
        self.disp_component = 0

    def _plot_debug_indicators(self):
        """Plot regime indicators for debugging."""
        # Plot holding days
        self.plot("Holding days", "days", self.holding_days)
        self.plot("Holding days", "exit limit", 10)

        # Plot Entry & Exit Signals
        self.plot("Entry & Exit Signals", "Entry signal", self.entry_signal)

        # Plot Z Score
        # self.plot("Z Score", "Score", self.z_score)
        self.plot("Z Score", "ZIRP Entry", 1.5)
        self.plot("Z Score", "Entry", 1.5)
        self.plot("Z Score", "ZIRP Exit", -0.75)
        self.plot("Z Score", "Exit", -1.0)
        self.plot("Z Score", "ZIRP Stop Loss", -3.75)
        self.plot("Z Score", "Stop Loss", -4.0)

        # Plot regime score
        self.plot("Regime Score", "Score", self.regime_score)
        self.plot("Regime Score", "QT Threshold (65)", 65)
        self.plot("Regime Score", "Transition Threshold (55)", 55)
        self.plot("Regime Score", "Transition Threshold (45)", 45)
        self.plot("Regime Score", "ZIRP Threshold (35)", 35)

        # Plot individual indicator components
        self.plot("Score Components", "VIX Component", self.vix_component)
        self.plot("Score Components", "Correlation Component", self.corr_component)
        self.plot("Score Components", "Rate Component", self.rate_component)
        self.plot("Score Components", "Term Struct Component", self.term_component)
        self.plot("Score Components", "Dispersion Component", self.disp_component)

        # Plot pair activation status (1 = active, 0 = inactive)
        all_pairs = self.qt_champion_pairs + self.zirp_pairs
        for pair_config in all_pairs:
            pair_name = pair_config['name']
            data = self.pair_data[pair_name]
            status = 1 if data.get('active', False) else 0
            self.plot("Active Pairs", pair_name, status)