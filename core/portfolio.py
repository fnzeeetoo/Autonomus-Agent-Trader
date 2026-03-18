"""Portfolio – tracks positions and P&L."""

from typing import List, Dict, Optional
from datetime import datetime
import uuid


class Position:
    """Represents an open position."""

    def __init__(self, symbol: str, quantity: float, entry_price: float, side: str):
        self.id = str(uuid.uuid4())
        self.symbol = symbol
        self.quantity = quantity
        self.entry_price = entry_price
        self.side = side  # "long" or "short"
        self.current_price = entry_price
        self.entry_time = datetime.utcnow()

    def update_price(self, price: float):
        """Update current market price."""
        self.current_price = price

    def unrealized_pnl(self) -> float:
        """Calculate unrealized P&L."""
        if self.side == "long":
            return (self.current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.current_price) * self.quantity

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "side": self.side,
            "current_price": self.current_price,
            "entry_time": self.entry_time.isoformat() + "Z",
            "unrealized_pnl": self.unrealized_pnl()
        }


class Portfolio:
    """Tracks all positions and realized P&L."""

    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}  # by id
        self.realized_pnl = 0.0
        self.trade_history: List[dict] = []

    def apply_fill(self, fill: dict):
        """Handle a fill from execution engine. Updates positions and cash."""
        symbol = fill["symbol"]
        side = fill["side"]
        quantity = fill["quantity"]
        price = fill["price"]

        if side == "buy":
            # Opening a long or closing a short? For simplicity, treat as open long.
            # In production, order management would handle position flattening/hedging.
            # We'll just create a new long position.
            pos = Position(symbol, quantity, price, "long")
            self.positions[pos.id] = pos
            self.cash -= quantity * price
        elif side == "sell":
            # If we have no positions, this could be a short sale. For simplicity, treat as opening short.
            pos = Position(symbol, quantity, price, "short")
            self.positions[pos.id] = pos
            self.cash += quantity * price
        else:
            raise ValueError(f"Unknown side: {side}")

        # Record the trade
        trade = {
            "id": fill["id"],
            "timestamp": fill["timestamp"],
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "type": fill["type"],
            "position_id": pos.id
        }
        self.trade_history.append(trade)

    def get_position(self, position_id: str) -> Optional[Position]:
        return self.positions.get(position_id)

    def get_all_positions(self) -> List[Position]:
        return list(self.positions.values())

    def update_prices(self, price_map: Dict[str, float]):
        """Update current prices for all positions."""
        for pos in self.positions.values():
            if pos.symbol in price_map:
                pos.update_price(price_map[pos.symbol])

    def total_unrealized_pnl(self) -> float:
        return sum(p.unrealized_pnl() for p in self.positions.values())

    def total_equity(self) -> float:
        return self.cash + self.total_unrealized_pnl() + self.realized_pnl

    def close_position(self, position_id: str, price: float) -> float:
        """Close a position and return realized P&L."""
        pos = self.positions.get(position_id)
        if not pos:
            raise KeyError(f"Position {position_id} not found")
        pnl = pos.unrealized_pnl()
        self.realized_pnl += pnl
        # Adjust cash
        if pos.side == "long":
            self.cash += pos.quantity * price
        else:
            self.cash -= pos.quantity * price
        # Remove position
        del self.positions[position_id]
        return pnl

    def to_dict(self) -> dict:
        return {
            "cash": self.cash,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.total_unrealized_pnl(),
            "equity": self.total_equity(),
            "positions": [p.to_dict() for p in self.positions.values()],
            "trade_count": len(self.trade_history)
        }
