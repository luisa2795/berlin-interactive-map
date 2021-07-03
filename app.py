import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import gpxpy
import requests
import json
import pymongo
import geopandas as gpd
from shapely.geometry import Point, shape

#function to convert gpx to points
def process_gpx_to_df(file_name):
    gpx = gpxpy.parse(open(file_name))  
    points = []
    for track in gpx.tracks:
        for segment in track.segments:        
            for point in segment.points:
                points.append(tuple([point.latitude, point.longitude]))
    return points

#Loading and preprocessing fuction
def load_data():
    #Load Distric data
    districts=gpd.read_file('data/bezirksgrenzen.geojson', driver='GeoJSON')
    #Load WC data
    df = pd.read_excel("https://www.berlin.de/sen/uvk/_assets/verkehr/infrastruktur/oeffentliche-toiletten/berliner-toiletten-standorte.xlsx")
    header_row = 2
    df.columns = df.iloc[header_row]
    df = df.drop(0).drop(1).drop(2)
    df = df.reset_index(drop=True)
    #Load Swimming Spots data
    response=requests.get("https://www.berlin.de/lageso/gesundheit/gesundheitsschutz/badegewaesser/liste-der-badestellen/index.php/index/all.gjson?q=")
    swim_spots=json.loads(response.text)['features']
    points = []
    #Load Hiking Data
    for i in range(1, 21):
        if i <10:
            points.append(process_gpx_to_df('data/Weg0'+str(i)+'.gpx'))
        else:
            points.append(process_gpx_to_df('data/Weg'+str(i)+'.gpx'))
    return df, response, swim_spots, points, districts

df, response, swim_spots, points, districts = load_data()

#create Berlin Map
m = folium.Map(location = [52.520008, 13.404954], tiles = "cartodbpositron", zoom_start=10)

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
cb8 = st.sidebar.checkbox("Hiking trails")
cb9 = st.sidebar.checkbox("Memorials")
cb11 = st.sidebar.checkbox("Monuments")
cb10 = st.sidebar.checkbox("Swimming spots")


#load district data 
cb_dist=[cb20, cb21, cb22, cb23, cb24, cb25, cb26, cb27, cb28, cb29, cb30, cb31]

districts_filtered=districts[cb_dist]

for _, r in districts_filtered.iterrows():
    sim_geo = gpd.GeoSeries(r['geometry'])
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j,
                           style_function=lambda x: {'fillColor': 'orange'})
    folium.Popup(r['Gemeinde_name']).add_to(geo_j)
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
    sl  = st.sidebar.slider("Price", min_value=0.0, max_value=float(df['Price'].max()), step = 0.1, value = float(df['Price'].max()))
    #Filter dataset
    df2 = df[(df['isOwnedByWall'] != int(cb1)-1) & (df['isHandicappedAccessible'] != int(cb2)-1) & 
    (df['canBePayedWithCoins'] != int(cb3)-1) & (df['canBePayedInApp'] != int(cb4)-1) & (df['canBePayedWithNFC'] != int(cb5)-1) & 
    (df['hasUrinal'] != int(cb6)-1) & (df['hasChangingTable'] != int(cb7)-1) & (df['Price'] <= sl)]
    df2 = df2.reset_index(drop=True)
    
    #Add markers
    for i in range(df2.shape[0]):
        point = Point(df2.loc[i, 'Longitude'], df2.loc[i, 'Latitude'])
        for _, r in districts_filtered.iterrows():
            polygon = shape(r['geometry'])
            if polygon.contains(point):
                folium.Marker([df2.loc[i, 'Latitude'], df2.loc[i, 'Longitude']], popup=df2.loc[i, 'Street'], tooltip=df2.loc[i, 'Street']).add_to(m)

#hiking trails      
if cb8:
    for i in range(len(points)):
        folium.PolyLine(points[i]).add_to(m)

#memorials
if cb9:
    client = pymongo.MongoClient()
    db = client.berlin
    items = db.memorials.find()
    items = list(items)
    marker_cluster = folium.plugins.MarkerCluster().add_to(m)
    for item in items:
        location = [item["lat"], item["lon"]]
        point = Point(item["lon"], item["lat"])
        for _, r in districts_filtered.iterrows():
            polygon = shape(r['geometry'])
            if polygon.contains(point):
                folium.Marker(location=location, popup = item['name'], tooltip=item['name']).add_to(marker_cluster)

#swimming spots
if cb10:
    for spot in swim_spots:
        location2=list(reversed(spot['geometry']['coordinates']))
        point2 = Point(location2[1], location2[0])
        for _, r in districts_filtered.iterrows():
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
    # Initialize connection.
    #client = pymongo.MongoClient(**st.secrets["mongo"])
    client = pymongo.MongoClient()
    db = client.berlin
    items = db.monuments.find()
    items = list(items) 

    #plot memoorials in the map
    for item in items:
        location3 = [item["lat"], item["lon"]]
        point = Point(item["lon"], item["lat"])
        for _, r in districts_filtered.iterrows():
            polygon = shape(r['geometry'])
            if polygon.contains(point):
                folium.Marker(location=location3, popup = item['name'], tooltip=item['name']).add_to(m)

#call the map
folium_static(m)

