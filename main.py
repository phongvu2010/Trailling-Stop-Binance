import pandas as pd
import pytz
import streamlit as st

from base_sql import Session, create_table
from dataset import getPrices, getKlines
from datetime import datetime
from os import path
from streamer import Kline
# from streamlit_autorefresh import st_autorefresh

# This functions creates the table if it does not exist
create_table()

# Create a new session
session = Session()

# Basic Page Configuration
# Find more emoji here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title = 'Trailling Stop Binance',
                   page_icon = '✅', layout = 'centered',
                   initial_sidebar_state = 'expanded')

# Inject CSS with Markdown
with open('style.css') as f:
    st.markdown(f'<style>{ f.read() }</style>', unsafe_allow_html = True)

# if 'detail_slider' not in st.session_state:
#     # Set the initial default value of the slider widget
#     st.session_state.detail_slider = ''

path_order_file = 'data/Orders.csv'
if path.exists(path_order_file):
    df_order = pd.read_csv(path_order_file)
    df_order['time_order'] = pd.to_datetime(df_order['time_order'])
else: df_order = pd.DataFrame()

prices = getPrices()
timezone = pytz.timezone('Asia/Ho_Chi_Minh')

# Run the autorefresh about every 300000 milliseconds (300 seconds)
# and stop after it's been refreshed 100 times.
# st_autorefresh(interval = 300000, limit = 100, key = 'refresh_page')

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

    limit_detail = st.slider('Limit Delta', value = 0.01, min_value = 0.01, max_value = 0.1)

    columns = st.columns(2)
    with columns[0]:
        price = prices.at[symbol, 'price']
        act_price = st.number_input('Act Price', value = price, step = 0.00000001, format = '%.8f')

    with columns[1]:
        if type_order == 'Buy': limit = act_price * (1 - limit_detail)
        else: limit = act_price * (1 + limit_detail)
        limit_price = st.number_input('Limit Price', value = limit, step = 0.00000001, format = '%.8f')

    detail = st.slider('Trailing Delta', value = 0.5, min_value = 0.1, max_value = 10.0, key = 'detail_slider')

    # Every form must have a submit button.
    with st.form('order_trailling_stop', clear_on_submit = True):
        submitted = st.form_submit_button('Add Order', type = 'primary', use_container_width = True)

        if submitted:
            add_order = {
                'time_order': datetime.combine(date_order, time_order),
                'symbol': symbol,
                'type': type_order,
                'act_price': round(act_price, 8),
                'limit_price': round(limit_price, 8),
                'delta': detail
            }
            df_add_order = pd.DataFrame(list(add_order.items())).set_index(0).T
            df_order = pd.concat([df_order, df_add_order]) \
                        .drop_duplicates(subset = 'symbol', keep = 'last') \
                        .sort_values('time_order', ascending = False) \
                        .reset_index(drop = True)
            df_order.to_csv(path_order_file, index = False)

with st.container():
    st.title('Trailling Stop on Binance')

    st.write(datetime.now(timezone).strftime("%d/%m/%Y, %H:%M:%S"))

    symbol_order = st.selectbox('Symbol', df_order['symbol'].to_list(), label_visibility = 'collapsed')

    with st.expander('Ordered Detail', expanded = False):
        order = df_order[df_order['symbol'] == symbol_order]
        st.write(order.to_dict('records')[0])

    col1, col2 = st.columns([3, 1])
    with col1:
        freqs = ['5min', '15min', '30min', '1H', '2H', '4H']
        period = st.radio('Period', freqs, index = 0, horizontal = True, label_visibility = 'visible')
    with col2:
        selected_ordered = st.radio('By Order', (False, True), horizontal = True, label_visibility = 'visible')


#     df = getKlinesOrdered(data, order)
#     df = data.join(df, how = 'outer').reset_index()
#     if selected_ordered:
#         df.dropna(subset = ['act_price'], inplace = True)

#     df = df.resample(period, on = 'index').agg({
#         'open': 'first',
#         'high': 'max',
#         'low': 'min',
#         'close': 'last',
#         'volume': 'sum',
#         'act_price': 'last',
#         'actived': 'last',
#         'limit_price': 'last',
#         'stoploss': 'last'
#         })

#     colors = []
#     for i in range(len(df.close)):
#         if i != 0:
#             if df.close[i] > df.close[i - 1]:
#                 colors.append('green')
#             else:
#                 colors.append('red')
#         else:
#             colors.append('red')

#     fig = make_subplots(rows = 2, cols = 1, row_heights = [80, 20], shared_xaxes = True, vertical_spacing = 0)
#     fig.append_trace(
#         go.Candlestick(
#             x = df.index,
#             open = df.open,
#             high = df.high,
#             low = df.low,
#             close = df.close,
#             increasing_line_color = 'green',
#             decreasing_line_color = 'red',
#             showlegend = False
#         ), row = 1, col = 1
#     )
#     fig.append_trace(
#         go.Bar(
#             x = df.index,
#             y = df.volume,
#             marker = dict(
#                 color = colors
#             ),
#             showlegend = False
#         ), row = 2, col = 1
#     )
#     fig.append_trace(
#         go.Scatter(
#             x = df.index,
#             y = df.act_price,
#             line = dict(color = '#034EFF', width = 1, dash = 'dot'),
#             name = 'Act Price',
#             showlegend = True,
#             mode = 'lines'
#         ), row = 1, col = 1
#     )
#     fig.append_trace(
#         go.Scatter(
#             x = df.index,
#             y = df.actived,
#             line = dict(color = '#BEF702', width = 1),
#             name = 'Actived',
#             showlegend = True,
#             mode = 'lines'
#         ), row = 1, col = 1
#     )
#     fig.append_trace(
#         go.Scatter(
#             x = df.index,
#             y = df.limit_price,
#             line = dict(color = '#FF4E03', width = 1, dash = 'dot'),
#             name = 'Limit Price',
#             showlegend = True,
#             mode = 'lines'
#         ), row = 1, col = 1
#     )
#     fig.append_trace(
#         go.Scatter(
#             x = df.index,
#             y = df.stoploss,
#             line = dict(color = '#F78502', width = 1),
#             name = 'StopLoss',
#             showlegend = True,
#             mode = 'lines'
#         ), row = 1, col = 1
#     )
#     fig.update_layout(
#         go.Layout(
#             autosize = True, height = 500,
#             margin = go.layout.Margin(l = 5, r = 5, b = 5, t = 10, pad = 5),
#             hovermode = 'x',
#             xaxis_rangeslider_visible = False,
#             yaxis_autorange = True,
#             legend = dict(
#                 orientation = 'h',
#                 x = 0, y = 0.98,
#                 xanchor = 'left',
#                 yanchor = 'top'
#             )
#         )
#     )
#     st.plotly_chart(fig, use_container_width = True)

#     # st.dataframe(df, use_container_width = True)

# Creating a single-element container
placeholder = st.empty()

data = getKlines(symbol_order)
# data = pd.DataFrame(columns = ['open', 'high', 'low', 'close', 'volume'])
Kline(session, data, symbol_order, placeholder).run()






# import numpy as np

# from plotly import graph_objs as go
# from plotly.subplots import make_subplots




# @st.cache_data(ttl = 300, show_spinner = False)
# def getKlinesOrdered(data, order):
#     order.set_index('time_order', inplace = True)

#     df = data.join(order, how = 'outer')
#     df.index = pd.to_datetime(df.index)
#     df.sort_index(inplace = True)
#     df.ffill(inplace = True)
#     df.dropna(inplace = True)

#     df['actived'] = np.where(df['type'] == 'Buy',
#                              np.where(df['act_price'] > df['low'], df['act_price'], np.nan),
#                              np.where(df['act_price'] < df['high'], df['act_price'], np.nan))
#     df['actived'].ffill(inplace = True)

#     df['limited'] = np.where(df['type'] == 'Buy',
#                              np.where((df['limit_price'] > df['low']) & df['actived'].notna(),
#                                       df['limit_price'], np.nan),
#                              np.where((df['limit_price'] < df['high']) & df['actived'].notna(),
#                                       df['limit_price'], np.nan))
#     df['limited'].ffill(inplace = True)
#     limited = df.dropna(subset = ['limited'])

#     df = pd.concat([df[df['limited'].isna()], limited.head(1)])

#     df['stoploss'] = np.nan
#     df_ = df.copy().dropna(subset = ['actived'])
#     for i in df_.index:
#         a = df_.loc[:i, ['high', 'low', 'close', 'type', 'delta']]
#         if a.at[i, 'type'] == 'Buy':
#             b = a.at[i, 'low']
#             df_.at[i, 'stoploss'] = b * (1 + (a.at[i, 'delta'] / 100)) \
#                 if b <= min(a['low'].to_list()) else np.nan
#         else:
#             b = a.at[i, 'high']
#             df_.at[i, 'stoploss'] = b * (1 - (a.at[i, 'delta'] / 100)) \
#                 if b >= max(a['high'].to_list()) else np.nan
#     df['stoploss'] = df_['stoploss'].ffill()

#     df['cuttedloss'] = np.where(df['type'] == 'Buy',
#                                 np.where(df['stoploss'] < df['close'], df['close'], np.nan),
#                                 np.where(df['stoploss'] > df['close'], df['close'], np.nan))
#     df['cuttedloss'].ffill(inplace = True)
#     cuttedloss = df.dropna(subset = ['cuttedloss'])

#     df = pd.concat([df[df['cuttedloss'].isna()], cuttedloss.head(1)])

#     return df[['act_price', 'limit_price', 'delta', 'actived', 'limited', 'stoploss', 'cuttedloss']]
