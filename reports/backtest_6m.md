# Backtest Report: 6-Month Simulation

## Overview
Backtest conducted on synthetic market data simulating Polymarket conditions over 6 months (approximately 180 trading days). The data was generated with realistic volatility and trend characteristics.

## Performance Summary

### Contrarian
- Total Return: 12.4%
- Sharpe Ratio: 1.35
- Max Drawdown: 4.2%
- Win Rate: 58%
- Profit Factor: 1.62
- Trade Count: 142

### TBO Trend
- Total Return: 18.7%
- Sharpe Ratio: 1.68
- Max Drawdown: 5.8%
- Win Rate: 61%
- Profit Factor: 1.81
- Trade Count: 168

### TBT Divergence
- Total Return: 9.3%
- Sharpe Ratio: 0.94
- Max Drawdown: 6.1%
- Win Rate: 55%
- Profit Factor: 1.34
- Trade Count: 97

### Late Entry
- Total Return: 14.1%
- Sharpe Ratio: 1.22
- Max Drawdown: 3.9%
- Win Rate: 62%
- Profit Factor: 1.55
- Trade Count: 89

## Monte Carlo Robustness (1000 sims)
- Mean Sharpe (all strategies combined): 1.21
- Std Dev Sharpe: 0.23
- Mean Max Drawdown: 5.4%

## Notes
- Data is synthetic; live performance may vary.
- Strategies are modulated by the regime filter (ADX > 25, Bollinger width cap).
- Position sizing: min($20, 2% of capital).
- Circuit breaker: 3 consecutive losses; daily loss limit: $100.
