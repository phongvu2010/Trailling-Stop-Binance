import pandas as pd
import pytz
import streamlit as st

from dataset import get_prices, get_klines
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from os import path
from visualization import update

# Basic Page Configuration
# Find more emoji here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title = 'Trailling Stop Binance',
                   page_icon = '✅', layout = 'centered',
                   initial_sidebar_state = 'collapsed')

# Inject CSS with Markdown
with open('style.css') as f:
    st.markdown(f'<style>{ f.read() }</style>', unsafe_allow_html = True)

prices = get_prices()

path_file_orders = 'orders.csv'
if path.isfile(path_file_orders):
    df_order = pd.read_csv(path_file_orders)
else: df_order = pd.DataFrame()

# Run the autorefresh about every 300000 milliseconds (300 seconds)
# and stop after it's been refreshed 100 times.
st_autorefresh(interval = 300000, limit = 100, key = 'refresh_page')

with st.sidebar:
    columns = st.columns(2)
    with columns[0]:
        symbol = st.selectbox('Symbol', prices.index.to_list())

    with columns[1]:
        type_order = st.selectbox('Type', ('Buy', 'Sell'))

    timezone = pytz.timezone('Asia/Ho_Chi_Minh')
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
        act_price = st.number_input('Act Price', value = price, step = 0.00000001, format = '%.8f')

    with columns[1]:
        if type_order == 'Buy': limit = act_price * (1 - limit_detail)
        else: limit = act_price * (1 + limit_detail)
        limit_price = st.number_input('Limit Price', value = limit, step = 0.00000001, format = '%.8f')

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
            df_add_order = pd.DataFrame(list(add_order.items())).set_index(0).T
            df_order = pd.concat([df_order, df_add_order]) \
                        .sort_values(['time_order'], ascending = False) \
                        .drop_duplicates(subset = 'symbol', keep = 'first') \
                        .reset_index(drop = True)
            df_order.to_csv(path_file_orders, index = False)

with st.container():
    st.title('Trailling Stop on Binance')
    import time
    st.write(time.strftime('%Z', time.localtime()))
    st.write(datetime.now(timezone).strftime('%d/%m/%Y, %H:%M:%S'))

    if not df_order.empty:
        symbol_order = st.selectbox('Symbol',
                                    df_order['symbol'].unique(),
                                    label_visibility = 'collapsed')

        with st.expander('Ordered Detail', expanded = False):
            order = df_order[df_order['symbol'] == symbol_order]
            st.write(order.to_dict('records')[0])

        col1, col2 = st.columns([3, 1])
        with col1:
            freqs = ['5min', '15min', '30min', '1H', '2H', '4H']
            period = st.radio('Period', freqs, index = 1,
                              horizontal = True, label_visibility = 'visible')
        with col2:
            selected_ordered = st.radio('By Order', (False, True),
                                        horizontal = True, label_visibility = 'visible')

        # Creating a single-element container
        placeholder = st.empty()

        if not order.empty:
            order.set_index('time_order', inplace = True)
            data = get_klines(symbol_order)
            update(data, placeholder, period, order.head(1), selected_ordered)
