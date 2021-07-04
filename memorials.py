import pymongo
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import folium
import geojson
import geopandas as gpd

# Initialize connection.
client = pymongo.MongoClient(**st.secrets["mongo"])
db = client.berlin

#create Berlin Map
m = folium.Map(location = [52.520008, 13.404954], tiles = "cartodbpositron", zoom_start=10 )


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



#plot memorials in the map
items = db.memorials.find()
items = list(items)
marker_cluster = folium.plugins.MarkerCluster().add_to(m)
for item in items:
    
    html=f"""
    <p><h5> {item['name']}</h5> </p>
    <p>Visit <a href= {item['url']}>the link</a> for more information.</p>
    """
    iframe = folium.IFrame(html=html,  height=500)
    popup = folium.Popup(iframe, max_width=2650)
    location = [item["lat"], item["lon"]]
    folium.Marker(location=location, popup = popup,  tooltip=item['name']).add_to(marker_cluster)

#call the map
folium_static(m)


