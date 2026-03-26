import yfinance as yf
from sqlalchemy import create_engine, text
import pandas as pd
import os
import datetime as dt
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

tickers = ["TTE.PA", "MC.PA", "AIR.PA", "BNP.PA", "SAN.PA"]

# Connexion avec variables d'environnement
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")

engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

# Récupérer la dernière date chargée
with engine.connect() as conn:
    result = conn.execute(text("SELECT MAX(\"Date\") as max_date FROM raw_stock_prices"))
    max_date = result.fetchone()[0]

# Si table vide, charger depuis 2024-01-01
if max_date is None:
    datedeb = "2024-01-01"
else:
    # Charger depuis le jour suivant
    datedeb = (max_date + dt.timedelta(days=1)).strftime("%Y-%m-%d")

datefin = dt.date.today()

# Si pas de nouvelles données, sortir
if datedeb >= datefin.strftime("%Y-%m-%d"):
    print("✅ Données à jour, aucune nouvelle donnée à charger")
    exit(0)

# Télécharger les données
df = yf.download(tickers, start=datedeb, end=datefin)

# Si aucune donnée (week-end, jour férié)
if df.empty:
    print("✅ Aucune donnée boursière disponible pour cette période")
    exit(0)

df = df.stack(level=1)
df.columns.name = None
df = df.reset_index()

# Vérifier les doublons potentiels
with engine.connect() as conn:
    existing = pd.read_sql(
        f"SELECT DISTINCT \"Date\", \"Ticker\" FROM raw_stock_prices WHERE \"Date\" >= '{datedeb}'",
        conn
    )

# Filtrer les lignes déjà présentes
df = df.merge(existing, on=['Date', 'Ticker'], how='left', indicator=True)
df = df[df['_merge'] == 'left_only'].drop(columns=['_merge'])

if len(df) == 0:
    print("✅ Aucune nouvelle donnée (doublons détectés)")
    exit(0)

# Ajouter colonne loaded_at pour traçabilité
df['loaded_at'] = dt.datetime.now()

# Append sans truncate
df.to_sql('raw_stock_prices', engine, if_exists='append', index=False)

print(f"✅ {len(df)} nouvelles lignes chargées depuis {datedeb}")