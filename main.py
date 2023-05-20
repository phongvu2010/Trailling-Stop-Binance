import pandas as pd
import streamlit as st

from dataset import getPrices, getKlines
from datetime import datetime
from plotly import graph_objs as go
# from plotly.subplots import make_subplots

# Basic Page Configuration
# Find more emoji here: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title = st.secrets['page_title'],
                   page_icon = '📈', layout = 'wide',
                   initial_sidebar_state = 'expanded')

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
            limit_price = st.number_input('Limit Price', float(prices.at[symbol, 'price']) * 0.9, format = '%.8f')

        detail = st.slider('Trailing Delta', value = 0.5, min_value = 0.1, max_value = 10.0, step = 0.1, format = '%.2f')

        # Every form must have a submit button.
        submitted = st.form_submit_button('Add Order', type = 'primary')

if submitted:
    add_order = {
        'symbol': prices.at[symbol, 'symbol'],
        'type': type_order,
        'date_order': datetime.combine(date_order, time_order),
        'act_price': round(act_price, 8),
        'limit_price': round(limit_price, 8),
        'delta': detail
    }
    df = pd.DataFrame(list(add_order.items())).set_index(0).T
    st.dataframe(df)
    # st.write('Delta', detail)


data = getKlines(prices.at[symbol, 'symbol'])

fig = go.Figure()
# fig.add_trace(
#     go.Scatter(
#         x = data.index,
#         y = data.close,
#         name = 'Price',
#         mode = 'lines'
#     )
# )

fig.add_trace(
    go.Candlestick(
        x = data.index,
        open = data.open,
        high = data.high,
        low = data.low,
        close = data.close,
        increasing_line_color = 'green',
        decreasing_line_color = 'red',
        showlegend = False
    )
)

fig.update_layout(
    go.Layout(
        autosize = True,
        margin = go.layout.Margin(l = 5, r = 5, b = 20, t = 20, pad = 8),
        xaxis_rangeslider_visible = False
    )
)

st.plotly_chart(fig, use_container_width = True)
