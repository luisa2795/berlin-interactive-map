#

import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import pandas as pd
import xml.etree.ElementTree as ET
import urllib.request
from folium.plugins import FastMarkerCluster
from urllib.request import urlopen
from xml.etree.ElementTree import parse
import streamlit as st
import plotly.express as px

#creating the map
#create Berlin Map
m = folium.Map(location = [52.520008, 13.404954], tiles = "cartodbpositron", zoom_start=10 ) 

#get data and create a dataframe out of it
df = pd.DataFrame(columns=['uid', 'name', 'url', 'strasse', 'ortsteil', 'inhalt', 'erlauterung', 'autor', 'lon', 'lat'])
var_url = urlopen('https://gedenktafeln-in-berlin.de/index.php?id=31&type=123')
xmldoc = parse(var_url)

for item in xmldoc.iterfind('item'):
    uid = item.findtext('uid')
    name = item.findtext('Name')
    url = item.findtext('url')
    strasse = item.findtext('strasse')
    ortsteil = item.findtext('ortsteil')
    inhalt = item.findtext('inhalt')
    erlauterung = item.findtext('erlauterung')
    autor = item.findtext('autor')
    #lon and lat are wrong in the file, should be swapped
    lon = item.findtext('latitude')
    lat = item.findtext('longitude')
    df = df.append({'uid': uid, 'name': name, 'url': url, 'strasse': strasse, 'ortsteil': ortsteil, 'inhalt': inhalt, 'erlauterung': erlauterung, 'autor': autor, 'lon': lon, 'lat': lat}, ignore_index=True)

#remove empty values
mask = (df['name'] != '') & (df['lat'] != '') & (df['lon'] != '')
df = df[mask]

#convert lon and lat to float
df = df[df['lon'].notnull()].copy()
df['lon'] = df['lon'].astype(float)

df = df[df['lat'].notnull()].copy()
df['lat'] = df['lat'].astype(float)

#plot memoorials in the map
df_memorials = df

#CREATE THE MAP USING PLOTLY
fig = px.scatter_mapbox(df_memorials, lat="lat", lon="lon", hover_name="name", hover_data=["lat", "lon"],
                        color_discrete_sequence=["fuchsia"], zoom=10, height=500)
fig.update_layout(mapbox_style="carto-darkmatter")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig)
