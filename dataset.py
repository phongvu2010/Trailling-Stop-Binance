import pandas as pd
import streamlit as st

from base_sql import save_klines
from binance.client import Client
from datetime import datetime

client = Client()

@st.cache_data(ttl = 60 * 2, show_spinner = False)
def get_prices():
    data = client.get_all_tickers()

    return pd.DataFrame(data).set_index('symbol').astype('float')

@st.cache_data(ttl = 60 * 60, show_spinner = False)
def get_klines(symbol, tick_interval = '5m'):
    data = client.get_klines(symbol = symbol.upper(), interval = tick_interval, limit = 1000)

    df = pd.DataFrame(data)
    df = df[df.columns[0:6]]
    df.rename(columns = {0: 'start_time', 1: 'open', 2: 'high',
                         3: 'low', 4: 'close', 5: 'volume'}, inplace = True)

    df['symbol'] = symbol
    df['start_time'] = df['start_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))

    df = df.set_index(['start_time', 'symbol']).astype('float').sort_index().reset_index()
    save_klines(df)

    return df[['start_time', 'open', 'high', 'low', 'close', 'volume']].set_index(['start_time'])
