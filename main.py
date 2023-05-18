import streamlit as st

from dataset import getPrices, getKlines, getKlines2
from datetime import datetime
from plotly import graph_objs as go
from plotly.subplots import make_subplots

# Basic Page Configuration
# Find more emoji here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title = st.secrets['page_title'],
                   page_icon = '📈', layout = 'wide',
                   initial_sidebar_state = 'expanded')

# Inject CSS with Markdown
with open('style.css') as f:
    st.markdown(f'<style>{ f.read() }</style>', unsafe_allow_html = True)

prices = getPrices()

with st.expander('Add Order Trailling Stop', expanded = False):
    with st.form('order_trailling_stop'):
        columns = st.columns(4)
        with columns[0]:
            displays = prices['symbol'].to_list()
            options = list(range(len(displays)))
            symbol = st.selectbox('Symbol', options, format_func = lambda x: displays[x])
        with columns[1]:
            date_order = st.date_input('Date Order', datetime.now())
        with columns[2]:
            act_price = st.number_input('Act Price', float(prices.at[symbol, 'price']), format = '%.8f')
        with columns[3]:
            detail = st.number_input('Trailing Delta', value = 0.5, min_value = 0.1, max_value = 10.0, step = 0.1, format = '%.2f')

        columns = st.columns(4)
        with columns[0]:
            type_order = st.selectbox('Type', ('Buy / Long', 'Sell / Short'), index = 0)
        with columns[1]:
            time_order = st.time_input('Time Order', datetime.now())
        with columns[2]:
            limit_price = st.number_input('Limit Price', float(prices.at[symbol, 'price']) * 0.9, format = '%.8f')

        # Every form must have a submit button.
        submitted = st.form_submit_button('Add Order', type = 'primary')

if submitted:
    st.write('Symbol', symbol)

data = getKlines2(prices.at[symbol, 'symbol'])
# data.set_index('time', inplace = True)

# st.line_chart(data[['open', 'close']])

fig = go.Figure()
fig.add_trace(
    go.Candlestick(
        x = data.index,
        open = data['open'],
        high = data['high'],
        low = data['low'],
        close = data['close'],
        increasing_line_color = 'green',
        decreasing_line_color = 'red',
        showlegend = False
    )
)
# fig.add_trace(go.Scatter(x = data['time'], y = data['close']))

fig.update_layout(
    go.Layout(
        autosize = True,
        height = 500,
        margin = go.layout.Margin(l = 10, r = 10, b = 5, t = 30, pad = 0),
        # xaxis = {'visible': False, 'showticklabels': True}
    )
)

# def update_y(y): y.ticksuffix = '      '
# fig.for_each_yaxis(update_y)

st.plotly_chart(fig, use_container_width = True)