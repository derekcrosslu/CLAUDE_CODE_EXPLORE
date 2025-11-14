"""
Kalshi API Wrapper - Prediction Market Data Integration

Provides clean interface to Kalshi prediction markets for:
- Market data retrieval
- Event probability tracking
- Series information
- Orderbook analysis

Usage:
    from SCRIPTS.strategy_components.sentiment.kalshi_api_wrapper import KalshiAPI

    kalshi = KalshiAPI()
    markets = kalshi.get_markets(series_ticker="FED")
    prob = kalshi.get_market_probability("FED-23DEC-T4.75")
"""

import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import time


class KalshiAPI:
    """
    Kalshi Prediction Markets API Client

    Accesses public market data endpoints without authentication.
    Provides probability data for regime detection, volatility forecasting,
    and sentiment analysis.
    """

    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

    def __init__(self, cache_ttl: int = 60):
        """
        Initialize Kalshi API client.

        Args:
            cache_ttl: Cache time-to-live in seconds (default: 60s)
        """
        self.session = requests.Session()
        self.cache = {}
        self.cache_ttl = cache_ttl

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to Kalshi API with caching.

        Args:
            endpoint: API endpoint path (e.g., "/markets")
            params: Query parameters

        Returns:
            JSON response as dictionary
        """
        # Create cache key
        cache_key = f"{endpoint}:{str(params)}"

        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return cached_data

        # Make request
        url = f"{self.BASE_URL}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Cache response
            self.cache[cache_key] = (data, time.time())

            return data
        except requests.exceptions.RequestException as e:
            raise Exception(f"Kalshi API request failed: {e}")

    def get_series(self, ticker: str) -> Dict:
        """
        Get series information.

        Args:
            ticker: Series ticker (e.g., "FED", "INXD", "VIX")

        Returns:
            Series data dictionary
        """
        return self._make_request(f"/series/{ticker}")

    def get_markets(self,
                    series_ticker: Optional[str] = None,
                    status: str = "open",
                    limit: int = 100) -> List[Dict]:
        """
        Get markets with optional filtering.

        Args:
            series_ticker: Filter by series (e.g., "FED", "INXD")
            status: Market status ("open", "closed", "settled")
            limit: Maximum number of results

        Returns:
            List of market dictionaries
        """
        params = {"status": status, "limit": limit}
        if series_ticker:
            params["series_ticker"] = series_ticker

        response = self._make_request("/markets", params)
        return response.get("markets", [])

    def get_event(self, event_ticker: str) -> Dict:
        """
        Get event details.

        Args:
            event_ticker: Event ticker

        Returns:
            Event data dictionary
        """
        return self._make_request(f"/events/{event_ticker}")

    def get_orderbook(self, market_ticker: str) -> Dict:
        """
        Get orderbook for specific market.

        Args:
            market_ticker: Market ticker

        Returns:
            Orderbook with YES and NO bids
        """
        return self._make_request(f"/markets/{market_ticker}/orderbook")

    def get_market_probability(self, market_ticker: str) -> float:
        """
        Get current probability (0.0 to 1.0) for a YES outcome.

        Uses mid-price from orderbook for most accurate estimate.

        Args:
            market_ticker: Market ticker

        Returns:
            Probability as float (0.0 to 1.0)
        """
        try:
            orderbook = self.get_orderbook(market_ticker)

            # Get best YES bid and best NO bid
            yes_bids = orderbook.get("yes", [])
            no_bids = orderbook.get("no", [])

            if not yes_bids or not no_bids:
                # Fallback to market data if orderbook unavailable
                markets = self.get_markets()
                for market in markets:
                    if market.get("ticker") == market_ticker:
                        yes_price = market.get("yes_price", 50)
                        return yes_price / 100.0
                return 0.5  # Default to 50% if no data

            # Best bid prices (in cents)
            best_yes_bid = yes_bids[0][0] if yes_bids else 0
            best_no_bid = no_bids[0][0] if no_bids else 0

            # Calculate implied probability
            # NO bid implies (100 - NO price) for YES
            # Take average of YES bid and implied YES from NO bid
            yes_from_no = 100 - best_no_bid
            mid_price = (best_yes_bid + yes_from_no) / 2

            return mid_price / 100.0

        except Exception as e:
            print(f"Warning: Could not get probability for {market_ticker}: {e}")
            return 0.5  # Default to neutral

    def get_fed_rate_probabilities(self) -> Dict[str, float]:
        """
        Get Federal Reserve rate decision probabilities.

        Returns:
            Dictionary mapping rate targets to probabilities
            Example: {"4.75": 0.23, "5.00": 0.65, "5.25": 0.12}
        """
        try:
            markets = self.get_markets(series_ticker="FED", status="open")

            probabilities = {}
            for market in markets:
                ticker = market.get("ticker", "")
                title = market.get("title", "")

                # Extract rate from ticker (e.g., "FED-23DEC-T4.75" -> "4.75")
                if "-T" in ticker:
                    rate = ticker.split("-T")[-1]
                    prob = self.get_market_probability(ticker)
                    probabilities[rate] = prob

            return probabilities

        except Exception as e:
            print(f"Warning: Could not get Fed rate probabilities: {e}")
            return {}

    def get_vix_range_probabilities(self) -> Dict[str, float]:
        """
        Get VIX range probabilities.

        Returns:
            Dictionary mapping VIX ranges to probabilities
            Example: {"<20": 0.45, "20-25": 0.35, ">25": 0.20}
        """
        try:
            markets = self.get_markets(series_ticker="VIX", status="open")

            probabilities = {}
            for market in markets:
                ticker = market.get("ticker", "")
                title = market.get("title", "")

                # Extract range from title or ticker
                prob = self.get_market_probability(ticker)
                probabilities[title] = prob

            return probabilities

        except Exception as e:
            print(f"Warning: Could not get VIX probabilities: {e}")
            return {}

    def get_market_changes(self,
                          series_ticker: str,
                          lookback_minutes: int = 60) -> List[Tuple[str, float]]:
        """
        Get probability changes over time (requires caching).

        Args:
            series_ticker: Series to monitor
            lookback_minutes: Time window to check

        Returns:
            List of (market_ticker, probability_change) tuples
        """
        # This is a simplified version - full implementation would need
        # persistent storage to track changes over time
        markets = self.get_markets(series_ticker=series_ticker)

        changes = []
        for market in markets:
            ticker = market.get("ticker", "")
            current_prob = self.get_market_probability(ticker)

            # In production, compare to historical probability
            # For now, return current probabilities
            changes.append((ticker, current_prob))

        return changes


# Utility functions for common queries

def get_fed_hike_probability() -> float:
    """
    Quick function to get probability of Fed rate hike at next meeting.

    Returns:
        Probability of rate increase (0.0 to 1.0)
    """
    kalshi = KalshiAPI()
    try:
        # Get current Fed rate probabilities
        probs = kalshi.get_fed_rate_probabilities()

        if not probs:
            return 0.5

        # Find current rate and higher rates
        rates = sorted([float(r) for r in probs.keys()])
        if len(rates) < 2:
            return 0.5

        # Assume current rate is most likely
        current_rate_idx = rates.index(max(probs.items(), key=lambda x: x[1])[0])

        # Sum probabilities of higher rates
        hike_prob = sum(probs[str(r)] for r in rates[current_rate_idx + 1:])

        return hike_prob
    except Exception as e:
        print(f"Warning: Could not calculate Fed hike probability: {e}")
        return 0.5


def get_high_volatility_probability() -> float:
    """
    Quick function to get probability of high volatility (VIX > 25).

    Returns:
        Probability of high volatility (0.0 to 1.0)
    """
    kalshi = KalshiAPI()
    try:
        vix_probs = kalshi.get_vix_range_probabilities()

        # Sum probabilities for VIX > 25
        high_vol_prob = sum(
            prob for range_name, prob in vix_probs.items()
            if ">25" in range_name or "25-30" in range_name or ">30" in range_name
        )

        return high_vol_prob
    except Exception as e:
        print(f"Warning: Could not calculate high volatility probability: {e}")
        return 0.5
