import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

st.title("Météo & Pollution - France")

# PREFECTURES
df_villes = pd.DataFrame([
    # Auvergne-Rhône-Alpes
    {'ville': 'Lyon', 'region': 'Auvergne-Rhône-Alpes', 'lat': 45.7640, 'lon': 4.8357},
    {'ville': 'Clermont-Ferrand', 'region': 'Auvergne-Rhône-Alpes', 'lat': 45.7772, 'lon': 3.0870},
    {'ville': 'Saint-Étienne', 'region': 'Auvergne-Rhône-Alpes', 'lat': 45.4397, 'lon': 4.3872},
    {'ville': 'Grenoble', 'region': 'Auvergne-Rhône-Alpes', 'lat': 45.1885, 'lon': 5.7245},
    {'ville': 'Chambéry', 'region': 'Auvergne-Rhône-Alpes', 'lat': 45.5646, 'lon': 5.9178},
    {'ville': 'Annecy', 'region': 'Auvergne-Rhône-Alpes', 'lat': 45.8992, 'lon': 6.1294},
    # Bourgogne-Franche-Comté
    {'ville': 'Dijon', 'region': 'Bourgogne-Franche-Comté', 'lat': 47.3220, 'lon': 5.0415},
    {'ville': 'Besançon', 'region': 'Bourgogne-Franche-Comté', 'lat': 47.2380, 'lon': 6.0243},
    # Bretagne
    {'ville': 'Rennes', 'region': 'Bretagne', 'lat': 48.1173, 'lon': -1.6778},
    {'ville': 'Brest', 'region': 'Bretagne', 'lat': 48.3905, 'lon': -4.4860},
    {'ville': 'Vannes', 'region': 'Bretagne', 'lat': 47.6586, 'lon': -2.7603},
    {'ville': 'Saint-Brieuc', 'region': 'Bretagne', 'lat': 48.5144, 'lon': -2.7651},
    # Centre-Val de Loire
    {'ville': 'Orléans', 'region': 'Centre-Val de Loire', 'lat': 47.9029, 'lon': 1.9093},
    {'ville': 'Tours', 'region': 'Centre-Val de Loire', 'lat': 47.3941, 'lon': 0.6848},
    # Grand Est
    {'ville': 'Strasbourg', 'region': 'Grand Est', 'lat': 48.5734, 'lon': 7.7521},
    {'ville': 'Metz', 'region': 'Grand Est', 'lat': 49.1193, 'lon': 6.1757},
    {'ville': 'Reims', 'region': 'Grand Est', 'lat': 49.2583, 'lon': 4.0317},
    {'ville': 'Nancy', 'region': 'Grand Est', 'lat': 48.6921, 'lon': 6.1844},
    # Hauts-de-France
    {'ville': 'Lille', 'region': 'Hauts-de-France', 'lat': 50.6292, 'lon': 3.0573},
    {'ville': 'Amiens', 'region': 'Hauts-de-France', 'lat': 49.8941, 'lon': 2.2958},
    # Île-de-France
    {'ville': 'Paris', 'region': 'Île-de-France', 'lat': 48.8566, 'lon': 2.3522},
    {'ville': 'Versailles', 'region': 'Île-de-France', 'lat': 48.8014, 'lon': 2.1301},
    # Normandie
    {'ville': 'Rouen', 'region': 'Normandie', 'lat': 49.4432, 'lon': 1.0993},
    {'ville': 'Caen', 'region': 'Normandie', 'lat': 49.1829, 'lon': -0.3707},
    # Nouvelle-Aquitaine
    {'ville': 'Bordeaux', 'region': 'Nouvelle-Aquitaine', 'lat': 44.8378, 'lon': -0.5792},
    {'ville': 'Limoges', 'region': 'Nouvelle-Aquitaine', 'lat': 45.8336, 'lon': 1.2611},
    {'ville': 'Poitiers', 'region': 'Nouvelle-Aquitaine', 'lat': 46.5802, 'lon': 0.3404},
    {'ville': 'Pau', 'region': 'Nouvelle-Aquitaine', 'lat': 43.2951, 'lon': -0.3708},
    # Occitanie
    {'ville': 'Toulouse', 'region': 'Occitanie', 'lat': 43.6047, 'lon': 1.4442},
    {'ville': 'Montpellier', 'region': 'Occitanie', 'lat': 43.6108, 'lon': 3.8767},
    {'ville': 'Nîmes', 'region': 'Occitanie', 'lat': 43.8367, 'lon': 4.3601},
    {'ville': 'Perpignan', 'region': 'Occitanie', 'lat': 42.6886, 'lon': 2.8948},
    # Pays de la Loire
    {'ville': 'Nantes', 'region': 'Pays de la Loire', 'lat': 47.2184, 'lon': -1.5536},
    {'ville': 'Angers', 'region': 'Pays de la Loire', 'lat': 47.4784, 'lon': -0.5632},
    {'ville': 'Le Mans', 'region': 'Pays de la Loire', 'lat': 48.0077, 'lon': 0.1984},
    # PACA
    {'ville': 'Marseille', 'region': 'PACA', 'lat': 43.2965, 'lon': 5.3698},
    {'ville': 'Nice', 'region': 'PACA', 'lat': 43.7102, 'lon': 7.2620},
    {'ville': 'Toulon', 'region': 'PACA', 'lat': 43.1242, 'lon': 5.9280},
    {'ville': 'Avignon', 'region': 'PACA', 'lat': 43.9493, 'lon': 4.8055}
])

# SELECTEURS
st.subheader("Sélection")

# Sélecteur 1 : Région
region_choisie = st.selectbox("Région :", sorted(df_villes['region'].unique()))

# Filtrer villes de la région
villes_region = df_villes[df_villes['region'] == region_choisie]

# Sélecteur 2 : Ville
ville_choisie = st.selectbox("Ville :", villes_region['ville'].tolist())

st.write("---")

#FONCTIONS EXTRACTION
def extraire_meteo(df):
    meteo_list = []
    for _, row in df.iterrows():
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": row['lat'],
                "longitude": row['lon'],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"
            }
        )
        if response.status_code == 200:
            data = response.json()['current']
            meteo_list.append({
                'lat': row['lat'], 'lon': row['lon'],
                'temperature': data['temperature_2m'],
                'humidite': data['relative_humidity_2m'],
                'vent': data['wind_speed_10m']
            })
        time.sleep(0.3)
    return pd.DataFrame(meteo_list)

def extraire_pollution(df):
    pollution_list = []
    for _, row in df.iterrows():
        response = requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                "latitude": row['lat'],
                "longitude": row['lon'],
                "current": "pm10,pm2_5,european_aqi"
            }
        )
        if response.status_code == 200:
            data = response.json()['current']
            pollution_list.append({
                'lat': row['lat'], 'lon': row['lon'],
                'aqi': data['european_aqi'],
                'pm2_5': data['pm2_5'],
                'pm10': data['pm10']
            })
        time.sleep(0.3)
    return pd.DataFrame(pollution_list)

# ===== BOUTON CHARGEMENT =====
if st.button("Charger les données"):
    
    # Extraction données
    df_meteo = extraire_meteo(villes_region)
    df_pollution = extraire_pollution(villes_region)
    
    # Jointures données
    df_final = villes_region.merge(df_meteo, on=['lat', 'lon']) \
                            .merge(df_pollution, on=['lat', 'lon'])
    
    # FOCUS VILLE
    st.subheader(f"{ville_choisie}")
    
    ville_data = df_final[df_final['ville'] == ville_choisie].iloc[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Température", f"{ville_data['temperature']:.1f}°C")
        st.metric("Humidité", f"{ville_data['humidite']:.0f}%")
    with col2:
        st.metric("Vent", f"{ville_data['vent']:.1f} km/h")
        st.metric("AQI", f"{ville_data['aqi']:.0f}")
    with col3:
        st.metric("PM2.5", f"{ville_data['pm2_5']:.1f} ug/m³")
        st.metric("PM10", f"{ville_data['pm10']:.1f} ug/m³")
    
    # STATS REGION
    st.write("---")
    st.subheader(f"Région {region_choisie}")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.metric("Température moyenne", f"{df_final['temperature'].mean():.1f}°C")
        st.metric("AQI moyen", f"{df_final['aqi'].mean():.0f}")
    
    with col_b:
        ville_plus_chaude = df_final.loc[df_final['temperature'].idxmax(), 'ville']
        ville_plus_polluee = df_final.loc[df_final['aqi'].idxmax(), 'ville']
        st.metric("Ville la plus chaude", ville_plus_chaude)
        st.metric("Ville la plus polluée", ville_plus_polluee)
    
    # TOP
    st.write("---")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Températures")
        top_temp = df_final.nlargest(len(df_final), 'temperature')[['ville', 'temperature']]
        
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.barh(top_temp['ville'], top_temp['temperature'], color='orange')
        ax1.set_xlabel('Top Température (°C)')
        ax1.invert_yaxis()
        st.pyplot(fig1)
    
    with col_right:
        st.subheader("Top  Pollution (AQI)")
        top_aqi = df_final.nlargest(len(df_final), 'aqi')[['ville', 'aqi']]
        
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.barh(top_aqi['ville'], top_aqi['aqi'], color='red')
        ax2.set_xlabel('AQI')
        ax2.invert_yaxis()
        st.pyplot(fig2)
    
    # Tableau complet région
    st.write("---")
    st.subheader("Détails des préfectures")
    st.dataframe(
    df_final[['ville', 'temperature', 'humidite', 'vent', 'aqi', 'pm2_5', 'pm10']]
    .set_index('ville')
)