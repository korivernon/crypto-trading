from constants import *
import ccxt

def stop_loss(security, percentage, account,against=USD):
    print(f"\nstop_loss(security={security}, percentage={percentage}, account={account})")
    symbol = f"{security}/{against}" 
    holding_qty = account.fetch_balance()[security]
    if int(holding_qty["free"]) == 0: 
        logging.error("Holding quantity is 0.")
        return False

    avg_purchase = 0
    orders = account.fetch_my_trades(symbol=symbol, since=1667086277)
    for order in orders:
        order_info = order["info"]
        if order_info["side"] == BUY:
            avg_purchase += float(order_info["price"]) * order["amount"] + order["fee"]["cost"]
    current_price = float(fetch_price([symbol])[symbol]["price"]) * float(holding_qty['free'])  
    threshold = (avg_purchase - avg_purchase * (percentage/100))
    if ( threshold > current_price ):
        logging.critical("Execute stop loss.")
        try:
            account.createMarketOrder (symbol, SELL, holding_qty["free"])
        except Exception:
            logging.error("Exchange order not placed")
            logging.critical("Cash Balance:" , get_balance(account), "Security Balance:",get_balance(account,against)["free"], "TOUSD: $", get_balance(account,against)["toUsd"], "Percentage", percentage, "Average purchase:", avg_purchase)
            return False
        logging.error("Exchange order executed")
        logging.critical("Cash Balance:" , get_balance(account),  "Security Balance:",get_balance(account,against)["free"], "TOUSD: $", get_balance(account,against)["toUsd"], percentage, "Average purchase:", avg_purchase)
        return True
    else:
        print("Do not execute stop loss.")
        print("unrealized profit/loss:",current_price - (avg_purchase))
    # account.create_order(security, SELL, security_balance )
    print("Cash Balance:" , get_balance(account), "Security Balance:",get_balance(account,against)["free"], "TOUSD: $", get_balance(account,against)["toUsd"], "TOUSD: $", get_balance(account,against)["toUsd"], "Percentage", percentage, "Average purchase:", avg_purchase)
    return False 

def realize_profits(security, percentage, account,against=USD):
    print(f"\nrealize_profits(security={security}, percentage={percentage}, account={account})")
    symbol = f"{security}/{against}"
    holding_qty = account.fetch_balance()[security]
    if int(holding_qty["free"]) == 0: 
        logging.error("Holding quantity is 0.")
        return False
    avg_purchase = 0
    orders = account.fetch_my_trades(symbol=symbol, since=1667086277)
    for order in orders:
        order_info = order["info"]
        if order_info["side"] == BUY:
            avg_purchase += float(order_info["price"]) * order["amount"] + order["fee"]["cost"]
    current_price = float(fetch_price([symbol])[symbol]["price"]) * float(holding_qty['free'])  
    threshold = (avg_purchase + avg_purchase * (percentage/100))
    # print("current price: ",current_price, "purchase price",avg_purchase , "threshold", threshold)
    if ( threshold < current_price ):
        logging.critical("Execute realize profits")
        try:
            account.createMarketOrder (symbol, SELL, holding_qty["free"])
        except Exception:
            logging.error("Exchange order not placed")
            logging.critical("Cash Balance: $" , get_balance(account)["free"], "Security Balance:",get_balance(account,against)["free"], "TOUSD: $", get_balance(account,against)["toUsd"], "TOUSD: $", get_balance(account,against)["toUsd"], "Percentage", percentage, "Average purchase:", avg_purchase)
            return False
        logging.error("Exchange order executed")
        logging.critical("Cash Balance: $" , get_balance(account)["free"], "Security Balance:",get_balance(account,against)["free"], "TOUSD: $", get_balance(account,against)["toUsd"], "Percentage", percentage, "Average purchase:", avg_purchase)
        return True
    else:
        print("Do not execute realize profits.")
        print("unrealized profit/loss:",current_price - (avg_purchase))
    # account.create_order(security, SELL, security_balance )
    print("Cash Balance: $" , get_balance(account)["free"],  "Security Balance:",get_balance(account,against)["free"], "TOUSD: $", get_balance(account,against)["toUsd"], "Percentage", percentage, "Average purchase:", avg_purchase)
    return False

def execute_market_sell_order(security, account, against=USD):
    print(f"\nexecute_market_sell_order(security={security}, account={account}, against={against})")
    symbol = f"{security}/{against}"
    holding_qty = account.fetch_balance()[security]

    if int(holding_qty["free"]) != 0: # need to make sure the holding quantity is basically zero.
        logging.critical("Executing Market Sell Order")
        try:
            account.createMarketOrder (symbol, SELL, holding_qty["free"])
        except Exception:
            logging.error("Exchange order not placed")
            # if against != USD:
            #     logging.critical("Cash Balance: $", get_balance(account)["free"], "Security Balance:",get_balance(account,against)["free"], "TOUSD: $", get_balance(account,against)["toUsd"])
            # else:
            #     logging.critical("Cash Balance: $", get_balance(account)["free"])
            return False
        logging.error("Exchange order executed")
    else:
        logging.error("Holding quantity is 0.")
        return False
    logging.critical("Cash Balance:" , get_balance(account)["free"], "Security Balance:",get_balance(account,against)["free"], "TOUSD: $", get_balance(account,against)["toUsd"])
    return True