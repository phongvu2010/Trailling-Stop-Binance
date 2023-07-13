import pandas as pd
import pytz
import streamlit as st

from dataset import get_orders, get_prices
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Basic Page Configuration
# Find more emoji here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title = 'Trailling Stop Binance',
                   page_icon = '✅', layout = 'centered',
                   initial_sidebar_state = 'collapsed')

# Inject CSS with Markdown
with open('style.css') as f:
    st.markdown(f'<style>{ f.read() }</style>', unsafe_allow_html = True)

params = st.experimental_get_query_params()
timezone = pytz.timezone('Asia/Ho_Chi_Minh')
df_order = get_orders()
prices = get_prices()

# Run the autorefresh about every 300000 milliseconds (300 seconds)
# and stop after it's been refreshed 100 times.
if not params:
    st_autorefresh(interval = 300000, limit = 100, key = 'refresh_page')

with st.sidebar:
    columns = st.columns(2)
    with columns[0]:
        symbol = st.selectbox('Symbol', prices.index.to_list())

    with columns[1]:
        type_order = st.selectbox('Type', ('Buy', 'Sell'))

    columns = st.columns(2)
    with columns[0]:
        date_order = st.date_input('Date Order', datetime.now(timezone))

    with columns[1]:
        time_order = st.time_input('Time Order', datetime.now(timezone))

    limit_detail = st.slider('Limit Delta', value = 0.01,
                             min_value = 0.01, max_value = 0.1)

    columns = st.columns(2)
    with columns[0]:
        price = prices.at[symbol, 'price']
        act_price = st.number_input('Act Price', value = price,
                                    step = 0.00000001, format = '%.8f')

    with columns[1]:
        if type_order == 'Buy': limit = act_price * (1 - limit_detail)
        else: limit = act_price * (1 + limit_detail)
        limit_price = st.number_input('Limit Price', value = limit,
                                      step = 0.00000001, format = '%.8f')

    delta = st.slider('Trailing Delta', value = 0.5,
                      min_value = 0.1, max_value = 10.0)

    # Every form must have a submit button.
    with st.form('order_trailling_stop', clear_on_submit = True):
        submitted = st.form_submit_button('Add Order', type = 'primary',
                                           use_container_width = True,)
        if submitted:
            add_order = {
                'time_order': datetime.combine(date_order, time_order),
                'symbol': symbol,
                'type': type_order,
                'act_price': round(act_price, 8),
                'limit_price': round(limit_price, 8),
                'delta': delta
            }
            df_order = get_orders(add_order)

with st.container():
    st.dataframe(df_order)