"""
Kalshi Sentiment Monitor - Probability Shift Detection

Monitors Kalshi prediction market probability changes to detect
shifts in market sentiment and generate trading signals.

Usage:
    from SCRIPTS.strategy_components.sentiment.kalshi_sentiment_monitor import KalshiSentimentMonitor

    monitor = KalshiSentimentMonitor()
    shifts = monitor.detect_sentiment_shifts()

    if shifts["fed"]["shift_magnitude"] > 0.1:
        # Significant Fed expectations shift detected
        pass
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import os
from .kalshi_api_wrapper import KalshiAPI


class KalshiSentimentMonitor:
    """
    Monitor Kalshi prediction market sentiment changes.

    Tracks:
    - Probability shifts over time
    - Sudden sentiment changes
    - Divergence between markets
    """

    def __init__(self, history_file: Optional[str] = None):
        """
        Initialize sentiment monitor.

        Args:
            history_file: Path to store historical probabilities
                         (default: .kalshi_sentiment_history.json in temp)
        """
        self.kalshi = KalshiAPI(cache_ttl=60)  # 1-minute cache

        # Set up history storage
        if history_file is None:
            import tempfile
            self.history_file = os.path.join(
                tempfile.gettempdir(),
                '.kalshi_sentiment_history.json'
            )
        else:
            self.history_file = history_file

        self.history = self._load_history()

    def _load_history(self) -> Dict:
        """Load historical probabilities from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def _save_history(self):
        """Save historical probabilities to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save sentiment history: {e}")

    def update_probabilities(self):
        """
        Update current probabilities and store in history.

        Should be called periodically (e.g., every hour).
        """
        timestamp = datetime.utcnow().isoformat()

        # Get current Fed probabilities
        try:
            fed_probs = self.kalshi.get_fed_rate_probabilities()
            if fed_probs:
                if "fed" not in self.history:
                    self.history["fed"] = []
                self.history["fed"].append({
                    "timestamp": timestamp,
                    "probabilities": fed_probs
                })
        except Exception as e:
            print(f"Warning: Could not update Fed probabilities: {e}")

        # Get current VIX probabilities
        try:
            vix_probs = self.kalshi.get_vix_range_probabilities()
            if vix_probs:
                if "vix" not in self.history:
                    self.history["vix"] = []
                self.history["vix"].append({
                    "timestamp": timestamp,
                    "probabilities": vix_probs
                })
        except Exception as e:
            print(f"Warning: Could not update VIX probabilities: {e}")

        # Keep only last 168 hours (1 week) of history
        max_history = 168
        for key in ["fed", "vix"]:
            if key in self.history and len(self.history[key]) > max_history:
                self.history[key] = self.history[key][-max_history:]

        self._save_history()

    def get_probability_shift(self,
                             market: str,
                             lookback_hours: int = 24) -> Dict[str, float]:
        """
        Calculate probability shifts over time window.

        Args:
            market: Market category ("fed" or "vix")
            lookback_hours: Hours to look back

        Returns:
            Dictionary mapping outcomes to probability changes
        """
        if market not in self.history or len(self.history[market]) < 2:
            return {}

        history = self.history[market]

        # Get most recent probability
        current = history[-1]["probabilities"]

        # Find probability from lookback_hours ago
        target_time = datetime.fromisoformat(history[-1]["timestamp"])
        past_probs = None

        for entry in reversed(history[:-1]):
            entry_time = datetime.fromisoformat(entry["timestamp"])
            hours_ago = (target_time - entry_time).total_seconds() / 3600

            if hours_ago >= lookback_hours:
                past_probs = entry["probabilities"]
                break

        if past_probs is None:
            # Use oldest available if not enough history
            past_probs = history[0]["probabilities"]

        # Calculate shifts
        shifts = {}
        all_outcomes = set(list(current.keys()) + list(past_probs.keys()))

        for outcome in all_outcomes:
            current_prob = current.get(outcome, 0.0)
            past_prob = past_probs.get(outcome, 0.0)
            shift = current_prob - past_prob
            shifts[outcome] = shift

        return shifts

    def detect_sentiment_shifts(self,
                                lookback_hours: int = 24,
                                shift_threshold: float = 0.10) -> Dict:
        """
        Detect significant sentiment shifts.

        Args:
            lookback_hours: Time window to check
            shift_threshold: Minimum shift to flag (0.10 = 10%)

        Returns:
            Dictionary with detected shifts:
            {
                "fed": {
                    "shifts": {...},
                    "max_shift": float,
                    "shift_magnitude": float,
                    "significant": bool
                },
                "vix": {...}
            }
        """
        result = {}

        for market in ["fed", "vix"]:
            shifts = self.get_probability_shift(market, lookback_hours)

            if shifts:
                max_shift = max(abs(s) for s in shifts.values())
                shift_magnitude = sum(abs(s) for s in shifts.values()) / 2

                result[market] = {
                    "shifts": shifts,
                    "max_shift": max_shift,
                    "shift_magnitude": shift_magnitude,
                    "significant": max_shift >= shift_threshold
                }
            else:
                result[market] = {
                    "shifts": {},
                    "max_shift": 0.0,
                    "shift_magnitude": 0.0,
                    "significant": False
                }

        return result

    def get_sentiment_signal(self) -> Dict[str, str]:
        """
        Get trading signal based on sentiment shifts.

        Returns:
            Dictionary with signals:
            {
                "fed_signal": "BULLISH" | "NEUTRAL" | "BEARISH",
                "vix_signal": "LOW_VOL" | "NEUTRAL" | "HIGH_VOL",
                "overall": "RISK_ON" | "NEUTRAL" | "RISK_OFF"
            }
        """
        shifts = self.detect_sentiment_shifts()

        # Analyze Fed shifts
        fed_shifts = shifts["fed"]["shifts"]
        fed_signal = "NEUTRAL"

        if fed_shifts:
            # Check if probabilities shifting toward cuts (bullish)
            # or hikes (bearish)
            rates = sorted([float(r) for r in fed_shifts.keys()])
            if len(rates) >= 2:
                # Sum positive shifts on lower rates vs higher rates
                mid_idx = len(rates) // 2
                lower_shift = sum(fed_shifts.get(str(r), 0) for r in rates[:mid_idx])
                upper_shift = sum(fed_shifts.get(str(r), 0) for r in rates[mid_idx:])

                if lower_shift > 0.15:  # Shift toward cuts
                    fed_signal = "BULLISH"
                elif upper_shift > 0.15:  # Shift toward hikes
                    fed_signal = "BEARISH"

        # Analyze VIX shifts
        vix_shifts = shifts["vix"]["shifts"]
        vix_signal = "NEUTRAL"

        if vix_shifts:
            # Check if shifting toward high or low vol
            high_vol_shift = 0.0
            low_vol_shift = 0.0

            for range_name, shift in vix_shifts.items():
                if "<15" in range_name or "<20" in range_name:
                    low_vol_shift += shift
                elif ">25" in range_name or ">30" in range_name:
                    high_vol_shift += shift

            if high_vol_shift > 0.10:
                vix_signal = "HIGH_VOL"
            elif low_vol_shift > 0.10:
                vix_signal = "LOW_VOL"

        # Overall signal
        if fed_signal == "BULLISH" and vix_signal != "HIGH_VOL":
            overall = "RISK_ON"
        elif fed_signal == "BEARISH" or vix_signal == "HIGH_VOL":
            overall = "RISK_OFF"
        else:
            overall = "NEUTRAL"

        return {
            "fed_signal": fed_signal,
            "vix_signal": vix_signal,
            "overall": overall
        }


# Helper function for quick sentiment check
def get_sentiment_signal() -> str:
    """
    Quick function to get overall sentiment signal.

    Returns:
        "RISK_ON", "NEUTRAL", or "RISK_OFF"
    """
    monitor = KalshiSentimentMonitor()
    monitor.update_probabilities()
    signal = monitor.get_sentiment_signal()
    return signal["overall"]
