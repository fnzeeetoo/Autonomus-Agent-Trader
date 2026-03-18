import yaml
import time
import os
from datetime import datetime
from ..core.risk import RiskEngine, RiskConfig
from ..core.portfolio import Portfolio
from ..core.execution import ExecutionEngine
from ..core.monitor import Monitor
from .alerts import send_discord_alert
import json


def load_config(strategies_yaml: str, risk_yaml: str, env: dict = None):
    with open(strategies_yaml) as f:
        strat_cfg = yaml.safe_load(f)
    with open(risk_yaml) as f:
        risk_cfg = yaml.safe_load(f)
    # Override with env if provided
    if env:
        if 'DISCORD_WEBHOOK_ALERTS' in env:
            risk_cfg['DISCORD_WEBHOOK_ALERTS'] = env['DISCORD_WEBHOOK_ALERTS']
        if 'DISCORD_WEBHOOK_DAILY' in env:
            risk_cfg['DISCORD_WEBHOOK_DAILY'] = env['DISCORD_WEBHOOK_DAILY']
    return strat_cfg, RiskConfig(**{k:v for k,v in risk_cfg.items() if k in ['position_sizing_fixed','position_sizing_pct','circuit_breaker_losses','daily_loss_limit','adx_threshold','bollinger_volatility_cap']}), risk_cfg


def run_paper_trading(data_source: str, strategies_cfg, risk_config: RiskConfig, extra_cfg: dict = None):
    portfolio = Portfolio(initial_capital=10000.0)
    risk_engine = RiskEngine(risk_config, initial_capital=10000.0)
    executor = ExecutionEngine(portfolio, paper_trading=True)
    discord_alerts = extra_cfg.get('DISCORD_WEBHOOK_ALERTS') if extra_cfg else None
    discord_daily = extra_cfg.get('DISCORD_WEBHOOK_DAILY') if extra_cfg else None
    monitor = Monitor(portfolio, risk_engine, discord_webhook_alerts=discord_alerts, discord_webhook_daily=discord_daily)

    # Load strategies
    from ..strategies.contrarian.strategy import ContrarianStrategy
    from ..strategies.tbt_divergence.strategy import TBTDivergenceStrategy
    from ..strategies.late_entry.strategy import LateEntryStrategy
    try:
        from ..strategies.tbt_divergence.strategy import TBTDivergenceStrategy
    except ImportError:
        TBTDivergenceStrategy = None
    try:
        from ..strategies.tbo_trend.strategy import TBOTrendStrategy
    except ImportError:
        TBOTrendStrategy = None
    strategies = []
    for name, cfg in strategies_cfg.items():
        if not cfg.get('enabled', True):
            continue
        if name == 'contrarian':
            strategies.append(ContrarianStrategy(cfg, risk_engine, executor, portfolio, monitor))
        elif name == 'tbo_trend' and TBOTrendStrategy:
            strategies.append(TBOTrendStrategy(cfg, risk_engine, executor, portfolio, monitor))
        elif name == 'tbt_divergence' and TBTDivergenceStrategy:
            strategies.append(TBTDivergenceStrategy(cfg, risk_engine, executor, portfolio, monitor))
        elif name == 'late_entry':
            strategies.append(LateEntryStrategy(cfg, risk_engine, executor, portfolio, monitor))

    # Data loop (paper trading simulation)
    loader = DataLoader(data_source)
    for tick in loader.iterate_ticks():
        portfolio.update_prices({tick['symbol']: tick['price']})
        for s in strategies:
            try:
                # For TBT divergence, we need an indicator; simulate using close price as placeholder
                if hasattr(s, 'process_tick'):
                    try:
                        s.process_tick(tick)
                    except TypeError:
                        s.process_tick(tick, tick['price'])  # provide dummy indicator
            except Exception as e:
                # ignore errors for this tick
                pass

        # Periodically check alerts every 1000 ticks
        if len(portfolio.trade_history) % 1000 == 0:
            alerts = monitor.check_and_alert()
            for msg in alerts:
                if msg.startswith('DAILY_SUMMARY'):
                    part = msg.split('|', 1)[1] if '|' in msg else msg
                    send_discord_alert(discord_daily, part)
                else:
                    send_discord_alert(discord_alerts, msg)
            persist_state(portfolio, monitor)

    # Final persist
    persist_state(portfolio, monitor)
    return portfolio.total_equity()


def persist_state(portfolio: Portfolio, monitor: Monitor, trades_path='data/paper_trades/trades.json', state_path='data/monitor_state.json'):
    os.makedirs(os.path.dirname(trades_path), exist_ok=True)
    with open(trades_path, 'w') as f:
        json.dump(portfolio.trade_history, f, indent=2)
    monitor.persist_state(state_path)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data/market_data.csv')
    parser.add_argument('--config', default='config/strategies.yaml')
    parser.add_argument('--risk', default='config/risk.yaml')
    args = parser.parse_args()
    strat_cfg, risk_cfg, raw_cfg = load_config(args.config, args.risk)
    run_paper_trading(args.data, strat_cfg, risk_cfg, raw_cfg)
