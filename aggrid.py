import pandas as pd
import streamlit as st

from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

def create_grid(df, gridOptions):
    return AgGrid(
        df,
        gridOptions = gridOptions,
        # reload_data = False,
        # data_return_mode = 'AS_INPUT',
        # update_mode = 'SELECTION_CHANGED',
        # fit_columns_on_grid_load = True,
        # Add theme color to the table: alpine, balham, material, streamlit 
        theme = 'material',
        # enable_enterprise_modules = True,
        # allow_unsafe_jscode = True,
        width = '100%'
    )

def list_orders(placeholder, df):
    with placeholder.container():
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

        gb = GridOptionsBuilder.from_dataframe(df)

        # Add pagination
        gb.configure_pagination(enabled = False,
                                paginationAutoPageSize = True,
                                paginationPageSize = 15)

        gb.configure_default_column(editable = True, resizable = False, filterable = True,
                                    sortable = True, groupable = False)
        gb.configure_column(field = 'symbol',
                            header_name = 'Symbol',
                            editable = False,
                            width = 120)
        gb.configure_column(field = 'time_order',
                            header_name = 'Time',
                            valueFormatter = 'value.date.datetime()')
        gb.configure_column(field = 'type',
                            header_name = 'Type',
                            cellEditor = 'agSelectCellEditor',
                            cellEditorParams = {'values': ['Buy', 'Sell']},
                            width = 100)
        # gb.configure_column(field = 'enabled',
        #                     header_name = 'Niêm yết',
        #                     cellRenderer = checkbox_renderer,
        #                     width = 60)

        # Add a sidebar
        # gb.configure_side_bar(filters_panel = True, columns_panel = True)

        # Enable multi-row selection
        # gb.configure_selection(selection_mode = 'multiple',
        #                        use_checkbox = False,
        #                        groupSelectsChildren = 'Group checkbox select children')

        grid_response = create_grid(df, gb.build())

        # sel_row = grid_response['selected_rows']
        # df_sel_row = pd.DataFrame(sel_row)
        # if not df_sel_row.empty:
        #     df = df_sel_row[['market', 'symbol', 'company_name', 'enabled']]
        #     # st.dataframe(df, use_container_width = True)
        #     if st.button('Save', type = 'primary'):
        #         if not df.empty:
        #             insert_companies(df, True)
        #             st.cache_data.clear()


from dataset import get_orders

df_order = get_orders()

# Creating a single-element container
placeholder = st.empty()

list_orders(placeholder, df_order)