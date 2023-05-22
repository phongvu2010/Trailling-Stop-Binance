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
                   page_icon = '✅', layout = 'centered',
                   initial_sidebar_state = 'auto')

# Inject CSS with Markdown
with open('style.css') as f:
    st.markdown(f'<style>{ f.read() }</style>', unsafe_allow_html = True)

prices = getPrices().set_index('symbol').astype('float')

path_order_file = 'data/Orders.csv'
df_order = pd.DataFrame()
if path.exists(path_order_file):
    df_order = pd.read_csv(path_order_file)

@st.cache_data(ttl = 300, show_spinner = False)
def getKlinesOrdered(symbol, order):
    data = getKlines(symbol)
    order.set_index('time_order', inplace = True)

    df = data.join(order, how = 'outer')
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace = True)
    df.ffill(inplace = True)
    df.dropna(inplace = True)
    df = df[['symbol', 'type', 'open', 'high', 'low', 'close',
             'volume', 'act_price', 'limit_price', 'delta']]

    df = df.astype({'open': 'float', 'high': 'float', 'low': 'float',
                    'close': 'float', 'volume': 'float', 'act_price': 'float',
                    'limit_price': 'float', 'delta': 'float'})

    df['actived'] = np.where(df['type'] == 'Buy',
                             np.where(df['act_price'] > df['low'], df['act_price'], np.nan),
                             np.where(df['act_price'] < df['high'], df['act_price'], np.nan))
    df['actived'].ffill(inplace = True)

    df['limited'] = np.where(df['type'] == 'Buy',
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
        if a.at[i, 'type'] == 'Buy':
            b = a.at[i, 'low']
            df_.at[i, 'stoploss'] = b * (1 + (a.at[i, 'delta'] / 100)) \
                if b <= min(a['low'].to_list()) else np.nan
        else:
            b = a.at[i, 'high']
            df_.at[i, 'stoploss'] = b * (1 - (a.at[i, 'delta'] / 100)) \
                if b >= max(a['high'].to_list()) else np.nan
    df['stoploss'] = df_['stoploss'].ffill()

    df['cuttedloss'] = np.where(df['type'] == 'Buy',
                                np.where(df['stoploss'] < df['close'], df['close'], np.nan),
                                np.where(df['stoploss'] > df['close'], df['close'], np.nan))
    df['cuttedloss'].ffill(inplace = True)
    cuttedloss = df.dropna(subset = ['cuttedloss'])

    df = pd.concat([df[df['cuttedloss'].isna()], cuttedloss.head(1)])

    return df

with st.sidebar:
    # with st.expander('Add Order', expanded = True):
        columns = st.columns(2)
        with columns[0]:
            symbol = st.selectbox('Symbol', prices.index.to_list())

        with columns[1]:
            type_order = st.selectbox('Type', ('Buy', 'Sell'))

        columns = st.columns(2)
        with columns[0]:
            date_order = st.date_input('Date Order')

        with columns[1]:
            time_order = st.time_input('Time Order')

        columns = st.columns(2)
        with columns[0]:
            price = prices.at[symbol, 'price']
            act_price = st.number_input('Act Price', price, step = 0.00000001, format = '%.8f')

        with columns[1]:
            if type_order == 'Buy': limit = act_price * 0.95
            else: limit = act_price * 1.05
            limit_price = st.number_input('Limit Price', limit, step = 0.00000001, format = '%.8f')

        detail = st.slider('Trailing Delta', value = 0.5, min_value = 0.1, max_value = 10.0)

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

    symbol_order = st.selectbox('Symbol', df_order['symbol'].to_list(), label_visibility = 'collapsed')

    with st.expander('Ordered Detail', expanded = False):
        order = df_order[df_order['symbol'] == symbol_order]
        st.write(order.to_dict('records'))

    freqs = ['5min', '15min', '30min', '1H', '2H', '4H']
    period = st.radio('Period', freqs, index = 3, horizontal = True, label_visibility = 'collapsed')

    df = getKlinesOrdered(symbol_order, order).reset_index()
    df = df.resample(period, on = 'index').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'act_price': 'last',
        'actived': 'last',
        'limit_price': 'last',
        'stoploss': 'last'
        })

    # data = getKlines(symbol)
    # df = pd.concat([df, data])

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
            legend = dict(orientation = 'h', yanchor = 'top', y = 1.03, xanchor = 'left', x = 0)
        )
    )
    st.plotly_chart(fig, use_container_width = True)

    # st.dataframe(df, use_container_width = True)
