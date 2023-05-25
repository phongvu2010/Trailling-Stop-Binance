# https://medium.com/@chris_42047/real-time-price-updates-from-binance-exchange-using-web-sockets-python-cd8374c50fcd
# https://dev.to/ken_mwaura1/crypto-data-bot-using-python-binance-websockets-and-postgresql-db-5fnd
import pandas as pd
import streamlit as st
import time  # to simulate a real time data, time loop

from binance.client import Client
from datetime import datetime
from plotly import graph_objs as go
from threading import Lock
from websockets import BinanceSocketManager

class CandleStick():
    def __init__(self, symbol, data):
        self.symbol = symbol
        self.data = data
        self.client = Client(st.secrets['binance']['api_key'], st.secrets['binance']['api_secret'])
        self.bm = BinanceSocketManager(self.client)
        self.lock = Lock()

    def handle_message(self, message):
        self.lock.acquire()

        time = datetime.fromtimestamp(message['k']['t'] / 1000)
        open = message['k']['o']
        high = message['k']['h']
        low = message['k']['l']
        close = message['k']['c']
        volume = message['k']['v']

        if time not in self.data.index:
            self.data.loc[time] = [open, high, low, close, volume]
        else:
            self.data.loc[self.data.index == time, 'open'] = open
            self.data.loc[self.data.index == time, 'high'] = high
            self.data.loc[self.data.index == time, 'low'] = low
            self.data.loc[self.data.index == time, 'close'] = close
            self.data.loc[self.data.index == time, 'volume'] = volume

        self.lock.release()

    def on_message(self, message):
        if 'k' in message:
            self.handle_message(message)

    def connect(self):
        print('LOG', 'Connecting to websocket')
        self.bm.start_kline_socket(self.symbol, callback = self.on_message, interval = '1m')
        self.bm.start()

data = pd.DataFrame(columns = ['open', 'high', 'low', 'close', 'volume'])

CandleStick('BTCUSDT', data).connect()

st.set_page_config(page_title = 'Real-Time / Live Data Science Dashboard',
                   page_icon = '✅', layout = 'wide')

# Inject CSS with Markdown
with open('style.css') as f:
    st.markdown(f'<style>{ f.read() }</style>', unsafe_allow_html = True)

st.title('Real-Time / Live Data Science Dashboard')

# creating a single-element container
placeholder = st.empty()

# near real-time / live feed simulation
for seconds in range(200):
    with placeholder.container():
        fig = go.Figure()
        fig.add_trace(
            go.Candlestick(
                x = data.index,
                open = data.open,
                high = data.high,
                low = data.low,
                close = data.close,
                increasing_line_color = 'green',
                decreasing_line_color = 'red',
                showlegend = False
            )
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
        st.dataframe(data, use_container_width = True)
        time.sleep(1)
