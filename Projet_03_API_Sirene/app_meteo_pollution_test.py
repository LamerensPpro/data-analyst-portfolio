import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Configuration page
st.set_page_config(
    page_title="Météo + Pollution France",
    page_icon="🌤️",
    layout="wide"
)

# Titre
st.title("🌤️ Dashboard Météo & Pollution - France")
st.markdown("*Données temps réel via Open-Meteo API*")
st.markdown("---")

# ===== DONNÉES DES VILLES =====
VILLES_FRANCE = {
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Marseille": {"lat": 43.2965, "lon": 5.3698},
    "Lyon": {"lat": 45.7640, "lon": 4.8357},
    "Toulouse": {"lat": 43.6047, "lon": 1.4442},
    "Nice": {"lat": 43.7102, "lon": 7.2620},
    "Nantes": {"lat": 47.2184, "lon": -1.5536},
    "Strasbourg": {"lat": 48.5734, "lon": 7.7521},
    "Bordeaux": {"lat": 44.8378, "lon": -0.5792},
    "Lille": {"lat": 50.6292, "lon": 3.0573},
    "Pau": {"lat": 43.2951, "lon": -0.3708}
}

# ===== FONCTIONS API =====
@st.cache_data(ttl=3600)  # Cache 1h
def get_meteo_data(lat, lon):
    """Récupère données météo"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code",
        "hourly": "temperature_2m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Europe/Paris",
        "forecast_days": 7
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

@st.cache_data(ttl=3600)
def get_pollution_data(lat, lon):
    """Récupère données pollution"""
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,european_aqi",
        "timezone": "Europe/Paris"
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

@st.cache_data(ttl=3600)
def get_all_cities_data():
    """Récupère données toutes villes"""
    all_data = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, (ville, coords) in enumerate(VILLES_FRANCE.items()):
        status_text.text(f"Chargement {ville}...")
        
        meteo = get_meteo_data(coords["lat"], coords["lon"])
        pollution = get_pollution_data(coords["lat"], coords["lon"])
        
        if meteo and pollution:
            data = {
                "ville": ville,
                "lat": coords["lat"],
                "lon": coords["lon"],
                "temperature": meteo["current"]["temperature_2m"],
                "humidite": meteo["current"]["relative_humidity_2m"],
                "vent": meteo["current"]["wind_speed_10m"],
                "precipitation": meteo["current"].get("precipitation", 0),
                "aqi": pollution["current"]["european_aqi"],
                "pm2_5": pollution["current"]["pm2_5"],
                "pm10": pollution["current"]["pm10"],
                "ozone": pollution["current"]["ozone"],
                "no2": pollution["current"]["nitrogen_dioxide"]
            }
            all_data.append(data)
        
        progress_bar.progress((i + 1) / len(VILLES_FRANCE))
        time.sleep(0.3)
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(all_data)

# ===== SIDEBAR =====
st.sidebar.header("🎯 Navigation")

mode = st.sidebar.radio(
    "Choisir le mode :",
    ["📊 Vue d'ensemble", "🏙️ Détail ville"]
)

# ===== MODE VUE D'ENSEMBLE =====
if mode == "📊 Vue d'ensemble":
    st.header("📊 Vue d'ensemble - 10 villes")
    
    # Chargement données
    with st.spinner("Chargement des données..."):
        df = get_all_cities_data()
    
    st.success(f"✅ {len(df)} villes chargées - Dernière mise à jour : {datetime.now().strftime('%H:%M:%S')}")
    
    # Métriques globales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🌡️ Ville la plus chaude",
            f"{df.loc[df['temperature'].idxmax(), 'ville']}",
            f"{df['temperature'].max():.1f}°C"
        )
    
    with col2:
        st.metric(
            "❄️ Ville la plus froide",
            f"{df.loc[df['temperature'].idxmin(), 'ville']}",
            f"{df['temperature'].min():.1f}°C"
        )
    
    with col3:
        st.metric(
            "🏭 Ville la plus polluée",
            f"{df.loc[df['aqi'].idxmax(), 'ville']}",
            f"AQI {df['aqi'].max()}"
        )
    
    with col4:
        st.metric(
            "🌿 Ville la plus propre",
            f"{df.loc[df['aqi'].idxmin(), 'ville']}",
            f"AQI {df['aqi'].min()}"
        )
    
    st.markdown("---")
    
    # Graphiques
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🌡️ Températures")
        fig_temp = px.bar(
            df.sort_values('temperature', ascending=True),
            x='temperature',
            y='ville',
            orientation='h',
            color='temperature',
            color_continuous_scale='RdYlBu_r',
            labels={'temperature': 'Température (°C)'},
            height=400
        )
        fig_temp.update_layout(showlegend=False)
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col_right:
        st.subheader("🏭 Qualité de l'air (AQI)")
        
        # Couleurs selon AQI
        colors = ['green' if x < 30 else 'orange' if x < 50 else 'red' for x in df['aqi']]
        
        fig_aqi = go.Figure(go.Bar(
            x=df.sort_values('aqi', ascending=True)['aqi'],
            y=df.sort_values('aqi', ascending=True)['ville'],
            orientation='h',
            marker=dict(color=colors)
        ))
        fig_aqi.update_layout(
            xaxis_title="Indice AQI",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig_aqi, use_container_width=True)
    
    # Carte France
    st.subheader("🗺️ Carte des villes")
    
    fig_map = px.scatter_geo(
        df,
        lat='lat',
        lon='lon',
        text='ville',
        size='aqi',
        color='temperature',
        color_continuous_scale='RdYlBu_r',
        hover_name='ville',
        hover_data={
            'temperature': ':.1f',
            'aqi': True,
            'lat': False,
            'lon': False
        },
        scope='europe',
        height=500
    )
    
    fig_map.update_geos(
        center=dict(lat=46.5, lon=2.5),
        projection_scale=6,
        showland=True,
        landcolor='lightgray'
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Tableau données
    st.subheader("📋 Données détaillées")
    st.dataframe(
        df.style.background_gradient(subset=['temperature'], cmap='RdYlBu_r')
              .background_gradient(subset=['aqi'], cmap='RdYlGn_r'),
        use_container_width=True
    )

# ===== MODE DÉTAIL VILLE =====
else:
    st.header("🏙️ Détail par ville")
    
    # Sélection ville
    ville_selectionnee = st.selectbox(
        "Choisir une ville :",
        list(VILLES_FRANCE.keys())
    )
    
    coords = VILLES_FRANCE[ville_selectionnee]
    
    # Chargement données
    with st.spinner(f"Chargement données {ville_selectionnee}..."):
        meteo = get_meteo_data(coords["lat"], coords["lon"])
        pollution = get_pollution_data(coords["lat"], coords["lon"])
    
    if meteo and pollution:
        st.success(f"✅ Données chargées - {datetime.now().strftime('%H:%M:%S')}")
        
        # Métriques actuelles
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🌡️ Température",
                f"{meteo['current']['temperature_2m']:.1f}°C"
            )
        
        with col2:
            st.metric(
                "💧 Humidité",
                f"{meteo['current']['relative_humidity_2m']}%"
            )
        
        with col3:
            st.metric(
                "💨 Vent",
                f"{meteo['current']['wind_speed_10m']:.1f} km/h"
            )
        
        with col4:
            aqi = pollution['current']['european_aqi']
            aqi_label = "Bon" if aqi < 30 else "Moyen" if aqi < 50 else "Mauvais"
            st.metric(
                "🏭 AQI",
                aqi,
                aqi_label
            )
        
        st.markdown("---")
        
        # Prévisions 7 jours
        st.subheader("📅 Prévisions 7 jours")
        
        daily_data = pd.DataFrame({
            'Date': pd.to_datetime(meteo['daily']['time']),
            'Temp Max': meteo['daily']['temperature_2m_max'],
            'Temp Min': meteo['daily']['temperature_2m_min'],
            'Précipitations': meteo['daily']['precipitation_sum']
        })
        
        fig_previsions = go.Figure()
        
        fig_previsions.add_trace(go.Scatter(
            x=daily_data['Date'],
            y=daily_data['Temp Max'],
            name='Temp Max',
            line=dict(color='red')
        ))
        
        fig_previsions.add_trace(go.Scatter(
            x=daily_data['Date'],
            y=daily_data['Temp Min'],
            name='Temp Min',
            line=dict(color='blue')
        ))
        
        fig_previsions.update_layout(
            xaxis_title="Date",
            yaxis_title="Température (°C)",
            height=400
        )
        
        st.plotly_chart(fig_previsions, use_container_width=True)
        
        # Détails pollution
        st.subheader("🏭 Détails pollution")
        
        col_poll1, col_poll2 = st.columns(2)
        
        with col_poll1:
            st.metric("PM2.5", f"{pollution['current']['pm2_5']:.1f} µg/m³")
            st.metric("PM10", f"{pollution['current']['pm10']:.1f} µg/m³")
            st.metric("Ozone", f"{pollution['current']['ozone']:.1f} µg/m³")
        
        with col_poll2:
            st.metric("NO2", f"{pollution['current']['nitrogen_dioxide']:.1f} µg/m³")
            st.metric("SO2", f"{pollution['current']['sulphur_dioxide']:.1f} µg/m³")
            st.metric("CO", f"{pollution['current']['carbon_monoxide']:.1f} µg/m³")

# Footer
st.markdown("---")
st.markdown("*Données fournies par Open-Meteo API | Mise à jour automatique toutes les heures*")
