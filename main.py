import numpy as np
import pandas as pd
import streamlit as st

from dataset import getPrices, getKlines
from datetime import datetime
from os import path
from plotly import graph_objs as go
from plotly.subplots import make_subplots

# Basic Page Configuration
# Find more emoji here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title = st.secrets['page_title'],
                   page_icon = '✅', layout = 'wide',
                   initial_sidebar_state = 'collapsed')

# Inject CSS with Markdown
with open('style.css') as f:
    st.markdown(f'<style>{ f.read() }</style>', unsafe_allow_html = True)

prices = getPrices()

with st.sidebar:
    with st.form('order_trailling_stop', clear_on_submit = True):
        columns = st.columns(2)
        with columns[0]:
            displays = prices['symbol'].to_list()
            options = list(range(len(displays)))
            symbol = st.selectbox('Symbol', options, format_func = lambda x: displays[x])

        with columns[1]:
            type_order = st.selectbox('Type', ('Buy / Long', 'Sell / Short'), index = 0)

        columns = st.columns(2)
        with columns[0]:
            date_order = st.date_input('Date Order', datetime.now())

        with columns[1]:
            time_order = st.time_input('Time Order', datetime.now())

        columns = st.columns(2)
        with columns[0]:
            act_price = st.number_input('Act Price', float(prices.at[symbol, 'price']), format = '%.8f')

        with columns[1]:
            limit_price = st.number_input('Limit Price', format = '%.8f')

        detail = st.slider('Trailing Delta', value = 0.5,
                           min_value = 0.1, max_value = 10.0,
                           step = 0.1, format = '%.2f')

        # Every form must have a submit button.
        submitted = st.form_submit_button('Add Order', type = 'primary')

    if submitted & (act_price > 0) & (limit_price > 0):
        add_order = {
            'time_order': datetime.combine(date_order, time_order),
            'symbol': prices.at[symbol, 'symbol'],
            'type': type_order,
            'act_price': round(act_price, 8),
            'limit_price': round(limit_price, 8),
            'delta': detail
        }
        df = pd.DataFrame(list(add_order.items())).set_index(0).T

        path_file = 'data/Orders.csv'
        if path.exists(path_file):
            df_ = pd.read_csv(path_file)
            df = pd.concat([df, df_]).drop_duplicates(subset = 'symbol', keep = 'first')
            df.reset_index(drop = True, inplace = True)
        df.to_csv(path_file, index = False)

orders = pd.read_csv('data/Orders.csv')

@st.cache_data(ttl = 300)
def getKlinesOrdered(symbol_name):
    order = orders[orders['symbol'] == symbol_name]
    order.set_index('time_order', inplace = True)

    data = getKlines(symbol_name)

    df = data.join(order, how = 'outer')
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace = True)
    df.ffill(inplace = True)
    df.dropna(inplace = True)
    # df.reset_index(drop = True, inplace = True)
    df = df.astype({'open': 'float', 'high': 'float', 'low': 'float',
                    'close': 'float', 'volume': 'float', 'act_price': 'float',
                    'limit_price': 'float', 'delta': 'float'})
    df['actived'] = np.where(df['type'] == 'Buy / Long',
                            np.where(df['act_price'] > df['low'], df['act_price'], np.nan),
                            np.where(df['act_price'] < df['high'], df['act_price'], np.nan))
    df['actived'].ffill(inplace = True)
    df['limited'] = np.where(df['type'] == 'Buy / Long',
                            np.where((df['limit_price'] > df['low']) & df['actived'].notna(),
                                     df['limit_price'], np.nan),
                            np.where((df['limit_price'] < df['high']) & df['actived'].notna(),
                                     df['limit_price'], np.nan))
    df['limited'].ffill(inplace = True)
    limited = df.dropna(subset = ['limited'])

    df = pd.concat([df[df['limited'].isna()], limited.head(1)])

    df_ = df.copy().dropna(subset = ['actived'])
    for i in df_.index:
        a = df_.loc[:i, ['high', 'low', 'close', 'type', 'delta']]
        b = a.at[i, 'low']
        if a.at[i, 'type'] == 'Buy / Long':
            df_.at[i, 'stoploss'] = b * (1 + a.at[i, 'delta'] / 100) if b <= min(a['low'].to_list()) else np.nan
        else:
            df_.at[i, 'stoploss'] = b * (1 - a.at[i, 'delta'] / 100) if b >= max(a['high'].to_list()) else np.nan
    df['stoploss'] = df_['stoploss'].ffill()

    df['cuttedloss'] = np.where(df['type'] == 'Buy / Long',
                                np.where(df['stoploss'] < df['close'], df['close'], np.nan),
                                np.where(df['stoploss'] > df['close'], df['close'], np.nan))
    df['cuttedloss'].ffill(inplace = True)
    cuttedloss = df.dropna(subset = ['cuttedloss'])

    df = pd.concat([df[df['cuttedloss'].isna()], cuttedloss.head(1)])

    return df

with st.container():
    st.title('Trailling Stop on Binance')

    st.subheader('Ordered List ')
    st.dataframe(orders, use_container_width = True)

    cols = st.columns(5)
    symbol_name = cols[0].selectbox('Symbol', orders['symbol'].to_list(), label_visibility = 'collapsed')

    df = getKlinesOrdered(symbol_name)
    
    fig = make_subplots(rows = 1, cols = 1)
    fig.append_trace(
        go.Candlestick(
            x = df.index,
            open = df.open,
            high = df.high,
            low = df.low,
            close = df.close,
            increasing_line_color = 'green',
            decreasing_line_color = 'red',
            showlegend = False
        ), row = 1, col = 1
    )
    fig.append_trace(
        go.Scatter(
            x = df.index,
            y = df.act_price,
            line = dict(color = '#034EFF', width = 1, dash = 'dot'),
            name = 'Act Price',
            showlegend = True,
            mode = 'lines'
        ), row = 1, col = 1
    )
    fig.append_trace(
        go.Scatter(
            x = df.index,
            y = df.actived,
            line = dict(color = '#BEF702', width = 1),
            name = 'Actived',
            showlegend = True,
            mode = 'lines'
        ), row = 1, col = 1
    )
    fig.append_trace(
        go.Scatter(
            x = df.index,
            y = df.limit_price,
            line = dict(color = '#FF4E03', width = 1, dash = 'dot'),
            name = 'Limit Price',
            showlegend = True,
            mode = 'lines'
        ), row = 1, col = 1
    )
    fig.append_trace(
        go.Scatter(
            x = df.index,
            y = df.limited,
            line = dict(color = '#02F7F7', width = 1),
            name = 'Limited',
            showlegend = True,
            mode = 'lines'
        ), row = 1, col = 1
    )
    fig.append_trace(
        go.Scatter(
            x = df.index,
            y = df.stoploss,
            line = dict(color = '#F78502', width = 1),
            name = 'StopLoss',
            showlegend = True,
            mode = 'lines'
        ), row = 1, col = 1
    )
    fig.update_layout(
        go.Layout(
            autosize = True,
            margin = go.layout.Margin(l = 5, r = 5, b = 5, t = 30, pad = 8),
            xaxis_rangeslider_visible = False,
            # legend = dict(yanchor = 'top', y = 1, xanchor = 'left', x = 0)
            legend = dict(orientation = 'h', yanchor = 'top', y = 1.03, xanchor = 'left', x = 0)
        )
    )
    st.plotly_chart(fig, use_container_width = True)

    st.dataframe(df, use_container_width = True)
