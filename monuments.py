import pymongo
import streamlit as st
from folium.plugins import MarkerCluster
from folium.plugins import FastMarkerCluster
from streamlit_folium import folium_static
import folium

#create Berlin Map
m = folium.Map(location = [52.520008, 13.404954], tiles = "cartodbpositron", zoom_start=10 ) 

# Initialize connection.
client = pymongo.MongoClient(**st.secrets["mongo"])
db = client.berlin
items = db.monuments.find()
items = list(items) 

#plot memoorials in the map
for item in items:
    location = [item["lat"], item["lon"]]
    folium.Marker(location=location, popup = item['name'], tooltip=item['name']).add_to(m)

#call the map
folium_static(m)    