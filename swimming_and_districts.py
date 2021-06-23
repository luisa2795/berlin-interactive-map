
import folium
from streamlit_folium import folium_static
import requests
import json
import geojson
import fiona
import geopandas as gpd
import streamlit as st

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


#get data
response=requests.get("https://www.berlin.de/lageso/gesundheit/gesundheitsschutz/badegewaesser/liste-der-badestellen/index.php/index/all.gjson?q=")
swim_spots=json.loads(response.text)['features']

for spot in swim_spots:
    location=list(reversed(spot['geometry']['coordinates']))
    properties=spot['properties']
    color_pic=spot['properties']['data']['farbe']
    color='green' if 'gruen' in color_pic else (
        'orange' if 'gelb' in color_pic else
        'red')
    html_popup=folium.Html(
        '''<b>Water Quality </b><br>
        Escherichia coli: {}  per 100ml<br>
        Intestinal Enterococci: {} per 100ml<br>
        Visibility depth: {}cm<br>
        Temperature: {}°C<br>
        <i> Date of last measurements: {}</i>
        '''
        .format(
            properties['data']['eco'], 
            properties['data']['ente'], 
            properties['data']['sicht'],
            properties['data']['temp'],
            properties['data']['dat'],
            ), 
        script=True)
    folium.Marker(
        location=location, 
        tooltip=properties['title'],
        popup=folium.Popup(html_popup, max_width=450),
        icon=folium.Icon(
            icon='tint',
            color=color
            )
        ).add_to(m)


folium_static(m)
