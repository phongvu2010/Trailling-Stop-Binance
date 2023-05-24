# page_title = 'Trailling Stop Binance'

# [mongodb]
# db_host = 'i4ao1my.mongodb.net'
# db_user = 'phongvu2010'
# db_pswd = 'NArzNRhhgAZFw6iv'
# cluster = 'cluster0'


import certifi
import streamlit as st

from pymongo import MongoClient
from urllib import parse

@st.cache_resource()
def init_connection():
    env = st.secrets['mongodb']
    db_host = env['db_host']
    db_user = parse.quote_plus(env['db_user'])
    db_pswd = parse.quote_plus(env['db_pswd'])
    cluster = env['cluster']

    URL = f'mongodb+srv://{ db_user }:{ db_pswd }@{ cluster }.{ db_host }/?retryWrites=true&w=majority'

    return MongoClient(URL, tlsCAFile = certifi.where())

client = init_connection()

@st.cache_data(ttl = 600)
def get_data():
    db = client.get_database('Binance')  # establish connection to the 'sample_guide' db
    col = db.get_collection('Klines')
    items = col.find() # return all result from the 'planets' collection
    items = list(items)    
    
    return items

# data = get_data()
# print(data)


# li = [{"name" : "Mary", "pet": "dog"},
#       {"name" : "John", "pet": "cat"},
#       {"name" : "Robert", "pet": "bird"}]

# di = {"name" : "Hunter", "full": "Do"}

# db = client.get_database('Binance')  # establish connection to the 'sample_guide' db
# col = db.get_collection('Klines')
# x = col.insert_many(li)
# print(x.inserted_ids)

# x = col.insert_one(di)
# print(x.inserted_id)
# mycol.insert_one(mydict)