USD = "USD"
BUY = "buy"
SELL = "sell"

import ccxt

# import api keys
import config
import logging
import pprint
import pandas as pd
def fetch_price(securities, exchange = ccxt.gemini()):
    sec_dict = {}
    for security in securities:
        ticker = exchange.fetch_ticker(security)
        print(ticker['bid'])
        print(ticker['ask'])
        sec_dict[security] = {'price':ticker['info']['price'] ,'bid': ticker['bid'], 'ask': ticker['ask']}
    return sec_dict

def get_balance(account,against=USD):
    bal = account.fetch_balance()[against]
    if against == USD:
        bal["toUsd"] == None
    else:
        bal["toUsd"] = bal["free"] * float(fetch_price([f"{against}/{USD}"])["price"])
    return bal

def get_ohlcv(acct=ccxt.gemini({'apiKey': config.apiKey, 'secret': config.apiSecret}), security='ETH/USD',time_period='1m'):
    ohlcv = acct.fetch_ohlcv(security, time_period)
    print(ohlcv)

def main():
    ex = ccxt.gemini({'apiKey':config.apiKey,'secret':config.apiSecret})
    ohlcv = ex.fetch_ohlcv('ETH/USD','1m')
    df = pd.DataFrame(ohlcv, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df['date'] = pd.to_datetime(df['date'], unit='ms')
    df.set_index('date', inplace=True)
    df = df.sort_index(ascending=True)
    df.head()
    print(df)
    print(ex.fetch_ticker('ETH/USD')   )
if __name__ == '__main__':
    main()