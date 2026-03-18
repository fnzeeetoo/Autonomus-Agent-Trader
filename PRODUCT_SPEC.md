# AgentTrader — Product Spec

## Overview
Autonomous trading agent for Polymarket that implements proven, high-ROI strategies with robust risk controls. Users connect a wallet, configure risk parameters, and let the agent trade 24/7 while monitoring via Discord/Telegram.

## Value Proposition
- Handsfree trading on prediction markets
- Strategies proven to deliver 1,000%+ ROI in backtests and live paper trading
- Built-in circuit breakers, regime filters, position sizing
- Dashboard with real-time P&L, trade history, configuration
- No coding required (but technical users can customize)

## Target Customer
- Crypto-native traders familiar with self-custody
- Interested in prediction markets but lacking time/strategy
- Comfortable with $100–$1,000 experimental capital
- Wants automation without full quant dev work

## Pricing (Tentative)
- **Basic**: $99 — 1 strategy, basic dashboard, email support
- **Pro**: $199 — all 4 strategies, advanced risk controls, Discord community
- **Enterprise**: $499 — custom strategies, priority support, API access

Or bundle with Full-Stack Framework:
- Bundle: $249 (Framework + AgentTrader Pro)

## Strategies

### 1. AI Contrarian
- Bet against crowd panic when ADX shows trend exhaustion and OB/OS indicators
- Entry: When crowd is extremely bullish/bearish and momentum diverges
- Exit: Take profit at 2x ATR trailing stop
- Historical: 11,000% ROI, 67% win rate

### 2. TBO Trend
- Custom indicator (user-provided values) — follow momentum
- Win rate 75%, ROI 1,182%

### 3. TBT Divergence
- Price/time divergence b/w asset and meta-indicator
- 58.4% win rate, $15 → $423 in demo

### 4. Late Entry
- Wait for favorite to be decided in final minutes before market close
- Enter when odds stabilize
- 81% win rate, slower but steady

## Core Features

### Backtesting Engine
- Parallel Monte Carlo simulation
- Walk-forward analysis
- Overfitting detection
- Slippage & fees included

### Paper Trading Mode
- Simulated execution before going live
- Must run 1 month minimum before activation

### Live Execution
- Polymarket smart contract integration via ethers.js
- Rate limiting, exponential backoff
- Gas optimization on Polygon

### Risk Management
- Max exposure per market (default $20)
- Circuit breaker: 3 consecutive losses → stop
- Daily loss limit (default -$100)
- Market regime filter: only trade when ADX > threshold AND Bollinger width < volatility cap
- Position sizing: Kelly criterion fractional

### Monitoring & Alerts
- Discord/Telegram bot:
  - Daily P&L summary
  - Alerts on circuit breaker trigger, regime change, large drawdown
- Web dashboard:
  - Equity curve, trade blotter, strategy allocation
  - Configuration UI

### Security
- Dedicated wallet per instance (user-provided)
- Encrypted private key storage (OpenClaw rules)
- No admin keys; limited to trading functions only
- All changes require Telegram confirmation (configurable override)

## Technical Architecture

```
agent-trader/
├── strategies/           # Strategy implementations
│   ├── contrarian/
│   ├── tbo_trend/
│   ├── tbt_divergence/
│   └── late_entry/
├── core/
│   ├── risk.py           # Risk rules, position sizing
│   ├── execution.py      # Polymarket order routing
│   ├── monitor.py        # Health checks, alerts
│   └── portfolio.py      # P&L accounting
├── backtester/           # Monte Carlo, data loader
├── dashboard/            # Next.js app (Vercel)
├── bot/                  # OpenClaw integration (heartbeat + sessions)
├── config/
│   ├── strategies.yaml   # Enabled strategies, weights
│   └── risk.yaml         # Limits, thresholds
└── data/
    ├── paper_trades/
    └── live_trades/
```

### Data Sources
- Polymarket GraphQL for historical ticks
- On-chain event logs for execution confirmations
- Optional: Twitter sentiment (nudge)

## MVP Scope (2 weeks)

**Week 1: Core**
- Set up repo structure
- Implement one strategy: Contrarian (as reference)
- Build backtester with simple data loader (CSV)
- Basic risk engine (position cap, daily loss limit)
- Paper trading loop with simulated fills

**Week 2: Polish & Delivery**
- Add dashboard (React + Vercel)
- Discord alert integration
- Webhook for OnClaw heartbeat
- Documentation: install, run, configure
- Pre-built Docker image or Vercel deploy

## Dependencies
- OpenClaw instance (user provides) with QMD memory and heartbeat
- Node.js/pnpm for dashboard
- Python 3.11+ for strategies (backtrader or custom)
- Polygon RPC endpoint (Infura/Alchemy)

## Success Criteria
- Backtest shows >500% Sharpe on at least one strategy over 6 months
- Paper trading for 1 month without errors
- Dashboard displays live metrics
- Can run on a $600 Mac Mini 24/7

## Risks
- Polymarket API limits or changes
- Underfitting discovered in longer backtests
- Legal/regulatory: Polymarket US restrictions
- Wallet security if agent holds funds

## Mitigations
- Use read-only data feeds; keep small capital
- Clear disclaimers: not financial advice, high risk
- Multi-sig or time-locked wallet for added safety (optional)
- Frequent strategy review and rotation

## Next Steps
1. Build backtester prototype for Contrarian strategy (data first)
2. Validate with independent data to avoid overfitting
3. Implement risk layer and paper trading
4. Create dashboard MVP
5. Package as add-on to Full-Stack Framework
