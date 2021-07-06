import pymongo
import requests
import json

def load_data():
    #initialize mongo client and database
    client = pymongo.MongoClient('mongodb+srv://doadmin:A79tz5F16P3Z84kW@berlin-map-db-d1b8496c.mongo.ondigitalocean.com/berlin-map?authSource=admin&replicaSet=berlin-map-db&tls=true&tlsCAFile=ca-certificate.crt')
    db = client['berlin-map']
    #Load Distric data
    districts=list(db.districtcoordinates.find())
    #Load WC data
    toilets=list(db.toilets.find())
    #Load Swimming Spots data
    response=requests.get("https://www.berlin.de/lageso/gesundheit/gesundheitsschutz/badegewaesser/liste-der-badestellen/index.php/index/all.gjson?q=")
    swim_spots=json.loads(response.text)['features']
    #Load Memorials data
    items = db.memorials.find()
    #Load Monuments data
    items2 = db.monuments.find()
    return toilets, response, swim_spots, districts, items, items2