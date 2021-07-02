from pymongo import MongoClient
from pprint import pprint
import requests
import json
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import pandas as pd
import urllib.request
from folium.plugins import FastMarkerCluster
from geopy.extra.rate_limiter import RateLimiter
from urllib.request import urlopen
from xml.etree.ElementTree import parse
import xml.etree.ElementTree as ET
from geopy.geocoders import Nominatim
import xmltodict
import streamlit as st


client = MongoClient()
db = client['berlin']



#MEMORIALS transform and load data
var_url = urlopen('https://gedenktafeln-in-berlin.de/index.php?id=31&type=123')
xmldoc = parse(var_url)

memorials= []
for item in xmldoc.iterfind('item'):
    uid = item.findtext('uid')
    name = item.findtext('Name')
    url = item.findtext('url')
    strasse = item.findtext('strasse')
    ortsteil = item.findtext('ortsteil')
    inhalt = item.findtext('inhalt')
    erlauterung = item.findtext('erlauterung')
    autor = item.findtext('autor')
    image = item.findtext('url')
    #lon and lat are wrong in the file, should be swapped
    lon = item.findtext('latitude')
    lat = item.findtext('longitude')
    if((name!='') & (lon!='') & (lat!='')):
        a={'uid': uid, 'name': name, 'url': url, 'strasse': strasse, 'ortsteil': ortsteil, 'inhalt': inhalt, 'erlauterung': erlauterung, 'autor': autor, 'lon': float(lon), 'lat': float(lat)}
        memorials.append(a)

#create file monuments and insert it in the database
db.memorials.insert_many(memorials)




#MONUMENTS transform and load data
#import data
df = pd.read_csv('data/denkmalliste_berlin_092020.csv')

#Data Cleaning
df = pd.read_csv('data/denkmalliste_berlin_092020.csv')
df = df[df['Adresse'].notna()]

#creating a new column
tmp_1 = df["Adresse"].str.split("/", n = 1, expand = True)
tmp_2 = tmp_1[0].str.split(",", n = 1, expand = True)
df['address'] = tmp_2[0]


#converting address ro coordinates
locator = Nominatim(user_agent='myGeocoder')
# 1 - conveneint function to delay between geocoding calls (this min delay can be a problem)
geocode = RateLimiter(locator.geocode, min_delay_seconds=3)
# 2- - create location column
df['location'] = df['address'].apply(geocode)
# 3 - create longitude, laatitude and altitude from location column (returns tuple)
df['point'] = df['location'].apply(lambda loc: tuple(loc.point) if loc else None)
# 4 - split point column into latitude, longitude and altitude columns
df[['latitude', 'longitude', 'altitude']] = pd.DataFrame(df['point'].tolist(), index=df.index)

#make sure there is no null value for latitude and longitute
df = df[df['latitude'].notna()]
df = df[df['longitude'].notna()]

#delete uneccessary columns
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df = df.drop(['location', 'point', 'altitude'], axis=1)

#convert dataframe to a dictionary
monuments = df.T.to_dict().values()

#create file monuments and insert it in database
db.monuments.insert_many(monuments)   