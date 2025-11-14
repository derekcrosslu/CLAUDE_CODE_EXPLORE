"""
Kalshi Volatility Forecast - Implied Volatility from Prediction Markets

Uses Kalshi VIX range probabilities to forecast expected volatility
and generate trading signals.

Usage:
    from SCRIPTS.strategy_components.sentiment.kalshi_vol_forecast import KalshiVolForecast

    vol_forecast = KalshiVolForecast()
    expected_vix = vol_forecast.get_expected_vix()

    if expected_vix > 25:
        # High volatility expected - reduce position sizes
        pass
"""

from typing import Dict, Optional, Tuple
from .kalshi_api_wrapper import KalshiAPI


class KalshiVolForecast:
    """
    Forecast volatility using Kalshi VIX prediction markets.

    Provides:
    - Expected VIX level (probability-weighted)
    - Volatility regime forecast
    - Trading signals based on vol expectations
    """

    def __init__(self):
        """Initialize volatility forecaster."""
        self.kalshi = KalshiAPI(cache_ttl=180)  # 3-minute cache

    def get_expected_vix(self) -> float:
        """
        Calculate expected VIX level from Kalshi probabilities.

        Uses midpoint of each range weighted by probability.

        Returns:
            Expected VIX value (e.g., 18.5)
        """
        try:
            vix_probs = self.kalshi.get_vix_range_probabilities()

            if not vix_probs:
                return 20.0  # Default to historical average

            expected_vix = 0.0

            for range_name, prob in vix_probs.items():
                # Extract range from name
                midpoint = self._extract_range_midpoint(range_name)
                expected_vix += midpoint * prob

            return expected_vix

        except Exception as e:
            print(f"Warning: Could not calculate expected VIX: {e}")
            return 20.0

    def _extract_range_midpoint(self, range_name: str) -> float:
        """
        Extract midpoint from VIX range name.

        Args:
            range_name: Range description (e.g., "20-25", "<15", ">30")

        Returns:
            Midpoint value
        """
        range_lower = range_name.lower()

        # Handle different range formats
        if "-" in range_lower:
            # Range format: "20-25"
            parts = range_lower.split("-")
            try:
                lower = float(parts[0].strip())
                upper = float(parts[1].strip())
                return (lower + upper) / 2
            except:
                return 20.0

        elif "<" in range_lower:
            # Less than format: "<15"
            try:
                value = float(range_lower.replace("<", "").strip())
                return value - 2.5  # Assume 2.5 below threshold
            except:
                return 12.5

        elif ">" in range_lower:
            # Greater than format: ">30"
            try:
                value = float(range_lower.replace(">", "").strip())
                return value + 5.0  # Assume 5 above threshold
            except:
                return 35.0

        # Default
        return 20.0

    def get_vol_surprise_probability(self, threshold: float = 25.0) -> float:
        """
        Calculate probability of volatility surprise (spike).

        Args:
            threshold: VIX level considered "high" (default: 25)

        Returns:
            Probability of VIX exceeding threshold
        """
        try:
            vix_probs = self.kalshi.get_vix_range_probabilities()

            if not vix_probs:
                return 0.2  # Default 20% probability

            surprise_prob = 0.0

            for range_name, prob in vix_probs.items():
                midpoint = self._extract_range_midpoint(range_name)
                if midpoint >= threshold:
                    surprise_prob += prob

            return surprise_prob

        except Exception as e:
            print(f"Warning: Could not calculate vol surprise probability: {e}")
            return 0.2

    def get_vol_forecast_signal(self) -> Dict[str, any]:
        """
        Get complete volatility forecast signal.

        Returns:
            Dictionary with forecast and trading implications:
            {
                "expected_vix": float,
                "vol_regime": str,  # "LOW", "NORMAL", "HIGH"
                "surprise_prob": float,
                "position_sizing_factor": float,
                "signal": str  # "REDUCE_RISK", "NEUTRAL", "INCREASE_RISK"
            }
        """
        expected_vix = self.get_expected_vix()
        surprise_prob = self.get_vol_surprise_probability()

        # Classify regime
        if expected_vix < 15:
            vol_regime = "LOW"
            signal = "INCREASE_RISK"
            sizing_factor = 1.2
        elif expected_vix < 20:
            vol_regime = "NORMAL"
            signal = "NEUTRAL"
            sizing_factor = 1.0
        elif expected_vix < 25:
            vol_regime = "ELEVATED"
            signal = "REDUCE_RISK"
            sizing_factor = 0.8
        else:
            vol_regime = "HIGH"
            signal = "REDUCE_RISK"
            sizing_factor = 0.5

        # Adjust for surprise probability
        if surprise_prob > 0.3:  # >30% chance of spike
            signal = "REDUCE_RISK"
            sizing_factor = min(sizing_factor, 0.7)

        return {
            "expected_vix": expected_vix,
            "vol_regime": vol_regime,
            "surprise_prob": surprise_prob,
            "position_sizing_factor": sizing_factor,
            "signal": signal
        }

    def should_reduce_positions(self, vix_threshold: float = 22.0) -> bool:
        """
        Simple signal: Should positions be reduced due to vol expectations?

        Args:
            vix_threshold: VIX level to trigger reduction (default: 22)

        Returns:
            True if position reduction recommended
        """
        expected_vix = self.get_expected_vix()
        return expected_vix >= vix_threshold

    def get_volatility_adjusted_position_size(self,
                                              base_size: float) -> float:
        """
        Adjust position size based on volatility forecast.

        Args:
            base_size: Base position size (e.g., 1.0 = 100%)

        Returns:
            Volatility-adjusted position size
        """
        signal = self.get_vol_forecast_signal()
        sizing_factor = signal["position_sizing_factor"]

        return base_size * sizing_factor

    def get_vol_term_structure(self) -> Dict[str, float]:
        """
        Get volatility term structure if available.

        Checks for VIX markets at different time horizons.

        Returns:
            Dictionary mapping time horizon to expected VIX
            Example: {"1M": 18.5, "3M": 20.2, "6M": 21.5}
        """
        # This would require parsing different VIX series
        # For now, return current expected VIX
        expected_vix = self.get_expected_vix()

        return {
            "current": expected_vix
        }


# Helper functions for quick volatility checks

def get_expected_volatility() -> float:
    """
    Quick function to get expected VIX level.

    Returns:
        Expected VIX value
    """
    forecaster = KalshiVolForecast()
    return forecaster.get_expected_vix()


def is_high_vol_expected() -> bool:
    """
    Quick function to check if high volatility expected.

    Returns:
        True if VIX > 25 expected
    """
    expected_vix = get_expected_volatility()
    return expected_vix > 25.0
