import websocket
import json
import streamlit as st
import plotly.express as px
import pandas as pd
import time

from datetime import datetime
from threading import Thread, Lock
from streamlit.runtime.scriptrunner.script_run_context import add_script_run_ctx
from plotly.subplots import make_subplots
from plotly import graph_objs as go

# from base_sql import Session, create_table
# from binance.streams import ThreadedWebsocketManager
# from models import CryptoPrice

# from pprint import pprint

def update(df, placeholder, lock):
    lock.acquire()

    with placeholder.container():
        with st.container():
            fig = make_subplots(rows = 1, cols = 1)
            fig.append_trace(
                go.Bar(
                    x = df.index,
                    y = df.Quantity,
                    showlegend = False
                ), row = 1, col = 1
            )
            # fig.append_trace(
            #     go.Candlestick(
            #         x = df.index,
            #         open = df.open,
            #         high = df.high,
            #         low = df.low,
            #         close = df.close,
            #         increasing_line_color = 'green',
            #         decreasing_line_color = 'red',
            #         showlegend = False
            #     ), row = 1, col = 1
            # )
            fig.update_layout(
                go.Layout(
                    autosize = True, height = 450,
                    margin = go.layout.Margin(l = 5, r = 5, b = 20, t = 20, pad = 8),
                    xaxis_rangeslider_visible = False
                )
            )
            st.plotly_chart(fig, use_container_width = True)

            st.markdown('### Detailed Data View')
            st.dataframe(df, use_container_width = True)

    lock.release()

class Kline():        
    def __init__(self, symbol, df, placeholder):
    # def __init__(self, session, symbol, placeholder, interval = '5m', data = None):
        self.symbol = symbol
        self.df = df
        self.placeholder = placeholder
        self.lock = Lock()
        self.url = 'wss://stream.binance.com:9443/ws'
        self.stream = f'{self.symbol.lower()}@aggTrade'
#         self.session = session
#         self.data = data
#         self.interval = interval
#         # Socket manager using threads
#         self.twm = ThreadedWebsocketManager()

        self.times = []

    def on_open(self, ws):
        print('LOG', f'Opening WebSocket stream for {self.symbol}')

        subscribe_message = {'method': 'SUBSCRIBE',
                             'params': [self.stream],
                             'id': 1}
        ws.send(json.dumps(subscribe_message))

    def handle_message(self, message):
        self.lock.acquire()

        timestamp = datetime.utcfromtimestamp(int(message['T']) / 1000)
        price = float(message['p'])
        qty = float(message['q'])
        USDvalue = price * qty
        side = 'BUY' if message['m'] == False else 'SELL'

        if side == 'BUY':
            df = self.df
        else:
            df = self.df

        if timestamp not in df.index:
            df.loc[timestamp] = [price, qty, USDvalue]
        else:
            df.loc[df.index == timestamp, 'Quantity'] += qty
            df.loc[df.index == timestamp, 'USD Value'] += USDvalue

        self.lock.release()

    def on_message(self, ws, message):
        message = json.loads(message)
        self.times.append(time.time())
        if 'e' in message:
            self.handle_message(message)

            thr = Thread(target = update,
                         args = (self.df, self.placeholder, self.lock,))
            add_script_run_ctx(thr)
            thr.start()

#     def handle_socket_message(self, msg):
#         if 'k' in msg:
#             self.handle_message(msg['k'])

#             thr = Thread(target = update, args = (self.data, self.placeholder, self.lock)).start()
#             # add_script_run_ctx(thr)
#             # thr.start()
#         pprint(msg['k'])

    def run(self):
        print('LOG', 'Connecting to websocket')
        # Start is required to initialise its interal loop
        # self.twm.start()
        # self.twm.start_kline_socket(symbol = self.symbol, interval = self.interval, callback = self.handle_socket_message)

        # Join the threaded managers to the main thread
        # self.twm.join()

        self.ws = websocket.WebSocketApp(self.url,
                                        #  on_close = on_close,
                                        #  on_error = self.on_error,
                                         on_open = self.on_open,
                                         on_message = self.on_message)
        self.ws.run_forever()



















#     def handle_message(self, candle):
#         self.lock.acquire()

#         time = datetime.fromtimestamp(candle['t'] / 1000)
#         if isinstance(self.data, pd.DataFrame):
#             if time not in self.data.index:
#                 self.data.loc[time] = [candle['o'], candle['h'], candle['l'], candle['c'], candle['v']]
#             else:
#                 self.data.loc[self.data.index == time, 'open'] = candle['o']
#                 self.data.loc[self.data.index == time, 'high'] = candle['h']
#                 self.data.loc[self.data.index == time, 'low'] = candle['l']
#                 self.data.loc[self.data.index == time, 'close'] = candle['c']
#                 self.data.loc[self.data.index == time, 'volume'] = candle['v']

#         if candle['x']:
#             # Create price entries
#             crypto = CryptoPrice(start_time = time,
#                                  symbol = candle['s'],
#                                  open = candle['o'],
#                                  high = candle['h'],
#                                  low = candle['l'],
#                                  close = candle['c'],
#                                  volume = candle['v'])
#             try:
#                 self.session.add(crypto)
#                 self.session.commit()
#             except Exception as e:
#                 self.session.rollback()
#                 print(e)
#             finally:
#                 self.session.close()

#         self.lock.release()


















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