"""
Client BigQuery partagé, initialisé depuis les variables d'environnement.
"""

import os
from dotenv import load_dotenv
from google.cloud import bigquery

load_dotenv()

KEYFILE = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
PROJECT_ID = os.environ["GCP_PROJECT_ID"]
DATASET = os.environ["GCP_DATASET"]


def obtenir_client():
    return bigquery.Client.from_service_account_json(KEYFILE, project=PROJECT_ID)