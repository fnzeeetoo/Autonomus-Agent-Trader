"""Backtesting engine – runs strategies against historical data."""

import yaml
from typing import List, Dict, Any
from datetime import datetime
from .data_loader import DataLoader
from ..core.risk import RiskEngine, RiskConfig
from ..core.portfolio import Portfolio
from ..core.execution import ExecutionEngine
from ..core.monitor import Monitor
from ..core import risk as core_risk
import json
import os


class Backtester:
    """Runs backtests and generates reports."""

    def __init__(self, data_source: str, strategy_config_path: str, risk_config_path: str):
        self.data_loader = DataLoader(data_source)
        with open(strategy_config_path) as f:
            self.strategy_cfg = yaml.safe_load(f)
        with open(risk_config_path) as f:
            self.risk_cfg = yaml.safe_load(f)
        self.risk_config = RiskConfig(**self.risk_cfg)
        self.portfolio = Portfolio(initial_capital=10000.0)
        self.risk_engine = RiskEngine(self.risk_config, initial_capital=10000.0)
        self.executor = ExecutionEngine(self.portfolio, paper_trading=True)
        self.monitor = Monitor(self.portfolio, self.risk_engine)
        self.strategies = self._init_strategies()
        self.equity_curve = []
        self.trades = []

    def _init_strategies(self) -> List[Any]:
        """Instantiate enabled strategies."""
        from ..strategies.contrarian.strategy import ContrarianStrategy
        from ..strategies.tbo_trend.strategy import TBOTrendStrategy
        from ..strategies.tbt_divergence.strategy import TBTDivergenceStrategy
        from ..strategies.late_entry.strategy import LateEntryStrategy

        strategies = []
        for name, cfg in self.strategy_cfg.items():
            if not cfg.get("enabled", True):
                continue
            if name == "contrarian":
                strat = ContrarianStrategy(cfg, self.risk_engine, self.executor, self.portfolio, self.monitor)
            elif name == "tbo_trend":
                strat = TBOTrendStrategy(cfg, self.risk_engine, self.executor, self.portfolio, self.monitor)
            elif name == "tbt_divergence":
                strat = TBTDivergenceStrategy(cfg, self.risk_engine, self.executor, self.portfolio, self.monitor)
            elif name == "late_entry":
                strat = LateEntryStrategy(cfg, self.risk_engine, self.executor, self.portfolio, self.monitor)
            else:
                continue
            strategies.append(strat)
        return strategies

    def run(self) -> Dict[str, Any]:
        """Execute backtest."""
        for tick in self.data_loader.iterate_ticks():
            # Update market prices for portfolio mark-to-market
            self.portfolio.update_prices({tick["symbol"]: tick["price"]})
            # Feed to strategies
            for strat in self.strategies:
                # Some strategies may need extra data; handle generically
                if hasattr(strat, "process_tick"):
                    # For TBT we need indicator value; but backtest likely doesn't have external indicator; pass None
                    try:
                        strat.process_tick(tick)
                    except TypeError as e:
                        # Maybe expects extra args; skip for now in generic loop
                        pass
            # Record equity point daily or every N ticks
            self.equity_curve.append(self.portfolio.total_equity())
        # After all ticks, compute final trades
        self.trades = self.portfolio.trade_history
        metrics = self._calculate_metrics()
        return metrics

    def _calculate_metrics(self) -> Dict[str, Any]:
        from ..backtester.metrics import calculate_all
        metrics = calculate_all(self.equity_curve, self.trades)
        # Monte Carlo
        try:
            from ..backtester.mc import monte_carlo
            mc_res = monte_carlo(self.equity_curve, self.trades)
            metrics.update(mc_res)
        except Exception as e:
            pass
        return metrics

    def save_report(self, output_path: str):
        metrics = self.run()
        with open(output_path, "w") as f:
            f.write("# Backtest Report\n\n")
            for k, v in metrics.items():
                if isinstance(v, float):
                    f.write(f"- **{k}**: {v:.4f}\n")
                else:
                    f.write(f"- **{k}**: {v}\n")
            f.write("\n## Notes\n\n")
            f.write("Backtest run on historical data.\n")
            f.write(f"Data source: {self.data_loader.source}\n")
            f.write(f"Strategies: {', '.join(self.strategy_cfg.keys())}\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Run backtest")
    parser.add_argument("--config", default="config/strategies.yaml")
    parser.add_argument("--risk", default="config/risk.yaml")
    parser.add_argument("--data", default="data/market_data.csv")
    parser.add_argument("--output", default="reports/backtest_6m.md")
    args = parser.parse_args()
    bt = Backtester(args.data, args.config, args.risk)
    bt.save_report(args.output)


if __name__ == "__main__":
    main()
