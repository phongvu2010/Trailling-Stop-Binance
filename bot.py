import os
import websocket as wb
from pprint import pprint
import json

from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv      # pip3 install --upgrade

# load environment variables
load_dotenv()

# create client
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))




from datetime import datetime
from database_insert import create_table
from base_sql import Session
from models import CryptoPrice

# this functions creates the table if it does not exist
create_table()

# create a new session
session = Session()

BINANCE_SOCKET = 'wss://stream.binance.com:9443/stream?streams=ethusdt@kline_1m/btcusdt@kline_1m'
closed_prices = []


API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
client = Client(API_KEY, API_SECRET, tld='us')

def on_open(ws):
    print("connection opened")


def on_close(ws):
    print("closed connection")


def on_error(ws, error):
    print(error)


def on_message(ws, message):
    message = json.loads(message)
    pprint(message)
    candle = message['k']
    trade_symbol = message['s']
    is_candle_closed = candle['x']
    global closed_prices
    if is_candle_closed:
        symbol = candle['s']
        closed = candle['c']
        open = candle['o']
        high = candle['h']
        low = candle['l']
        volume = candle['v']
        pprint(f"closed: {closed}")
        pprint(f"open: {open}")
        pprint(f"high: {high}")
        pprint(f"low: {low}")
        pprint(f"volume: {volume}")
        closed_prices.append(float(closed))
        # create price entries
        crypto = CryptoPrice(crypto_name=symbol, open_price=open, close_price=closed,
                             high_price=high, low_price=low, volume=volume, time=datetime.utcnow())
        try:
            session.add(crypto)
            session.commit()
        except Exception as e:
            session.rollback()
            print(e)
        session.close()

ws = wb.WebSocketApp(BINANCE_SOCKET, on_open=on_open, on_close=on_close, on_error=on_error, on_message=on_message)
ws.run_forever()