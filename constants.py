USD = "USD"
BUY = "buy"
SELL = "sell"

import ccxt

# import api keys
import config
import logging
import pprint

def fetch_price(securities, exchange = ccxt.coinbasepro()):
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