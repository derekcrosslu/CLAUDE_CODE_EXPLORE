# Kalshi Prediction Market Integration

**Purpose**: Integrate Kalshi prediction market data into QuantConnect trading strategies for enhanced regime detection, volatility forecasting, and sentiment analysis.

**When to use this skill**: When developing strategies that benefit from forward-looking market probabilities, Fed policy expectations, or volatility forecasting.

## Quick Access CLI

Use the `kalshi` CLI for quick data access:

```bash
# List available markets
kalshi markets

# Get Fed rate probabilities
kalshi fed

# Get VIX range probabilities
kalshi vix

# Get market regime classification
kalshi regime

# Get sentiment analysis
kalshi sentiment

# Get Fed hedge recommendation
kalshi hedge

# Access detailed documentation
kalshi docs api
kalshi docs components
kalshi docs regime
kalshi docs fed_hedge
kalshi docs volatility
kalshi docs sentiment
kalshi docs examples
```

## Available Components

### 1. KalshiAPI - Core API Client

**File**: `SCRIPTS/strategy_components/sentiment/kalshi_api_wrapper.py`

Access Kalshi prediction market data without authentication.

```python
from SCRIPTS.strategy_components.sentiment import KalshiAPI

kalshi = KalshiAPI()

# Get Fed rate probabilities
fed_probs = kalshi.get_fed_rate_probabilities()
# Returns: {"4.75": 0.23, "5.00": 0.65, "5.25": 0.12}

# Get VIX range probabilities
vix_probs = kalshi.get_vix_range_probabilities()
# Returns: {"<20": 0.45, "20-25": 0.35, ">25": 0.20}

# Get single market probability
prob = kalshi.get_market_probability("FED-23DEC-T5.00")
# Returns: 0.65
```

**Key Features**:
- No API key required (public endpoints)
- Built-in caching (60s TTL)
- Fed rate probabilities
- VIX range probabilities
- Market orderbook data

### 2. KalshiRegimeDetector - Market Regime Classification

**File**: `SCRIPTS/strategy_components/sentiment/kalshi_regime_detector.py`

Classify market regimes for dynamic position sizing.

```python
from SCRIPTS.strategy_components.sentiment import KalshiRegimeDetector

detector = KalshiRegimeDetector()

# Get complete regime
regime = detector.get_current_regime()
# Returns: {
#     "fed": "NEUTRAL",        # TIGHTENING | NEUTRAL | EASING
#     "volatility": "NORMAL",  # LOW | NORMAL | HIGH
#     "risk": "NEUTRAL"        # RISK_ON | NEUTRAL | RISK_OFF
# }

# Simple risk check
if detector.should_reduce_risk():
    # Reduce positions

# Position sizing multiplier
multiplier = detector.get_position_sizing_multiplier()
# Returns: 0.5 (RISK_OFF) | 1.0 (NEUTRAL) | 1.5 (RISK_ON)
```

**Use Cases**:
- Dynamic position sizing based on regime
- Risk-off detection for position reduction
- Risk-on detection for increased exposure

### 3. KalshiFedHedge - Fed Event Hedging

**File**: `SCRIPTS/strategy_components/sentiment/kalshi_fed_hedge.py`

Hedge around Federal Reserve decision events.

```python
from SCRIPTS.strategy_components.sentiment import KalshiFedHedge

hedge = KalshiFedHedge()

# Get hedge signal
signal = hedge.get_hedge_signal()
# Returns: {
#     "should_hedge": True,
#     "uncertainty": 0.65,
#     "tail_risk": 0.18,
#     "hedge_ratio": 0.35,
#     "rationale": "Fed hedge recommended: High uncertainty (65%)"
# }

# Adjust position
current_size = 1.0
adjusted = hedge.get_position_adjustment(current_size)
# Returns: 0.65 (reduced by 35%)
```

**Use Cases**:
- Reduce exposure before Fed decisions with high uncertainty
- Detect tail risk probabilities
- Calculate appropriate hedge ratios

### 4. KalshiVolForecast - Volatility Forecasting

**File**: `SCRIPTS/strategy_components/sentiment/kalshi_vol_forecast.py`

Forecast expected volatility using VIX prediction markets.

```python
from SCRIPTS.strategy_components.sentiment import KalshiVolForecast

vol_forecast = KalshiVolForecast()

# Get expected VIX
expected_vix = vol_forecast.get_expected_vix()
# Returns: 18.5

# Get complete forecast
signal = vol_forecast.get_vol_forecast_signal()
# Returns: {
#     "expected_vix": 18.5,
#     "vol_regime": "NORMAL",
#     "surprise_prob": 0.12,
#     "position_sizing_factor": 1.0,
#     "signal": "NEUTRAL"
# }

# Adjust for volatility
base_size = 1.0
adjusted = vol_forecast.get_volatility_adjusted_position_size(base_size)
```

**Use Cases**:
- Forward-looking volatility expectations
- Position sizing based on expected volatility
- Volatility surprise detection

### 5. KalshiSentimentMonitor - Sentiment Shift Detection

**File**: `SCRIPTS/strategy_components/sentiment/kalshi_sentiment_monitor.py`

Monitor probability changes to detect sentiment shifts.

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
#         "significant": True
#     }
# }

# Get trading signal
signal = monitor.get_sentiment_signal()
# Returns: {
#     "fed_signal": "BULLISH",
#     "vix_signal": "LOW_VOL",
#     "overall": "RISK_ON"
# }
```

**Use Cases**:
- Detect significant sentiment shifts (>10% moves)
- Generate trading signals from probability changes
- Track historical probability trends

## Quick Helper Functions

For simple use cases:

```python
# Regime
from SCRIPTS.strategy_components.sentiment import get_regime_signal
signal = get_regime_signal()  # "RISK_ON" | "NEUTRAL" | "RISK_OFF"

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
signal = get_sentiment_signal()  # "RISK_ON" | "NEUTRAL" | "RISK_OFF"
```

## Strategy Integration Example

```python
from AlgorithmImports import *
from SCRIPTS.strategy_components.sentiment import (
    KalshiRegimeDetector,
    KalshiFedHedge,
    KalshiVolForecast,
    KalshiSentimentMonitor
)

class KalshiEnhancedStrategy(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2024, 1, 1)
        self.SetCash(100000)

        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol

        # Initialize Kalshi components
        self.regime = KalshiRegimeDetector()
        self.fed_hedge = KalshiFedHedge()
        self.vol_forecast = KalshiVolForecast()
        self.sentiment = KalshiSentimentMonitor()

        # Update sentiment hourly
        self.Schedule.On(
            self.DateRules.EveryDay(),
            self.TimeRules.Every(TimeSpan.FromHours(1)),
            lambda: self.sentiment.update_probabilities()
        )

    def OnData(self, data):
        if not data.ContainsKey(self.spy):
            return

        # Get all signals
        regime = self.regime.get_current_regime()
        fed_signal = self.fed_hedge.get_hedge_signal()
        vol_signal = self.vol_forecast.get_vol_forecast_signal()
        sentiment_signal = self.sentiment.get_sentiment_signal()

        # Calculate position
        position = 1.0

        # Adjust for regime
        position *= self.regime.get_position_sizing_multiplier()

        # Adjust for Fed hedge
        if fed_signal["should_hedge"]:
            position *= (1.0 - fed_signal["hedge_ratio"])

        # Adjust for volatility
        position *= vol_signal["position_sizing_factor"]

        # Adjust for sentiment
        if sentiment_signal["overall"] == "RISK_OFF":
            position *= 0.7
        elif sentiment_signal["overall"] == "RISK_ON":
            position *= 1.2

        # Apply position
        self.SetHoldings(self.spy, position)

        self.Debug(f"Regime: {regime['risk']}, Position: {position:.2f}")
```

## When to Use Each Component

### Use KalshiRegimeDetector when:
- You need overall market regime classification
- You want dynamic position sizing based on risk environment
- You're building regime-based trading strategies

### Use KalshiFedHedge when:
- Fed decision dates are approaching
- You want to reduce exposure during Fed uncertainty
- You need tail risk measurement for Fed events

### Use KalshiVolForecast when:
- You need forward-looking volatility expectations
- You want to adjust positions based on expected vol
- You're building volatility-sensitive strategies

### Use KalshiSentimentMonitor when:
- You want to detect sentiment shifts early
- You need to track probability changes over time
- You want trading signals from sentiment changes

### Combine multiple components when:
- Building comprehensive risk management systems
- Developing adaptive strategies that respond to market conditions
- Creating multi-factor position sizing algorithms

## Best Practices

### 1. Update Frequency
```python
# Update sentiment hourly for shift detection
self.Schedule.On(
    self.DateRules.EveryDay(),
    self.TimeRules.Every(TimeSpan.FromHours(1)),
    self.UpdateSentiment
)

# Check regime before each trade
regime = self.regime.get_current_regime()
```

### 2. Combine Multiple Signals
```python
# Use consensus approach
risk_off_signals = sum([
    detector.should_reduce_risk(),
    fed_hedge.get_hedge_signal()["should_hedge"],
    vol_forecast.should_reduce_positions()
])

# Act when 2+ signals agree
if risk_off_signals >= 2:
    self.ReducePositions()
```

### 3. Error Handling
```python
try:
    regime = self.regime.get_current_regime()
except Exception as e:
    self.Debug(f"Kalshi error: {e}")
    regime = {"risk": "NEUTRAL"}  # Fallback
```

### 4. Backtesting Limitations
- Kalshi data is real-time only
- For backtesting, use simulated probabilities or historical proxy data
- Components return default values if API unavailable

## Detailed Documentation

For comprehensive documentation, use:

```bash
# Complete component documentation
cat SCRIPTS/strategy_components/sentiment/README.md

# Or use the CLI
kalshi docs api          # API integration guide
kalshi docs components   # Component overview
kalshi docs regime       # Regime detection details
kalshi docs fed_hedge    # Fed hedging details
kalshi docs volatility   # Volatility forecasting
kalshi docs sentiment    # Sentiment monitoring
kalshi docs examples     # Strategy examples
```

## Reference Documentation

For deeper details on specific topics:

- **API Integration**: `.claude/skills/kalshi/reference/api_integration.md`
- **Component Overview**: `.claude/skills/kalshi/reference/component_overview.md`
- **Regime Detection**: `.claude/skills/kalshi/reference/regime_detection.md`
- **Fed Hedging**: `.claude/skills/kalshi/reference/fed_hedge.md`
- **Volatility Forecasting**: `.claude/skills/kalshi/reference/volatility_forecast.md`
- **Sentiment Monitoring**: `.claude/skills/kalshi/reference/sentiment_monitor.md`
- **Strategy Examples**: `.claude/skills/kalshi/reference/strategy_examples.md`

## No Setup Required

- **No API key needed**: Uses public Kalshi endpoints
- **No authentication**: All market data is publicly accessible
- **Built-in caching**: Automatic rate limit protection
- **Works out of the box**: Import and use immediately

## Troubleshooting

**API Errors**:
1. Check internet connection
2. Verify Kalshi API accessibility: https://api.elections.kalshi.com/trade-api/v2/series
3. Components have built-in caching to avoid rate limits

**Import Errors**:
```python
import sys
sys.path.append('/path/to/CLAUDE_CODE_EXPLORE')
from SCRIPTS.strategy_components.sentiment import KalshiAPI
```

---

**Version**: 1.0.0
**Created**: 2025-11-14
**Components**: 5 (API, Regime, FedHedge, VolForecast, Sentiment)
**Lines of Code**: 1,863
