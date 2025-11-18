"""
Cointegration Monitor for QuantConnect

Monitors cointegration health of trading pairs using:
1. ADF Test (Augmented Dickey-Fuller) - Tests spread stationarity
2. Half-Life - Measures mean reversion speed

Usage in main.py:
    from helpers import CointegrationMonitor

    def initialize(self):
        self.cointegration_monitor = CointegrationMonitor(qb=self)

    def on_data(self, data):
        # Update spread history
        self.cointegration_monitor.update_spread(pair_name, spread_value)

        # Check cointegration health (weekly)
        health = self.cointegration_monitor.get_pair_health(pair_name)
        if health['status'] == 'BROKEN':
            self.liquidate_pair(pair_name)
"""

import numpy as np
from collections import deque
from datetime import timedelta


class CointegrationMonitor:
    """
    Monitors cointegration health using ADF test and half-life

    Health Status:
    - HEALTHY: ADF p-value < 0.10, half-life < 30 days
    - WARNING: ADF p-value 0.10-0.15 or half-life 30-60 days
    - BROKEN: ADF p-value > 0.15 or half-life > 60 days
    """

    def __init__(self, qb=None, lookback_days=90, check_frequency_days=7,
                 enable_adf=True, enable_half_life=True,
                 adf_healthy_threshold=0.10, adf_warning_threshold=0.15,
                 half_life_warning_threshold=30, half_life_broken_threshold=60):
        """
        Initialize cointegration monitor

        Args:
            qb: QuantConnect algorithm instance
            lookback_days: Days of spread history to maintain (default: 90)
            check_frequency_days: How often to run tests (default: 7 days)
            enable_adf: Enable ADF test filter (default: True)
            enable_half_life: Enable half-life filter (default: True)
            adf_healthy_threshold: ADF p-value threshold for healthy (default: 0.10)
            adf_warning_threshold: ADF p-value threshold for warning (default: 0.15)
            half_life_warning_threshold: Half-life threshold for warning in days (default: 30)
            half_life_broken_threshold: Half-life threshold for broken in days (default: 60)
        """
        self.qb = qb
        self.lookback_days = lookback_days
        self.check_frequency = timedelta(days=check_frequency_days)

        # Filter flags
        self.enable_adf = enable_adf
        self.enable_half_life = enable_half_life

        # Storage for each pair
        self.pairs = {}

        # Thresholds (now configurable)
        self.adf_healthy_threshold = adf_healthy_threshold
        self.adf_warning_threshold = adf_warning_threshold
        self.half_life_warning_threshold = half_life_warning_threshold
        self.half_life_broken_threshold = half_life_broken_threshold

        if self.qb:
            self.qb.debug("CointegrationMonitor initialized")

            # Create cointegration chart
            coint_chart = Chart("Cointegration Health")
            self.qb.add_chart(coint_chart)

    def add_pair(self, pair_name):
        """
        Add a pair to monitor

        Args:
            pair_name: Name of the pair (e.g., 'PNC_KBE')
        """
        if pair_name not in self.pairs:
            self.pairs[pair_name] = {
                'spread_history': deque(maxlen=self.lookback_days),
                'last_check': None,
                'adf_pvalue': None,
                'half_life': None,
                'status': 'UNKNOWN'
            }

            if self.qb:
                # Add series for this pair
                self.qb.plot("Cointegration Health", f"{pair_name} ADF p-value", 0)
                self.qb.plot("Cointegration Health", f"{pair_name} Half-Life", 0)

    def update_spread(self, pair_name, spread_value):
        """
        Update spread history for a pair

        Args:
            pair_name: Name of the pair
            spread_value: Current spread value
        """
        if pair_name not in self.pairs:
            self.add_pair(pair_name)

        self.pairs[pair_name]['spread_history'].append(spread_value)

    def should_check(self, pair_name):
        """
        Check if it's time to run cointegration tests

        Args:
            pair_name: Name of the pair

        Returns:
            bool: True if should check
        """
        if pair_name not in self.pairs:
            return False

        last_check = self.pairs[pair_name]['last_check']

        # Check if we have enough data
        if len(self.pairs[pair_name]['spread_history']) < 30:
            return False

        # Check if enough time has passed
        if last_check is None:
            return True

        if self.qb and (self.qb.time - last_check) >= self.check_frequency:
            return True

        return False

    def calculate_adf_test(self, spread_series):
        """
        Calculate ADF test p-value for spread stationarity

        Simplified ADF test implementation (Dickey-Fuller)
        For production, consider using statsmodels.tsa.stattools.adfuller

        Args:
            spread_series: Array of spread values

        Returns:
            float: p-value (lower = more stationary = better cointegration)
        """
        try:
            # Simple Dickey-Fuller test
            # Regress: Δspread_t = α + β*spread_(t-1) + ε_t
            # H0: β = 0 (unit root, non-stationary)
            # H1: β < 0 (stationary)

            spreads = np.array(spread_series)
            spread_lag = spreads[:-1]
            spread_diff = np.diff(spreads)

            # OLS regression
            n = len(spread_diff)
            X = np.column_stack([np.ones(n), spread_lag])

            # Calculate beta
            beta = np.linalg.lstsq(X, spread_diff, rcond=None)[0][1]

            # Calculate t-statistic
            residuals = spread_diff - (X @ np.array([0, beta]))
            std_error = np.sqrt(np.sum(residuals**2) / (n - 2))
            beta_std = std_error / np.sqrt(np.sum((spread_lag - np.mean(spread_lag))**2))
            t_stat = beta / beta_std

            # Approximate p-value from t-statistic
            # Critical values (MacKinnon 1996):
            # 1%: -3.43, 5%: -2.86, 10%: -2.57

            if t_stat < -3.43:
                p_value = 0.01
            elif t_stat < -2.86:
                p_value = 0.05
            elif t_stat < -2.57:
                p_value = 0.10
            else:
                # Linear interpolation for approximate p-value
                p_value = max(0.15, min(1.0, 0.15 + (t_stat + 2.57) * 0.1))

            return p_value

        except Exception as e:
            if self.qb:
                self.qb.debug(f"ADF test error: {str(e)}")
            return 1.0  # Return worst case

    def calculate_half_life(self, spread_series):
        """
        Calculate half-life of mean reversion

        Half-life = time for spread to revert halfway to mean

        Args:
            spread_series: Array of spread values

        Returns:
            float: Half-life in days (or None if calculation fails)
        """
        try:
            spreads = np.array(spread_series)

            # Demean the spread
            spread_mean = np.mean(spreads)
            spread_demeaned = spreads - spread_mean

            # AR(1) regression: spread_t = α + β*spread_(t-1) + ε
            spread_lag = spread_demeaned[:-1]
            spread_current = spread_demeaned[1:]

            # Calculate beta (mean reversion coefficient)
            numerator = np.dot(spread_lag, spread_current)
            denominator = np.dot(spread_lag, spread_lag)

            if denominator == 0:
                return None

            beta = numerator / denominator

            # Half-life formula: HL = -log(2) / log(β)
            # β should be between 0 and 1 for mean reversion
            if beta > 0 and beta < 1:
                half_life = -np.log(2) / np.log(beta)
                return half_life
            else:
                # No mean reversion detected
                return 9999  # Very large number

        except Exception as e:
            if self.qb:
                self.qb.debug(f"Half-life calculation error: {str(e)}")
            return None

    def check_pair_health(self, pair_name):
        """
        Run cointegration health check for a pair

        Args:
            pair_name: Name of the pair

        Returns:
            dict: Health status with ADF p-value, half-life, and status
        """
        if pair_name not in self.pairs:
            return None

        pair_data = self.pairs[pair_name]

        if not self.should_check(pair_name):
            # Return cached results
            return {
                'adf_pvalue': pair_data['adf_pvalue'],
                'half_life': pair_data['half_life'],
                'status': pair_data['status']
            }

        # Run tests (only if enabled)
        spread_series = list(pair_data['spread_history'])

        # ADF test (only if enabled)
        if self.enable_adf:
            adf_pvalue = self.calculate_adf_test(spread_series)
        else:
            adf_pvalue = None

        # Half-life (only if enabled)
        if self.enable_half_life:
            half_life = self.calculate_half_life(spread_series)
        else:
            half_life = None

        # Determine status
        status = self.determine_status(adf_pvalue, half_life)

        # Update cached values
        pair_data['adf_pvalue'] = adf_pvalue
        pair_data['half_life'] = half_life
        pair_data['status'] = status
        if self.qb:
            pair_data['last_check'] = self.qb.time

        # Plot (only if values exist)
        if self.qb:
            if adf_pvalue is not None:
                self.qb.plot("Cointegration Health", f"{pair_name} ADF p-value", adf_pvalue)
            if half_life is not None and half_life < 200:  # Cap for plotting
                self.qb.plot("Cointegration Health", f"{pair_name} Half-Life", half_life)

        # Log if warning or broken
        if status != 'HEALTHY' and self.qb:
            adf_str = f"{adf_pvalue:.3f}" if adf_pvalue is not None else "N/A"
            half_life_str = f"{half_life:.1f}" if half_life is not None else "N/A"
            self.qb.debug(f"Cointegration {status}: {pair_name} | ADF p-value={adf_str} | Half-Life={half_life_str}")

        return {
            'adf_pvalue': adf_pvalue,
            'half_life': half_life,
            'status': status
        }

    def determine_status(self, adf_pvalue, half_life):
        """
        Determine cointegration health status based on enabled filters

        Args:
            adf_pvalue: ADF test p-value
            half_life: Half-life in days

        Returns:
            str: 'HEALTHY', 'WARNING', or 'BROKEN'
        """
        # Check ADF (only if enabled)
        if self.enable_adf and adf_pvalue is not None:
            if adf_pvalue > self.adf_warning_threshold:
                return 'BROKEN'

        # Check half-life (only if enabled)
        if self.enable_half_life and half_life is not None:
            if half_life > self.half_life_broken_threshold:
                return 'BROKEN'

        # Warning conditions (only for enabled filters)
        if self.enable_adf and adf_pvalue is not None:
            if adf_pvalue > self.adf_healthy_threshold:
                return 'WARNING'

        if self.enable_half_life and half_life is not None:
            if half_life > self.half_life_warning_threshold:
                return 'WARNING'

        return 'HEALTHY'

    def get_position_multiplier(self, pair_name):
        """
        Get position size multiplier based on cointegration health

        Args:
            pair_name: Name of the pair

        Returns:
            float: Multiplier (1.0 = full size, 0.5 = half size, 0.0 = no positions)
        """
        health = self.check_pair_health(pair_name)

        if health is None:
            return 1.0  # Default to full size if no data

        status = health['status']

        if status == 'HEALTHY':
            return 1.0
        elif status == 'WARNING':
            return 0.5  # Reduce to 50%
        elif status == 'BROKEN':
            return 0.0  # No new positions
        else:  # UNKNOWN - not enough data yet
            return 1.0  # Allow trading until we have data

    def should_exit_pair(self, pair_name):
        """
        Check if pair should be exited due to broken cointegration

        Args:
            pair_name: Name of the pair

        Returns:
            bool: True if should exit
        """
        health = self.check_pair_health(pair_name)

        if health is None:
            return False

        return health['status'] == 'BROKEN'

    def get_all_pairs_status(self):
        """
        Get status summary for all monitored pairs

        Returns:
            dict: Status for each pair
        """
        status_summary = {}

        for pair_name in self.pairs.keys():
            health = self.check_pair_health(pair_name)
            if health:
                status_summary[pair_name] = health

        return status_summary
