"""Contrarian strategy – bet against crowd panic with momentum divergence."""

import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional
from ...core.risk import RiskEngine
from ...core.execution import ExecutionEngine
from ...core.portfolio import Portfolio
from ...core.monitor import Monitor


class ContrarianStrategy:
    """Contrarian trading strategy."""

    def __init__(self, config: Dict[str, Any], risk_engine: RiskEngine, executor: ExecutionEngine, portfolio: Portfolio, monitor: Monitor):
        self.config = config
        self.risk_engine = risk_engine
        self.executor = executor
        self.portfolio = portfolio
        self.monitor = monitor
        # Strategy parameters
        self.rsi_period = config.get("rsi_period", 14)
        self.rsi_overbought = config.get("rsi_overbought", 70)
        self.rsi_oversold = config.get("rsi_oversold", 30)
        self.panic_volume_multiplier = config.get("panic_volume_multiplier", 2.0)
        # Indicators cache
        self.close_history = []
        self.volume_history = []

    def process_tick(self, tick: Dict[str, Any]):
        """Process a new market tick."""
        # Append to history
        self.close_history.append(tick["price"])
        self.volume_history.append(tick["volume"])
        # Keep enough for RSI (need period+1)
        if len(self.close_history) > max(self.rsi_period, 20) + 10:
            self.close_history = self.close_history[-(max(self.rsi_period, 20) + 10):]
            self.volume_history = self.volume_history[-(max(self.rsi_period, 20) + 10):]

        if len(self.close_history) < self.rsi_period + 1:
            return

        # Compute RSI
        closes = np.array(self.close_history)
        deltas = np.diff(closes)
        up = np.where(deltas > 0, deltas, 0)
        down = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(up[-self.rsi_period:])
        avg_loss = np.mean(down[-self.rsi_period:])
        if avg_loss == 0:
            rsi = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        # Compute ATR (14 period)
        highs = np.array([tick.get("high", tick["price"]) for tick in self.close_history[-14:]])  # simplify using price
        lows = np.array([tick.get("low", tick["price"]) for tick in self.close_history[-14:]])
        # For demo, use close as high/low if not provided
        atr = np.mean(highs - lows) if len(highs) == len(lows) else (closes[-1] - closes[-14]) / 14

        # Volume check: recent volume spike vs average
        recent_volume = tick["volume"]
        avg_volume = np.mean(self.volume_history[:-1]) if len(self.volume_history) > 1 else recent_volume
        volume_spike = recent_volume > avg_volume * self.panic_volume_multiplier

        # Momentum divergence: price makes new low but RSI higher (or vice versa)
        # We compare current price to recent min and RSI to recent min
        if len(closes) >= 5:
            recent_min_price = np.min(closes[-5:])
            recent_max_price = np.max(closes[-5:])
            recent_min_rsi = np.min([self._compute_rsi_at_index(i) for i in range(-5, 0)])
            recent_max_rsi = np.max([self._compute_rsi_at_index(i) for i in range(-5, 0)])
            bullish_div = (closes[-1] <= recent_min_price and rsi > recent_min_rsi * 1.1) or (closes[-1] >= recent_max_price and rsi < recent_max_rsi * 0.9)
        else:
            bullish_div = False

        # Determine regime
        adx = 30  # placeholder (would compute actual ADX)
        bollinger_width = 1.5  # placeholder
        median_width = 1.0
        if not self.risk_engine.check_regime(adx, bollinger_width, median_width):
            return

        # Entry signals
        if volume_spike and bullish_div:
            # Determine direction: if RSI oversold and price new low -> long; if overbought and new high -> short
            if rsi < self.rsi_oversold and closes[-1] <= recent_min_price:
                side = "buy"
            elif rsi > self.rsi_overbought and closes[-1] >= recent_max_price:
                side = "sell"
            else:
                return
            # Position size
            cash_size = self.risk_engine.calculate_position_size(tick["price"], tick["price"] - atr if side == "buy" else tick["price"] + atr)
            qty = cash_size / tick["price"]
            # Submit order
            fill = self.executor.simulate_fill(tick["symbol"], side, qty, tick["price"])
            # Set stop? We'll track for exit
            # For simplicity, we'll let the paper trader exit on opposite signal or after N ticks.
            # In production, need proper position tracking and exit logic.
            # For MVP demo, we'll let the paper trader exit on opposite signal or after a fixed distance.
        # Exit: trailing stop at 2x ATR from highest high since entry (for long). Need position tracking.
        # We'll handle exits in a separate pass or via separate module.

    def _compute_rsi_at_index(self, idx_offset: int) -> float:
        """Compute RSI from close_history at offset from end."""
        if len(self.close_history) < self.rsi_period + 1:
            return 50.0
        # Get slice up to that index (idx_offset negative)
        closes = self.close_history[:idx_offset] if idx_offset < 0 else self.close_history
        if len(closes) < self.rsi_period + 1:
            return 50.0
        last_n = closes[-self.rsi_period-1:]
        deltas = np.diff(last_n)
        up = np.where(deltas > 0, deltas, 0)
        down = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(up)
        avg_loss = np.mean(down)
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
