# internally defined consts and functions
import config
from constants import *
from sell import *

pp = pprint.PrettyPrinter(indent=4)

# markets = exchange.load_markets()

securities = ["ETH/USD"]
def analyze_orderbook(securities_dict, exchange = ccxt.coinbasepro(), range = 10):
    for security in securities_dict.keys():
        order_book = exchange.fetch_order_book(security)
        bids = []
        asks = []
        for key in order_book.keys():
            print(key)
            if key == 'bids' or key == 'asks':
                for _ in order_book[key]:
                    if key == "bids":
                        if securities_dict[security]['bid'] - range <= _[0] <= securities_dict[security]['bid'] + range:
                            bids.append( [_[0], _[1], float(securities_dict[security]['price'])] )
                            # _.append(float(securities_dict[security]['price']))
                    else: 
                        if securities_dict[security]['ask'] - range <= _[0] <= securities_dict[security]['ask'] + range :
                            asks.append( [_[0], _[1], float(securities_dict[security]['price'])] )
    return {"bids": bids, "asks":asks}

def double_down(security, percentage, account,against=USD):
    cash_balance = get_balance(account,against)
    security_balance = account.fetch_balance()[security]

    print("Cash Balance:" , cash_balance, "Security Balance:",security_balance, "Percentage", percentage)
    pass

def main():
    exchange_id = 'gemini'
    exchange_class = getattr(ccxt, exchange_id)
    exch = exchange_class({
        'apiKey': config.apiKey,
        'secret': config.apiSecret
    }) 

    # securities_dict = fetch_price(securities)
    # print(securities_dict)
    # print(analyze_orderbook(securities_dict, range = 0.10))

    stop_loss("ETH", 3, exch,"BTC")
    realize_profits("ETH", 6, exch)
    execute_market_sell_order("BTC",exch)

    # print(coinbase.fetch_balance()["USD"])

    # print(pp.pprint(coinbase.fetchOpenOrders(symbol="BTC/USD", since=1667086277)))
    # print(fetch_price(["BTC/USD" ]))



    # print("making sure this is working:" ,get_balance(coinbase,"BTC")["toUsd"])
    # print(coinbase.fetchOpenOrders(symbol="BTC/USD", since=1667086277))
    # coinbase.createMarketOrder ("ETH/USD", SELL, 0.01)
main()

