import websocket
import json
import streamlit as st
import plotly.express as px
import pandas as pd
from threading import Thread, Lock
# from streamlit.script_run_context import add_script_run_ctx
from streamlit.runtime.scriptrunner.script_run_context import add_script_run_ctx
from datetime import datetime
import time

# def on_close(ws, close_status_code, close_msg):
#     print('LOG', 'Closed orderbook client')

def update(df_buy, df_sell, placeholder, lock):
    lock.acquire()

    with placeholder.container():
        # Create three columns
        kpi1, kpi2 = st.columns(2)
        current_sumSellVolumes = df_sell['Quantity'].sum()
        previous_sumSellVolumes = df_sell.iloc[:-1]['Quantity'].sum()
        current_sumBuyVolumes = df_buy['Quantity'].sum()
        previous_sumBuyVolumes = df_buy.iloc[:-1]['Quantity'].sum()

        # Fill in those three columns with respective metrics or KPIs
        kpi2.metric(label = 'Sell quantity 📉', value = round(current_sumSellVolumes, 2),
                    delta = round(current_sumSellVolumes - previous_sumSellVolumes, 2))

        kpi1.metric(label = 'Buy quantity 📈', value = round(current_sumBuyVolumes, 2),
                    delta = round(current_sumBuyVolumes - previous_sumBuyVolumes, 2))

        # Create two columns for charts
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.markdown('### Buy Volumes')
            fig = px.bar(data_frame = df_buy, x = df_buy.index, y = 'Quantity')
            st.write(fig)

        with fig_col2:
            st.markdown('### Sell Volumes')
            fig2 = px.bar(data_frame = df_sell, x = df_sell.index, y = 'Quantity')
            st.write(fig2)

        st.markdown('### Detailed Data View')
        st.dataframe(df_buy)
        st.dataframe(df_sell)

    lock.release()

class Kline():
    def __init__(self, symbol, df_buy, df_sell, placeholder):
        self.symbol = symbol
        self.df_buy = df_buy
        self.df_sell = df_sell
        self.placeholder = placeholder
        self.lock = Lock()
        self.url = 'wss://stream.binance.com:9443/ws'
        self.stream = f'{self.symbol.lower()}@aggTrade'
        self.times = []

    # def on_error(self, ws, error):
    #     print(self.times)
    #     print('ERROR', error)

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
            df = self.df_buy
        else:
            df = self.df_sell

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
                         args = (self.df_buy, self.df_sell, self.placeholder, self.lock,))
            add_script_run_ctx(thr)
            thr.start()

    def run(self):
        print('LOG', 'Connecting to websocket')
        self.ws = websocket.WebSocketApp(self.url,
                                        #  on_close = on_close,
                                        #  on_error = self.on_error,
                                         on_open = self.on_open,
                                         on_message = self.on_message)
        self.ws.run_forever()














# # from base_sql import Session, create_table
# from binance.streams import ThreadedWebsocketManager
# from datetime import datetime
# from models import CryptoPrice
# from plotly import graph_objs as go
# from pprint import pprint
# # from streamlit.runtime.scriptrunner.script_run_context import add_script_run_ctx#, get_script_run_ctx
# from threading import Thread, Lock

# def update(data, placeholder, lock):
#     lock.acquire()

#     with placeholder.container():
#         fig = go.Figure()
#         fig.add_trace(
#             go.Candlestick(
#                 x = data.index,
#                 open = data.open,
#                 high = data.high,
#                 low = data.low,
#                 close = data.close,
#                 increasing_line_color = 'green',
#                 decreasing_line_color = 'red',
#                 showlegend = False
#             )
#         )
#         fig.update_layout(
#             go.Layout(
#                 autosize = True, height = 450,
#                 margin = go.layout.Margin(l = 5, r = 5, b = 20, t = 20, pad = 8),
#                 xaxis_rangeslider_visible = False
#             )
#         )
#         st.plotly_chart(fig, use_container_width = True)

#         st.markdown('### Detailed Data View')
#         st.dataframe(data, use_container_width = True)

#     lock.release()

# class Kline():
#     def __init__(self, session, symbol, placeholder, interval = '5m', data = None):
#         self.session = session
#         self.placeholder = placeholder
#         self.data = data
#         self.symbol = symbol
#         self.interval = interval

#         # Socket manager using threads
#         self.twm = ThreadedWebsocketManager()
#         self.lock = Lock()

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

#     def handle_socket_message(self, msg):
#         if 'k' in msg:
#             self.handle_message(msg['k'])

#             thr = Thread(target = update, args = (self.data, self.placeholder, self.lock)).start()
#             # add_script_run_ctx(thr)
#             # thr.start()
#         pprint(msg['k'])

#     def run(self):
#         # Start is required to initialise its interal loop
#         self.twm.start()

#         self.twm.start_kline_socket(symbol = self.symbol, interval = self.interval, callback = self.handle_socket_message)

#         # Join the threaded managers to the main thread
#         self.twm.join()













# # This functions creates the table if it does not exist
# create_table()

# # Create a new session
# session = Session()

# data = pd.DataFrame(columns = ['open', 'high', 'low', 'close', 'volume'])

# Kline(session, 'BNBBTC', data = data).run()

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