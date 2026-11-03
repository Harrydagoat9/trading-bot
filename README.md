# Alpaca Paper-Trading Bot

A simple moving-average crossover bot that trades with fake money on Alpaca.

## Setup (one time)
1. Make a free account at alpaca.markets, switch to **Paper Trading**, and generate API keys.
2. In this folder, run: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and paste in your paper keys.

## Run
- Test one check: `python bot.py --once`
- Run continuously: `python bot.py` (checks every 15 min while the market is open; Ctrl+C to stop)

Every decision is logged to the screen and to `trades.log`.

## Change the settings
Edit `config.py` — which stocks, the moving-average lengths, and dollars per trade.

## How the strategy works
- Fast average = average price over the last 10 days. Slow average = last 30 days.
- Fast above slow → uptrend → buy (if not already holding).
- Fast below slow → downtrend → sell (if holding).

## Safety
- Hard-coded to Alpaca's paper URL; the bot exits if that's changed.
- Caps at 3 positions and $1,000 per buy by default.
