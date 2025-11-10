# Synthetic Data Generation for Financial Time Series

**Date:** November 10, 2025
**Purpose:** Research methods for generating realistic synthetic financial data to automate walkforward validation pipeline
**Target:** Match real backtest results (Sharpe -9.462, 6 trades) for testing Monte Carlo framework

---

## Executive Summary

**Objective:** Generate synthetic OHLCV data that:
1. Preserves realistic statistical properties (volatility clustering, fat tails, autocorrelation)
2. Can be controlled to match specific backtest results
3. Enables full automation of walkforward testing without API costs
4. Validates Monte Carlo logic before running expensive cloud backtests

**Recommendation:** **Hybrid GARCH + Geometric Brownian Motion** approach
- Simple to implement
- Controllable parameters to match target metrics
- Preserves realistic volatility patterns
- Fast generation (~seconds for years of data)
- No complex ML training required

---

## Research Findings

### 1. State-of-the-Art Methods (2024-2025)

#### A. Diffusion Models (DDPMs)
**Source:** Quantitative Finance 2025, arXiv:2410.18897

**Method:**
- Denoising diffusion probabilistic models
- Wavelet transformation to convert time series to images
- Generate synthetic series by reversing diffusion process

**Pros:**
- ✅ State-of-the-art quality
- ✅ Captures complex patterns
- ✅ Published research validates approach

**Cons:**
- ❌ Complex to implement (requires deep learning expertise)
- ❌ Slow training (hours to days)
- ❌ Hard to control specific outputs (Sharpe, trade count)
- ❌ Requires GPU for reasonable performance

**Verdict:** ❌ **Not suitable** - Too complex for our immediate needs

---

#### B. TimeGAN (Time-Series GANs)
**Source:** Kaggle, research papers

**Method:**
- Generative Adversarial Networks for time series
- Learns both distribution and temporal dynamics
- Trained on real financial data

**Pros:**
- ✅ High-quality synthetic data
- ✅ Preserves temporal patterns
- ✅ Good for augmentation

**Cons:**
- ❌ Requires training data
- ❌ Complex implementation
- ❌ Difficult to control specific metrics
- ❌ Training instability (GANs)

**Verdict:** ⚠️ **Possible future enhancement** - Good quality but overkill for initial implementation

---

#### C. GARCH + Bootstrap
**Source:** Multiple academic papers, EViews blog

**Method:**
- Fit GARCH(1,1) model to capture volatility clustering
- Bootstrap residuals to generate new sequences
- Preserves heteroscedasticity patterns

**Pros:**
- ✅ Proven method (decades of research)
- ✅ Preserves volatility clustering
- ✅ Fast to compute
- ✅ Simple implementation (arch library in Python)

**Cons:**
- ⚠️ Requires historical data to fit model
- ⚠️ May not capture all stylized facts
- ⚠️ Limited control over specific outputs

**Verdict:** ✅ **Strong candidate** - Good balance of quality and simplicity

---

#### D. Geometric Brownian Motion (GBM)
**Source:** Monte Carlo simulation standard, multiple implementations

**Method:**
- Simulate price paths using stochastic differential equation
- dS = μS dt + σS dW
- Where μ = drift, σ = volatility, dW = Wiener process

**Pros:**
- ✅ Very simple to implement
- ✅ Fast computation
- ✅ **Highly controllable** - can tune μ and σ to match target Sharpe
- ✅ Standard in finance
- ✅ No training required

**Cons:**
- ❌ Doesn't capture volatility clustering
- ❌ Assumes log-normal returns (not realistic)
- ❌ Missing fat tails

**Verdict:** ✅ **Good starting point** - Simple and controllable

---

#### E. PriceGenerator Library
**Source:** GitHub - Tim55667757/PriceGenerator

**Method:**
- Python library specifically for synthetic OHLCV generation
- Controls statistical parameters (trend, volatility, seasonality)
- Outputs Pandas DataFrame or CSV

**Features:**
- ✅ Candlestick generation (OHLCV)
- ✅ Control trend, volatility, noise
- ✅ Ready-to-use library
- ✅ Export to CSV for QuantConnect

**Verdict:** ✅ **Excellent tool** - Purpose-built for our use case

---

## Recommended Approach

### Phase 1: Hybrid GARCH-GBM with PriceGenerator

**Implementation Strategy:**

```python
# 1. Use PriceGenerator for base OHLCV structure
from pricegenerator import PriceGenerator

pg = PriceGenerator()
pg.Generate(
    ticker="SPY",
    start_date="2023-01-01",
    end_date="2024-12-31",
    days=730,

    # Control parameters to match target Sharpe
    trend=-0.15,  # Negative for -9.462 Sharpe
    volatility=0.20,  # 20% annual vol
    noise=0.05  # 5% noise
)

# 2. Add GARCH volatility clustering
from arch import arch_model

# Fit GARCH to returns
returns = pg.returns()
garch = arch_model(returns, vol='Garch', p=1, q=1)
garch_fit = garch.fit()

# Generate conditional volatility
cond_vol = garch_fit.conditional_volatility

# 3. Apply to prices
prices_adjusted = prices * (cond_vol / cond_vol.mean())

# 4. Validate statistics match target
sharpe = returns.mean() / returns.std() * np.sqrt(252)
# Tune parameters until sharpe ≈ -9.462
```

---

### Parameter Tuning to Match Backtest Results

**Target Metrics:**
- Sharpe Ratio: **-9.462**
- Total Trades: **6** (over 2-year period)
- Win Rate: **33%**

**Tuning Strategy:**

#### 1. Match Sharpe Ratio
```python
# Sharpe = (mean_return - risk_free) / std_return * sqrt(252)
# For Sharpe = -9.462:
# mean_return = -9.462 * std_return / sqrt(252)

target_sharpe = -9.462
annual_vol = 0.20  # 20% volatility

# Daily values
daily_std = annual_vol / np.sqrt(252)
daily_mean = target_sharpe * daily_std / np.sqrt(252)

# This gives us ~-2.38% daily return with 1.26% daily std
```

#### 2. Match Trade Count
```python
# Our momentum breakout strategy:
# - Lookback period: 20 days
# - Generates 6 trades in 2 years = ~3 trades/year

# To match this, ensure:
# - Strong trends with occasional reversals
# - Low volatility clustering (fewer false breakouts)
# - Controlled number of new highs

# Use PriceGenerator with:
periods = 20  # Match strategy lookback
up_moves_rare = True  # Only ~3 breakouts per year
```

#### 3. Match Win Rate
```python
# 33% win rate = 2 wins, 4 losses

# Generate data where:
# - Breakouts fail ~67% of the time
# - After breakout, price mean-reverts quickly

# Approach:
# - Use negative drift after detected breakout
# - Add mean reversion component
```

---

## Implementation Plan

### Step 1: Install Dependencies (5 min)
```bash
pip install PriceGenerator arch pandas numpy matplotlib
```

### Step 2: Generate Base Synthetic Data (15 min)
```python
# Script: generate_synthetic_spy.py

from pricegenerator import PriceGenerator
import pandas as pd

# Generate 2 years of daily data
pg = PriceGenerator()
df = pg.Generate(
    ticker="SPY",
    start_date="2023-01-01",
    end_date="2024-12-31",
    days=504,  # ~2 years of trading days

    # Initial parameters (will tune)
    init_price=400.0,
    trend=-0.002,  # -0.2% daily drift
    volatility=0.012,  # 1.2% daily vol (20% annual)
    max_close=450.0,
    min_close=350.0
)

df.to_csv("data/synthetic_spy_2023_2024.csv")
```

### Step 3: Add GARCH Volatility (20 min)
```python
from arch import arch_model
import numpy as np

# Load base data
df = pd.read_csv("data/synthetic_spy_2023_2024.csv")
returns = df['close'].pct_change().dropna()

# Fit GARCH(1,1)
model = arch_model(returns * 100, vol='Garch', p=1, q=1)
model_fit = model.fit(disp='off')

# Generate conditional volatility
cond_vol = model_fit.conditional_volatility / 100

# Apply to prices
df['close'] = df['close'] * (cond_vol / cond_vol.mean())
df['high'] = df['close'] * 1.01  # Rebuild OHLC
df['low'] = df['close'] * 0.99
df['open'] = df['close'].shift(1)
```

### Step 4: Validate Against Target Metrics (15 min)
```python
# Calculate actual metrics
returns = df['close'].pct_change()
sharpe = returns.mean() / returns.std() * np.sqrt(252)

print(f"Target Sharpe: -9.462")
print(f"Actual Sharpe: {sharpe:.3f}")

# Run momentum breakout strategy
trades = run_strategy(df)
print(f"Target Trades: 6")
print(f"Actual Trades: {len(trades)}")

# If metrics don't match, tune parameters and regenerate
```

### Step 5: Iterate Parameters (30 min)
```python
# Automated parameter search
from scipy.optimize import minimize

def objective(params):
    trend, vol = params
    df = generate_data(trend=trend, volatility=vol)
    sharpe = calculate_sharpe(df)
    trades = count_trades(df)

    # Minimize distance to target
    error = (sharpe - (-9.462))**2 + (trades - 6)**2
    return error

# Find optimal parameters
result = minimize(
    objective,
    x0=[-0.002, 0.012],
    method='Nelder-Mead'
)

optimal_trend, optimal_vol = result.x
```

### Step 6: Generate Final Dataset (10 min)
```python
# Use optimized parameters
df_final = generate_synthetic_data(
    trend=optimal_trend,
    volatility=optimal_vol,
    garch=True
)

# Export for QuantConnect format
df_final.to_csv(
    "data/synthetic_spy_matched.csv",
    columns=['date', 'open', 'high', 'low', 'close', 'volume']
)
```

---

## Alternative: Simple Parametric Approach

If PriceGenerator doesn't work well, use pure Geometric Brownian Motion with controlled parameters:

```python
import numpy as np
import pandas as pd

def generate_synthetic_ohlcv(
    days=504,
    initial_price=400.0,
    target_sharpe=-9.462,
    annual_vol=0.20,
    trades_per_year=3
):
    """
    Generate synthetic OHLCV data matching target statistics
    """
    # Calculate drift from target Sharpe
    daily_vol = annual_vol / np.sqrt(252)
    daily_drift = target_sharpe * daily_vol / np.sqrt(252)

    # Generate price path
    returns = np.random.normal(
        daily_drift,
        daily_vol,
        days
    )

    prices = initial_price * np.exp(np.cumsum(returns))

    # Generate OHLC from close prices
    # High = close + random(0, 2%)
    # Low = close - random(0, 2%)
    # Open = previous close + small noise

    high = prices * (1 + np.abs(np.random.normal(0, 0.01, days)))
    low = prices * (1 - np.abs(np.random.normal(0, 0.01, days)))
    open_ = np.roll(prices, 1) * (1 + np.random.normal(0, 0.002, days))
    volume = np.random.uniform(50_000_000, 150_000_000, days)

    df = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=days, freq='D'),
        'open': open_,
        'high': high,
        'low': low,
        'close': prices,
        'volume': volume
    })

    return df

# Generate and validate
df = generate_synthetic_ohlcv()
sharpe = calculate_sharpe(df)
print(f"Generated Sharpe: {sharpe:.3f}")
```

---

## Validation Checklist

Before using synthetic data in walkforward testing:

- [ ] **Sharpe ratio matches target** (within ±10%)
- [ ] **Trade count matches** (within ±2 trades)
- [ ] **Win rate matches** (within ±10%)
- [ ] **Price range realistic** (350-450 for SPY)
- [ ] **No data anomalies** (gaps, zeros, negatives)
- [ ] **Volume present** (even if random)
- [ ] **Date continuity** (no missing days)
- [ ] **OHLC consistency** (High >= Open/Close/Low, Low <= all)

---

## Expected Benefits

### 1. Full Pipeline Automation
- Test walkforward logic without API costs
- Unlimited iterations for development
- Fast feedback loop (seconds vs minutes)

### 2. Validation Confidence
- Know framework works BEFORE hitting QC API
- Debug issues locally
- Catch bugs early

### 3. Reproducibility
- Fixed random seed = identical results
- Compare runs consistently
- Share test data with team

### 4. Cost Savings
- $0 for unlimited local tests
- Only use QC API when confident
- Avoid wasted backtest credits

---

## Next Steps

1. ✅ Research complete
2. ⏳ Implement PriceGenerator approach (1 hour)
3. ⏳ Add GARCH volatility clustering (30 min)
4. ⏳ Tune parameters to match -9.462 Sharpe (1 hour)
5. ⏳ Generate final synthetic dataset
6. ⏳ Run walkforward wrapper with synthetic data
7. ⏳ Validate results match expectations
8. ⏳ Document generation process
9. ⏳ Test with real QC backtest for comparison

**Total Estimated Time:** 4-5 hours

---

## References

1. **Diffusion Models:** "Generation of synthetic financial time series by diffusion models" (Quantitative Finance, 2025)
2. **TimeGAN:** "Time-series Generative Adversarial Networks" (NeurIPS)
3. **GARCH Bootstrap:** "Bootstrap prediction for returns and volatilities in GARCH models" (ScienceDirect)
4. **PriceGenerator:** GitHub - Tim55667757/PriceGenerator
5. **GBM:** Standard textbooks on quantitative finance

---

**Report Status:** ✅ Complete
**Recommendation:** Implement Hybrid GARCH-GBM with PriceGenerator
**Priority:** HIGH - Blocks full automation
**Next Action:** Start implementation (Step 1)
