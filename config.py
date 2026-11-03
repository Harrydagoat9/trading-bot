# ---- Settings you can change ----

SYMBOLS = ["SPY", "AAPL", "MSFT"]   # stocks/ETFs the bot watches
FAST_MA = 10                        # fast moving average (days)
SLOW_MA = 30                        # slow moving average (days)
DOLLARS_PER_TRADE = 1000            # how much (fake) money to put into each buy
MAX_POSITIONS = 3                   # never hold more than this many stocks at once
CHECK_EVERY_MINUTES = 15            # how often the bot checks while the market is open

# Paper trading ONLY. The bot refuses to run against any other URL.
TRADING_URL = "https://paper-api.alpaca.markets"
DATA_URL = "https://data.alpaca.markets"
