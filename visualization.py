import numpy as np
import pandas as pd
import streamlit as st

from plotly import graph_objs as go
from plotly.subplots import make_subplots

@st.cache_data(ttl = 60 * 5, show_spinner = False)
def getKlinesOrdered(data, order):
    df = data.join(order[['type', 'act_price', 'limit_price', 'delta']], how = 'outer')
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace = True)
    df.ffill(inplace = True)
    df.dropna(inplace = True)

    df['actived'] = np.where(df['type'] == 'Buy',
                             np.where(df['act_price'] > df['close'], df['act_price'], np.nan),
                             np.where(df['act_price'] < df['close'], df['act_price'], np.nan))
    df['actived'].ffill(inplace = True)

    # df['limited'] = np.where(df['type'] == 'Buy',
    #                          np.where((df['limit_price'] > df['low']) & df['actived'].notna(),
    #                                   df['limit_price'], np.nan),
    #                          np.where((df['limit_price'] < df['high']) & df['actived'].notna(),
    #                                   df['limit_price'], np.nan))
    # df['limited'].ffill(inplace = True)
    # limited = df.dropna(subset = ['limited'])
    # df = pd.concat([df[df['limited'].isna()], limited.head(1)])

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
    df['stoploss'] = np.where(df['stoploss'].isna(), df['limit_price'], df['stoploss'])

    df['cuttedloss'] = np.where(df['type'] == 'Buy',
                                np.where(df['stoploss'] < df['close'], df['stoploss'], np.nan),
                                np.where(df['stoploss'] > df['close'], df['stoploss'], np.nan))
    df['cuttedloss'].ffill(inplace = True)
    cuttedloss = df.dropna(subset = ['cuttedloss'])
    df = pd.concat([df[df['cuttedloss'].isna()], cuttedloss.head(1)])

    return df[['act_price', 'actived', 'stoploss', 'cuttedloss']]

def update(data, placeholder, period, order, selected_ordered, lock):
    lock.acquire()

    df = getKlinesOrdered(data, order)
    df = data.join(df, how = 'outer').reset_index()
    df.dropna(subset = ['close'], inplace = True)
    if selected_ordered:
        df.dropna(subset = ['act_price'], inplace = True)

    df = df.resample(period, on = 'index').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
        'act_price': 'last',
        'actived': 'last',
        'stoploss': 'last',
        'cuttedloss': 'last'
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
                marker = dict(color = colors),
                showlegend = False
            ), row = 2, col = 1
        )
        fig.append_trace(
            go.Scatter(
                x = df.index,
                y = df.act_price,
                line = dict(color = '#0303FC', width = 1),
                name = 'Active Price',
                showlegend = True
            ), row = 1, col = 1
        )
        fig.append_trace(
            go.Scatter(
                x = df.index,
                y = df.actived,
                line = dict(color = '#49FC03', dash = 'dot', width = 1),
                name = 'Actived Price',
                showlegend = True
            ), row = 1, col = 1
        )
        fig.append_trace(
            go.Scatter(
                x = df.index,
                y = df.stoploss,
                line = dict(color = '#F78502', dash = 'dashdot', width = 1),
                name = 'Stop Loss',
                showlegend = True
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
                    x = 0, y = 1.05,
                    xanchor = 'left',
                    yanchor = 'top'
                )
            )
        )
        st.plotly_chart(fig, use_container_width = True)

        st.markdown('### Detailed Data View ###')
        df.sort_index(ascending = False, inplace = True)
        df = df[["open", "high", "low", "close", "volume"]]
        df = df.style.format({"open": "{:.8f}",
                              "high": "{:.8f}",
                              "low": "{:.8f}",
                              "close": "{:.8f}",
                              "volume": "{:.2f}"})
        st.dataframe(df, use_container_width = True)

    lock.release()
