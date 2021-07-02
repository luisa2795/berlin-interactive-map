from pymongo import MongoClient
from pprint import pprint
import requests
import json
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import pandas as pd
import xml.etree.ElementTree as ET
import urllib.request
from folium.plugins import FastMarkerCluster
from urllib.request import urlopen
from xml.etree.ElementTree import parse
import xml.etree.ElementTree as ET
import streamlit as st
import xmltodict

client = MongoClient()
db = client['berlin']

#MEMORIALS transform and load data
var_url = urlopen('https://gedenktafeln-in-berlin.de/index.php?id=31&type=123')
xmldoc = parse(var_url)

monuments= []
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
        monuments.append(a)

#insert in db
db.monuments.insert_many(monuments)        