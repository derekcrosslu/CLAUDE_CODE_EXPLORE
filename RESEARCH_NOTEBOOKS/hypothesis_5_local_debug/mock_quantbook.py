"""
Mock QuantConnect QuantBook API for local testing
This allows us to run the exact QC notebook code locally
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class MockSymbol:
    """Mock QuantConnect Symbol"""
    def __init__(self, ticker):
        self.ticker = ticker
        self.Value = ticker

    def __repr__(self):
        return f"Symbol({self.ticker})"

    def __str__(self):
        return self.ticker


class MockSecurity:
    """Mock QuantConnect Security"""
    def __init__(self, ticker):
        self.Symbol = MockSymbol(ticker)
        self.ticker = ticker


class Resolution:
    """Mock Resolution enum"""
    Daily = "Daily"
    Hour = "Hour"
    Minute = "Minute"


class QuantBook:
    """
    Mock QuantConnect QuantBook for local testing
    Generates synthetic price data that mimics real QC History API
    """

    def __init__(self):
        self.securities = {}
        print("✓ Mock QuantBook initialized (local testing mode)")

    def AddEquity(self, ticker, resolution=Resolution.Daily):
        """Add equity security (mock)"""
        security = MockSecurity(ticker)
        self.securities[ticker] = security
        return security

    def History(self, symbols, start_date, end_date, resolution=Resolution.Daily):
        """
        Mock History method that returns DataFrame in same format as QC

        Returns multi-index DataFrame: (symbol, time) -> columns
        """
        if not isinstance(symbols, list):
            symbols = [symbols]

        # Extract tickers
        tickers = []
        for sym in symbols:
            if isinstance(sym, MockSymbol):
                tickers.append(sym.ticker)
            elif isinstance(sym, str):
                tickers.append(sym)
            else:
                tickers.append(str(sym))

        if len(tickers) == 0:
            return pd.DataFrame()

        # Generate date range (business days only)
        dates = pd.bdate_range(start=start_date, end=end_date)

        if len(dates) == 0:
            return pd.DataFrame()

        # Generate synthetic price data for each ticker
        all_data = []

        for ticker in tickers:
            # Use ticker hash as seed for reproducibility
            seed = hash(ticker) % 10000
            np.random.seed(seed)

            n_days = len(dates)

            # Generate realistic-looking prices with trend + noise
            base_price = 50 + (hash(ticker) % 100)
            trend = np.linspace(0, 5, n_days)
            noise = np.random.randn(n_days).cumsum() * 0.5
            prices = base_price + trend + noise

            # Ensure prices stay positive
            prices = np.maximum(prices, 1.0)

            # Generate OHLC data
            for i, date in enumerate(dates):
                open_price = prices[i] * (1 + np.random.randn() * 0.001)
                close_price = prices[i]
                high_price = max(open_price, close_price) * (1 + abs(np.random.randn()) * 0.005)
                low_price = min(open_price, close_price) * (1 - abs(np.random.randn()) * 0.005)
                volume = int(1000000 + np.random.randn() * 100000)

                all_data.append({
                    'symbol': MockSymbol(ticker),
                    'time': pd.Timestamp(date),
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume
                })

        # Create DataFrame with multi-index like QC
        df = pd.DataFrame(all_data)
        df = df.set_index(['symbol', 'time'])

        return df


# Mock QuantConnect imports so notebook can import them
class QuantConnect:
    """Mock QuantConnect module"""
    pass


print("✓ Mock QuantConnect API loaded")
