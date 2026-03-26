"""
DAG Airflow - Pipeline données boursières
Version V1 : Simple et fonctionnel

3 tâches :
1. Ingestion des données via yfinance
2. Transformations dbt
3. Tests dbt
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Configuration par défaut
default_args = {
    'owner': 'pascal',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Définition du DAG
dag = DAG(
    'stock_data_pipeline',
    default_args=default_args,
    description='Pipeline quotidien de données boursières',
    schedule_interval='0 19 * * 1-5',  # Tous les jours de semaine à 19h (après clôture bourse)
    catchup=False,
    tags=['stocks', 'dbt', 'finance'],
)

# Tâche 1 : Ingestion des données
def ingest_stock_data():
    """Exécute le script d'ingestion Python"""
    import sys
    sys.path.insert(0, '/opt/airflow/scripts')
    
    # Import et exécution du script
    import importlib.util
    spec = importlib.util.spec_from_file_location("ingest", "/opt/airflow/scripts/01_ingest_stock_data.py")
    ingest_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ingest_module)
    
    print("✅ Ingestion terminée")

task_ingest = PythonOperator(
    task_id='ingest_stock_data',
    python_callable=ingest_stock_data,
    dag=dag,
)

# Tâche 2 : Transformations dbt
task_dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='cd /opt/airflow/stock_analysis && dbt run --profiles-dir /opt/airflow/stock_analysis',
    dag=dag,
)

# Tâche 3 : Tests dbt
task_dbt_test = BashOperator(
    task_id='dbt_test',
    bash_command='cd /opt/airflow/stock_analysis && dbt test --profiles-dir /opt/airflow/stock_analysis',
    dag=dag,
)

# Définition des dépendances
task_ingest >> task_dbt_run >> task_dbt_test
