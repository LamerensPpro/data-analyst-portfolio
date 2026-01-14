import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Titre
st.title("🌤️ Météo + Pollution - Villes France")
st.write("Données temps réel via API Open-Meteo")

# Liste des villes
villes = {
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Marseille": {"lat": 43.2965, "lon": 5.3698},
    "Lyon": {"lat": 45.7640, "lon": 4.8357},
    "Toulouse": {"lat": 43.6047, "lon": 1.4442},
    "Nice": {"lat": 43.7102, "lon": 7.2620},
    "Bordeaux": {"lat": 44.8378, "lon": -0.5792},
    "Lille": {"lat": 50.6292, "lon": 3.0573},
    "Pau": {"lat": 43.2951, "lon": -0.3708}
}

# Sélection ville
ville_choisie = st.selectbox("Choisir une ville :", list(villes.keys()))

# Récupérer coordonnées
lat = villes[ville_choisie]["lat"]
lon = villes[ville_choisie]["lon"]

# Bouton pour charger les données
if st.button("Charger les données"):
    
    with st.spinner("Chargement..."):
        
        # API Météo
        url_meteo = "https://api.open-meteo.com/v1/forecast"
        params_meteo = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"
        }
        
        response_meteo = requests.get(url_meteo, params=params_meteo)
        
        # API Pollution
        url_pollution = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params_pollution = {
            "latitude": lat,
            "longitude": lon,
            "current": "pm10,pm2_5,european_aqi"
        }
        
        response_pollution = requests.get(url_pollution, params=params_pollution)
    
    # Afficher les résultats
    if response_meteo.status_code == 200 and response_pollution.status_code == 200:
        
        meteo = response_meteo.json()
        pollution = response_pollution.json()
        
        st.success("✅ Données chargées !")
        
        # Afficher météo
        st.subheader("🌡️ Météo")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            temp = meteo["current"]["temperature_2m"]
            st.metric("Température", f"{temp}°C")
        
        with col2:
            humidite = meteo["current"]["relative_humidity_2m"]
            st.metric("Humidité", f"{humidite}%")
        
        with col3:
            vent = meteo["current"]["wind_speed_10m"]
            st.metric("Vent", f"{vent} km/h")
        
        # Afficher pollution
        st.subheader("🏭 Qualité de l'air")
        col4, col5, col6 = st.columns(3)
        
        with col4:
            aqi = pollution["current"]["european_aqi"]
            st.metric("AQI", aqi)
        
        with col5:
            pm25 = pollution["current"]["pm2_5"]
            st.metric("PM2.5", f"{pm25} µg/m³")
        
        with col6:
            pm10 = pollution["current"]["pm10"]
            st.metric("PM10", f"{pm10} µg/m³")
        
        # Graphique simple
        st.subheader("📊 Comparaison")
        
        fig, ax = plt.subplots(figsize=(8, 4))
        categories = ["Température", "Humidité", "AQI"]
        valeurs = [temp, humidite, aqi]
        
        ax.bar(categories, valeurs, color=['orange', 'blue', 'red'])
        ax.set_ylabel("Valeur")
        ax.set_title(f"Données actuelles - {ville_choisie}")
        
        st.pyplot(fig)
        
    else:
        st.error("❌ Erreur lors du chargement des données")
