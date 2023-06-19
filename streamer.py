import json
import pandas as pd
import streamlit as st
import websocket

from datetime import datetime
from models import CryptoPrice
from plotly import graph_objs as go
from plotly.subplots import make_subplots
# from pprint import pprint
from streamlit.runtime.scriptrunner.script_run_context import add_script_run_ctx
from threading import Thread, Lock

def on_close(ws, close_status_code, close_msg):
    print('LOG:', close_status_code)
    print(close_msg)

def on_error(ws, error):
    print('ERROR:', error)

def update(df, placeholder, lock):
    lock.acquire()

    with placeholder.container():
        with st.container():
            fig = make_subplots(rows = 1, cols = 1)
            fig.append_trace(
                go.Candlestick(
                    x = df.index,
                    open = df.open,
                    high = df.high,
                    low = df.low,
                    close = df.close,
                    increasing_line_color = 'green',
                    decreasing_line_color = 'red',
                    showlegend = False
                ), row = 1, col = 1
            )
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
    def __init__(self, session, symbol, placeholder, interval = '5m', df = None):
        self.session = session
        self.symbol = symbol
        self.placeholder = placeholder
        self.interval = interval
        self.df = df
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

        if isinstance(self.df, pd.DataFrame):
            if timestamp not in self.df.index:
                self.df.loc[timestamp] = [open_price, high_price, low_price, close_price, volume]
            else:
                self.df.loc[self.df.index == timestamp, 'open'] = open_price
                self.df.loc[self.df.index == timestamp, 'high'] = high_price
                self.df.loc[self.df.index == timestamp, 'low'] = low_price
                self.df.loc[self.df.index == timestamp, 'close'] = close_price
                self.df.loc[self.df.index == timestamp, 'volume'] = volume

        if candle['x']:
            try:
                # Create price entries
                price = CryptoPrice(start_time = timestamp,
                                    symbol = symbol,
                                    open = open_price,
                                    high = high_price,
                                    low = low_price,
                                    close = close_price,
                                    volume = volume)
                self.session.add(price)
                self.session.commit()
            except Exception as e:
                self.session.rollback()
                print(e)
            finally:
                self.session.close()

        self.lock.release()

    def on_message(self, ws, message):
        message = json.loads(message)
        if 'k' in message:
            # pprint(message['k'])
            self.handle_message(message['k'])
            thr = Thread(target = update, args = (self.df, self.placeholder, self.lock))
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