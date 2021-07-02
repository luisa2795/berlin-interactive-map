from geopy.geocoders import Nominatim
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd
from folium.plugins import FastMarkerCluster
import streamlit as st

#import data
df = pd.read_csv('data/denkmalliste_berlin_092020.csv')

#Data Cleaning
df = pd.read_csv('data/denkmalliste_berlin_092020.csv')
df = df.drop(['Ensemble_Info', 'Zugehörigkeit', 'Adresse2', 'Architekt und weitere Informationen'], axis=1)
df = df[df['Adresse'].notna()]

#creating a new column
tmp_1 = df["Adresse"].str.split("/", n = 1, expand = True)
tmp_2 = tmp_1[0].str.split(",", n = 1, expand = True)
df['address'] = tmp_2[0]

#selecting a sample form data
df = df.sample(n=100)


#converting address ro coordinates
locator = Nominatim(user_agent='myGeocoder')
# 1 - conveneint function to delay between geocoding calls (this min delay can be a problem)
geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
# 2- - create location column
df['location'] = df['address'].apply(geocode)
# 3 - create longitude, laatitude and altitude from location column (returns tuple)
df['point'] = df['location'].apply(lambda loc: tuple(loc.point) if loc else None)
# 4 - split point column into latitude, longitude and altitude columns
df[['latitude', 'longitude', 'altitude']] = pd.DataFrame(df['point'].tolist(), index=df.index)

#make sure there is no null value for latitude and longitute
df = df[df['latitude'].notna()]
df = df[df['longitude'].notna()]

#create the map
m = folium.Map(location = [52.520008, 13.404954], tiles = "cartodbpositron", zoom_start=10 ) 
df_monuments = df
for i,r in df_monuments.iterrows():
    location = [r["latitude"], r["longitude"]]
    folium.Marker(location=location, popup = r['ID'], tooltip=r['ID'], 
                 icon=folium.Icon( icon='eject')).add_to(m)

folium_static(m)                 