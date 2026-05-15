import yfinance as yf
import pandas as pd
from google.cloud import bigquery
from google.cloud.bigquery import SchemaField, LoadJobConfig, WriteDisposition

TICKERS = ["BTC-USD", "ETH-USD", "SOL-USD"]
DATASET = "crypto_data"
TABLE_ID = "prix_crypto"

SCHEMA = [
    SchemaField("date", "DATE"),
    SchemaField("ticker", "STRING"),
    SchemaField("close", "FLOAT"),
    SchemaField("high", "FLOAT"),
    SchemaField("low", "FLOAT"),
    SchemaField("open", "FLOAT"),
    SchemaField("volume", "FLOAT"),
]

def get_project():
    client = bigquery.Client()
    return client.project

def download_prices(tickers, start, end):
    df = yf.download(tickers, start=start, end=end)
    df = df.stack(level=1, future_stack=True).reset_index()
    df.columns.name = None
    df.columns = [c.lower() for c in df.columns]
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

def load_to_bq(df, write_mode):
    client = bigquery.Client()
    table = f"{client.project}.{DATASET}.{TABLE_ID}"
    client.create_dataset(DATASET, exists_ok=True)
    job_config = LoadJobConfig(schema=SCHEMA, write_disposition=write_mode)
    job = client.load_table_from_dataframe(df, table, job_config=job_config)
    job.result()
    print(f"{job.output_rows} lignes chargées")

def load_history():
    end = str(pd.Timestamp.today().date() + pd.Timedelta(days=1))
    df = download_prices(["BTC-USD", "ETH-USD", "SOL-USD"], 
                         start="2021-01-01", end=end)
    load_to_bq(df, WriteDisposition.WRITE_TRUNCATE)

def load_daily():
    today = pd.Timestamp.today().date()
    client = bigquery.Client()
    table = f"{client.project}.{DATASET}.{TABLE_ID}"
    
    # Suppression doublon date
    client.query(f"DELETE FROM `{table}` WHERE date = '{today}'").result()
    
    df = download_prices(TICKERS, start=str(today), end=str(today + pd.Timedelta(days=1)))
    if df.empty:
        print("Pas de données aujourd'hui")
        return
    load_to_bq(df, WriteDisposition.WRITE_APPEND)