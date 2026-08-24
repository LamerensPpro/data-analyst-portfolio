from bigquery_client import obtenir_client, PROJECT_ID

client = obtenir_client()
client.query(f"DELETE FROM `{PROJECT_ID}.rh_paie_analytics_anomalies_metier.historique_anomalies` WHERE TRUE").result()
print("Table vidée.")