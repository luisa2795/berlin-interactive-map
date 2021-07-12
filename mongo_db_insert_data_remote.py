
#this code creates berlin database and uploads the data for monuments and memorials

#import packages
from pymongo import MongoClient, GEOSPHERE
import requests
import json
import pandas as pd
import urllib.request
from geopy.extra.rate_limiter import RateLimiter
from urllib.request import urlopen
from xml.etree.ElementTree import parse
import xml.etree.ElementTree as ET
from geopy.geocoders import Nominatim
from io import StringIO
#import dns


client = MongoClient(
    'mongodb+srv://doadmin:A79tz5F16P3Z84kW@berlin-map-db-d1b8496c.mongo.ondigitalocean.com/berlin-map?authSource=admin&replicaSet=berlin-map-db&tls=true&tlsCAFile=ca-certificate.crt'
    )

db = client['berlin-map']

#PUBLIC Toilets transform and load data
df_wc = pd.read_excel("https://www.berlin.de/sen/uvk/_assets/verkehr/infrastruktur/oeffentliche-toiletten/berliner-toiletten-standorte.xlsx")
header_row = 2
df_wc.columns = df_wc.iloc[header_row]
df_wc = df_wc.drop(0).drop(1).drop(2)
df_wc = df_wc.reset_index(drop=True)

#convert dataframe to a dictionary
toilets = df_wc.T.to_dict().values()

#create file monuments and insert it in the database
db.toilets.insert_many(toilets)

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
response=requests.get('https://www.berlin.de/landesdenkmalamt/_assets/pdf-und-zip/denkmale/liste-karte-datenbank/denkmalliste_berlin.csv')
data = StringIO(response.text)
df=pd.read_csv(data, sep=";")


#df = pd.read_csv('data/denkmalliste_berlin_092020.csv')

#select only 10 monuments for each district
df_charlotengburg = df[df['Bezirk'] == 'Charlottenburg-Wilmersdorf'].sample(n=6)
df_reinickendorf = df[df['Bezirk'] == 'Reinickendorf'].sample(n=6)
df_treptow_kopenick = df[df['Bezirk'] == 'Treptow-Köpenick'].sample(n=6)
df_pankow = df[df['Bezirk'] == 'Pankow'].sample(n=6)
df_neukölln = df[df['Bezirk'] == 'Neukölln'].sample(n=6)
df_lichtenberg = df[df['Bezirk'] == 'Lichtenberg'].sample(n=6)
df_marzahn_hellersdorf = df[df['Bezirk'] == 'Marzahn-Hellersdorf'].sample(n=6)
df_spandau = df[df['Bezirk'] == 'Spandau'].sample(n=6)
df_steglitz_zehlendorf = df[df['Bezirk'] == 'Steglitz-Zehlendorf'].sample(n=6)
df_mitte= df[df['Bezirk'] == 'Mitte'].sample(n=6)
df_friedrichshain_kreuzberg= df[df['Bezirk'] == 'Friedrichshain-Kreuzberg'].sample(n=6)
df_tempelhof_schöneberg = df[df['Bezirk'] == 'Tempelhof-Schöneberg'].sample(n=6)

df_monuments_combined = pd.concat([df_charlotengburg, df_reinickendorf, df_treptow_kopenick, df_pankow, df_neukölln, df_lichtenberg, 
                                     df_marzahn_hellersdorf, df_spandau, df_steglitz_zehlendorf, df_mitte, df_friedrichshain_kreuzberg, df_tempelhof_schöneberg], ignore_index=True)

#Data Cleaning
df_monuments_combined = df_monuments_combined[df_monuments_combined['Adresse'].notna()]

#creating a new column
tmp_1 = df_monuments_combined["Adresse"].str.split("/", n = 1, expand = True)
tmp_2 = tmp_1[0].str.split(",", n = 1, expand = True)
tmp_2 =  tmp_2.astype(str) + ', Berlin, Germany'
df_monuments_combined['address'] = tmp_2[0]

#converting address ro coordinates
locator = Nominatim(user_agent='myGeocoder')
# 1 - conveneint function to delay between geocoding calls (this min delay can be a problem)
geocode = RateLimiter(locator.geocode, min_delay_seconds=3)
# 2- - create location column
df_monuments_combined['location'] = df_monuments_combined['address'].apply(geocode)
# 3 - create longitude, laatitude and altitude from location column (returns tuple)
df_monuments_combined['point'] = df_monuments_combined['location'].apply(lambda loc: tuple(loc.point) if loc else None)
# 4 - split point column into latitude, longitude and altitude columns
df_monuments_combined[['latitude', 'longitude', 'altitude']] = pd.DataFrame(df_monuments_combined['point'].tolist(), index=df_monuments_combined.index)

#make sure there is no null value for latitude and longitute
df_monuments_combined = df_monuments_combined[df_monuments_combined['latitude'].notna()]
df_monuments_combined = df_monuments_combined[df_monuments_combined['longitude'].notna()]

#delete uneccessary columns
df_monuments_combined = df_monuments_combined.loc[:, ~df_monuments_combined.columns.str.contains('^Unnamed')]
df_monuments_combined = df_monuments_combined.drop(['location', 'point', 'altitude'], axis=1)

#convert dataframe to a dictionary
monuments = df_monuments_combined.T.to_dict().values()

#create file monuments and insert it in database
db.monuments.insert_many(monuments)   


#DISTRICTS transform and load data
#get the data from ODIS berlin
dist_response=requests.get('https://tsb-opendata.s3.eu-central-1.amazonaws.com/bezirksgrenzen/bezirksgrenzen.geojson')
geojson=json.loads(dist_response.text)

#define collection
coords=db.districtcoordinates

# create 2dsphere index and initialize unordered bulk insert
coords.create_index([("geometry", GEOSPHERE)])
bulk = coords.initialize_unordered_bulk_op()

for feature in geojson['features']:
  # append to bulk insert list
  bulk.insert(feature)

# execute bulk operation to the DB
result = bulk.execute()
print ("Number of Features successully inserted:", result["nInserted"])



#BOUNDARY (states) insert to DB
response= requests.get('https://opendata.arcgis.com/datasets/ef4b445a53c1406892257fe63129a8ea_0.geojson')
states=json.loads(response.text)

#define collection
boundary=db.states

# create 2dsphere index and initialize unordered bulk insert
boundary.create_index([("geometry", GEOSPHERE)])
bulk1 = boundary.initialize_unordered_bulk_op()

for feature in states['features']:
  # append to bulk insert list
  bulk1.insert(feature)

# execute bulk operation to the DB
result1 = bulk1.execute()
print ("Number of Features successully inserted:", result1["nInserted"])
