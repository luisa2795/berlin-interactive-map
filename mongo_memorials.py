import streamlit as st
import pymongo

# Initialize connection.
client = pymongo.MongoClient(**st.secrets["mongo"])


db = client.berlin
items = db.monuments.find()
items = list(items)  # make hashable for st.cache

# Print results.
for item in items:
    st.write(item['name'])
