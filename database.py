import streamlit as st
import pymongo

# URL = 'mongodb+srv://phongvu2010:<password>@cluster0.i4ao1my.mongodb.net/?retryWrites=true&w=majority'
URL = f'mongodb+srv://phongvu2010:85GGS4qxioSsi4MH@cluster0.i4ao1my.mongodb.net/'
# ac-ynvala9-shard-00-02.i4ao1my.mongodb.net

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(**st.secrets['mongo'])

client = init_connection()

# Pull data from the collection.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl = 600)
def get_data():
    db = client.mydb
    items = db.mycollection.find()
    items = list(items)  # make hashable for st.cache_data
    return items

items = get_data()

# Print results.
for item in items:
    st.write(f"{item['name']} has a :{item['pet']}:")

db.mycollection.insertMany([{"name" : "Mary", "pet": "dog"}, {"name" : "John", "pet": "cat"}, {"name" : "Robert", "pet": "bird"}])