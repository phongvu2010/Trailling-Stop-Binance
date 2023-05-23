import pandas as pd
import streamlit as st

from binance.client import Client
from datetime import datetime
from os import path

# client = Client(st.secrets['binance']['api_key'], st.secrets['binance']['api_secret'])
client = Client()

@st.cache_data(ttl = 120, show_spinner = False)    # Cache data for 2 minute
def getPrices():
    return pd.DataFrame(client.get_all_tickers())

@st.cache_data(ttl = 300, show_spinner = False)    # Cache data for 5 minute
def getKlines(symbol, interval = Client.KLINE_INTERVAL_5MINUTE):
    df = pd.DataFrame(client.get_klines(symbol = symbol.upper(), interval = interval, limit = 1000))
    df = df[df.columns[0:6]]

    df.rename(columns = {0: 'time', 1: 'open', 2: 'high',
                         3: 'low', 4: 'close', 5: 'volume'},
              inplace = True)
    df.time = df.time.apply(lambda x: datetime.fromtimestamp(x / 1000))

    path_file = 'data/' + symbol.upper() + '.feather'
    if path.exists(path_file):
        df_ = pd.read_feather(path_file)
        df = pd.concat([df, df_]).drop_duplicates(subset = 'time', keep = 'first')
        df.reset_index(drop = True, inplace = True)
    df.to_feather(path_file)

    return df.set_index('time').sort_index()
