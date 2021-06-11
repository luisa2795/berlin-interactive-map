import streamlit as st
import folium
from streamlit_folium import folium_static

#create Berlin Map
m = folium.Map(location = [52.520008, 13.404954], zoom_start=10 )

#show Alexander Platz
# add marker for Liberty Bell
tooltip = "Alexander Platz"
folium.Marker([52.522150, 13.413140], popup="Liberty Bell", tooltip=tooltip ).add_to(m)

#call the map
folium_static(m)