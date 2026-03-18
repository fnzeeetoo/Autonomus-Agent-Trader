"""TBT Divergence strategy – price/time divergence between asset and meta-indicator."""

import numpy as np
from typing import Dict, Any
from ...core.risk import RiskEngine
from ...core.execution import ExecutionEngine
from ...core.portfolio import Portfolio
from ...core.monitor import Monitor


class TBTDivergenceStrategy:
    """TBT Divergence strategy."""

    def __init__(self, config: Dict[str, Any], risk_engine: RiskEngine, executor: ExecutionEngine, portfolio: Portfolio, monitor: Monitor):
        self.config = config
        self.risk_engine = risk_engine
        self.executor = executor
        self.portfolio = portfolio
        self.monitor = monitor
        self.indicator_period = config.get("indicator_period", 14)
        self.divergence_threshold = config.get("divergence_threshold", 0.05)
        self.close_history = []
        self.indicator_history = []

    def process_tick(self, tick: Dict[str, Any], indicator_value: float):
        """Process a new tick with an external meta-indicator value."""
        self.close_history.append(tick["price"])
        self.indicator_history.append(indicator_value)
        # Keep limited window
        if len(self.close_history) > self.indicator_period + 10:
            self.close_history = self.close_history[-(self.indicator_period + 10):]
            self.indicator_history = self.indicator_history[-(self.indicator_period + 10):]

        if len(self.close_history) < self.indicator_period:
            return

        # Compute price change over lookback
        lookback = self.indicator_period
        price_change = (self.close_history[-1] - self.close_history[-lookback]) / self.close_history[-lookback]
        indicator_change = (self.indicator_history[-1] - self.indicator_history[-lookback]) / max(1, abs(self.indicator_history[-lookback]))

        # Detect divergence: price and indicator move in opposite directions beyond threshold
        if abs(price_change) > self.divergence_threshold and abs(indicator_change) > self.divergence_threshold:
            if price_change > 0 and indicator_change < -self.divergence_threshold:
                # Price up, indicator down -> bearish divergence -> sell
                side = "sell"
                cash_size = self.risk_engine.calculate_position_size(tick["price"], tick["price"] * 1.02)
                qty = cash_size / tick["price"]
                self.executor.simulate_fill(tick["symbol"], side, qty, tick["price"])
            elif price_change < 0 and indicator_change > self.divergence_threshold:
                # Price down, indicator up -> bullish divergence -> buy
                side = "buy"
                cash_size = self.risk_engine.calculate_position_size(tick["price"], tick["price"] * 0.98)
                qty = cash_size / tick["price"]
                self.executor.simulate_fill(tick["symbol"], side, qty, tick["price"])

        # Note: The indicator must be supplied from external source (e.g., sentiment model)
        # For testing, a simple moving average of price could be used as a stand-in.
