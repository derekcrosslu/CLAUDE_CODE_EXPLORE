"""
Kalshi Sentiment Components

Prediction market data integration for trading strategies.

Components:
- KalshiAPI: API client for Kalshi prediction markets
- KalshiRegimeDetector: Market regime classification
- KalshiFedHedge: Fed event hedging signals
- KalshiVolForecast: Volatility forecasting
- KalshiSentimentMonitor: Sentiment shift detection

Quick Start:
    >>> from SCRIPTS.strategy_components.sentiment import KalshiRegimeDetector
    >>> detector = KalshiRegimeDetector()
    >>> regime = detector.get_current_regime()
    >>> print(regime)
    {'fed': 'NEUTRAL', 'volatility': 'NORMAL', 'risk': 'NEUTRAL'}
"""

from .kalshi_api_wrapper import KalshiAPI
from .kalshi_regime_detector import (
    KalshiRegimeDetector,
    FedRegime,
    VolatilityRegime,
    RiskRegime,
    get_regime_signal
)
from .kalshi_fed_hedge import KalshiFedHedge, should_hedge_fed
from .kalshi_vol_forecast import (
    KalshiVolForecast,
    get_expected_volatility,
    is_high_vol_expected
)
from .kalshi_sentiment_monitor import (
    KalshiSentimentMonitor,
    get_sentiment_signal
)

__all__ = [
    # API Client
    'KalshiAPI',

    # Regime Detection
    'KalshiRegimeDetector',
    'FedRegime',
    'VolatilityRegime',
    'RiskRegime',
    'get_regime_signal',

    # Fed Hedge
    'KalshiFedHedge',
    'should_hedge_fed',

    # Volatility Forecast
    'KalshiVolForecast',
    'get_expected_volatility',
    'is_high_vol_expected',

    # Sentiment Monitor
    'KalshiSentimentMonitor',
    'get_sentiment_signal',
]
