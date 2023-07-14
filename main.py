# import pandas as pd
import pytz
import streamlit as st

# from base_sql import engine, get_orders, save_orders
from dataset import get_orders, get_prices, get_klines
from datetime import datetime
# from streamer import Kline
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from streamlit_autorefresh import st_autorefresh

# from threading import Lock
# from visualization import update

@st.cache_data(ttl = 60 * 60, show_spinner = False)
def get_data(symbol_order):
    return get_klines(symbol_order)

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
    st.title('Trailling Stop on Binance')
    st.write(datetime.now(timezone).strftime('%d/%m/%Y, %H:%M'))

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

        # # Creating a single-element container
        # placeholder = st.empty()

        # if not order.empty:
        #     order.set_index('time_order', inplace = True)
        #     if not params:
        #         data = get_klines(symbol_order)
        #         update(data, placeholder, period, order.head(1), selected_ordered, Lock())
        #     else:
        #         if params['realtime']:
        #             data = get_data(symbol_order)
        #             Kline(data, symbol_order, placeholder, period, order.head(1), selected_ordered).run()

# https://stackoverflow.com/questions/74449270/python-streamlit-aggrid-add-new-row-to-aggrid-table
with st.container():
    # checkbox_renderer = JsCode("""
    #     class CheckboxRenderer {
    #         init(params) {
    #             this.params = params;
    #             this.eGui = document.createElement('input');
    #             this.eGui.type = 'checkbox';
    #             this.eGui.checked = params.value;
    #             this.checkedHandler = this.checkedHandler.bind(this);
    #             this.eGui.addEventListener('click', this.checkedHandler);
    #         }
    #         checkedHandler(e) {
    #             let checked = e.target.checked;
    #             let colId = this.params.column.colId;
    #             this.params.node.setDataValue(colId, checked);
    #         }
    #         getGui(params) {
    #             return this.eGui;
    #         }
    #         destroy(params) {
    #             this.eGui.removeEventListener('click', this.checkedHandler);
    #         }
    #     } //end class
    # """)

    gb = GridOptionsBuilder.from_dataframe(df_order)
    # Add pagination
    # gb.configure_pagination(enabled = True,
    #                         paginationAutoPageSize = False,
    #                         paginationPageSize = 15)

    # gb.configure_default_column(resizable = True, filterable = True,
    #                             sortable = True, editable = True, groupable = False)
    # gb.configure_column(field = 'symbol',
    #                     header_name = 'Mã CK',
    #                     editable = False,
    #                     width = 60)
    # gb.configure_column(field = 'market',
    #                     header_name = 'Sàn',
    #                     cellEditor = 'agSelectCellEditor',
    #                     cellEditorParams = {'values': ['HNX', 'HSX', 'UPCOM']},
    #                     width = 60)
    # gb.configure_column(field = 'company_name',
    #                     header_name = 'Tên công ty',
    #                     valueFormatter = 'value.toUpperCase()')
    # gb.configure_column(field = 'enabled',
    #                     header_name = 'Niêm yết',
    #                     cellRenderer = checkbox_renderer,
    #                     width = 60)

    # Add a sidebar
    # gb.configure_side_bar(filters_panel = True, columns_panel = True)

    # Enable multi-row selection
    gb.configure_selection(selection_mode = 'multiple', use_checkbox = False,
                           groupSelectsChildren = 'Group checkbox select children')
    gridOptions = gb.build()

    # grid_response = m.list_aggrid(data_companies, gridOptions)
    grid_response = AgGrid(
        df_order, gridOptions = gridOptions, reload_data = False,
        data_return_mode = 'AS_INPUT',
        update_mode = 'SELECTION_CHANGED',
        fit_columns_on_grid_load = True,
        # Add theme color to the table: alpine, balham, material, streamlit 
        # theme = 'streamlit',
        enable_enterprise_modules = True,
        # allow_unsafe_jscode = True,
        width = '100%'
    )

    # sel_row = grid_response['selected_rows']
    # df_sel_row = pd.DataFrame(sel_row)
    # if not df_sel_row.empty:
    #     df = df_sel_row[['market', 'symbol', 'company_name', 'enabled']]
    #     # st.dataframe(df, use_container_width = True)
    #     if st.button('Save', type = 'primary'):
    #         if not df.empty:
    #             insert_companies(df, True)
    #             st.cache_data.clear()