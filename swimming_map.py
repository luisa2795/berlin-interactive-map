
import folium
from streamlit_folium import folium_static
import requests
import json

#create Berlin Map
m = folium.Map(location = [52.520008, 13.404954], tiles = "cartodbpositron", zoom_start=10 ) 

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


