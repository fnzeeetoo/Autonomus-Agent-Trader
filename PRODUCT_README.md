# AgentTrader Product Summary

## What Is AgentTrader?
AgentTrader is an autonomous trading system for Polymarket, featuring four distinct strategies, a robust risk engine, backtesting capabilities, and a live paper‑trading loop with Discord alerts. It is designed to run as a long‑running OpenClaw agent.

## Components Delivered

### Core (`core/`)
- **risk.py** – Position sizing, circuit breaker, daily loss limit, regime filter.
- **execution.py** – Order simulation and fill tracking.
- **portfolio.py** – Position management and P&L.
- **monitor.py** – Alerting and state persistence.

### Strategies (`strategies/`)
1. **Contrarian** – Enters against crowd panic with momentum divergence; exits with 2× ATR trailing stop.
2. **TBO Trend** – Dual‑period SMA crossover following momentum.
3. **TBT Divergence** – Price/indicator divergence detector.
4. **Late Entry** – Enters in final minutes before market close when odds stabilize.

### Backtester (`backtester/`)
- CSV/SQLite data loader.
- Metrics: Sharpe, max drawdown, win rate, profit factor, Calmar.
- Monte Carlo simulation (bootstrap returns).

### Dashboard (`dashboard/`)
- Next.js 14 app with Tailwind and Recharts.
- Pages: `/` (equity curve), `/trades` (blotter), `/config` (strategy & risk config).
- API routes for reading data and updating configuration YAML.
- Deployable to Vercel (includes `vercel.json`).

### Bot (`bot/`)
- Heartbeat registration for OpenClaw.
- Discord webhook alerts (circuit breaker, daily summary, drawdown warnings).

### Configuration (`config/`)
- `strategies.yaml` – enable/disable strategies and tune parameters.
- `risk.yaml` – risk limits and regime thresholds.

### Data (`data/`)
- `paper_trades/` – live equity curve and trades JSON during paper trading.
- `live_trades/` – reserved for future live trading.

## Outstandings / Future Work

- **Live Trading** – Integration with Polygon RPC and wallet signing is scaffolded but not enabled; requires secure key management and thorough testing.
- **Data Persistence** – Dashboard uses local JSON files; production should switch to a database (PostgreSQL/SQLite) for reliability.
- **Alerting** – Discord webhook placeholders; need actual webhook URLs and possibly richer message formatting.
- **Deployment** – Dashboard is ready for Vercel; environment variables `NEXT_PUBLIC_API_BASE` may be needed if API routes change.
- **Strategy Refinement** – TBT Divergence currently shows lower Sharpe; could benefit from a more predictive meta‑indicator.
- **Testing** – Unit tests for strategies and core modules are minimal; expand coverage.

## Quick Start

```bash
# Python backtester / paper trader
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m backtester.engine --data data/market_data.csv --config config/strategies.yaml --risk config/risk.yaml --output reports/backtest_6m.md

# Dashboard
cd dashboard
npm install
npm run dev
```

See `README.md` for full details.
