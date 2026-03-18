# AgentTrader — Polymarket Strategy Research

## Objective
Build an autonomous agent that identifies profitable traders on predictive markets (Polymarket), analyzes their strategies, and replicates trades with risk management.

## Core Hypothesis
Top traders on Polymarket have identifiable patterns (position sizing, market selection, timing). An agent can monitor their activity, extract signals, and execute trades automatically while managing drawdown.

## Components

### 1. Data Ingestion
- **Polymarket GraphQL API**: Fetch recent trades, order book, market data
- **Trader leaderboard**: Identify top performers (ROI, consistency)
- **On-chain feeds**: Event subscription to trades when they happen

### 2. Strategy Analysis
- **Pattern extraction**:
  - Preferred markets (politics, crypto, sports)
  - Position sizing (always 5% of wallet, etc.)
  - Timing (buy/sell windows relative to events)
  - Exit behavior (take profit, stop loss patterns)
- **Clustering**: Group traders by style (momentum, contrarian, event-driven)
- **Signal generation**: When a top trader opens a position, decide whether to follow (with lag to avoid front-running detection)

### 3. Execution Layer
- **Wallet integration**: Self-custodied wallet with private key stored securely (encrypted)
- **Trade execution**: Submit orders via Polymarket smart contracts
- **Risk controls**:
  - Max exposure per market
  - Overall portfolio drawdown limit (e.g., stop if -20%)
  - Daily loss limit
  - Minimum balance threshold

### 4. Monitoring & Reporting
- Dashboard of current positions, P&L, followed traders
- Telegram alerts for large moves or stop-loss triggers
- Daily summary email

### 5. Security & Safety
- No leverage (Polymarket is binary outcomes, but still)
- Rate limiting to avoid API bans
- "Pause" button accessible via Telegram command
- All trades require human confirmation once (gradual autonomy increase)
- Separate wallet from main funds

## Implementation Plan

### Phase 1: Research & Scoping (Week 1)
- Set up Polymarket API access (GraphQL endpoint, rate limits)
- Scrape historical data for top 100 traders (backfill)
- Build a simple notebook analysis to see if patterns exist
- Identify which traders to follow (criteria: >30 trades, positive ROI, consistent)

### Phase 2: Monitor & Log (Week 2)
- Agent that polls every 5 minutes for new trades from followed traders
- Store in local database (SQLite)
- Generate daily digest of what they're trading

### Phase 3: Paper Trading (Week 3)
- Simulate execution based on follow signals
- Track hypothetical P&L
- Refine signal weighting (ensemble of traders vs single)

### Phase 4: Live Trading with Safety (Week 4)
- Connect wallet with small amount (e.g., $100)
- Execute with 1% of capital per trade
- Human confirmation required for first 10 trades
- Gradually reduce confirmation as confidence grows

### Phase 5: Scale & Optimize (Week 5+)
- Increase capital, add more traders
- Explore predictive models beyond copying (e.g., predict trader movements)
- Multi-market expansion (Kalshi, Meteora)

## Tools & APIs
- Polymarket GraphQL (https://github.com/polymarket/polymarket-interface)
- ethers.js / viem for on-chain interactions
- OpenClaw for orchestration (heartbeat to monitor, sessions for analysis)
- Supabase or SQLite for storage
- Telegram for alerts

## Risks
- Polymarket regulatory risk (US restricted)
- Trader strategies may not be replicable (liquidity, timing)
- On-chain fees (gas) on Polygon
- Account termination if detected as bot

## Mitigations
- Use small capital, separate wallet
- Add random delays to avoid pattern detection
- Keep trades below certain size to stay under radar
- Stay within API rate limits

## Success Criteria
- Positive Sharpe ratio in paper trading (1 month)
- 3 consecutive profitable weeks in live trading
- No major security incidents

## Next Step
Build the data collector script to fetch and store Polymarket trades. Then run analysis to validate the premise before writing execution code.
