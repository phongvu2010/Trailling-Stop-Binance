import pandas as pd
import streamlit as st
import time
import spreadsheet_api as ssheet
from binance.client import Client
from datetime import datetime

client = Client()

@st.cache_data(ttl = 60 * 60 * 1, show_spinner = False)
def get_orders(d_obj = {}):
    sheet = ssheet.SpreadSheets('1BO5ojBc7shuBcb5GDTPkb9wnU3Aj6KnK126rfsEoWIs')

    data = sheet.read_from_gsheet('Orders')
    data['time_order'] = pd.to_datetime(data['time_order'])
    data['act_price'] = data['act_price'].astype(float)
    data['limit_price'] = data['limit_price'].astype(float)
    data['delta'] = data['delta'].astype(float)

    if d_obj:
        df_obj = pd.DataFrame(list(d_obj.items())).set_index(0).T

        data = pd.concat([data, df_obj])
        data['time_order'] = pd.to_datetime(data['time_order'])
        data = data.sort_values(['time_order'], ascending = False)
        data = data.drop_duplicates(subset = 'symbol', keep = 'first')

        temp = data.copy()
        temp['time_order'] = temp['time_order'].dt.strftime('%Y-%m-%d %H:%M:%S')
        temp['act_price'] = temp['act_price'].astype(str)
        temp['limit_price'] = temp['limit_price'].astype(str)
        temp['delta'] = temp['delta'].astype(str)

        sheet.write_to_gsheet(temp, 'Orders')
        st.cache_data.clear()

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

    return df
