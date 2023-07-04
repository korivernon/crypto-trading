import config
import ccxt
from rsi_indicator import rsi
from tradingviewscraper import check_signals
from redmail import gmail
gmail.username = config.email
gmail.password = config.password
import time
from datetime import datetime, timedelta

class Account:
    def __init__(self, exch = ccxt.gemini({'apiKey':config.apiKey, 'secret':config.apiSecret})):
        self.exch = exch
        self.balance = self.getBalanceInUSD()
        self.active_trades = self.getActiveTrades()
        self.recently_purchased = {}

    def getBalanceInUSD(self):
        exchange = self.exch
        balances = exchange.fetch_balance()['free']
        balance = 0
        for token, value in balances.items():
            if float(value) != 0:
                if token != 'USDT' or token != 'USD':
                    request = token + '/USDT'
                    try:
                        price = float(exchange.fetchTicker(request)['last'])
                    except:
                        try:
                            request = token + '/BTC'
                            price = float(exchange.fetchTicker(request)['last'])
                            val_btc = (float(value)) * price
                            price = float(exchange.fetchTicker('BTC/USDT')['last'])
                            balance += val_btc * price
                        except:
                            try:
                                request = token + '/ETH'
                                price = float(exchange.fetchTicker(request)['last'])
                                val_btc = (float(value)) * price
                                price = float(exchange.fetchTicker('ETH/USDT')['last'])
                                balance += val_btc * price

                            except:
                                balance += float(value)
                    else:
                        balance += price * float(value)
                else:
                    balance += float(value)
        return balance

    def check_recent_trade(self, symbol='ETH/USD'):
        trades = self.exch.fetch_my_trades(symbol)

        latest_timestamp = float('-inf')
        for trade in trades:
            if latest_timestamp < trade['timestamp']:
                latest_timestamp = trade['timestamp']
                print(trade)
        latest_timestamp = str(latest_timestamp)[:10]
        latest = datetime.utcfromtimestamp(int(latest_timestamp))
        dnow = datetime.now()
        print('latest', latest, type(latest))
        print('datetime now', dnow, type(dnow))
        return timedelta(latest, dnow).min
    def getBalanceUSD(self):
        exchange = self.exch
        balances = exchange.fetch_balance()['free']
        balance = 0
        for token, value in balances.items():
            if float(value) != 0:
                balance += float(value)
        return balance
    def average_purchase_price(self, symbol='ETH/USD'):
        exchange = self.exch
        associated_trades = exchange.fetchMyTrades(symbol=symbol)
        avg_sum = 0
        shares_owned = 0
        for trade in associated_trades:
            if trade['side'] == 'buy':
                avg_sum += trade['amount'] * trade['price']
                shares_owned += trade['amount']
            elif trade['side'] == 'sell':
                avg_sum -= trade['amount'] * trade['price']
                shares_owned -= trade['amount']
        return avg_sum / shares_owned

    def shares_outstanding(self, symbol='ETH/USD'):
        exchange = self.exch
        associated_trades = exchange.fetchMyTrades(symbol=symbol)
        shares_owned = 0
        for trade in associated_trades:
            if trade['side'] == 'buy':
                shares_owned += trade['amount']
            elif trade['side'] == 'sell':
                shares_owned -= trade['amount']
        return shares_owned

    def total_fees(self, symbol='ETH/USD'):
        exchange = self.exch
        associated_trades = exchange.fetchMyTrades(symbol=symbol)
        fee = 0
        for trade in associated_trades:
            if trade['fee']['currency'] == 'USD':
                fee += trade['fee']['cost']
            else:
                request = trade['fee']['currency'] + '/USD'
                fee = trade['fee']['cost'] * float(exchange.fetch_ticker(request)['last'])
        return fee

    def getActiveTrades(self):
        active_trades = {}
        for key, value in self.exch.fetch_balance().items():
            if key == 'info' or key == 'free' or key == 'USD' or key == 'used' or key == 'total': continue
            check_entry = key + '/USD'

            entry = self.average_purchase_price(check_entry)
            latest_price = float(self.exch.fetchTicker(check_entry)['last'])
            total_fees = self.total_fees(check_entry)
            active_trades[key] = {
                'amount': self.shares_outstanding(check_entry),
                'entry': entry,
                'total_fees': total_fees,
                'latest_price': latest_price,
                'total_gain': (latest_price/entry)-1,
                'total_gain_fees': (latest_price/(entry + total_fees))-1
            }
        return active_trades

    def rsi_value(self, symbol='ETH/USD'):
        _rsi = rsi(exchange=self.exch, symbol=symbol)
        # 30 is the sweet spot and 70 is the max tolerance ... if it's 30 or below 1, if it's 70 or above -1
        rsi_value = _rsi['RSI_14'].iloc[-1]
        return rsi_value

    def rsi_indicator(self, symbol='ETH/USD'):
        _rsi = rsi(exchange=self.exch, symbol=symbol)
        # 30 is the sweet spot and 70 is the max tolerance ... if it's 30 or below 1, if it's 70 or above -1
        rsi_value = self.rsi_value( symbol='ETH/USD')

        indicator = 0
        if rsi_value <= 30: indicator = 1
        elif rsi_value >= 70: indicator = -1
        elif rsi_value <= 50:
            indicator = abs(1-(abs (30-rsi_value)/20) )*1
        elif rsi_value <70:
            indicator = abs(1-( abs(rsi_value-70) / 20)) * -1
        return indicator

    def place_buy_market_order(self, symbol, amt):
        last_price = self.exch.fetchTicker(symbol)['last']
        try:
            order = self.exch.create_limit_order(symbol=symbol, side='buy', amount=amt, price=last_price)
        except Exception as e:
            print(f"\t{e}\n\t\tInvalid Limit Order Quantity.")
            gmail.send(
                subject=f"CMon: Buy Order FAILED {symbol}. Amount: {amt}",
                sender=f"{config.email}",
                receivers=[f"{config.email}"],
                # A plot in body
                html=f"""Market buy order FAILED for {symbol}. Amount: {amt}."""
            )
            return {'status': f'Invalid Limit Order Quantity: {e}'}
        return order

    def tvs_enter_trade(self, env='dev'):
        # first look for opportunities in tradingview scraper

        tvscraper = check_signals().query("decision == 'BUY'")
        for index,row in tvscraper.iterrows():
            if row['with'] == 'USDT' or row['with'] == 'USD':
                free_balance = self.getBalanceUSD()
            elif row['with'] in self.active_trades.keys():
                free_balance = self.active_trades[row['with']]['amount']
            symbol = f'{row["buy"]}/{row["with"]}'
            print('symbol', symbol, 'free balance', free_balance)
            if free_balance != 0:
                weight = row['total weight']
                # we want to get the total ((100/4) / 5 ) * weight
                amount_free_to_use = (((1/4)/5) * weight) * free_balance
                print(amount_free_to_use)
                # convert from the amount we want to use to the specified amount
                amt =  amount_free_to_use/ self.exch.fetchTicker(symbol)['last']
                print('buy', symbol, 'with', amt)
                order = self.place_buy_market_order(symbol, amt)
                if order['status'] == 'filled':
                    gmail.send(
                        subject=f"CMon: Buy Order Filled {symbol}. Amount: {amt}",
                        sender=f"{config.email}",
                        receivers=[f"{config.email}"],
                        # A plot in body
                        html=f"""
                            Market buy order filled for {symbol}. Amount: {amt}.
                            """
                    )

                    print("Market buy order filled")
                else:
                    print("Market buy order failed")
def main():
    acct = Account()
    print('account value:',acct.balance)
    print('get balance usd:', acct.getBalanceUSD())
    print('active trades:', acct.active_trades)
    print('rsi indicator:',acct.rsi_indicator())
    print('rsi value:',acct.rsi_value())
    # print('enter trade where:\n',acct.tvs_enter_trade())
    print('timestamp:', acct.check_recent_trade(), type(acct.check_recent_trade()))

if __name__ == '__main__':
    main()