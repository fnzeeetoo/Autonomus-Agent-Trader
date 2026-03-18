"""Risk management engine."""

from dataclasses import dataclass
from typing import List
import datetime


@dataclass
class RiskConfig:
    """Risk configuration."""
    position_sizing_fixed: float = 20.0  # Fixed $ per trade
    position_sizing_pct: float = 0.02   # 2% of capital
    circuit_breaker_losses: int = 3     # Consecutive losses to trigger
    daily_loss_limit: float = -100.0    # Daily loss limit in USD
    adx_threshold: float = 25.0         # Minimum ADX for trend
    bollinger_volatility_cap: float = 2.0  # Max BB width (multiple of median)


class RiskEngine:
    """Manages position sizing and risk limits."""

    def __init__(self, config: RiskConfig, initial_capital: float = 10000.0):
        self.config = config
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.consecutive_losses = 0
        self.daily_pnl = 0.0
        self.daily_reset_date = datetime.date.today()
        self.circuit_triggered = False
        self.regime_filter_active = True

    def reset_daily(self):
        """Reset daily P&L at start of new day."""
        today = datetime.date.today()
        if today != self.daily_reset_date:
            self.daily_pnl = 0.0
            self.daily_reset_date = today

    def calculate_position_size(self, entry_price: float, stop_price: float) -> float:
        """
        Calculate position size in cash amount.
        Uses fixed $20 or 2% of current capital, whichever is smaller.
        Returns cash amount to allocate.
        """
        fixed = self.config.position_sizing_fixed
        pct = self.current_capital * self.config.position_sizing_pct
        size = min(fixed, pct)
        # Ensure size is at least enough for 1 unit
        return max(size, entry_price)

    def record_trade_result(self, pnl: float):
        """Record trade result for circuit breaker and daily limits."""
        self.reset_daily()
        self.daily_pnl += pnl
        if pnl < 0:
            self.consecutive_losses += 1
            if self.consecutive_losses >= self.config.circuit_breaker_losses:
                self.circuit_triggered = True
        else:
            self.consecutive_losses = 0

        if self.daily_pnl <= self.config.daily_loss_limit:
            self.circuit_triggered = True

    def check_regime(self, adx: float, bollinger_width: float, median_width: float) -> bool:
        """
        Check if market regime is acceptable for trading.
        Requires ADX > threshold and volatility not too high.
        """
        if not self.regime_filter_active:
            return True
        if adx < self.config.adx_threshold:
            return False
        if bollinger_width > self.config.bollinger_volatility_cap * median_width:
            return False
        return True

    def can_trade(self) -> bool:
        """Check if trading is allowed (circuit breaker not triggered)."""
        return not self.circuit_triggered

    def reset_circuit(self):
        """Allow trading again (manual reset)."""
        self.circuit_triggered = False
        self.consecutive_losses = 0

    def update_capital(self, pnl: float):
        """Update current capital after a trade."""
        self.current_capital += pnl
        self.record_trade_result(pnl)
