# https://medium.com/@chris_42047/real-time-price-updates-from-binance-exchange-using-web-sockets-python-cd8374c50fcd
# https://dev.to/ken_mwaura1/crypto-data-bot-using-python-binance-websockets-and-postgresql-db-5fnd

import asyncio

# from binance.client import Client, 
from binance.streams import BinanceSocketManager
from binance import AsyncClient#, BinanceSocketManager

# from binance.enums import *

async def main():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    ts = bm.kline_socket('BNBBTC')
    # then start receiving messages
    async with ts as tscm:
        while True:
            res = await tscm.recv()
            print(res)

    await client.close_connection()

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())









# import pandas as pd
# # import streamlit as st
# import time  # to simulate a real time data, time loop
# import websocket

# # from binance.client import Client
# from datetime import datetime
# # from plotly import graph_objs as go
# from threading import Lock
# # from websockets import BinanceSocketManager

# class CandleStick():
#     def __init__(self, symbol, data):
#         self.symbol = symbol
#         self.data = data
#         self.uri = f'wss://stream.binance.com:9443/ws/{symbol}@kline_1m'
#         self.websocket = websocket
#         # self.client = Client(st.secrets['binance']['api_key'], st.secrets['binance']['api_secret'])
#         # self.bm = BinanceSocketManager(self.client)
#         self.lock = Lock()

#     def handle_message(self, ws, message):
#         self.lock.acquire()

#         time = datetime.fromtimestamp(message['k']['t'] / 1000)
#         open = message['k']['o']
#         high = message['k']['h']
#         low = message['k']['l']
#         close = message['k']['c']
#         volume = message['k']['v']

#         if time not in self.data.index:
#             self.data.loc[time] = [open, high, low, close, volume]
#         else:
#             self.data.loc[self.data.index == time, 'open'] = open
#             self.data.loc[self.data.index == time, 'high'] = high
#             self.data.loc[self.data.index == time, 'low'] = low
#             self.data.loc[self.data.index == time, 'close'] = close
#             self.data.loc[self.data.index == time, 'volume'] = volume

#         self.lock.release()

#     def on_message(self, ws, message):
#         if 'k' in message:
#             self.handle_message(message)
#         print(message)

#     def connect(self):
#         print('LOG', 'Connecting to websocket')
#         self.websocket.WebSocketApp(self.uri, on_message = self.on_message).run_forever()
#         # self.bm.start_kline_socket(self.symbol, callback = self.on_message, interval = '1m')
#         # self.bm.start()

# data = pd.DataFrame(columns = ['open', 'high', 'low', 'close', 'volume'])

# CandleStick('btcusdt', data).connect()
