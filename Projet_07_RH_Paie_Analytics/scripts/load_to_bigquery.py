"""
Chargement des CSV bruts dans BigQuery (Projet 7 - RH/Paie Analytics)
"""

import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

load_dotenv()

KEYFILE = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
PROJECT_ID = os.environ["GCP_PROJECT_ID"]
DATASET = os.environ["GCP_DATASET"]

FICHIERS = {
    "raw_salaries": "data/raw/salaries.csv",
    "raw_contrats": "data/raw/contrats.csv",
    "raw_evenements": "data/raw/evenements.csv",
    "raw_paies": "data/raw/paies.csv",
    "raw_smic_historique": "data/raw/smic_historique.csv",
}


def creer_dataset_si_absent(client, dataset_id, location="EU"):
    try:
        client.get_dataset(dataset_id)
        print(f"Dataset {dataset_id} déjà existant.")
    except NotFound:
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = location
        client.create_dataset(dataset)
        print(f"Dataset {dataset_id} créé.")


def charger_csv_vers_bigquery(client, table_id, chemin_csv):
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition="WRITE_TRUNCATE",
    )

    with open(chemin_csv, "rb") as fichier:
        job = client.load_table_from_file(fichier, table_id, job_config=job_config)

    job.result()
    table = client.get_table(table_id)
    print(f"{table.num_rows} lignes chargées dans {table_id}")


if __name__ == "__main__":
    client = bigquery.Client.from_service_account_json(KEYFILE, project=PROJECT_ID)

    dataset_id = f"{PROJECT_ID}.{DATASET}"
    creer_dataset_si_absent(client, dataset_id)

    for nom_table, chemin in FICHIERS.items():
        table_id = f"{PROJECT_ID}.{DATASET}.{nom_table}"
        charger_csv_vers_bigquery(client, table_id, chemin)