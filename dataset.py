import pandas as pd
# import requests
import streamlit as st

from base_sql import engine
from binance.client import Client
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

client = Client()

@st.cache_data(ttl = 60 * 2, show_spinner = False)
def getPrices():
    # endpoint = 'https://api.binance.com/api/v3/ticker/price'
    # data = requests.get(endpoint).json()
    data = client.get_all_tickers()

    return pd.DataFrame(data).set_index('symbol').astype('float')

@st.cache_data(ttl = 60 * 60, show_spinner = False)
def getKlines(symbol, tick_interval = '5m'):
    # endpoint = 'https://api.binance.com/api/v3/klines?symbol=' + symbol + '&interval=' + tick_interval
    # data = requests.get(endpoint).json()
    data = client.get_klines(symbol = symbol.upper(), interval = tick_interval, limit = 1000)

    df = pd.DataFrame(data)
    df = df[df.columns[0:6]]
    df.rename(columns = {0: 'start_time', 1: 'open', 2: 'high',
                         3: 'low', 4: 'close', 5: 'volume'}, inplace = True)

    df['symbol'] = symbol
    df['start_time'] = df['start_time'].apply(lambda x: datetime.fromtimestamp(x / 1000))

    df = df.set_index(['start_time', 'symbol']).astype('float').sort_index().reset_index()

    df.to_sql('price_data_temp', engine, if_exists = 'replace', index = False)
    try:
        with engine.connect() as conn:
            conn.execute(text('''
                INSERT INTO public.price_data (start_time, symbol, open, high, low , close, volume)
                SELECT * FROM public.price_data_temp
                ON CONFLICT (start_time, symbol) DO NOTHING;
            '''))

            conn.execute(text('''DROP TABLE price_data_temp;'''))
            conn.commit()
    except SQLAlchemyError as e:
        conn.rollback()
        print(str(e))
    finally:
        conn.close()

    # path_file = 'data/' + symbol.upper() + '.feather'
    # if path.exists(path_file):
    #     df_ = pd.read_feather(path_file)
    #     df = pd.concat([df, df_])
    #     df = df.drop_duplicates(subset = 'time', keep = 'first').reset_index(drop = True)
    # df.to_feather(path_file)

    return df[['start_time', 'open', 'high', 'low', 'close', 'volume']].set_index(['start_time'])

df = getKlines('BNBETH')
# print(df)
