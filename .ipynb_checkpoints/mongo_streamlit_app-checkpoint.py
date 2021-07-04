#How to make the connection with MongoDB

import pymongo
import streamlit as st
from folium.plugins import MarkerCluster
from folium.plugins import FastMarkerCluster
from streamlit_folium import folium_static

# Initialize connection.
client = pymongo.MongoClient(**st.secrets["mongo"])


db = client.berlin
items = db.monuments.find()
items = list(items)  # make hashable for st.cache

# Print results.
for item in items:
    st.write(item['name'])
