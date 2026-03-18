"""Execution engine – simulates fills and can integrate with web3 for live trading."""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import numpy as np
from .portfolio import Position, Portfolio


class ExecutionEngine:
    """Handles order submission, filling, and lifetime tracking."""

    def __init__(self, portfolio: Portfolio, paper_trading: bool = True):
        self.portfolio = portfolio
        self.paper_trading = paper_trading
        self.fills = []  # List of fill dictionaries

    def submit_market_order(self, symbol: str, side: str, quantity: float, price: float) -> Dict[str, Any]:
        """
        Submit a market order.
        Returns a fill record.
        """
        fill = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "type": "market"
        }
        self.portfolio.apply_fill(fill)
        self.fills.append(fill)
        return fill

    def simulate_fill(self, symbol: str, side: str, quantity: float, price: float, slippage_bps: float = 0) -> Dict[str, Any]:
        """In paper trading, optionally add slippage."""
        if slippage_bps > 0:
            if side == "buy":
                price *= 1 + slippage_bps / 10000
            else:
                price *= 1 - slippage_bps / 10000
        return self.submit_market_order(symbol, side, quantity, price)

    def get_recent_fills(self, since: Optional[datetime] = None) -> list:
        if since is None:
            return self.fills[-100:]
        return [f for f in self.fills if datetime.fromisoformat(f["timestamp"].replace("Z", "")) >= since]
