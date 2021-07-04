import pymongo
import streamlit as st
from folium.plugins import MarkerCluster
from folium.plugins import FastMarkerCluster
from streamlit_folium import folium_static
import geopandas as gpd
import folium
import base64
import streamlit.components.v1 as components  # Import Streamlit

#create Berlin Map
m = folium.Map(location = [52.520008, 13.404954], tiles = "cartodbpositron", zoom_start=10)
border_style = {'color': '#000000', 'weight': '1.5', 'fillColor': '#58b5d1', 'fillOpacity': 0.08}
boundary = folium.GeoJson(open('./data/berlin.geojson').read(), name='Berlin Boundary', style_function= lambda x: border_style, overlay=False)
boundary.add_to(m)


#setting filters
cb0 = st.sidebar.checkbox("Reinickendorf")
cb1 = st.sidebar.checkbox("Charlottenburg-Wilmersdorf")
cb2 = st.sidebar.checkbox("Treptow-Köpenick")
cb3 = st.sidebar.checkbox("Pankow")
cb4 = st.sidebar.checkbox("Neukölln")
cb5 = st.sidebar.checkbox("Lichtenberg")
cb6 = st.sidebar.checkbox("Marzahn-Hellersdorf")
cb7 = st.sidebar.checkbox("Spandau")
cb8 = st.sidebar.checkbox("Steglitz-Zehlendorf")
cb9 = st.sidebar.checkbox("Mitte")
cb10 = st.sidebar.checkbox("Friedrichshain-Kreuzberg")
cb11= st.sidebar.checkbox("Tempelhof-Schöneberg")

cb_dist=[cb0, cb1, cb2, cb3, cb4, cb5, cb6, cb7, cb8, cb9, cb10, cb11]


#load district data
districts=gpd.read_file('data/bezirksgrenzen.geojson', driver='GeoJSON')

districts_filtered=districts[cb_dist]

for _, r in districts_filtered.iterrows():
    sim_geo = gpd.GeoSeries(r['geometry'])
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j,
                           style_function=lambda x: {'fillColor': 'orange'})
    folium.Popup(r['Gemeinde_name']).add_to(geo_j)
    geo_j.add_to(m)





# Initialize connection.
client = pymongo.MongoClient(**st.secrets["mongo"])
db = client.berlin
items = db.monuments.find()
items = list(items) 



#plot memoorials in the map
for item in items:
    html=f"""
    <img src="./data/images/charlottenburg.jpg" alt="Charlottenburg"> 
    <p><h5> Type: {item['Typ']}</h5> </p>
    <p><h5> Description: {item['Bezeichnung']}</h5> </p>
    <p>There are over 10 thousand monuments in Berlin. To access the full list, click 
    <a href="https://www.berlin.de/landesdenkmalamt/_assets/pdf-und-zip/denkmale/liste-karte-datenbank/denkmalliste_berlin.csv">here</a>.</p>
    """
    iframe = folium.IFrame(html=html, width=350, height=150)
    popup = folium.Popup(iframe, max_width=2650)
    location = [item["latitude"], item["longitude"]]
    folium.Marker(location=location, popup = popup, icon=folium.DivIcon(html=f"""
            <div><svg>
                <circle cx="45" cy="45" r="10" fill="#69b3a2" opacity=".4"/>
                <rect x="40", y="40" width="10" height="10", fill="red", opacity=".3" 
            </svg></div>""")).add_to(m)

#call the map
folium_static(m)    