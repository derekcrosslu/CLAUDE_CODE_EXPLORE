"""
Kalshi Fed Hedge - Federal Reserve Event Hedging

Provides hedging signals for Fed rate decision events using Kalshi
prediction market probabilities.

Usage:
    from SCRIPTS.strategy_components.sentiment.kalshi_fed_hedge import KalshiFedHedge

    hedge = KalshiFedHedge()
    signal = hedge.get_hedge_signal()

    if signal["should_hedge"]:
        # Reduce equity exposure before Fed decision
        pass
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from .kalshi_api_wrapper import KalshiAPI


class KalshiFedHedge:
    """
    Fed event hedging using Kalshi prediction markets.

    Detects:
    - Upcoming Fed decision dates
    - Uncertainty in rate expectations
    - Tail risk scenarios (unexpected hikes/cuts)
    """

    def __init__(self):
        """Initialize Fed hedge analyzer."""
        self.kalshi = KalshiAPI(cache_ttl=180)  # 3-minute cache

    def get_fed_uncertainty(self) -> float:
        """
        Calculate Fed decision uncertainty.

        High uncertainty = market pricing multiple outcomes fairly evenly
        Low uncertainty = market confident in one outcome

        Returns:
            Uncertainty score (0.0 to 1.0)
            - 0.0: Very certain (one rate 90%+ probability)
            - 1.0: Maximum uncertainty (all rates equal probability)
        """
        try:
            fed_probs = self.kalshi.get_fed_rate_probabilities()

            if not fed_probs or len(fed_probs) < 2:
                return 0.5  # Default to moderate uncertainty

            # Calculate entropy as measure of uncertainty
            # Higher entropy = more uncertainty
            probabilities = list(fed_probs.values())

            # Normalize if needed
            total = sum(probabilities)
            if total > 0:
                probabilities = [p / total for p in probabilities]

            # Calculate Shannon entropy
            entropy = 0.0
            for p in probabilities:
                if p > 0:
                    entropy -= p * (p ** 0.5)  # Simplified entropy

            # Normalize to 0-1 range
            max_entropy = len(probabilities) ** 0.5
            if max_entropy > 0:
                uncertainty = entropy / max_entropy
            else:
                uncertainty = 0.5

            return min(max(uncertainty, 0.0), 1.0)

        except Exception as e:
            print(f"Warning: Could not calculate Fed uncertainty: {e}")
            return 0.5

    def get_tail_risk_probability(self) -> float:
        """
        Calculate probability of tail risk Fed decision.

        Tail risk = unexpected large move (50+ bps hike or any cut
        when hikes expected, or vice versa).

        Returns:
            Tail risk probability (0.0 to 1.0)
        """
        try:
            fed_probs = self.kalshi.get_fed_rate_probabilities()

            if not fed_probs:
                return 0.0

            # Sort rates
            rates = sorted([float(r) for r in fed_probs.keys()])

            if len(rates) < 3:
                return 0.0

            # Find most likely rate
            most_likely_rate = max(fed_probs.items(), key=lambda x: x[1])[0]
            most_likely_idx = rates.index(float(most_likely_rate))

            # Tail risk = probability in tails (furthest from most likely)
            # Sum top and bottom 25% of rate distribution
            tail_size = max(1, len(rates) // 4)

            lower_tail_prob = sum(
                fed_probs[str(r)] for r in rates[:tail_size]
            )
            upper_tail_prob = sum(
                fed_probs[str(r)] for r in rates[-tail_size:]
            )

            tail_risk = lower_tail_prob + upper_tail_prob

            return min(tail_risk, 1.0)

        except Exception as e:
            print(f"Warning: Could not calculate tail risk: {e}")
            return 0.0

    def should_hedge_fed_event(self,
                               uncertainty_threshold: float = 0.6,
                               tail_risk_threshold: float = 0.15) -> bool:
        """
        Determine if hedging is recommended for Fed event.

        Args:
            uncertainty_threshold: Min uncertainty to trigger hedge (0.6 = 60%)
            tail_risk_threshold: Min tail risk to trigger hedge (0.15 = 15%)

        Returns:
            True if hedging recommended
        """
        uncertainty = self.get_fed_uncertainty()
        tail_risk = self.get_tail_risk_probability()

        # Hedge if either uncertainty or tail risk is elevated
        should_hedge = (
            uncertainty >= uncertainty_threshold or
            tail_risk >= tail_risk_threshold
        )

        return should_hedge

    def get_hedge_signal(self) -> Dict[str, any]:
        """
        Get complete Fed hedge signal.

        Returns:
            Dictionary with hedging recommendation:
            {
                "should_hedge": bool,
                "uncertainty": float,
                "tail_risk": float,
                "hedge_ratio": float,  # Suggested hedge size (0.0 to 1.0)
                "rationale": str
            }
        """
        uncertainty = self.get_fed_uncertainty()
        tail_risk = self.get_tail_risk_probability()

        should_hedge = self.should_hedge_fed_event()

        # Calculate suggested hedge ratio
        # Higher uncertainty/tail risk = larger hedge
        hedge_ratio = min(
            (uncertainty * 0.5) + (tail_risk * 0.5),
            0.5  # Max 50% hedge
        )

        # Generate rationale
        if should_hedge:
            reasons = []
            if uncertainty >= 0.6:
                reasons.append(f"High uncertainty ({uncertainty:.1%})")
            if tail_risk >= 0.15:
                reasons.append(f"Elevated tail risk ({tail_risk:.1%})")
            rationale = "Fed hedge recommended: " + ", ".join(reasons)
        else:
            rationale = "No Fed hedge needed - market expectations clear"

        return {
            "should_hedge": should_hedge,
            "uncertainty": uncertainty,
            "tail_risk": tail_risk,
            "hedge_ratio": hedge_ratio if should_hedge else 0.0,
            "rationale": rationale
        }

    def get_position_adjustment(self, current_position_size: float) -> float:
        """
        Get suggested position size adjustment for Fed event risk.

        Args:
            current_position_size: Current position size (e.g., 1.0 = 100%)

        Returns:
            Adjusted position size
        """
        signal = self.get_hedge_signal()

        if not signal["should_hedge"]:
            return current_position_size

        # Reduce position by hedge ratio
        adjustment_factor = 1.0 - signal["hedge_ratio"]
        adjusted_size = current_position_size * adjustment_factor

        return adjusted_size


# Helper function for quick hedge check
def should_hedge_fed() -> bool:
    """
    Quick function to check if Fed hedging recommended.

    Returns:
        True if hedging recommended
    """
    hedge = KalshiFedHedge()
    signal = hedge.get_hedge_signal()
    return signal["should_hedge"]
