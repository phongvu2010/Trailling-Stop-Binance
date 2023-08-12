import pytz
import streamlit as st

from dataset import get_orders, get_prices, get_klines
from datetime import datetime
from streamer import Kline
from streamlit_autorefresh import st_autorefresh

from threading import Lock
from visualization import update

@st.cache_data(ttl = 60 * 60, show_spinner = False)
def get_data(symbol_order):
    return get_klines(symbol_order)

# Basic Page Configuration
# Find more emoji here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title = 'Trailling Stop Binance',
                   page_icon = '✅', layout = 'wide',
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

    delta = st.slider('Trailing Delta', value = 1.0,
                      min_value = 0.1, max_value = 10.0)

    columns = st.columns(2)
    with columns[0]:
        price = prices.at[symbol, 'price']
        act_price = st.number_input('Act Price', value = price,
                                    step = 0.00000001, format = '%.8f')

    with columns[1]:
        if type_order == 'Buy': limit = act_price * (1 + delta / 100)
        else: limit = act_price * (1 - delta / 100)
        limit_price = st.number_input('Limit Price', value = limit,
                                      step = 0.00000001, format = '%.8f')

    # Every form must have a submit button.
    with st.form('order_trailling_stop', clear_on_submit = True):
        submitted = st.form_submit_button('Add Order', type = 'primary',
                                           use_container_width = True)
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
    st.title('Trailling Stop on Binance')
    

    if not df_order.empty:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write(datetime.now(timezone))
            symbol_order = st.selectbox('Symbol',
                                        df_order['symbol'].unique(),
                                        label_visibility = 'collapsed')
        with col2:
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
            if not params:
                order.set_index('time_order', inplace = True)
                data = get_klines(symbol_order)
                update(data, placeholder, period, order.head(1), selected_ordered, Lock())
            else:
                if params['realtime']:
                    data = get_data(symbol_order)
                    Kline(data, symbol_order, placeholder, period, order.head(1), selected_ordered).run()
