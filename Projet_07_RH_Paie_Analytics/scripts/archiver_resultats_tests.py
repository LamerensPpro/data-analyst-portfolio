"""
Archive les résultats de dbt test (store_failures) avec horodatage et code anomalie.
"""

from datetime import datetime
from google.cloud.exceptions import NotFound
from bigquery_client import obtenir_client, PROJECT_ID

SCHEMA_FAILURES = "rh_paie_analytics_anomalies_metier"
TABLE_ARCHIVE = "historique_anomalies"


def creer_table_archive_si_absente(client):
    from google.cloud import bigquery

    table_id = f"{PROJECT_ID}.{SCHEMA_FAILURES}.{TABLE_ARCHIVE}"
    try:
        client.get_table(table_id)
    except NotFound:
        schema = [
            bigquery.SchemaField("date_run", "TIMESTAMP"),
            bigquery.SchemaField("nom_test", "STRING"),
            bigquery.SchemaField("matricule", "INT64"),
            bigquery.SchemaField("mois", "DATE"),
            bigquery.SchemaField("code_anomalie", "STRING"),
        ]
        table = bigquery.Table(table_id, schema=schema)
        client.create_table(table)
        print(f"Table {table_id} créée.")


def archiver_resultats(client):
    date_run = datetime.now().isoformat()

    query = f"""
    SELECT table_name
    FROM `{PROJECT_ID}.{SCHEMA_FAILURES}.INFORMATION_SCHEMA.TABLES`
    WHERE table_name != '{TABLE_ARCHIVE}'
    """
    tables_echec = [row.table_name for row in client.query(query).result()]

    for table in tables_echec:
        requete_archive = f"""
        INSERT INTO `{PROJECT_ID}.{SCHEMA_FAILURES}.{TABLE_ARCHIVE}`
        SELECT
            TIMESTAMP('{date_run}') as date_run,
            '{table}' as nom_test,
            matricule,
            mois,
            code_anomalie
        FROM `{PROJECT_ID}.{SCHEMA_FAILURES}.{table}`
        """
        client.query(requete_archive).result()
        print(f"Archivé : {table}")


if __name__ == "__main__":
    client = obtenir_client()
    creer_table_archive_si_absente(client)
    archiver_resultats(client)