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
     html=f"""
    
        <h5> {item['Typ']}</h5>
        <img src="data/charlotenburg.jpg" alt="Charlotengurg">
        <p>There are over 200 monuments in charlotenburg</p>
        """
    iframe = folium.IFrame(html=html, width=200, height=200)
    popup = folium.Popup(iframe, max_width=2650)
    location = [item["latitude"], item["longitude"]]
    folium.Marker(location=location, popup = popup, icon=folium.DivIcon(html=f"""
            <div><svg>
                <circle cx="50" cy="50" r="40" fill="#69b3a2" opacity=".4"/>
                <rect x="35", y="35" width="30" height="30", fill="red", opacity=".3" 
            </svg></div>""")).add_to(m)

#call the map
folium_static(m)    