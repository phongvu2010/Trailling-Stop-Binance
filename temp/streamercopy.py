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

def on_close(ws, close_status_code, close_msg):
    print('LOG', 'Closed orderbook client')


def update(df_buy,df_sell, placeholder, lock):
    lock.acquire()
    with placeholder.container():
        # create three columns
        kpi1, kpi2 = st.columns(2)
        current_sumSellVolumes = df_sell['Quantity'].sum()
        previous_sumSellVolumes = df_sell.iloc[:-1]['Quantity'].sum()
        current_sumBuyVolumes = df_buy['Quantity'].sum()
        previous_sumBuyVolumes = df_buy.iloc[:-1]['Quantity'].sum()
        # fill in those three columns with respective metrics or KPIs
        kpi2.metric(label="Sell quantity 📉", value=round(current_sumSellVolumes, 2),
                    delta=round(current_sumSellVolumes - previous_sumSellVolumes, 2))
        kpi1.metric(label="Buy quantity 📈", value=round(current_sumBuyVolumes, 2),
                    delta=round(current_sumBuyVolumes - previous_sumBuyVolumes, 2))

        # create two columns for charts

        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.markdown("### Buy Volumes")
            fig = px.bar(data_frame=df_buy, x=df_buy.index, y='Quantity')
            st.write(fig)
        with fig_col2:
            st.markdown("### Sell Volumes")
            fig2 = px.bar(data_frame=df_sell, x=df_sell.index, y='Quantity')
            st.write(fig2)
        st.markdown("### Detailed Data View")
        st.dataframe(df_buy)
        st.dataframe(df_sell)
    lock.release()


class Stream():
    def __init__(self, df_buy, df_sell, placeholder):
        self.symbol = 'BTCUSDT'
        self.df_buy = df_buy
        self.df_sell = df_sell
        self.placeholder = placeholder
        self.lock = Lock()
        self.url = "wss://stream.binance.com:9443/ws"
        self.stream = f"{self.symbol.lower()}@aggTrade"
        self.times = []

    def on_error(self, ws, error):
        print(self.times)
        print('ERROR', error)

    def on_open(self, ws):
        print('LOG', f'Opening WebSocket stream for {self.symbol}')

        subscribe_message = {"method": "SUBSCRIBE",
                             "params": [self.stream],
                             "id": 1}
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

            thr = Thread(target=update, args=(self.df_buy, self.df_sell, self.placeholder, self.lock,))
            add_script_run_ctx(thr)
            thr.start()


    def connect(self):
        print('LOG', 'Connecting to websocket')
        self.ws = websocket.WebSocketApp(self.url, on_close=on_close, on_error=self.on_error,
                                         on_open=self.on_open, on_message=self.on_message)
        self.ws.run_forever()