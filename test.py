import pandas as pd
import streamlit as st

from base_sql import Session, create_table
from streamer import Kline

# This functions creates the table if it does not exist
create_table()

# Create a new session
session = Session()

# data = pd.DataFrame(columns = ['open', 'high', 'low', 'close', 'volume'])
data = pd.DataFrame(columns = [ 'Price', 'Quantity', 'USD Value'])

st.set_page_config(page_title = 'Real-Time Data Science Dashboard', page_icon = '✅', layout = 'wide')

st.title('Real-Time / Live Data Science Dashboard')

# Creating a single-element container
placeholder = st.empty()

Kline(session, 'BTCUSDT', placeholder, interval = '5m', df = data).run()
