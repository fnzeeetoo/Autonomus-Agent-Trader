"""Late Entry strategy – wait for favorite to be decided in final minutes before market close, enter when odds stabilize."""

import numpy as np
from datetime import datetime, time
from typing import Dict, Any
from ...core.risk import RiskEngine
from ...core.execution import ExecutionEngine
from ...core.portfolio import Portfolio
from ...core.monitor import Monitor


class LateEntryStrategy:
    """Late Entry strategy."""

    def __init__(self, config: Dict[str, Any], risk_engine: RiskEngine, executor: ExecutionEngine, portfolio: Portfolio, monitor: Monitor):
        self.config = config
        self.risk_engine = risk_engine
        self.executor = executor
        self.portfolio = portfolio
        self.monitor = monitor
        self.entry_minutes_before_close = config.get("entry_minutes_before_close", 15)
        self.stability_window = config.get("stability_window", 5)
        self.price_changes = []
        self.in_position = False

    def process_tick(self, tick: Dict[str, Any]):
        """Process tick data."""
        # Determine if we are near market close (assume a 24-hour market with close at 23:59 UTC, or use actual market hours)
        # For Polymarket, markets close at a specific time; we'll treat tick time as hint.
        # In a real implementation, we'd parse market end time from tick metadata.
        tick_time = datetime.fromtimestamp(tick.get("timestamp", 0))
        # For demo, we define "close" as 23:00 UTC; adjustable.
        market_close_hour = 23
        minutes_to_close = (market_close_hour - tick_time.hour) * 60 + (60 - tick_time.minute)
        if minutes_to_close > self.entry_minutes_before_close:
            return  # Too early

        # Track recent price changes to assess stability
        if not hasattr(self, 'last_price'):
            self.last_price = tick["price"]
            return
        change_pct = abs(tick["price"] - self.last_price) / self.last_price
        self.last_price = tick["price"]
        self.price_changes.append(change_pct)
        if len(self.price_changes) > self.stability_window:
            self.price_changes = self.price_changes[-self.stability_window:]

        avg_change = np.mean(self.price_changes) if self.price_changes else 0

        # If volatility is low (stable), and we are not in position, enter long (bet on favorite)
        if not self.in_position and avg_change < 0.001:  # less than 0.1% change in recent ticks
            side = "buy"
            cash_size = self.risk_engine.calculate_position_size(tick["price"], tick["price"] * 0.98)
            qty = cash_size / tick["price"]
            self.executor.simulate_fill(tick["symbol"], side, qty, tick["price"])
            self.in_position = True

        # If we are in position and close time arrived, exit
        if self.in_position and minutes_to_close <= 0:
            # Close position at market
            # For simplicity, we assume the portfolio holds one position; close all
            for pos in self.portfolio.get_all_positions():
                self.portfolio.close_position(pos.id, tick["price"])
            self.in_position = False
