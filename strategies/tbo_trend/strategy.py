"""TBO Trend strategy – follow momentum using custom indicator."""

import numpy as np
from typing import Dict, Any
from ...core.risk import RiskEngine
from ...core.execution import ExecutionEngine
from ...core.portfolio import Portfolio
from ...core.monitor import Monitor


class TBOTrendStrategy:
    """TBO Trend strategy."""

    def __init__(self, config: Dict[str, Any], risk_engine: RiskEngine, executor: ExecutionEngine, portfolio: Portfolio, monitor: Monitor):
        self.config = config
        self.risk_engine = risk_engine
        self.executor = executor
        self.portfolio = portfolio
        self.monitor = monitor
        self.fast_period = config.get("fast_period", 10)
        self.slow_period = config.get("slow_period", 30)
        self.close_history = []

    def process_tick(self, tick: Dict[str, Any]):
        """Process a new tick."""
        self.close_history.append(tick["price"])
        if len(self.close_history) > self.slow_period + 10:
            self.close_history = self.close_history[-(self.slow_period + 10):]

        if len(self.close_history) < self.slow_period:
            return

        # Compute fast and slow simple moving averages
        fast_sma = np.mean(self.close_history[-self.fast_period:])
        slow_sma = np.mean(self.close_history[-self.slow_period:])

        # Regime filter
        adx = 30  # placeholder
        bollinger_width = 1.5
        median_width = 1.0
        if not self.risk_engine.check_regime(adx, bollinger_width, median_width):
            return

        # Entry: fast crosses above slow -> long; fast crosses below slow -> short
        # Need previous state to detect crossover
        if not hasattr(self, 'prev_fast_sma'):
            self.prev_fast_sma = fast_sma
            self.prev_slow_sma = slow_sma
            return

        # Long crossover
        if self.prev_fast_sma <= self.prev_slow_sma and fast_sma > slow_sma:
            side = "buy"
            cash_size = self.risk_engine.calculate_position_size(tick["price"], tick["price"] * 0.98)
            qty = cash_size / tick["price"]
            self.executor.simulate_fill(tick["symbol"], side, qty, tick["price"])
        # Short crossover
        elif self.prev_fast_sma >= self.prev_slow_sma and fast_sma < slow_sma:
            side = "sell"
            cash_size = self.risk_engine.calculate_position_size(tick["price"], tick["price"] * 1.02)
            qty = cash_size / tick["price"]
            self.executor.simulate_fill(tick["symbol"], side, qty, tick["price"])

        self.prev_fast_sma = fast_sma
        self.prev_slow_sma = slow_sma

        # Exit: reverse signal or trailing stop can be added
