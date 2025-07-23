from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

from ingestion_covid import ingest_covid_api
from ingestion_pollution import ingest_pollution_api
from ingestion_water import ingest_water_api

# Importa correctamente la función de transformación
from utils.transform_all_collections import transform_all_collections

# Función que ejecuta la transformación completa
def transform_all(**context):
    print("Ejecutando transformaciones...")
    transform_all_collections()

# Opcional: función de carga si necesitas agregar más lógica después
def load_mongo():
    print("Carga final (placeholder) - si necesitas cargar algo más, hazlo aquí")

# Configuración por defecto del DAG
default_args = {
    'owner': 'rous',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definición del DAG principal
with DAG(
    'main_pipeline',
    default_args=default_args,
    description='Pipeline principal con ingestión, transformación y carga',
    schedule_interval=None,
    catchup=False,
) as dag:

    ingest_covid_task = PythonOperator(
        task_id='ingest_covid_api_task',
        python_callable=ingest_covid_api,
    )

    ingest_water_task = PythonOperator(
        task_id='ingest_water_api_task',
        python_callable=ingest_water_api,
    )

    ingest_pollution_task = PythonOperator(
        task_id='ingest_pollution_api_task',
        python_callable=ingest_pollution_api,
    )

    transform_all_task = PythonOperator(
        task_id='transform_all_task',
        python_callable=transform_all,
    )

    load_mongo_task = PythonOperator(
        task_id='load_mongo_task',
        python_callable=load_mongo,
    )

    # Define el orden de ejecución correcto
    ingest_covid_task >> ingest_water_task >> ingest_pollution_task >> transform_all_task >> load_mongo_task
