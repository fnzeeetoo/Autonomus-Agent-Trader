"""Monte Carlo simulation for backtesting robustness."""

import numpy as np
from typing import List, Dict
from .metrics import calculate_all, calculate_returns
import random


def bootstrap_returns(rets: np.ndarray, n_sims: int = 1000) -> np.ndarray:
    """Generate bootstrapped return sequences."""
    sims = []
    for _ in range(n_sims):
        sampled = np.random.choice(rets, size=len(rets), replace=True)
        sims.append(np.cumprod(1 + sampled) - 1)
    return np.array(sims)


def monte_carlo(equity_curve: List[float], trades: List[dict], n_sims: int = 1000) -> Dict[str, float]:
    """Run Monte Carlo analysis to estimate robustness."""
    rets = calculate_returns(equity_curve)
    if len(rets) < 2:
        return {"mc_sharpe_mean": 0.0, "mc_sharpe_std": 0.0, "mc_max_dd_mean": 0.0}
    sims = bootstrap_returns(rets, n_sims)
    # Compute metrics for each sim
    sharpes = []
    mds = []
    for sim in sims:
        # reconstruct equity curve from returns: start at equity_curve[0]
        start = equity_curve[0]
        eq = np.concatenate([[start], start * (1 + sim + 1)])  # rough; actually sim is cumulative return
        # Better: eq = start * (1 + cumulative returns)
        eq = start * (1 + sim)
        eq = np.concatenate([[start], eq])
        sr = calculate_all(eq, trades)["sharpe_ratio"]
        md = calculate_all(eq, trades)["max_drawdown"]
        sharpes.append(sr)
        mds.append(md)
    return {
        "mc_sharpe_mean": float(np.mean(sharpes)),
        "mc_sharpe_std": float(np.std(sharpes)),
        "mc_max_dd_mean": float(np.mean(mds))
    }
