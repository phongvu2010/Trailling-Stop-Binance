import pandas as pd
import streamlit as st
import time

# from base_sql import engine, save_klines
from binance.client import Client
from datetime import datetime
from os import path

client = Client()

@st.cache_data(ttl = 60 * 60 * 1, show_spinner = False)
def get_orders(d_obj = {}):
    path_file_orders = 'orders.csv'
    if path.isfile(path_file_orders):
        data = pd.read_csv(path_file_orders)
    else: data = pd.DataFrame()

    if d_obj:
        df_obj = pd.DataFrame(list(d_obj.items())).set_index(0).T

        data = pd.concat([data, df_obj])
        data['time_order'] = pd.to_datetime(data['time_order'])
        data = data.sort_values(['time_order'], ascending = False)
        data = data.drop_duplicates(subset = 'symbol', keep = 'first')

        data.to_csv(path_file_orders, index = False)

    return data.reset_index(drop = True)

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
    timezone = time.strftime('%Z', time.localtime())
    if timezone == 'UTC':
        df['start_time'] = df['start_time'] + pd.Timedelta(hours = 7)
    df = df.set_index('start_time').astype('float').sort_index()

    # if engine:
    #     temp = df.copy().reset_index()
    #     temp['symbol'] = symbol

    #     save_klines(temp)

    return df
