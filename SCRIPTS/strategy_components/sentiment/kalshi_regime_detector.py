"""
Kalshi Regime Detector - Market Regime Classification

Uses Kalshi prediction market probabilities to classify market regimes:
- Fed tightening vs easing
- High vs low volatility expectations
- Risk-on vs risk-off sentiment

Usage:
    from SCRIPTS.strategy_components.sentiment.kalshi_regime_detector import KalshiRegimeDetector

    detector = KalshiRegimeDetector()
    regime = detector.get_current_regime()

    if regime["volatility"] == "HIGH":
        # Reduce position sizes
        pass
"""

from typing import Dict, Optional
from enum import Enum
from .kalshi_api_wrapper import KalshiAPI


class FedRegime(Enum):
    """Federal Reserve policy regime"""
    TIGHTENING = "TIGHTENING"  # Likely rate hikes
    NEUTRAL = "NEUTRAL"         # No change expected
    EASING = "EASING"           # Likely rate cuts


class VolatilityRegime(Enum):
    """Market volatility regime"""
    LOW = "LOW"      # VIX < 15 expected
    NORMAL = "NORMAL"  # VIX 15-25
    HIGH = "HIGH"    # VIX > 25 expected


class RiskRegime(Enum):
    """Market risk sentiment"""
    RISK_ON = "RISK_ON"    # Low volatility, bullish
    NEUTRAL = "NEUTRAL"     # Mixed signals
    RISK_OFF = "RISK_OFF"  # High volatility, bearish


class KalshiRegimeDetector:
    """
    Detect market regimes using Kalshi prediction market data.

    Combines Fed rate expectations, volatility forecasts, and other
    prediction market signals to classify current market regime.
    """

    def __init__(self):
        """Initialize regime detector with Kalshi API."""
        self.kalshi = KalshiAPI(cache_ttl=300)  # 5-minute cache

    def get_fed_regime(self) -> FedRegime:
        """
        Classify Federal Reserve policy regime.

        Returns:
            FedRegime enum (TIGHTENING, NEUTRAL, EASING)
        """
        try:
            fed_probs = self.kalshi.get_fed_rate_probabilities()

            if not fed_probs:
                return FedRegime.NEUTRAL

            # Sort rates
            rates = sorted([float(r) for r in fed_probs.keys()])

            # Find most likely rate
            most_likely_rate = max(fed_probs.items(), key=lambda x: x[1])[0]
            most_likely_idx = rates.index(float(most_likely_rate))

            # Calculate probability weighted direction
            hike_prob = sum(
                fed_probs[str(r)] for r in rates[most_likely_idx + 1:]
            )
            cut_prob = sum(
                fed_probs[str(r)] for r in rates[:most_likely_idx]
            )

            # Classify regime
            if hike_prob > 0.4:
                return FedRegime.TIGHTENING
            elif cut_prob > 0.4:
                return FedRegime.EASING
            else:
                return FedRegime.NEUTRAL

        except Exception as e:
            print(f"Warning: Could not determine Fed regime: {e}")
            return FedRegime.NEUTRAL

    def get_volatility_regime(self) -> VolatilityRegime:
        """
        Classify expected volatility regime.

        Returns:
            VolatilityRegime enum (LOW, NORMAL, HIGH)
        """
        try:
            vix_probs = self.kalshi.get_vix_range_probabilities()

            if not vix_probs:
                return VolatilityRegime.NORMAL

            # Categorize probabilities
            low_vol_prob = 0.0
            normal_vol_prob = 0.0
            high_vol_prob = 0.0

            for range_name, prob in vix_probs.items():
                range_lower = range_name.lower()

                if "<15" in range_lower or "<20" in range_lower:
                    low_vol_prob += prob
                elif "15-20" in range_lower or "20-25" in range_lower:
                    normal_vol_prob += prob
                elif ">25" in range_lower or ">30" in range_lower:
                    high_vol_prob += prob

            # Classify based on highest probability
            if high_vol_prob > max(low_vol_prob, normal_vol_prob):
                return VolatilityRegime.HIGH
            elif low_vol_prob > normal_vol_prob:
                return VolatilityRegime.LOW
            else:
                return VolatilityRegime.NORMAL

        except Exception as e:
            print(f"Warning: Could not determine volatility regime: {e}")
            return VolatilityRegime.NORMAL

    def get_risk_regime(self) -> RiskRegime:
        """
        Classify overall market risk regime.

        Combines Fed policy and volatility expectations.

        Returns:
            RiskRegime enum (RISK_ON, NEUTRAL, RISK_OFF)
        """
        fed_regime = self.get_fed_regime()
        vol_regime = self.get_volatility_regime()

        # Risk-on: Easing Fed + Low volatility
        if fed_regime == FedRegime.EASING and vol_regime == VolatilityRegime.LOW:
            return RiskRegime.RISK_ON

        # Risk-off: Tightening Fed + High volatility
        if fed_regime == FedRegime.TIGHTENING and vol_regime == VolatilityRegime.HIGH:
            return RiskRegime.RISK_OFF

        # Risk-off: High volatility regardless of Fed
        if vol_regime == VolatilityRegime.HIGH:
            return RiskRegime.RISK_OFF

        # Risk-on: Low volatility + not tightening
        if vol_regime == VolatilityRegime.LOW and fed_regime != FedRegime.TIGHTENING:
            return RiskRegime.RISK_ON

        # Otherwise neutral
        return RiskRegime.NEUTRAL

    def get_current_regime(self) -> Dict[str, str]:
        """
        Get complete current market regime classification.

        Returns:
            Dictionary with regime classifications:
            {
                "fed": "TIGHTENING" | "NEUTRAL" | "EASING",
                "volatility": "LOW" | "NORMAL" | "HIGH",
                "risk": "RISK_ON" | "NEUTRAL" | "RISK_OFF"
            }
        """
        return {
            "fed": self.get_fed_regime().value,
            "volatility": self.get_volatility_regime().value,
            "risk": self.get_risk_regime().value
        }

    def should_reduce_risk(self) -> bool:
        """
        Simple signal: Should strategy reduce risk exposure?

        Returns:
            True if risk-off regime detected
        """
        risk_regime = self.get_risk_regime()
        return risk_regime == RiskRegime.RISK_OFF

    def should_increase_risk(self) -> bool:
        """
        Simple signal: Should strategy increase risk exposure?

        Returns:
            True if risk-on regime detected
        """
        risk_regime = self.get_risk_regime()
        return risk_regime == RiskRegime.RISK_ON

    def get_position_sizing_multiplier(self) -> float:
        """
        Get position sizing multiplier based on regime.

        Returns:
            Float multiplier (0.5 to 1.5)
            - RISK_OFF: 0.5 (reduce positions)
            - NEUTRAL: 1.0 (normal positions)
            - RISK_ON: 1.5 (increase positions)
        """
        risk_regime = self.get_risk_regime()

        if risk_regime == RiskRegime.RISK_OFF:
            return 0.5
        elif risk_regime == RiskRegime.RISK_ON:
            return 1.5
        else:
            return 1.0


# Helper function for quick regime check
def get_regime_signal() -> str:
    """
    Quick function to get regime signal.

    Returns:
        "RISK_ON", "NEUTRAL", or "RISK_OFF"
    """
    detector = KalshiRegimeDetector()
    regime = detector.get_current_regime()
    return regime["risk"]
