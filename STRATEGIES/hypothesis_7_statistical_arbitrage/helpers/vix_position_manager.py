"""
VIX-Based Position Manager for QuantConnect

Helper class to dynamically adjust position sizing based on VIX levels.
Supports multiple portfolio types with different risk profiles.

Usage in main.py:
    from vix_position_manager import VIXPositionManager

    def Initialize(self):
        # Configure portfolio type at initialization
        self.vix_manager = VIXPositionManager(
            portfolio_type='P1',  # or 'P2', 'P3', 'P4'
            qb=self  # Pass QuantConnect algorithm instance
        )

    def OnData(self, data):
        # Get current position sizing
        allocation_pct = self.vix_manager.get_allocation_percentage()

        # Use allocation_pct to scale position sizes
        scaled_position_size = self.base_position_size * (allocation_pct / 100)
"""

from datetime import timedelta


class VIXPositionManager:
    """
    Manages position sizing based on VIX volatility index

    Supports 4 portfolio types:
    - P1, P2 (Aggressive): 100% allocation, VIX > 30 full stop
    - P3, P4 (Conservative): 40% base, VIX > 20 reduce to 70%, VIX > 25 reduce to 25%
    """

    # Portfolio configurations
    PORTFOLIO_CONFIGS = {
        'P1': {
            'type': 'aggressive',
            'base_allocation': 100,  # 100% of assigned capital
            'vix_thresholds': [
                {'vix_max': 30, 'allocation_pct': 100},
                {'vix_max': 999, 'allocation_pct': 0}  # FULL STOP at VIX > 30
            ],
            'description': 'Aggressive: 100% allocation, exits at VIX > 30'
        },
        'P2': {
            'type': 'aggressive',
            'base_allocation': 100,
            'vix_thresholds': [
                {'vix_max': 30, 'allocation_pct': 100},
                {'vix_max': 999, 'allocation_pct': 0}  # FULL STOP at VIX > 30
            ],
            'description': 'Aggressive: 100% allocation, exits at VIX > 30'
        },
        'P3': {
            'type': 'conservative',
            'base_allocation': 40,  # 40% of assigned capital
            'vix_thresholds': [
                {'vix_max': 20, 'allocation_pct': 100},  # 40% × 100% = 40%
                {'vix_max': 25, 'allocation_pct': 70},   # 40% × 70% = 28%
                {'vix_max': 999, 'allocation_pct': 25}   # 40% × 25% = 10%
            ],
            'description': 'Conservative: 40% base, scales down at VIX > 20'
        },
        'P4': {
            'type': 'conservative',
            'base_allocation': 40,
            'vix_thresholds': [
                {'vix_max': 20, 'allocation_pct': 100},
                {'vix_max': 25, 'allocation_pct': 70},
                {'vix_max': 999, 'allocation_pct': 25}
            ],
            'description': 'Conservative: 40% base, scales down at VIX > 20'
        }
    }

    def __init__(self, portfolio_type='P1', qb=None, update_frequency_hours=1):
        """
        Initialize VIX Position Manager

        Args:
            portfolio_type (str): One of 'P1', 'P2', 'P3', 'P4'
            qb: QuantConnect algorithm instance (optional, for logging)
            update_frequency_hours (int): How often to fetch VIX (default: 1 hour)
        """
        if portfolio_type not in self.PORTFOLIO_CONFIGS:
            raise ValueError(f"Invalid portfolio_type: {portfolio_type}. Must be one of: {list(self.PORTFOLIO_CONFIGS.keys())}")

        self.portfolio_type = portfolio_type
        self.config = self.PORTFOLIO_CONFIGS[portfolio_type]
        self.qb = qb
        self.update_frequency = timedelta(hours=update_frequency_hours)

        # Cache for VIX data
        self.cached_vix = None
        self.last_vix_update = None
        self.vix_fetch_errors = 0
        self.max_consecutive_errors = 5

        # Fallback VIX value if data fetch fails
        self.fallback_vix = 15.0  # Assume normal market if can't fetch

        # VIX symbol (will be initialized on first fetch)
        self.vix_symbol = None

        # Setup VIX plotting
        if self.qb:
            self.qb.debug(f"VIXPositionManager initialized: {self.config['description']}")

            # Create VIX chart
            vix_chart = Chart("VIX Monitor")
            vix_chart.add_series(Series("VIX Level", SeriesType.LINE, 0))
            vix_chart.add_series(Series("Allocation %", SeriesType.LINE, 1))
            self.qb.add_chart(vix_chart)

    def get_vix_from_qc(self):
        """
        Fetch VIX from QuantConnect's built-in data (VIX index)

        Returns:
            dict with 'vix', 'timestamp' or None if fetch fails
        """
        try:
            if not self.qb:
                return None

            # Initialize VIX symbol if not already done
            if self.vix_symbol is None:
                self.vix_symbol = self.qb.add_index("VIX", Resolution.DAILY).symbol

            # Get current VIX price
            current_vix = self.qb.securities[self.vix_symbol].price

            if current_vix > 0:
                result = {
                    'vix': round(current_vix, 2),
                    'timestamp': self.qb.Time
                }

                # Reset error counter on success
                self.vix_fetch_errors = 0

                return result
            else:
                return None

        except Exception as e:
            self.vix_fetch_errors += 1

            if self.qb:
                self.qb.debug(f"VIX fetch error ({self.vix_fetch_errors}/{self.max_consecutive_errors}): {str(e)}")

            # If too many consecutive errors, log warning
            if self.vix_fetch_errors >= self.max_consecutive_errors:
                if self.qb:
                    self.qb.error(f"VIX fetch failed {self.vix_fetch_errors} times. Using fallback VIX={self.fallback_vix}")

            return None

    def get_current_vix(self, force_update=False):
        """
        Get current VIX with caching

        Args:
            force_update (bool): Force fetch even if cache is valid

        Returns:
            float: Current VIX level
        """
        # Check if cache is valid
        if not force_update and self.cached_vix is not None and self.last_vix_update is not None:
            if self.qb and (self.qb.Time - self.last_vix_update) < self.update_frequency:
                return self.cached_vix

        # Fetch new VIX data from QuantConnect
        vix_data = self.get_vix_from_qc()

        if vix_data:
            self.cached_vix = vix_data['vix']
            self.last_vix_update = vix_data['timestamp']
            return self.cached_vix
        else:
            # Use cached value if available, otherwise fallback
            if self.cached_vix is not None:
                if self.qb:
                    self.qb.debug(f"Using cached VIX: {self.cached_vix}")
                return self.cached_vix
            else:
                if self.qb:
                    self.qb.debug(f"Using fallback VIX: {self.fallback_vix}")
                return self.fallback_vix

    def get_position_sizing_recommendation(self, vix=None):
        """
        Get position sizing recommendation based on VIX level

        Args:
            vix (float): VIX level. If None, fetches current VIX

        Returns:
            dict with:
                - vix_level (float): Current VIX
                - base_allocation_pct (float): Base allocation for this portfolio
                - vix_scaling_pct (float): VIX-based scaling factor
                - final_allocation_pct (float): Final allocation percentage
                - risk_level (str): Risk description
                - action (str): Recommended action
        """
        # Get VIX if not provided
        if vix is None:
            vix = self.get_current_vix()

        # Find appropriate VIX threshold
        vix_scaling_pct = 0
        for threshold in self.config['vix_thresholds']:
            if vix < threshold['vix_max']:
                vix_scaling_pct = threshold['allocation_pct']
                break

        # Calculate final allocation
        base_allocation = self.config['base_allocation']
        final_allocation = (base_allocation / 100) * vix_scaling_pct

        # Determine risk level and action
        if vix < 15:
            risk_level = 'VERY_LOW'
            action = 'Normal conditions - full allocation'
        elif vix < 20:
            risk_level = 'LOW'
            action = 'Normal volatility'
        elif vix < 25:
            risk_level = 'MODERATE'
            if self.config['type'] == 'conservative':
                action = 'Elevated volatility - reduce to 70%'
            else:
                action = 'Elevated volatility - monitor closely'
        elif vix < 30:
            risk_level = 'HIGH'
            if self.config['type'] == 'conservative':
                action = 'High volatility - reduce to 25%'
            else:
                action = 'High volatility - prepare to exit'
        elif vix < 40:
            risk_level = 'VERY_HIGH'
            if self.config['type'] == 'aggressive':
                action = 'CRISIS - EXIT all positions'
            else:
                action = 'Crisis mode - minimal allocation (25%)'
        else:
            risk_level = 'EXTREME'
            action = 'EXTREME CRISIS - EXIT all positions'

        return {
            'vix_level': vix,
            'base_allocation_pct': base_allocation,
            'vix_scaling_pct': vix_scaling_pct,
            'final_allocation_pct': final_allocation,
            'risk_level': risk_level,
            'action': action,
            'portfolio_type': self.portfolio_type
        }

    def get_allocation_percentage(self, vix=None):
        """
        Get final allocation percentage (simplified interface)

        Args:
            vix (float): VIX level. If None, fetches current VIX

        Returns:
            float: Allocation percentage (0-100)
        """
        recommendation = self.get_position_sizing_recommendation(vix)
        return recommendation['final_allocation_pct']

    def should_exit_all_positions(self, vix=None):
        """
        Check if all positions should be exited based on VIX

        Args:
            vix (float): VIX level. If None, fetches current VIX

        Returns:
            bool: True if should exit all positions
        """
        allocation = self.get_allocation_percentage(vix)
        return allocation == 0

    def get_position_size_multiplier(self, base_position_size, vix=None):
        """
        Get scaled position size based on VIX

        Args:
            base_position_size (float): Base position size (e.g., 1.0 per pair)
            vix (float): VIX level. If None, fetches current VIX

        Returns:
            float: Scaled position size
        """
        allocation_pct = self.get_allocation_percentage(vix)
        return base_position_size * (allocation_pct / 100)

    def plot_vix(self, vix_level, allocation_pct):
        """
        Plot VIX level and allocation percentage

        Args:
            vix_level (float): Current VIX level
            allocation_pct (float): Current allocation percentage
        """
        if self.qb:
            self.qb.plot("VIX Monitor", "VIX Level", vix_level)
            self.qb.plot("VIX Monitor", "Allocation %", allocation_pct)

    def log_status(self, force_vix_update=False):
        """
        Log current VIX and position sizing status

        Args:
            force_vix_update (bool): Force fetch new VIX data
        """
        if not self.qb:
            return

        recommendation = self.get_position_sizing_recommendation(
            vix=self.get_current_vix(force_update=force_vix_update)
        )

        # Plot VIX and allocation
        self.plot_vix(recommendation['vix_level'], recommendation['final_allocation_pct'])

        self.qb.debug("="*70)
        self.qb.debug(f"VIX POSITION MANAGER - {self.portfolio_type}")
        self.qb.debug("="*70)
        self.qb.debug(f"Portfolio Type:    {self.portfolio_type} ({self.config['type']})")
        self.qb.debug(f"VIX Level:         {recommendation['vix_level']:.2f}")
        self.qb.debug(f"Risk Level:        {recommendation['risk_level']}")
        self.qb.debug(f"Base Allocation:   {recommendation['base_allocation_pct']}%")
        self.qb.debug(f"VIX Scaling:       {recommendation['vix_scaling_pct']}%")
        self.qb.debug(f"Final Allocation:  {recommendation['final_allocation_pct']:.1f}%")
        self.qb.debug(f"Action:            {recommendation['action']}")
        self.qb.debug("="*70)
