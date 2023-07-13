import numpy as np
import pandas as pd
import streamlit as st

from plotly import graph_objs as go
from plotly.subplots import make_subplots

@st.cache_data(ttl = 60 * 5, show_spinner = False)
def getKlinesOrdered(data, order):
    df = data.join(order, how = 'outer')
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace = True)
    df.ffill(inplace = True)
    df.dropna(inplace = True)

    df['actived'] = np.where(df['type'] == 'Buy',
                             np.where(df['act_price'] > df['low'], df['act_price'], np.nan),
                             np.where(df['act_price'] < df['high'], df['act_price'], np.nan))
    df['actived'].ffill(inplace = True)

    # df['limited'] = np.where(df['type'] == 'Buy',
    #                          np.where((df['limit_price'] > df['low']) & df['actived'].notna(),
    #                                   df['limit_price'], np.nan),
    #                          np.where((df['limit_price'] < df['high']) & df['actived'].notna(),
    #                                   df['limit_price'], np.nan))
    # df['limited'].ffill(inplace = True)
    # # limited = df.dropna(subset = ['limited'])
    # # df = pd.concat([df[df['limited'].isna()], limited.head(1)])

    df['stoploss'] = np.nan
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

    return df[[
        # 'act_price',
        'limit_price',
        # 'delta',
        'actived',
        # 'limited',
        'stoploss',
        # 'cuttedloss'
    ]]

def update(data, placeholder, period, order, selected_ordered, lock):
    lock.acquire()

    df = getKlinesOrdered(data, order)
    df = data.join(df, how = 'outer').reset_index()
    if selected_ordered:
        df.dropna(subset = ['stoploss'], inplace = True)

    df = df.resample(period, on = 'index').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
        # 'act_price': 'last',
        'actived': 'last',
        'limit_price': 'last',
        'stoploss': 'last'
    })

    with placeholder.container():
        colors = []
        for i in range(len(df.close)):
            if i != 0:
                if df.close[i] > df.close[i - 1]:
                    colors.append('green')
                else:
                    colors.append('red')
            else:
                colors.append('red')

        fig = make_subplots(rows = 2, cols = 1, row_heights = [80, 20],
                            shared_xaxes = True, vertical_spacing = 0)
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
            go.Bar(
                x = df.index,
                y = df.volume,
                marker = dict(
                    color = colors
                ),
                showlegend = False
            ), row = 2, col = 1
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
                autosize = True, height = 500,
                margin = go.layout.Margin(l = 5, r = 5, b = 5, t = 10, pad = 5),
                hovermode = 'x',
                xaxis_rangeslider_visible = False,
                yaxis_autorange = True,
                legend = dict(
                    orientation = 'h',
                    x = 0, y = 0.98,
                    xanchor = 'left',
                    yanchor = 'top'
                )
            )
        )
        st.plotly_chart(fig, use_container_width = True)

        st.markdown('### Detailed Data View ###')
        st.dataframe(df[['open', 'high', 'low', 'close', 'volume']].sort_index(ascending = False),
                     use_container_width = True)

    lock.release()
