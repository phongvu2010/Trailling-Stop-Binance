# import os
import websocket as wb
from pprint import pprint
import json

import pandas as pd
import websocket

from binance.client import Client
from datetime import datetime
from threading import Lock
from binance.streams import BinanceSocketManager, ThreadedWebsocketManager

from base_sql import Session, create_table
from binance.client import Client
# from binance.enums import *
from datetime import datetime
from dotenv import load_dotenv
from models import CryptoPrice

# This functions creates the table if it does not exist
create_table()

# Load environment variables
load_dotenv()

# Create a new session
session = Session()

# Create client
# API_KEY = os.environ.get('API_KEY')
# API_SECRET = os.environ.get('API_SECRET')
twm = ThreadedWebsocketManager()

BINANCE_SOCKET = 'wss://stream.binance.com:9443/btcusdt@kline_1m'
closed_prices = []

def handle_socket_message(ws, message):
    message = json.loads(message)
    pprint(message)

    # candle = message['k']
    # trade_symbol = message['s']
    # is_candle_closed = candle['x']

    # global closed_prices
    # if is_candle_closed:
    #     symbol = candle['s']
    #     closed = candle['c']
    #     open = candle['o']
    #     high = candle['h']
    #     low = candle['l']
    #     volume = candle['v']

    #     pprint(f'closed: {closed}')
    #     pprint(f'open: {open}')
    #     pprint(f'high: {high}')
    #     pprint(f'low: {low}')
    #     pprint(f'volume: {volume}')

    #     closed_prices.append(float(closed))

    #     # Create price entries
    #     crypto = CryptoPrice(crypto_name = symbol, open_price = open, close_price = closed,
    #                          high_price = high, low_price = low, volume = volume, time = datetime.utcnow())

    #     try:
    #         session.add(crypto)
    #         session.commit()
    #     except Exception as e:
    #         session.rollback()
    #         print(e)
    #     finally:
    #         session.close()

# start is required to initialise its internal loop
twm.start()
twm.start_kline_socket(callback = handle_socket_message, symbol = 'BTCUSDT')



