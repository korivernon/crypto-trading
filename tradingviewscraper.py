"""
A python script/bot which will collect (scrape) TradingView Signals for a list of coins.
Original Code by Michael Goode
Modified 7/15/2018 by Joaquin Roibal (@BlockchainEng)

Modified 7/4/2023 by Kori Vernon
"""
import pandas as pd
import requests, json, time, datetime

def mlog(market, *text):
	text = [str(i) for i in text]
	text = " ".join(text)
	datestamp = str(datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3])
	print("[{} {}] - {}".format(datestamp, market, text))


def get_signal(market, candle):
	headers = {'User-Agent': 'Mozilla/5.0'}
	url = "https://scanner.tradingview.com/crypto/scan"

	payload =	{
					"symbols": {
						"tickers": ["GEMINI:{}".format(market)],
						"query": { "types": [] }
					},
					"columns": [
						"Recommend.Other|{}".format(candle),
						"Recommend.All|{}".format(candle),
						"Recommend.MA|{}".format(candle),
						"RSI|{}".format(candle),
						"RSI[1]|{}".format(candle),
						"Stoch.K|{}".format(candle),
						"Stoch.D|{}".format(candle),
						"Stoch.K[1]|{}".format(candle),
						"Stoch.D[1]|{}".format(candle),
						"CCI20|{}".format(candle),
						"CCI20[1]|{}".format(candle),
						"ADX|{}".format(candle),
						"ADX+DI|{}".format(candle),
						"ADX-DI|{}".format(candle),
						"ADX+DI[1]|{}".format(candle),
						"ADX-DI[1]|{}".format(candle),
						"AO|{}".format(candle),
						"AO[1]|{}".format(candle),
						"Mom|{}".format(candle),
						"Mom[1]|{}".format(candle),
						"MACD.macd|{}".format(candle),
						"MACD.signal|{}".format(candle),
						"Rec.Stoch.RSI|{}".format(candle),
						"Stoch.RSI.K|{}".format(candle),
						"Rec.WR|{}".format(candle),
						"W.R|{}".format(candle),
						"Rec.BBPower|{}".format(candle),
						"BBPower|{}".format(candle),
						"Rec.UO|{}".format(candle),
						"UO|{}".format(candle),
						"EMA10|{}".format(candle),
						"close|{}".format(candle),
						"SMA10|{}".format(candle),
						"EMA20|{}".format(candle),
						"SMA20|{}".format(candle),
						"EMA30|{}".format(candle),
						"SMA30|{}".format(candle),
						"EMA50|{}".format(candle),
						"SMA50|{}".format(candle),
						"EMA100|{}".format(candle),
						"SMA100|{}".format(candle),
						"EMA200|{}".format(candle),
						"SMA200|{}".format(candle),
						"Rec.Ichimoku|{}".format(candle),
						"Ichimoku.BLine|{}".format(candle),
						"Rec.VWMA|{}".format(candle),
						"VWMA|{}".format(candle),
						"Rec.HullMA9|{}".format(candle),
						"HullMA9|{}".format(candle),
						"Pivot.M.Classic.S3|{}".format(candle),
						"Pivot.M.Classic.S2|{}".format(candle),
						"Pivot.M.Classic.S1|{}".format(candle),
						"Pivot.M.Classic.Middle|{}".format(candle),
						"Pivot.M.Classic.R1|{}".format(candle),
						"Pivot.M.Classic.R2|{}".format(candle),
						"Pivot.M.Classic.R3|{}".format(candle),
						"Pivot.M.Fibonacci.S3|{}".format(candle),
						"Pivot.M.Fibonacci.S2|{}".format(candle),
						"Pivot.M.Fibonacci.S1|{}".format(candle),
						"Pivot.M.Fibonacci.Middle|{}".format(candle),
						"Pivot.M.Fibonacci.R1|{}".format(candle),
						"Pivot.M.Fibonacci.R2|{}".format(candle),
						"Pivot.M.Fibonacci.R3|{}".format(candle),
						"Pivot.M.Camarilla.S3|{}".format(candle),
						"Pivot.M.Camarilla.S2|{}".format(candle),
						"Pivot.M.Camarilla.S1|{}".format(candle),
						"Pivot.M.Camarilla.Middle|{}".format(candle),
						"Pivot.M.Camarilla.R1|{}".format(candle),
						"Pivot.M.Camarilla.R2|{}".format(candle),
						"Pivot.M.Camarilla.R3|{}".format(candle),
						"Pivot.M.Woodie.S3|{}".format(candle),
						"Pivot.M.Woodie.S2|{}".format(candle),
						"Pivot.M.Woodie.S1|{}".format(candle),
						"Pivot.M.Woodie.Middle|{}".format(candle),
						"Pivot.M.Woodie.R1|{}".format(candle),
						"Pivot.M.Woodie.R2|{}".format(candle),
						"Pivot.M.Woodie.R3|{}".format(candle),
						"Pivot.M.Demark.S1|{}".format(candle),
						"Pivot.M.Demark.Middle|{}".format(candle),
						"Pivot.M.Demark.R1|{}".format(candle)
					]
				}

	resp = requests.post(url,headers=headers,data=json.dumps(payload)).json()
	signal = oscillator = resp["data"][0]["d"][1]

	return signal


def decide_decision(weight):
	if weight > 2:
		return "BUY"
	elif  -2 < weight <= 2:
		return "HOLD"
	else:
		return "SELL"


def check_signals():

	market_list = ["BTCUSDT", "ETHUSDT", "LTCUSD", "ETHBTC"]
	market_decode = {'BTCUSDT': {'buy':'BTC','with':'USDT'},
					 'ETHUSDT': {'buy':'ETH','with':'USDT'},
					 'LTCUSD': {'buy':'LTC', 'with':'USD'},
					 'ETHBTC': {'buy':'ETH', 'with':'BTC'} }
	candle_list = [5, 60, 240] #Represented in minutes
	signals_list = []
	df = pd.DataFrame(columns=['market','buy','with','5m','5m action','5m weight','60m','60m action','60m weight','240m','240m action','240m weight'])
	signals_security_dict = {}
	for candle in candle_list:
		signal1 = []
		msg = "Crypto Buy/Sell Signals from @tradingview - {} min candle\n\n".format(candle)
		for market in market_list:
			if market not in signals_security_dict.keys():
				signals_security_dict[market] = {'market':market,'buy':market_decode[market]['buy'],'with':market_decode[market]['with']}

			mlog(market, "{}, {} minute candle. TradingView".format(market, candle))
			signal = round(get_signal(market, candle),3)
			signals_security_dict[market][f'{candle}m'] = signal
			signal1.append(signal)
			msg += "{} {} : ".format(market, signal)
			if signal>0.5:
				add_action = "STRONG BUY"
				weight = 2
			elif signal>0:
				add_action = "BUY"
				weight = 1
			elif signal>-0.5:
				add_action = "SELL"
				weight = -1
			else:
				add_action = "STRONG SELL"
				weight = -2
			signals_security_dict[market][f'{candle}m action'] = add_action
			signals_security_dict[market][f'{candle}m weight'] = weight
			msg += add_action + '\n'
			mlog(market, signal)
		signals_list.append(signal1)
		print(msg)
	for key, value in signals_security_dict.items():
		df = pd.concat([df, pd.DataFrame(value, index=[0])], ignore_index=True)
	df['total weight'] = df.loc[:, ['5m weight', '60m weight','240m weight']].sum(axis=1)

	df['decision'] = df.apply(lambda x: decide_decision(x['total weight']),axis=1)
	return df

if __name__ == "__main__":
	print(check_signals())
