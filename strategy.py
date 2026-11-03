"""Moving-average crossover strategy.

Idea in plain English:
- A "moving average" is the average closing price over the last N days.
- The FAST average (10 days) reacts quickly to recent prices.
- The SLOW average (30 days) shows the longer-term trend.
- When the fast one is ABOVE the slow one, the price is trending up -> we want to own the stock.
- When the fast one drops BELOW the slow one, the trend has turned down -> we sell.
"""


def sma(values, n):
    """Simple moving average of the last n values."""
    if len(values) < n:
        return None
    return sum(values[-n:]) / n


def get_signal(closes, fast=10, slow=30, holding=False):
    """Return 'buy', 'sell', or 'hold' given a list of closing prices (oldest first)."""
    fast_avg = sma(closes, fast)
    slow_avg = sma(closes, slow)
    if fast_avg is None or slow_avg is None:
        return "hold"  # not enough data yet

    if fast_avg > slow_avg and not holding:
        return "buy"
    if fast_avg < slow_avg and holding:
        return "sell"
    return "hold"
