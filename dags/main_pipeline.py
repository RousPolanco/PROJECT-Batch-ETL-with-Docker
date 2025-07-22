from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Importa tus funciones reales de ingestión sin 'dags.' al inicio
from ingestion_covid import ingest_covid_api
from ingestion_pollution import ingest_pollution_api
from ingestion_water import ingest_water_api

# Aquí defino funciones simplificadas para transformación y carga, adapta a tu código real
def transform_all(**context):
    # Recuperar XComs de cada ingestión
    covid_count = context['ti'].xcom_pull(task_ids='ingest_covid_api_task', key='covid_records_count')
    pollution_count = context['ti'].xcom_pull(task_ids='ingest_pollution_api_task', key='pollution_records_count')
    water_count = context['ti'].xcom_pull(task_ids='ingest_water_api_task', key='water_records_count')
    
    print(f"Transformando datos: COVID={covid_count}, Pollution={pollution_count}, Water={water_count}")
    # Aquí agregas tu código real para limpiar y transformar datos

def load_mongo():
    print("Cargando datos transformados a MongoDB...")
    # Aquí agregas tu código real para cargar datos procesados

default_args = {
    'owner': 'rous',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

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
        provide_context=True,
    )

    load_mongo_task = PythonOperator(
        task_id='load_mongo_task',
        python_callable=load_mongo,
    )

    # Define el orden correcto: covid >> water >> pollution >> transform >> load
    ingest_covid_task >> ingest_water_task >> ingest_pollution_task >> transform_all_task >> load_mongo_task
