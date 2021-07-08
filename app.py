import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import gpxpy
import requests
import json
import pymongo
#import geopandas as gpd
from shapely.geometry import Point, shape
import dns
import base64
from folium.plugins import Fullscreen
import pymongo
import requests
import json

@st.cache(allow_output_mutation=True, show_spinner=False)
def load_data():
    #initialize mongo client and database
    client = pymongo.MongoClient('mongodb+srv://doadmin:A79tz5F16P3Z84kW@berlin-map-db-d1b8496c.mongo.ondigitalocean.com/berlin-map?authSource=admin&replicaSet=berlin-map-db&tls=true&tlsCAFile=ca-certificate.crt')
    db = client['berlin-map']
    #load Berlin Boundary
    boundary=list(db.boundary.find())[0]['geometry']
    #Load Distric data
    districts=list(db.districtcoordinates.find())
    #Load WC data
    toilets=list(db.toilets.find())
    #Load Swimming Spots data
    response=requests.get("https://www.berlin.de/lageso/gesundheit/gesundheitsschutz/badegewaesser/liste-der-badestellen/index.php/index/all.gjson?q=")
    swim_spots=json.loads(response.text)['features']
    #Load Memorials data
    items = list(db.memorials.find())
    #Load Monuments data
    items2 = list(db.monuments.find())
    client.close()
    return boundary, toilets, response, swim_spots, districts, items, items2


boundary, toilets, response, swim_spots, districts, memorials, monuments = load_data()

#create Berlin Map
m = folium.Map(location = [52.520008, 13.404954], tiles = "cartodbpositron", zoom_start=10)
border_style = {'color': '#000000', 'weight': '1.5', 'fillColor': '#58b5d1', 'fillOpacity': 0.08}
city_boundary = folium.GeoJson(boundary, name='Berlin Boundary', style_function= lambda x: border_style, overlay=False)
city_boundary.add_to(m)
#add full screen option to the map
Fullscreen().add_to(m)

#District filters
st.sidebar.markdown("**Districts**")
cb20 = st.sidebar.checkbox("Reinickendorf")
cb21 = st.sidebar.checkbox("Charlottenburg-Wilmersdorf")
cb22 = st.sidebar.checkbox("Treptow-Köpenick")
cb23 = st.sidebar.checkbox("Pankow")
cb24 = st.sidebar.checkbox("Neukölln")
cb25 = st.sidebar.checkbox("Lichtenberg")
cb26 = st.sidebar.checkbox("Marzahn-Hellersdorf")
cb27 = st.sidebar.checkbox("Spandau")
cb28 = st.sidebar.checkbox("Steglitz-Zehlendorf")
cb29 = st.sidebar.checkbox("Mitte")
cb30 = st.sidebar.checkbox("Friedrichshain-Kreuzberg")
cb31= st.sidebar.checkbox("Tempelhof-Schöneberg")

#Features filets
st.sidebar.markdown("**Features**")
cb0 = st.sidebar.checkbox("WC")
cb9 = st.sidebar.checkbox("Memorials")
cb11 = st.sidebar.checkbox("Monuments")
cb10 = st.sidebar.checkbox("Swimming spots")


#load district data 
cb_dist=[cb20, cb21, cb22, cb23, cb24, cb25, cb26, cb27, cb28, cb29, cb30, cb31]

districts_filtered=coords_filtered=[x[1] for x in zip(cb_dist,districts) if x[0]==True]

for r in districts_filtered:
    geo_j = folium.GeoJson(data=r['geometry'],
                           style_function=lambda x: {'fillColor': 'orange'})
    folium.Popup(r['properties']['Gemeinde_name']).add_to(geo_j)
    geo_j.add_to(m)

#WC
if cb0:
    st.sidebar.markdown("**WC Filters**")
    cb1 = st.sidebar.checkbox("Owned By Wall")
    cb2 = st.sidebar.checkbox("Wheelchair Accessible")
    cb3 = st.sidebar.checkbox("Can Be Payed With Coins")
    cb4 = st.sidebar.checkbox("Can Be Payed In App")
    cb5 = st.sidebar.checkbox("Can Be Payed With NFC")
    cb6 = st.sidebar.checkbox("Has Urinal")
    cb7 = st.sidebar.checkbox("Has Changing Table")
    df = pd.DataFrame(toilets)
    sl  = st.sidebar.slider("Price", min_value=0.0, max_value=float(df['Price'].max()), step = 0.1, value = float(df['Price'].max()))
    
    #Filter dataset
    df2 = df[(df['isOwnedByWall'] != int(cb1)-1) & (df['isHandicappedAccessible'] != int(cb2)-1) & 
    (df['canBePayedWithCoins'] != int(cb3)-1) & (df['canBePayedInApp'] != int(cb4)-1) & (df['canBePayedWithNFC'] != int(cb5)-1) & 
    (df['hasUrinal'] != int(cb6)-1) & (df['hasChangingTable'] != int(cb7)-1) & (df['Price'] <= sl)]
    df2 = df2.reset_index(drop=True)
    
    #Add markers
    marker_cluster2 = folium.plugins.MarkerCluster().add_to(m)
    for i in range(df2.shape[0]):
        point = Point(df2.loc[i, 'Longitude'], df2.loc[i, 'Latitude'])
        for r in districts_filtered:
            polygon = shape(r['geometry'])
            if polygon.contains(point):
                folium.Marker([df2.loc[i, 'Latitude'], df2.loc[i, 'Longitude']], popup=df2.loc[i, 'Street'], tooltip=df2.loc[i, 'Street'], icon=folium.Icon(icon='flag')).add_to(marker_cluster2)

#memorials
if cb9:
    
    items = memorials
    marker_cluster = folium.plugins.MarkerCluster().add_to(m)
    for item in items:
        html= f"""<center><p><b> {item['name']}</b> is created by
        <b> {item['autor']}</b> <br> 
            Click <a href= {item['url']}>here</a> to get a full description and pictures for this memorial.</p></center>
            """
        iframe = folium.IFrame(html=html, width=600, height=300)
        popup = folium.Popup(iframe, max_width=2650)
        location = [item["lat"], item["lon"]]
        point = Point(item["lon"], item["lat"])
        for r in districts_filtered:
            polygon = shape(r['geometry'])
            if polygon.contains(point):
                folium.Marker(location=location, popup = popup, tooltip=item['name']).add_to(marker_cluster)

#swimming spots
if cb10:
    for spot in swim_spots:
        location2=list(reversed(spot['geometry']['coordinates']))
        point2 = Point(location2[1], location2[0])
        for r in districts_filtered:
            polygon = shape(r['geometry'])
            if polygon.contains(point2):
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
                    location=location2, 
                    tooltip=properties['title'],
                    popup=folium.Popup(html_popup, max_width=450),
                    icon=folium.Icon(
                        icon='tint',
                        color=color
                        )
                    ).add_to(m)

#monuments
if cb11:
    
    items2 = monuments
    #plot monuments in the map
    for item in items2:
        png='data/images/{}.jpg'.format(item['Bezirk'])
        encoded=base64.b64encode(open(png, 'rb').read())
        html=folium.Html('''
        <img src="data:image/png;base64,{}">
        <p><i>picture: one of the monuments in {}</i> </p>
        <p>
        <b>Type:</b>{} <br> 
        <b> Description: </b> {} <br>
        There are over 10 thousand monuments in Berlin. <br>To access the full list, click 
        <a href="https://www.berlin.de/landesdenkmalamt/_assets/pdf-und-zip/denkmale/liste-karte-datenbank/denkmalliste_berlin.csv">here</a>.</p>
        '''.format(
            encoded.decode('UTF-8'),
            item['Bezirk'], 
            item['Typ'], 
            item['Bezeichnung']
            ), script=True)
        popup = folium.Popup(html, max_width=450)
        location3 = [item["latitude"], item["longitude"]]
        point = Point(item["longitude"], item["latitude"])
        for r in districts_filtered:
            polygon = shape(r['geometry'])
            if polygon.contains(point):
                folium.Marker(location=location3, popup=popup, icon=folium.DivIcon(html=f"""
            <div><svg>
                <circle cx="13" cy="13" r="13" fill="#69b3a2" opacity=".4"/>
                <rect x="8", y="8" width="10" height="10", fill="red", opacity=".3" 
            </svg></div>""")).add_to(m)

#call the map
folium_static(m)

