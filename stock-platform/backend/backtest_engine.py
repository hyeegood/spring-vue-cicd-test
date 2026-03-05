"""
Backtest engine: date range, stock list, entry rules -> win rate, avg return, max drawdown.
"""
from datetime import datetime, timedelta
from typing import List, Optional
import math
import yfinance as yf
import pandas as pd


def run_backtest(
    tickers: List[str],
    start_date: str,
    end_date: str,
    entry_rule: str = "ma20",  # ma20 | rsi
) -> dict:
    """
    Simple backtest: buy when price crosses above MA20 (or RSI<45), hold to end or stop/target.
    Returns { win_rate, avg_return, max_drawdown, trades }.
    """
    start = datetime.strptime(start_date[:10], "%Y-%m-%d")
    end = datetime.strptime(end_date[:10], "%Y-%m-%d")
    results = []
    all_returns = []

    for ticker in tickers:
        t = yf.Ticker(ticker)
        hist = t.history(start=start, end=end)
        if hist is None or len(hist) < 25:
            continue
        close = hist["Close"]
        ma20 = close.rolling(20).mean()
        rsi = _rsi(close, 14)

        entry_price = None
        for i in range(20, len(hist)):
            c = close.iloc[i]
            m = ma20.iloc[i]
            r = rsi.iloc[i] if rsi is not None and i < len(rsi) else 50
            if entry_price is None:
                if entry_rule == "ma20" and c > m and close.iloc[i - 1] <= ma20.iloc[i - 1]:
                    entry_price = c
                elif entry_rule == "rsi" and (r is None or (not math.isnan(r) and r < 45)) and entry_price is None:
                    entry_price = c
            else:
                ret_pct = (c - entry_price) / entry_price
                stop = entry_price * 0.92
                target = entry_price * 1.22
                if c <= stop:
                    all_returns.append(-0.08)
                    results.append({"ticker": ticker, "return": -0.08, "exit": "stop"})
                    entry_price = None
                elif c >= target:
                    all_returns.append(0.22)
                    results.append({"ticker": ticker, "return": 0.22, "exit": "target"})
                    entry_price = None
                elif i == len(hist) - 1:
                    all_returns.append(ret_pct)
                    results.append({"ticker": ticker, "return": ret_pct, "exit": "eod"})
                    entry_price = None

    if not all_returns:
        return {"win_rate": 0.0, "avg_return": 0.0, "max_drawdown": 0.0, "trades": []}
    wins = sum(1 for r in all_returns if r > 0)
    win_rate = wins / len(all_returns)
    avg_return = sum(all_returns) / len(all_returns)
    # Simplified max drawdown: from cumulative returns
    cum = 1.0
    peak = 1.0
    dd = 0.0
    for r in all_returns:
        cum *= 1 + r
        peak = max(peak, cum)
        dd = max(dd, (peak - cum) / peak if peak else 0)
    return {
        "win_rate": round(win_rate, 4),
        "avg_return": round(avg_return, 4),
        "max_drawdown": round(dd, 4),
        "trades": results[:50],
    }


def _rsi(close: pd.Series, period: int = 14) -> Optional[pd.Series]:
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    return 100 - (100 / (1 + rs))
