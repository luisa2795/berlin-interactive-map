import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static

#Loading and preprocessing fuction
def load_data():
    df = pd.read_excel("https://www.berlin.de/sen/uvk/_assets/verkehr/infrastruktur/oeffentliche-toiletten/berliner-toiletten-standorte.xlsx")
    header_row = 2
    df.columns = df.iloc[header_row]
    df = df.drop(0).drop(1).drop(2)
    df = df.reset_index(drop=True)
    return df

df = load_data()

#create Berlin Map
m = folium.Map(location = [52.520008, 13.404954], tiles = "cartodbpositron", zoom_start=10)

#setting filters
cb0 = st.sidebar.checkbox("WC")
cb1 = st.sidebar.checkbox("Owned By Wall")
cb2 = st.sidebar.checkbox("Wheelchair Accessible")
cb3 = st.sidebar.checkbox("Can Be Payed With Coins")
cb4 = st.sidebar.checkbox("Can Be Payed In App")
cb5 = st.sidebar.checkbox("Can Be Payed With NFC")
cb6 = st.sidebar.checkbox("Has Urinal")
cb7 = st.sidebar.checkbox("Has Changing Table")
sl  = st.sidebar.slider("Price", min_value=0.0, max_value=float(df['Price'].max()), step = 0.1, value = float(df['Price'].max()))

if cb0:
    #Filter dataset
    df2 = df[(df['isOwnedByWall'] != int(cb1)-1) & (df['isHandicappedAccessible'] != int(cb2)-1) & 
    (df['canBePayedWithCoins'] != int(cb3)-1) & (df['canBePayedInApp'] != int(cb4)-1) & (df['canBePayedWithNFC'] != int(cb5)-1) & 
    (df['hasUrinal'] != int(cb6)-1) & (df['hasChangingTable'] != int(cb7)-1) & (df['Price'] <= sl)]
    df2 = df2.reset_index(drop=True)
    
    #Add markers
    for i in range(df2.shape[0]):
        folium.Marker([df2.loc[i, 'Latitude'], df2.loc[i, 'Longitude']], popup=df2.loc[i, 'Street'], tooltip=df2.loc[i, 'Street']).add_to(m)

#call the map
folium_static(m)