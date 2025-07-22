from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
from utils.mongo_utils import insert_documents

WATER_API_URL = "https://api.waterdata.usgs.gov/ogcapi/v0/collections/daily/items?f=json&limit=100"
MONGO_COLLECTION = "raw_water"

def ingest_water_api(ti):
    response = requests.get(WATER_API_URL)
    if response.status_code == 200:
        data = response.json()
        
        # La data está en data['features'], una lista de dicts con observaciones
        features = data.get('features', [])
        
        inserted_ids = insert_documents(MONGO_COLLECTION, features)
        
        ti.xcom_push(key="water_records_count", value=len(inserted_ids))
    else:
        raise Exception(f"Failed to fetch Water data, status code {response.status_code}")

default_args = {
    'start_date': datetime(2025, 1, 1),
}

with DAG(
    dag_id="ingestion_water",
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=["ingestion"]
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_water_api_task",
        python_callable=ingest_water_api,
    )