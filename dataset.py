import pandas as pd
import streamlit as st

from binance.client import Client
from datetime import datetime

client = Client()

@st.cache_data(ttl = 60 * 2, show_spinner = False)
def get_prices():
    df = pd.DataFrame(client.get_all_tickers())

    return df.set_index('symbol').astype('float').sort_index()

@st.cache_data(ttl = 60 * 5, show_spinner = False)
def get_klines(symbol, tick_interval = '5m'):
    df = pd.DataFrame(client.get_klines(symbol = symbol.upper(),
                                        interval = tick_interval,
                                        limit = 1000))
    df = df[df.columns[0:6]]
    df.rename(columns = {0: 'start_time', 1: 'open', 2: 'high',
                         3: 'low', 4: 'close', 5: 'volume'}, inplace = True)

    df['start_time'] = df['start_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
    df['start_time'] = pd.to_datetime(df['start_time'], utc = False)

    # df['start_time'] = df['start_time'].dt.tz_localize(tz = 'Asia/Ho_Chi_Minh')

    return df.set_index('start_time').astype('float').sort_index()
