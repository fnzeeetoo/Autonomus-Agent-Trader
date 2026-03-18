"""Data loader for backtesting. Supports CSV and SQLite."""

import pandas as pd
import sqlite3
from typing import Optional, Generator
from datetime import datetime


class DataLoader:
    """Loads historical market data."""

    def __init__(self, source: str):
        """
        source: path to CSV file or SQLite database.
        If SQLite, expects a table named 'market_data' with columns: timestamp, open, high, low, close, volume.
        """
        self.source = source

    def load(self) -> pd.DataFrame:
        """Load all data into a DataFrame."""
        if self.source.endswith(".csv"):
            df = pd.read_csv(self.source, parse_dates=["timestamp"])
        elif self.source.endswith(".db") or self.source.endswith(".sqlite"):
            conn = sqlite3.connect(self.source)
            df = pd.read_sql_query("SELECT * FROM market_data ORDER BY timestamp", conn, parse_dates=["timestamp"])
            conn.close()
        else:
            raise ValueError(f"Unsupported data source: {self.source}")
        # Ensure required columns
        required = ["timestamp", "open", "high", "low", "close", "volume"]
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")
        return df

    def iterate_ticks(self) -> Generator[dict, None, None]:
        """Yield ticks one by one in chronological order."""
        df = self.load()
        df = df.sort_values("timestamp")
        for _, row in df.iterrows():
            tick = {
                "symbol": "POLYMARKET",  # default symbol, could be from data
                "timestamp": row["timestamp"].to_pydatetime(),
                "price": float(row["close"]),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "volume": float(row["volume"])
            }
            yield tick
