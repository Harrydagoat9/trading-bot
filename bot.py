"""Alpaca paper-trading bot. Run with:  python bot.py
Add --once to run a single check and exit (good for testing).
"""
import os
import sys
import time
import logging
from datetime import datetime, timedelta, timezone

import requests
from dotenv import load_dotenv

import config
from strategy import get_signal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("trades.log")],
)
log = logging.getLogger("bot")


class Alpaca:
    def __init__(self, key, secret):
        if "paper-api" not in config.TRADING_URL:
            sys.exit("Safety stop: TRADING_URL is not the paper-trading URL.")
        self.s = requests.Session()
        self.s.headers.update({"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret})

    def _get(self, url, **params):
        r = self.s.get(url, params=params, timeout=20)
        r.raise_for_status()
        return r.json()

    def account(self):
        return self._get(f"{config.TRADING_URL}/v2/account")

    def clock(self):
        return self._get(f"{config.TRADING_URL}/v2/clock")

    def positions(self):
        return {p["symbol"]: p for p in self._get(f"{config.TRADING_URL}/v2/positions")}

    def daily_closes(self, symbol, days):
        start = (datetime.now(timezone.utc) - timedelta(days=days * 2 + 10)).strftime("%Y-%m-%d")
        data = self._get(
            f"{config.DATA_URL}/v2/stocks/{symbol}/bars",
            timeframe="1Day", start=start, limit=1000, feed="iex", adjustment="all",
        )
        return [bar["c"] for bar in (data.get("bars") or [])]

    def market_order(self, symbol, side, notional=None, qty=None):
        body = {"symbol": symbol, "side": side, "type": "market", "time_in_force": "day"}
        if notional is not None:
            body["notional"] = str(round(notional, 2))
        else:
            body["qty"] = str(qty)
        r = self.s.post(f"{config.TRADING_URL}/v2/orders", json=body, timeout=20)
        r.raise_for_status()
        return r.json()


def run_once(api):
    positions = api.positions()
    for symbol in config.SYMBOLS:
        try:
            closes = api.daily_closes(symbol, config.SLOW_MA)
            holding = symbol in positions
            signal = get_signal(closes, config.FAST_MA, config.SLOW_MA, holding)
            log.info(f"{symbol}: last close {closes[-1] if closes else '?'} | holding={holding} | signal={signal}")

            if signal == "buy":
                if len(positions) >= config.MAX_POSITIONS:
                    log.info(f"{symbol}: skip buy, already at max positions")
                    continue
                api.market_order(symbol, "buy", notional=config.DOLLARS_PER_TRADE)
                positions[symbol] = {}
                log.info(f"{symbol}: BUY ${config.DOLLARS_PER_TRADE} submitted")
            elif signal == "sell":
                qty = positions[symbol]["qty"]
                api.market_order(symbol, "sell", qty=qty)
                positions.pop(symbol)
                log.info(f"{symbol}: SELL {qty} shares submitted")
        except Exception as e:
            log.error(f"{symbol}: error {e}")


def main():
    load_dotenv()
    key, secret = os.getenv("ALPACA_API_KEY"), os.getenv("ALPACA_SECRET_KEY")
    if not key or not secret:
        sys.exit("Missing keys. Copy .env.example to .env and paste in your Alpaca PAPER keys.")

    api = Alpaca(key, secret)
    acct = api.account()
    log.info(f"Connected to paper account. Equity: ${float(acct['equity']):,.2f}")

    if "--once" in sys.argv:
        run_once(api)
        return

    while True:
        try:
            if api.clock()["is_open"]:
                run_once(api)
            else:
                log.info("Market closed, waiting...")
        except Exception as e:
            log.error(f"Loop error: {e}")
        time.sleep(config.CHECK_EVERY_MINUTES * 60)


if __name__ == "__main__":
    main()
