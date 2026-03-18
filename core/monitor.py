"""Monitoring and alerting."""

import json
from datetime import datetime, timedelta
from typing import Optional, List
from .portfolio import Portfolio
from .risk import RiskEngine


class Monitor:
    """Generates alerts based on portfolio and risk state."""

    def __init__(self, portfolio: Portfolio, risk_engine: RiskEngine, discord_webhook_alerts: Optional[str] = None, discord_webhook_daily: Optional[str] = None):
        self.portfolio = portfolio
        self.risk_engine = risk_engine
        self.discord_webhook_alerts = discord_webhook_alerts
        self.discord_webhook_daily = discord_webhook_daily
        self.last_daily_summary_date: Optional[datetime.date] = None
        self.peak_equity = portfolio.initial_capital
        self.max_drawdown_pct = 0.0

    def check_and_alert(self) -> List[str]:
        """Run checks and return a list of alert messages."""
        alerts = []
        equity = self.portfolio.total_equity()
        # Update peak and drawdown
        if equity > self.peak_equity:
            self.peak_equity = equity
        dd_pct = (self.peak_equity - equity) / self.peak_equity * 100
        if dd_pct > self.max_drawdown_pct:
            self.max_drawdown_pct = dd_pct
            if dd_pct >= 10.0:
                alerts.append(f"⚠️ Drawdown warning: {dd_pct:.1f}% from peak")

        # Circuit breaker
        if self.risk_engine.circuit_triggered:
            alerts.append("🛑 Circuit breaker triggered! Trading halted.")

        # Check consecutive losses (redundant with circuit but may want separate)
        if self.risk_engine.consecutive_losses >= self.risk_engine.config.circuit_breaker_losses:
            alerts.append(f"🔴 {self.risk_engine.consecutive_losses} consecutive losses.")

        # Daily summary
        today = datetime.utcnow().date()
        if self.last_daily_summary_date != today:
            # Time to send daily summary (at end of day)
            self.last_daily_summary_date = today
            # Build summary
            realized = self.portfolio.realized_pnl
            unrealized = self.portfolio.total_unrealized_pnl()
            total = realized + unrealized
            summary = (
                f"📈 Daily P&L Summary\n"
                f"Realized: ${realized:.2f}\n"
                f"Unrealized: ${unrealized:.2f}\n"
                f"Total: ${total:.2f}\n"
                f"Equity: ${equity:.2f}\n"
                f"Drawdown: {dd_pct:.1f}%"
            )
            alerts.append(f"DAILY_SUMMARY|{summary}")

        return alerts

    async def send_discord(self, message: str):
        """Send a message to Discord via webhook."""
        import httpx
        if not self.discord_webhook_alerts and not self.discord_webhook_daily:
            return
        wh = self.discord_webhook_alerts if "DAILY_SUMMARY" not in message else self.discord_webhook_daily
        if not wh:
            return
        async with httpx.AsyncClient() as client:
            await client.post(wh, json={"content": message})

    def persist_state(self, path: str = "data/monitor_state.json"):
        """Save monitor state to file."""
        state = {
            "peak_equity": self.peak_equity,
            "max_drawdown_pct": self.max_drawdown_pct,
            "last_daily_summary_date": self.last_daily_summary_date.isoformat() if self.last_daily_summary_date else None
        }
        with open(path, "w") as f:
            json.dump(state, f, indent=2)

    def load_state(self, path: str = "data/monitor_state.json"):
        """Load monitor state from file."""
        import os
        if not os.path.exists(path):
            return
        with open(path, "r") as f:
            state = json.load(f)
        self.peak_equity = state.get("peak_equity", self.portfolio.initial_capital)
        self.max_drawdown_pct = state.get("max_drawdown_pct", 0.0)
        ld = state.get("last_daily_summary_date")
        if ld:
            self.last_daily_summary_date = datetime.date.fromisoformat(ld)
