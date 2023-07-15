import pandas as pd
import streamlit as st

from dataset import get_orders
from st_aggrid import AgGrid, GridOptionsBuilder

def data_upload():
    return get_orders()

def show_grid(newline):
    st.header('This is AG Grid Table')
    df = data_upload()

    if newline == 'yes':
        data = [['', '', 0]]
        df_empty = pd.DataFrame(data, columns = ['CollaboratorName', 'Location', "HourlyRate"])
        df = pd.concat([df, df_empty], axis = 0, ignore_index = True)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable = True)
    grid_table = AgGrid(
        df,
        key = 'select_grid',
        gridOptions = gb.build(),
        fit_columns_on_grid_load = True,
        allow_unsafe_jscode = True
    )

    return grid_table

def update(grid_table):
    grid_table_df = pd.DataFrame(grid_table['data'])
    grid_table_df.to_csv('data.csv', index = False)

addline = st.sidebar.radio('Add New Line', options = ['yes', 'no'], index = 1, horizontal = True)
grid_table = show_grid(addline)
st.sidebar.button('Update', on_click = update, args = [grid_table])