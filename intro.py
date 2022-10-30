import ccxt

# import api keys
import config

# print(ccxt.exchanges)
exchange = ccxt.coinbasepro()
markets = exchange.load_markets()
# for market in markets:
#     print(market)

USD = "USD"
BUY = "buy"
SELL = "sell"

securities = ["ETH/USD"]
'''
{
    'symbol': 'ETH/USD', 
    'timestamp': 1663683228830, 
    'datetime': '2022-09-20T14:13:48.830Z', 
    'high': None, 'low': None, 'bid': 1343.23, 
    'bidVolume': None, 'ask': 1343.33, 
    'askVolume': None, 'vwap': None, 'open': None, 
    'close': 1343.25, 'last': 1343.25, 'previousClose': None, 
    'change': None, 'percentage': None, 'average': None, 'baseVolume': 324571.95633972, 
    'quoteVolume': None, 
    'info': 
        {
            'ask': '1343.33', 'bid': '1343.23', 
            'volume': '324571.95633972', 'trade_id': '357922473', 'price': '1343.25', 
            'size': '0.08010189', 'time': '2022-09-20T14:13:48.830463Z'
        }
}
'''


def fetch_price(securities):
    sec_dict = {}
    for security in securities:
        ticker = exchange.fetch_ticker(security)
        print(ticker['bid'])
        print(ticker['ask'])
        sec_dict[security] = {'price':ticker['info']['price'] ,'bid': ticker['bid'], 'ask': ticker['ask']}
    return sec_dict



#ohlcv
print("ohlcv")
ohlcv = exchange.fetchOHLCV("ETH/USD", timeframe="15m",limit=5)
print(ohlcv)
for candle in ohlcv:
    print (candle)

print("order_book") # read the current order book

def analyze_orderbook(securities_dict, range = 10):
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

def stop_loss(security, percentage, account):
    symbol = f"{security}/USD"
    cash_balance = account.fetch_balance()[USD]
    holding_qty = account.fetch_balance()[security]

    avg_purchase = 0
    orders = account.fetch_my_trades(symbol=symbol, since=1667086277)
    for order in orders:
        order_info = order["info"]
        if order_info["side"] == BUY:
            avg_purchase += float(order_info["price"]) * order["amount"] + order["fee"]["cost"]
    current_price = float(fetch_price([symbol])[symbol]["price"]) * float(holding_qty['free'])  
    threshold = (avg_purchase - avg_purchase * (percentage/100))
    print("current price: ",current_price, "purchase price",avg_purchase , "threshold", threshold)
    if ( threshold > current_price ):
        account.createMarketOrder (symbol, SELL, holding_qty)
    else:
        print("HODL HODL HODL")
        print("unrealized profit/loss:",current_price - (avg_purchase))
    # account.create_order(security, SELL, security_balance )
    print("Cash Balance:" , cash_balance, "Security Balance:",holding_qty, "Percentage", percentage, "Average purchase:", avg_purchase)
    pass

def double_down(security, percentage, account):
    cash_balance = account.fetch_balance()[USD]
    security_balance = account.fetch_balance()[security]

    print("Cash Balance:" , cash_balance, "Security Balance:",security_balance, "Percentage", percentage)
    pass

def main():
    exchange_id = 'coinbasepro'
    exchange_class = getattr(ccxt, exchange_id)
    coinbase = exchange_class({
        'apiKey': config.coinbase_public_api_key,
        'secret': config.coinbase_secret_private_key,
        'password': config.coinbase_passphrase
    }) 

    securities_dict = fetch_price(securities)
    print(securities_dict)
    print(analyze_orderbook(securities_dict, range = 0.10))

    print("fetch trades" )
    # stop_loss("ETH")
    stop_loss("ETH", 3, coinbase)

    print(coinbase.fetch_balance()["USD"])
    print(coinbase.fetch_balance()["ETH"])
main()

