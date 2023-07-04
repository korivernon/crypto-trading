import pandas_ta as ta
import pandas as pd
import ccxt
import config

def rsi(exchange= ccxt.gemini({'apiKey': config.apiKey, 'secret': config.apiSecret}), symbol='ETH/USD'):
    symbol = 'ETH/USD'
    timeframe = '1m'
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
        if len(ohlcv):
            df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            df = pd.concat([df, df.ta.rsi()], axis=1)
            return df[-20:]
            print(exchange.iso8601 (exchange.milliseconds()))
    except Exception as e:
        print(type(e).__name__, str(e))