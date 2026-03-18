# AgentTrader MVP

Automated trading system with 4 strategies, risk management, backtesting, and dashboard.

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
pip install -r requirements.txt
```

For the dashboard:

```bash
cd dashboard
npm install
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in values:
- `POLYGON_RPC_URL` – your Polygon RPC endpoint
- `WALLET_PRIVATE_KEY` – private key for live trading (optional)
- `DISCORD_WEBHOOK_*` – Discord alert URLs
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` – for OpenClaw integration
- `DATA_SOURCE` – path to CSV or SQLite file with historical data

### 3. Prepare data

The data file should be CSV with columns:
`timestamp,open,high,low,close,volume`

For SQLite, ensure a table named `market_data` with the same columns.

Sample synthetic data generation script is in `scripts/generate_data.py`.

### 4. Run backtests

```bash
python -m backtester.engine --config config/strategies.yaml --risk config/risk.yaml --data data/market_data.csv --output reports/backtest_6m.md
```

### 5. Start paper trading

```bash
python -m bot.heartbeat --paper --config config/strategies.yaml
```

Paper trades are logged under `data/paper_trades/`.

### 6. Launch dashboard

```bash
cd dashboard
npm run dev
# Open http://localhost:3000
```

Dashboard reads data from local JSON files written by the paper trader. For a custom API, modify `dashboard/lib/data.ts`.

### 7. Deploy to Vercel

```bash
cd dashboard
vercel --prod
```

A `vercel.json` is included. The dashboard is statically generated from local files; you may need to set up an API route to read data if not using static JSON.

## Configuration

### `config/strategies.yaml`

Enable/disable strategies and set parameters:

```yaml
contrarian:
  enabled: true
  rsi_period: 14
  rsi_overbought: 70
  rsi_oversold: 30
  panic_volume_multiplier: 2.0

tbo_trend:
  enabled: true
  fast_period: 10
  slow_period: 30

tbt_divergence:
  enabled: true
  indicator_period: 14
  divergence_threshold: 0.05

late_entry:
  enabled: true
  entry_minutes_before_close: 15
  stability_window: 5
```

### `config/risk.yaml`

```yaml
position_sizing_fixed: 20.0
position_sizing_pct: 0.02
circuit_breaker_losses: 3
daily_loss_limit: -100.0
adx_threshold: 25.0
bollinger_volatility_cap: 2.0
```

## Project Structure

- `strategies/` – Four strategy implementations
- `core/` – Risk engine, execution, portfolio tracking, monitoring
- `backtester/` – Backtesting engine, data loader, metrics, Monte Carlo
- `dashboard/` – Next.js 14 front-end with Recharts
- `bot/` – Heartbeat and alerting logic
- `config/` – YAML configuration files
- `data/` – Trade logs (paper/live)
- `reports/` – Backtest reports

## Security Considerations

- Never commit `.env` with private keys
- Use environment variables for secrets
- Keep private keys offline for production
- Restrict Discord webhook URLs to authorized channels
- Consider using a wallet with limited funds for trading

## Troubleshooting

### Module import errors
Ensure you're running from the project root or have installed with `pip install -e .`.

### Dashboard shows no data
Check that the paper trader has generated files in `data/paper_trades/`. The dashboard reads `equity_curve.json` and `trades.json`.

### Alerts not sending
Verify Discord webhook URLs and network connectivity. Check logs for errors.

## License

MIT
