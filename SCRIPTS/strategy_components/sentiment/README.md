# Kalshi Prediction Market Integration

Integrate Kalshi prediction market data into your QuantConnect trading strategies for enhanced regime detection, volatility forecasting, and sentiment analysis.

## Components

### 1. KalshiAPI - API Client
**File**: `kalshi_api_wrapper.py`

Core API client for accessing Kalshi prediction market data.

**Features**:
- Public market data access (no authentication required)
- Built-in caching (60s TTL)
- Series, markets, events, and orderbook endpoints
- Probability calculation from orderbook data

**Usage**:
```python
from SCRIPTS.strategy_components.sentiment import KalshiAPI

kalshi = KalshiAPI()

# Get Fed rate probabilities
fed_probs = kalshi.get_fed_rate_probabilities()
# Returns: {"4.75": 0.23, "5.00": 0.65, "5.25": 0.12}

# Get market probability
prob = kalshi.get_market_probability("FED-23DEC-T5.00")
# Returns: 0.65 (65% probability)

# Get VIX range probabilities
vix_probs = kalshi.get_vix_range_probabilities()
# Returns: {"<20": 0.45, "20-25": 0.35, ">25": 0.20}
```

---

### 2. KalshiRegimeDetector - Market Regime Classification
**File**: `kalshi_regime_detector.py`

Classify market regimes using prediction market probabilities.

**Regimes**:
- **Fed Policy**: TIGHTENING | NEUTRAL | EASING
- **Volatility**: LOW | NORMAL | HIGH
- **Risk Sentiment**: RISK_ON | NEUTRAL | RISK_OFF

**Usage**:
```python
from SCRIPTS.strategy_components.sentiment import KalshiRegimeDetector

detector = KalshiRegimeDetector()

# Get complete regime classification
regime = detector.get_current_regime()
# Returns: {
#     "fed": "NEUTRAL",
#     "volatility": "NORMAL",
#     "risk": "NEUTRAL"
# }

# Simple risk check
if detector.should_reduce_risk():
    # Reduce position sizes

# Position sizing multiplier
multiplier = detector.get_position_sizing_multiplier()
# Returns: 0.5 (RISK_OFF) | 1.0 (NEUTRAL) | 1.5 (RISK_ON)
```

**Integration in Strategy**:
```python
class MyStrategy(QCAlgorithm):
    def Initialize(self):
        self.regime_detector = KalshiRegimeDetector()

    def OnData(self, data):
        regime = self.regime_detector.get_current_regime()

        if regime["risk"] == "RISK_OFF":
            # Reduce all positions by 50%
            for symbol in self.Portfolio.Keys:
                self.SetHoldings(symbol, self.Portfolio[symbol].Quantity * 0.5)
```

---

### 3. KalshiFedHedge - Fed Event Hedging
**File**: `kalshi_fed_hedge.py`

Hedge strategies around Federal Reserve decision events.

**Features**:
- Fed decision uncertainty measurement
- Tail risk probability (unexpected moves)
- Automatic hedge ratio calculation

**Usage**:
```python
from SCRIPTS.strategy_components.sentiment import KalshiFedHedge

hedge = KalshiFedHedge()

# Get complete hedge signal
signal = hedge.get_hedge_signal()
# Returns: {
#     "should_hedge": True,
#     "uncertainty": 0.65,
#     "tail_risk": 0.18,
#     "hedge_ratio": 0.35,
#     "rationale": "Fed hedge recommended: High uncertainty (65%), Elevated tail risk (18%)"
# }

# Adjust position size
current_size = 1.0
adjusted_size = hedge.get_position_adjustment(current_size)
# Returns: 0.65 (reduced by 35% hedge ratio)
```

**Integration in Strategy**:
```python
def OnData(self, data):
    hedge_signal = self.fed_hedge.get_hedge_signal()

    if hedge_signal["should_hedge"]:
        # Reduce exposure before Fed decision
        target_leverage = 1.0 - hedge_signal["hedge_ratio"]
        self.SetHoldings("SPY", target_leverage)
```

---

### 4. KalshiVolForecast - Volatility Forecasting
**File**: `kalshi_vol_forecast.py`

Forecast expected volatility using Kalshi VIX prediction markets.

**Features**:
- Expected VIX calculation (probability-weighted)
- Volatility surprise detection
- Position sizing based on vol expectations

**Usage**:
```python
from SCRIPTS.strategy_components.sentiment import KalshiVolForecast

vol_forecast = KalshiVolForecast()

# Get expected VIX level
expected_vix = vol_forecast.get_expected_vix()
# Returns: 18.5

# Get complete forecast signal
signal = vol_forecast.get_vol_forecast_signal()
# Returns: {
#     "expected_vix": 18.5,
#     "vol_regime": "NORMAL",
#     "surprise_prob": 0.12,
#     "position_sizing_factor": 1.0,
#     "signal": "NEUTRAL"
# }

# Adjust positions for volatility
base_size = 1.0
adjusted_size = vol_forecast.get_volatility_adjusted_position_size(base_size)
```

**Integration in Strategy**:
```python
def OnData(self, data):
    vol_signal = self.vol_forecast.get_vol_forecast_signal()

    if vol_signal["expected_vix"] > 25:
        # High volatility expected - reduce positions
        sizing_factor = 0.5
    else:
        sizing_factor = 1.0

    self.SetHoldings("SPY", 1.0 * sizing_factor)
```

---

### 5. KalshiSentimentMonitor - Sentiment Shift Detection
**File**: `kalshi_sentiment_monitor.py`

Monitor probability changes to detect sentiment shifts.

**Features**:
- Tracks historical probabilities
- Detects significant shifts (>10% moves)
- Generates trading signals from sentiment changes

**Usage**:
```python
from SCRIPTS.strategy_components.sentiment import KalshiSentimentMonitor

monitor = KalshiSentimentMonitor()

# Update probabilities (call periodically)
monitor.update_probabilities()

# Detect shifts
shifts = monitor.detect_sentiment_shifts(lookback_hours=24)
# Returns: {
#     "fed": {
#         "shifts": {"5.00": -0.15, "4.75": 0.15},
#         "max_shift": 0.15,
#         "shift_magnitude": 0.15,
#         "significant": True
#     },
#     "vix": {...}
# }

# Get trading signal
signal = monitor.get_sentiment_signal()
# Returns: {
#     "fed_signal": "BULLISH",
#     "vix_signal": "LOW_VOL",
#     "overall": "RISK_ON"
# }
```

**Integration in Strategy**:
```python
def Initialize(self):
    self.monitor = KalshiSentimentMonitor()
    # Update hourly
    self.Schedule.On(
        self.DateRules.EveryDay(),
        self.TimeRules.Every(TimeSpan.FromHours(1)),
        self.UpdateSentiment
    )

def UpdateSentiment(self):
    self.monitor.update_probabilities()

def OnData(self, data):
    signal = self.monitor.get_sentiment_signal()

    if signal["overall"] == "RISK_ON":
        self.SetHoldings("SPY", 1.5)  # Leverage up
    elif signal["overall"] == "RISK_OFF":
        self.SetHoldings("SPY", 0.5)  # Reduce exposure
```

---

## Complete Strategy Example

Here's a complete strategy integrating all Kalshi components:

```python
from AlgorithmImports import *
from SCRIPTS.strategy_components.sentiment import (
    KalshiRegimeDetector,
    KalshiFedHedge,
    KalshiVolForecast,
    KalshiSentimentMonitor
)


class KalshiEnhancedStrategy(QCAlgorithm):
    """
    Strategy enhanced with Kalshi prediction market data.

    Uses regime detection, Fed hedging, volatility forecasting,
    and sentiment monitoring to adjust positions dynamically.
    """

    def Initialize(self):
        self.SetStartDate(2024, 1, 1)
        self.SetCash(100000)

        # Add SPY
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol

        # Initialize Kalshi components
        self.regime_detector = KalshiRegimeDetector()
        self.fed_hedge = KalshiFedHedge()
        self.vol_forecast = KalshiVolForecast()
        self.sentiment_monitor = KalshiSentimentMonitor()

        # Update sentiment hourly
        self.Schedule.On(
            self.DateRules.EveryDay(),
            self.TimeRules.Every(TimeSpan.FromHours(1)),
            self.UpdateSentiment
        )

    def UpdateSentiment(self):
        """Update sentiment monitor with latest probabilities."""
        self.sentiment_monitor.update_probabilities()

    def OnData(self, data):
        if not data.ContainsKey(self.spy):
            return

        # Get all signals
        regime = self.regime_detector.get_current_regime()
        fed_signal = self.fed_hedge.get_hedge_signal()
        vol_signal = self.vol_forecast.get_vol_forecast_signal()
        sentiment = self.sentiment_monitor.get_sentiment_signal()

        # Calculate base position
        base_position = 1.0

        # Adjust for regime
        regime_multiplier = self.regime_detector.get_position_sizing_multiplier()
        base_position *= regime_multiplier

        # Adjust for Fed hedge
        if fed_signal["should_hedge"]:
            base_position *= (1.0 - fed_signal["hedge_ratio"])

        # Adjust for volatility
        base_position *= vol_signal["position_sizing_factor"]

        # Adjust for sentiment shifts
        if sentiment["overall"] == "RISK_OFF":
            base_position *= 0.7
        elif sentiment["overall"] == "RISK_ON":
            base_position *= 1.2

        # Apply position
        self.SetHoldings(self.spy, base_position)

        # Log decision
        self.Debug(f"Regime: {regime['risk']}, Fed Hedge: {fed_signal['should_hedge']}, "
                  f"Vol: {vol_signal['vol_regime']}, Sentiment: {sentiment['overall']}, "
                  f"Position: {base_position:.2f}")
```

---

## Installation & Setup

### Requirements

Add to your `requirements.txt`:
```
requests>=2.28.0
```

### No API Key Needed

Kalshi public market data endpoints don't require authentication. The components work out of the box.

### Caching

All components use built-in caching to minimize API calls:
- **KalshiAPI**: 60-second cache
- **KalshiRegimeDetector**: 5-minute cache
- **KalshiFedHedge**: 3-minute cache
- **KalshiVolForecast**: 3-minute cache
- **KalshiSentimentMonitor**: 1-minute cache

---

## Best Practices

### 1. Update Frequency

```python
# Good: Update hourly for sentiment shifts
self.Schedule.On(
    self.DateRules.EveryDay(),
    self.TimeRules.Every(TimeSpan.FromHours(1)),
    self.UpdateSentiment
)

# Good: Check regime before each trade
regime = self.regime_detector.get_current_regime()
```

### 2. Combine Multiple Signals

```python
# Don't rely on single signal
regime_says_risk_off = detector.should_reduce_risk()
fed_hedge_recommended = fed_hedge.get_hedge_signal()["should_hedge"]
high_vol_expected = vol_forecast.should_reduce_positions()

# Use consensus
if sum([regime_says_risk_off, fed_hedge_recommended, high_vol_expected]) >= 2:
    # Two or more signals agree - reduce risk
    self.ReducePositions()
```

### 3. Error Handling

```python
try:
    regime = self.regime_detector.get_current_regime()
except Exception as e:
    self.Debug(f"Kalshi error: {e}")
    # Fall back to default behavior
    regime = {"risk": "NEUTRAL"}
```

### 4. Backtesting Limitations

**Note**: Kalshi prediction market data is only available in real-time. For backtesting:
- Use simulated probabilities
- Or use historical volatility/Fed funds data as proxy
- Components will return default values if API unavailable

---

## API Reference

### Quick Helper Functions

For simple use cases, use the helper functions:

```python
# Regime
from SCRIPTS.strategy_components.sentiment import get_regime_signal
signal = get_regime_signal()  # Returns: "RISK_ON" | "NEUTRAL" | "RISK_OFF"

# Fed Hedge
from SCRIPTS.strategy_components.sentiment import should_hedge_fed
if should_hedge_fed():
    # Reduce positions

# Volatility
from SCRIPTS.strategy_components.sentiment import get_expected_volatility, is_high_vol_expected
vix = get_expected_volatility()  # Returns: 18.5
if is_high_vol_expected():  # VIX > 25
    # Reduce positions

# Sentiment
from SCRIPTS.strategy_components.sentiment import get_sentiment_signal
signal = get_sentiment_signal()  # Returns: "RISK_ON" | "NEUTRAL" | "RISK_OFF"
```

---

## Troubleshooting

### API Errors

If you get API errors:
1. Check internet connection
2. Verify Kalshi API is accessible: https://api.elections.kalshi.com/trade-api/v2/series
3. Check rate limits (components have built-in caching to avoid hitting limits)

### Import Errors

```python
# If you get import errors, check Python path:
import sys
sys.path.append('/path/to/CLAUDE_CODE_EXPLORE')

from SCRIPTS.strategy_components.sentiment import KalshiAPI
```

---

## Further Reading

- [Kalshi API Documentation](https://docs.kalshi.com/)
- [Prediction Markets Overview](https://help.kalshi.com/)
- Component source code in `SCRIPTS/strategy_components/sentiment/`

---

**Created**: 2025-11-14
**Version**: 1.0.0
**License**: MIT
