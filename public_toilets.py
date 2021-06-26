import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
import gpxpy
#import geopandas as gpd

#Loading and preprocessing fuction
def load_data():
    df = pd.read_excel("https://www.berlin.de/sen/uvk/_assets/verkehr/infrastruktur/oeffentliche-toiletten/berliner-toiletten-standorte.xlsx")
    header_row = 2
    df.columns = df.iloc[header_row]
    df = df.drop(0).drop(1).drop(2)
    df = df.reset_index(drop=True)
    return df

def process_gpx_to_df(file_name):
    gpx = gpxpy.parse(open(file_name))  
    points = []
    for track in gpx.tracks:
        for segment in track.segments:        
            for point in segment.points:
                points.append(tuple([point.latitude, point.longitude]))
    
    return points

df = load_data()
points = []
for i in range(1, 21):
    if i <10:
        points.append(process_gpx_to_df('2021_gpx/Weg0'+str(i)+'.gpx'))
    else:
        points.append(process_gpx_to_df('2021_gpx/Weg'+str(i)+'.gpx'))

#create Berlin Map
m = folium.Map(location = [52.520008, 13.404954], tiles = "cartodbpositron", zoom_start=10)

#setting filters
cb8 = st.sidebar.checkbox("Hiking trails")
cb0 = st.sidebar.checkbox("WC")
##setting filters
#cb10 = st.sidebar.checkbox("Reinickendorf")
#cb11 = st.sidebar.checkbox("Charlottenburg-Wilmersdorf")
#cb12 = st.sidebar.checkbox("Treptow-Köpenick")
#cb13 = st.sidebar.checkbox("Pankow")
#cb14 = st.sidebar.checkbox("Neukölln")
#cb15 = st.sidebar.checkbox("Lichtenberg")
#cb16 = st.sidebar.checkbox("Marzahn-Hellersdorf")
#cb17 = st.sidebar.checkbox("Spandau")
#cb18 = st.sidebar.checkbox("Steglitz-Zehlendorf")
#cb19 = st.sidebar.checkbox("Mitte")
#cb110 = st.sidebar.checkbox("Friedrichshain-Kreuzberg")
#cb111= st.sidebar.checkbox("Tempelhof-Schöneberg")

#cb_dist=[cb10, cb11, cb12, cb13, cb14, cb15, cb16, cb17, cb18, cb19, cb110, cb111]


#load district data
#districts=gpd.read_file('2021_gpx/bezirksgrenzen.geojson', driver='GeoJSON')

#districts_filtered=districts[cb_dist]

#for _, r in districts_filtered.iterrows():
#    sim_geo = gpd.GeoSeries(r['geometry'])
#    geo_j = sim_geo.to_json()
#    geo_j = folium.GeoJson(data=geo_j,
#                           style_function=lambda x: {'fillColor': 'orange'})
#    folium.Popup(r['Gemeinde_name']).add_to(geo_j)
#    geo_j.add_to(m)

if cb0:
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
        folium.Marker([df2.loc[i, 'Latitude'], df2.loc[i, 'Longitude']], popup=df2.loc[i, 'Street'], tooltip=df2.loc[i, 'Street']).add_to(m)
        
if cb8:
    for i in range(len(points)):
        folium.PolyLine(points[i]).add_to(m)

#call the map
folium_static(m)

