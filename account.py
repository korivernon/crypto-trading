import config
import ccxt
from rsi_indicator import rsi
class Account:
    def __init__(self, exch = ccxt.gemini({'apiKey':config.apiKey, 'secret':config.apiSecret})):
        self.exch = exch
        self.balance = self.getBalanceUSD()
        self.active_trades = self.getActiveTrades()

    def getBalanceUSD(self):
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
def main():
    acct = Account()
    print(acct.balance)
    print(acct.active_trades)
    print(acct.rsi_indicator())
    print(acct.rsi_value())

if __name__ == '__main__':
    main()