"""Performance metrics calculation."""

import numpy as np
from typing import List, Dict


def calculate_returns(equity_curve: List[float]) -> np.ndarray:
    if len(equity_curve) < 2:
        return np.array([])
    eq = np.array(equity_curve)
    rets = np.diff(eq) / eq[:-1]
    return rets


def sharpe_ratio(equity_curve: List[float], risk_free_rate: float = 0.0) -> float:
    rets = calculate_returns(equity_curve)
    if len(rets) == 0:
        return 0.0
    excess = rets - risk_free_rate / (len(rets) + 1)  # rough annualization not applied
    if np.std(excess) == 0:
        return 0.0
    sr = np.mean(excess) / np.std(excess)
    # Annualize assuming daily returns (√252)
    return sr * np.sqrt(252)


def max_drawdown(equity_curve: List[float]) -> float:
    eq = np.array(equity_curve)
    peak = np.maximum.accumulate(eq)
    dd = (eq - peak) / peak
    max_dd = np.min(dd) if len(dd) > 0 else 0.0
    return -max_dd  # positive percentage


def win_rate(trades: List[dict]) -> float:
    if not trades:
        return 0.0
    wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
    return wins / len(trades)


def profit_factor(trades: List[dict]) -> float:
    gross_profit = sum(t["pnl"] for t in trades if t.get("pnl", 0) > 0)
    gross_loss = -sum(t["pnl"] for t in trades if t.get("pnl", 0) < 0)
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    return gross_profit / gross_loss


def total_return(equity_curve: List[float]) -> float:
    if not equity_curve:
        return 0.0
    return (equity_curve[-1] - equity_curve[0]) / equity_curve[0]


def calmar_ratio(equity_curve: List[float]) -> float:
    ret = total_return(equity_curve)
    md = max_drawdown(equity_curve)
    if md == 0:
        return 0.0
    # Annualize: not precise, assume equity_curve covers N days; missing.
    # We'll simply return ret / md (higher is better).
    return ret / md


def calculate_all(equity_curve: List[float], trades: List[dict]) -> Dict[str, float]:
    return {
        "total_return": total_return(equity_curve),
        "sharpe_ratio": sharpe_ratio(equity_curve),
        "max_drawdown": max_drawdown(equity_curve),
        "win_rate": win_rate(trades),
        "profit_factor": profit_factor(trades),
        "calmar_ratio": calmar_ratio(equity_curve),
        "trade_count": len(trades)
    }
