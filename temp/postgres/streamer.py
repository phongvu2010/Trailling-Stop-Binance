# https://dev.to/ken_mwaura1/crypto-data-bot-using-python-binance-websockets-and-postgresql-db-5fnd
# https://discuss.streamlit.io/t/high-frequency-updates-from-websocket/36732

import json
import pandas as pd
import websocket

from datetime import datetime
from base_sql import save_klines
from streamlit.runtime.scriptrunner.script_run_context import add_script_run_ctx
from threading import Thread, Lock
from visualization import update

def on_close(ws, close_status_code, close_msg):
    print('LOG:', close_status_code)
    print(close_msg)

def on_error(ws, error):
    print('ERROR:', error)

class Kline():
    def __init__(self, df, symbol, placeholder, period, order, selected_ordered, interval = '5m'):
        self.df = df
        self.symbol = symbol
        self.placeholder = placeholder
        self.period = period
        self.order = order
        self.selected_ordered = selected_ordered
        self.interval = interval
        self.lock = Lock()

        self.url = 'wss://stream.binance.com:9443/ws'
        self.stream = f'{self.symbol.lower()}@kline_{self.interval}'

    def on_open(self, ws):
        print('LOG:', f'Opening WebSocket stream for {self.symbol}')

        subscribe_message = {'method': 'SUBSCRIBE', 'params': [self.stream], 'id': 1}
        ws.send(json.dumps(subscribe_message))

    def handle_message(self, candle):
        self.lock.acquire()

        timestamp = datetime.fromtimestamp(int(candle['t']) / 1000)
        symbol = candle['s']
        open_price = float(candle['o'])
        high_price = float(candle['h'])
        low_price = float(candle['l'])
        close_price = float(candle['c'])
        volume = float(candle['v'])

        if timestamp not in self.df.index:
            self.df.loc[timestamp] = [open_price, high_price, low_price, close_price, volume]
        else:
            self.df.loc[self.df.index == timestamp, 'open'] = open_price
            self.df.loc[self.df.index == timestamp, 'high'] = high_price
            self.df.loc[self.df.index == timestamp, 'low'] = low_price
            self.df.loc[self.df.index == timestamp, 'close'] = close_price
            self.df.loc[self.df.index == timestamp, 'volume'] = volume

        if candle['x']:
            df_temp = pd.DataFrame()
            df_temp.loc[1, 'start_time'] = timestamp
            df_temp.loc[1, 'symbol'] = symbol
            df_temp.loc[1, 'open'] = open_price
            df_temp.loc[1, 'high'] = high_price
            df_temp.loc[1, 'low'] = low_price
            df_temp.loc[1, 'close'] = close_price
            df_temp.loc[1, 'volume'] = volume
            save_klines(df_temp)

        self.lock.release()

    def on_message(self, ws, message):
        message = json.loads(message)
        if 'k' in message:
            self.handle_message(message['k'])
            thr = Thread(target = update, args = (self.df, self.placeholder, self.period,
                                                  self.order, self.selected_ordered, self.lock))
            add_script_run_ctx(thr)
            thr.start()

    def run(self):
        self.ws = websocket.WebSocketApp(self.url,
                                         on_close = on_close,
                                         on_error = on_error,
                                         on_open = self.on_open,
                                         on_message = self.on_message)
        self.ws.run_forever()

# {
#     'e': 'kline',
#     'E': 1686999646296,
#     's': 'BNBBTC',
#     'k': {
#         't': 1686999600000,
#         'T': 1686999659999,
#         's': 'BNBBTC',
#         'i': '1m',
#         'f': 223785814,
#         'L': 223785873,
#         'o': '0.00928400',
#         'c': '0.00927800',
#         'h': '0.00928500',
#         'l': '0.00927800',
#         'v': '60.79000000',
#         'n': 60,
#         'x': False,
#         'q': '0.56432172',
#         'V': '17.87400000',
#         'Q': '0.16593718',
#         'B': '0'
#     }
# }