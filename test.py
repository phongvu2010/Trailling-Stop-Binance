import numpy as np
import pandas as pd
import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts
import streamlit_lightweight_charts.dataSamples as data

path_file = 'data/BTCUSDT.feather'
df = pd.read_feather(path_file)
# df['time'] = df['time'].dt.strftime('%Y-%m-%d %X')
df.time = df.time.apply(lambda x: int(round(x.timestamp())))
df['color'] = np.where(df['open'] > df['close'],
                       'rgba(255,82,82, 0.8)',
                       'rgba(0, 150, 136, 0.8)')
# df.reset_index(drop = True, inplace = True)

df_1 = df[['time', 'close']]
df_1.columns = ['time', 'value']
priceVolumeSeriesArea = df_1.to_dict('records')
# print(priceVolumeSeriesArea)

df_2 = df[['time', 'volume', 'color']]
df_2.columns = ['time', 'value', 'color']
priceVolumeSeriesHistogram = df_2.to_dict('records')
# print(priceVolumeSeriesHistogram)


priceVolumeChartOptions = {
    "height": 500,
    "rightPriceScale": {
        "scaleMargins": {
            "top": 0.2,
            "bottom": 0.25,
        },
        "borderVisible": False,
    },
    "overlayPriceScales": {
        "scaleMargins": {
            "top": 0.7,
            "bottom": 0,
        }
    },
    "layout": {
        "background": {
            "type": 'solid',
            "color": '#131722'
        },
        "textColor": '#d1d4dc',
    },
    "grid": {
        "vertLines": {
            "color": 'rgba(42, 46, 57, 0)',
        },
        "horzLines": {
            "color": 'rgba(42, 46, 57, 0.6)',
        }
    }
}

priceVolumeSeries = [
    {
        "type": 'Area',
        "data": priceVolumeSeriesArea,
        "options": {
            "topColor": 'rgba(38,198,218, 0.56)',
            "bottomColor": 'rgba(38,198,218, 0.04)',
            "lineColor": 'rgba(38,198,218, 1)',
            "lineWidth": 2,
        }
    },
    {
        "type": 'Histogram',
        "data": priceVolumeSeriesHistogram,
        "options": {
            "color": '#26a69a',
            "priceFormat": {
                "type": 'volume',
            },
            "priceScaleId": "" # set as an overlay setting,
        },
        "priceScale": {
            "scaleMargins": {
                "top": 0.7,
                "bottom": 0,
            }
        }
    }
]
st.subheader("Price with Volume Series Chart sample")

renderLightweightCharts([
    {
        "chart": priceVolumeChartOptions,
        "series": priceVolumeSeries
    }
], 'priceAndVolume')