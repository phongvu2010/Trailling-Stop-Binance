import certifi
import streamlit as st

from pymongo import MongoClient, change_stream
from urllib import parse


# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource()
def init_connection():
    env = st.secrets['mongo']
    db_host = env['db_host']
    db_user = parse.quote_plus(env['db_user'])
    db_pswd = parse.quote_plus(env['db_pswd'])
    cluster = env['cluster']

    URL = f'mongodb+srv://{ db_user }:{ db_pswd }@{ cluster }.{ db_host }/?retryWrites=true&w=majority'

    return MongoClient(URL, tlsCAFile = certifi.where())

# Pull data from the collection.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl = 600, show_spinner = False)
def get_data(database, collection):
    client = init_connection()
    db = client.get_database(database)
    coll = db.get_collection(collection)

    return list(coll.find())

client = init_connection()
change_stream = change_stream.CollectionChangeStream()
print(change_stream)

# items = get_data('Binance', 'Klines')
# print(items)
# Print results.
# for item in items:
#     st.write(f"{item['name']} has a :{item['pet']}:")

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