import pandas as pd
import streamlit as st

from binance.client import Client
from os import path

client = Client()

# @st.cache_data(ttl = 60 * 60 * 1, show_spinner = False)
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
