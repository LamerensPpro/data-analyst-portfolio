import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

# ===== CONFIGURATION =====
st.title("🌤️ Météo + Pollution - Villes France")
st.write("Données temps réel via API Open-Meteo")
st.write("---")

# ===== SOURCE 1 : DATAFRAME VILLES =====
# Table de référence : villes françaises avec leurs coordonnées GPS

df_villes = pd.DataFrame([
    {'ville': 'Paris', 'lat': 48.8566, 'lon': 2.3522},
    {'ville': 'Marseille', 'lat': 43.2965, 'lon': 5.3698},
    {'ville': 'Lyon', 'lat': 45.7640, 'lon': 4.8357},
    {'ville': 'Toulouse', 'lat': 43.6047, 'lon': 1.4442},
    {'ville': 'Nice', 'lat': 43.7102, 'lon': 7.2620},
    {'ville': 'Bordeaux', 'lat': 44.8378, 'lon': -0.5792},
    {'ville': 'Lille', 'lat': 50.6292, 'lon': 3.0573},
    {'ville': 'Pau', 'lat': 43.2951, 'lon': -0.3708}
])

st.subheader("📍 Villes disponibles")
st.dataframe(df_villes, use_container_width=True)

# ===== FONCTIONS EXTRACTION API =====

def extraire_meteo(df_villes):
    """
    Appelle l'API météo pour chaque ville du DataFrame
    Retourne un DataFrame avec lat, lon et données météo
    """
    meteo_list = []
    
    for index, row in df_villes.iterrows():
        # Appel API
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": row['lat'],
            "longitude": row['lon'],
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current']
                
                # Construction ligne du DataFrame
                meteo_list.append({
                    'lat': row['lat'],
                    'lon': row['lon'],
                    'temperature': current['temperature_2m'],
                    'humidite': current['relative_humidity_2m'],
                    'vent': current['wind_speed_10m']
                })
            
            time.sleep(0.3)  # Respect limites API
            
        except Exception as e:
            st.warning(f"Erreur météo pour lat={row['lat']}, lon={row['lon']}: {e}")
    
    # Conversion en DataFrame
    df_meteo = pd.DataFrame(meteo_list)
    return df_meteo


def extraire_pollution(df_villes):
    """
    Appelle l'API pollution pour chaque ville du DataFrame
    Retourne un DataFrame avec lat, lon et données pollution
    """
    pollution_list = []
    
    for index, row in df_villes.iterrows():
        # Appel API
        url = "https://air-quality-api.open-meteo.com/v1/air-quality"
        params = {
            "latitude": row['lat'],
            "longitude": row['lon'],
            "current": "pm10,pm2_5,european_aqi"
        }
        
        try:
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current']
                
                # Construction ligne du DataFrame
                pollution_list.append({
                    'lat': row['lat'],
                    'lon': row['lon'],
                    'aqi': current['european_aqi'],
                    'pm2_5': current['pm2_5'],
                    'pm10': current['pm10']
                })
            
            time.sleep(0.3)  # Respect limites API
            
        except Exception as e:
            st.warning(f"Erreur pollution pour lat={row['lat']}, lon={row['lon']}: {e}")
    
    # Conversion en DataFrame
    df_pollution = pd.DataFrame(pollution_list)
    return df_pollution


# ===== INTERFACE UTILISATEUR =====

st.write("---")
st.subheader("🔄 Extraction des données")

if st.button("Charger les données météo + pollution"):
    
    # Barre de progression
    progress_bar = st.progress(0)
    status = st.empty()
    
    # ÉTAPE 1 : Extraction météo
    status.text("⏳ Extraction données météo...")
    df_meteo = extraire_meteo(df_villes)
    progress_bar.progress(33)
    
    st.success(f"✅ Météo extraite : {len(df_meteo)} lignes")
    with st.expander("Voir DataFrame météo"):
        st.dataframe(df_meteo)
    
    # ÉTAPE 2 : Extraction pollution
    status.text("⏳ Extraction données pollution...")
    df_pollution = extraire_pollution(df_villes)
    progress_bar.progress(66)
    
    st.success(f"✅ Pollution extraite : {len(df_pollution)} lignes")
    with st.expander("Voir DataFrame pollution"):
        st.dataframe(df_pollution)
    
    # ÉTAPE 3 : Jointures
    status.text("⏳ Jointures en cours...")
    
    # Join 1 : Villes + Météo
    df_step1 = df_villes.merge(
        df_meteo, 
        on=['lat', 'lon'], 
        how='left',
        indicator=True
    )
    
    # Vérification intégrité join 1
    nb_matches_1 = (df_step1['_merge'] == 'both').sum()
    st.info(f"🔗 Join 1 (Villes + Météo) : {nb_matches_1}/{len(df_villes)} matchs")
    df_step1 = df_step1.drop('_merge', axis=1)
    
    # Join 2 : (Villes + Météo) + Pollution
    df_final = df_step1.merge(
        df_pollution,
        on=['lat', 'lon'],
        how='left',
        indicator=True
    )
    
    # Vérification intégrité join 2
    nb_matches_2 = (df_final['_merge'] == 'both').sum()
    st.info(f"🔗 Join 2 (+ Pollution) : {nb_matches_2}/{len(df_villes)} matchs")
    df_final = df_final.drop('_merge', axis=1)
    
    progress_bar.progress(100)
    status.text("✅ Traitement terminé !")
    
    # Nettoyage affichage
    time.sleep(1)
    progress_bar.empty()
    status.empty()
    
    st.write("---")
    st.subheader("📊 Données consolidées")
    
    # Affichage DataFrame final
    st.dataframe(
        df_final.style.format({
            'lat': '{:.4f}',
            'lon': '{:.4f}',
            'temperature': '{:.1f}°C',
            'humidite': '{:.0f}%',
            'vent': '{:.1f} km/h',
            'aqi': '{:.0f}',
            'pm2_5': '{:.1f} µg/m³',
            'pm10': '{:.1f} µg/m³'
        }),
        use_container_width=True
    )
    
    # ===== ANALYSES =====
    
    st.write("---")
    st.subheader("📈 Analyses")
    
    # Métriques comparatives
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        ville_plus_chaude = df_final.loc[df_final['temperature'].idxmax(), 'ville']
        temp_max = df_final['temperature'].max()
        st.metric("🌡️ Ville la plus chaude", ville_plus_chaude, f"{temp_max:.1f}°C")
    
    with col2:
        ville_plus_froide = df_final.loc[df_final['temperature'].idxmin(), 'ville']
        temp_min = df_final['temperature'].min()
        st.metric("❄️ Ville la plus froide", ville_plus_froide, f"{temp_min:.1f}°C")
    
    with col3:
        ville_plus_polluee = df_final.loc[df_final['aqi'].idxmax(), 'ville']
        aqi_max = df_final['aqi'].max()
        st.metric("🏭 Ville la plus polluée", ville_plus_polluee, f"AQI {aqi_max:.0f}")
    
    with col4:
        ville_plus_propre = df_final.loc[df_final['aqi'].idxmin(), 'ville']
        aqi_min = df_final['aqi'].min()
        st.metric("🌿 Ville la plus propre", ville_plus_propre, f"AQI {aqi_min:.0f}")
    
    # Graphiques
    st.write("---")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🌡️ Températures par ville")
        
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        df_sorted = df_final.sort_values('temperature', ascending=True)
        ax1.barh(df_sorted['ville'], df_sorted['temperature'], color='orange')
        ax1.set_xlabel('Température (°C)')
        ax1.set_title('Températures actuelles')
        ax1.grid(axis='x', alpha=0.3)
        
        st.pyplot(fig1)
    
    with col_right:
        st.subheader("🏭 Qualité de l'air par ville")
        
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        df_sorted_aqi = df_final.sort_values('aqi', ascending=True)
        
        # Couleurs selon seuils AQI
        colors = ['green' if x < 30 else 'orange' if x < 50 else 'red' 
                  for x in df_sorted_aqi['aqi']]
        
        ax2.barh(df_sorted_aqi['ville'], df_sorted_aqi['aqi'], color=colors)
        ax2.set_xlabel('AQI (Indice Qualité Air)')
        ax2.set_title('Qualité de l\'air (vert=bon, orange=moyen, rouge=mauvais)')
        ax2.grid(axis='x', alpha=0.3)
        
        st.pyplot(fig2)
    
    # Corrélation
    st.write("---")
    st.subheader("🔍 Corrélation Température vs Pollution")
    
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.scatter(df_final['temperature'], df_final['aqi'], s=100, alpha=0.6)
    
    # Annotations
    for i, row in df_final.iterrows():
        ax3.annotate(
            row['ville'], 
            (row['temperature'], row['aqi']),
            fontsize=9,
            ha='right'
        )
    
    ax3.set_xlabel('Température (°C)')
    ax3.set_ylabel('AQI')
    ax3.set_title('Relation entre température et qualité de l\'air')
    ax3.grid(alpha=0.3)
    
    st.pyplot(fig3)
    
    # Export
    st.write("---")
    st.subheader("💾 Export des données")
    
    csv = df_final.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="📥 Télécharger CSV",
        data=csv,
        file_name='meteo_pollution_france.csv',
        mime='text/csv'
    )

st.write("---")
st.info("💡 **Méthodologie :** Extraction de 2 APIs distinctes → Jointures sur coordonnées GPS → Analyses comparatives")
