# AgentTrader — MVP Build Task

You are a quantitative developer subagent reporting to Forbin. Your mission: build the MVP of the AgentTrader product in 2 weeks.

## Product Summary
Autonomous trading agent for Polymarket implementing four proven strategies (Contrarian, TBO Trend, TBT Divergence, Late Entry) with risk controls and dashboard.

## MVP Scope (Week 1-2)

### Week 1 Deliverables
1. Repository structure (Python + TypeScript)
2. Data loader: fetch Polymarket historical ticks and store in CSV/SQLite
3. Contrarian strategy implementation:
   - Entry: When crowd panic (high volume, price drop) + momentum divergence (RSI vs price)
   - Exit: trailing stop at 2x ATR
4. Simple backtester: loop through data, compute P&L, Sharpe ratio
5. Risk engine:
   - Position sizing: fixed $20 per trade or 2% of capital (whichever smaller)
   - Circuit breaker: stop after 3 consecutive losses
   - Daily loss limit: -$100
6. Paper trading loop: simulate fills, log trades, update equity curve

### Week 2 Deliverables
1. Dashboard (Next.js) with:
   - Equity curve chart (recharts)
   - Trade blotter
   - Risk metrics (Sharpe, max drawdown, win rate)
   - Configuration page (enable/disable strategies, adjust limits)
2. Discord alerts (via webhook) for:
   - Circuit breaker triggered
   - Daily P&L summary
   - Large drawdown warning
3. Integration with OpenClaw heartbeat:
   - Agent runs as a long session
   - Reports status via Telegram/Discord
4. Documentation:
   - Install guide (Python deps, Polygon RPC)
   - Configuration (API keys, wallet address)
   - Deployment to Vercel (dashboard) and Mac Mini (agent)
5. Test on 6 months of historical data; produce backtest report

### Technical Requirements
- Python 3.11+, `pandas`, `numpy`, `web3.py`, `httpx`
- Data: Polymarket GraphQL (use `polymarket-py` or custom)
- Execution: Simulated for paper trading; live trades via Polymarket contract writes (stretch)
- Dashboard: Next.js 14, Tailwind, Recharts, deployable to Vercel
- Persistence: SQLite for trade logs; JSON for config

### Success Criteria
- Backtest Sharpe > 1.5 on Contrarian over 6 months
- Paper trading runs without errors for 48 hours
- Dashboard shows real-time metrics
- Can be installed by a technical user in <1 hour

## Constraints
- Start with one strategy (Contrarian); add TBO and TBT only if time permits
- Keep dependencies minimal; avoid cloud services (use local SQLite)
- Assume user provides:
  - Polygon RPC endpoint (Infura/Alchemy)
  - Wallet private key (for future live trading)
  - Telegram/Discord webhook URLs

## Deliverables
- GitHub repository `agent-trader` (fnzeeetoo)
- `README.md` with installation and usage
- `PRODUCT_READY.md` summarizing what's built and next steps
- Demo: backtest report in `reports/`

Work autonomously in your workspace. When finished, write `PRODUCT_READY.md` and exit.
