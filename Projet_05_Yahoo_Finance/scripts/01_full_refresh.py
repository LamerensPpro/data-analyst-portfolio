import yfinance as yf
from sqlalchemy import create_engine
import os
import datetime as dt
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

tickers = ["TTE.PA", "MC.PA", "AIR.PA", "BNP.PA", "SAN.PA"]

datedeb="2024-01-01"
datefin=dt.date.today()

df = yf.download(tickers, start=datedeb, end=datefin)
df = df.stack(level=1)
df.columns.name = None
df = df.reset_index()

# Connexion avec variables d'environnement
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")

engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")

# Vider la table au lieu de la supprimer
with engine.connect() as conn:
    conn.execute("TRUNCATE TABLE raw_stock_prices")
    conn.commit()

df.to_sql('raw_stock_prices', engine, if_exists='append', index=False)

print(f"✅ {len(df)} lignes")