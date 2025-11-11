from AlgorithmImports import *

class RSIMeanReversionStrategy(QCAlgorithm):
    """
    RSI Mean Reversion Strategy

    Hypothesis: Buy when RSI < 30 (oversold), sell when RSI > 70 (overbought)

    Entry: RSI crosses below 30 (oversold condition)
    Exit: RSI crosses above 70 (overbought condition) OR stop loss

    Parameters:
    - RSI Period: 14
    - Oversold Threshold: 30
    - Overbought Threshold: 70
    - Position Size: 100% of portfolio
    """

    def Initialize(self):
        # Set date range for backtest
        self.SetStartDate(2023, 1, 1)
        self.SetEndDate(2024, 12, 31)

        # Set initial cash
        self.SetCash(100000)

        # Add equity data
        self.symbol = self.AddEquity("SPY", Resolution.Daily).Symbol

        # Create RSI indicator
        self.rsi_period = 14
        self.rsi = self.RSI(self.symbol, self.rsi_period, Resolution.Daily)

        # RSI thresholds
        self.oversold_threshold = 30
        self.overbought_threshold = 70

        # Track position
        self.is_long = False

        # Warm up RSI indicator
        self.SetWarmUp(self.rsi_period, Resolution.Daily)

    def OnData(self, data: Slice):
        # Skip during warmup period
        if self.IsWarmingUp:
            return

        # Check if we have data
        if not data.ContainsKey(self.symbol):
            return

        bar = data[self.symbol]
        if bar is None:
            return

        # Check if RSI is ready
        if not self.rsi.IsReady:
            return

        rsi_value = self.rsi.Current.Value

        # Entry signal: RSI crosses below oversold threshold
        if not self.is_long and rsi_value < self.oversold_threshold:
            self.SetHoldings(self.symbol, 1.0)
            self.is_long = True
            self.Debug(f"{self.Time}: BUY - RSI {rsi_value:.2f} < {self.oversold_threshold} (Oversold)")

        # Exit signal: RSI crosses above overbought threshold
        elif self.is_long and rsi_value > self.overbought_threshold:
            self.Liquidate(self.symbol)
            self.is_long = False
            self.Debug(f"{self.Time}: SELL - RSI {rsi_value:.2f} > {self.overbought_threshold} (Overbought)")

    def OnEndOfAlgorithm(self):
        self.Debug(f"Final Portfolio Value: ${self.Portfolio.TotalPortfolioValue:,.2f}")
