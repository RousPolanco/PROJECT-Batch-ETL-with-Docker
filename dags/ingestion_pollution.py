from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
from utils.mongo_utils import insert_documents

POLLUTION_API_URL = "https://public.opendatasoft.com/api/records/1.0/search/?dataset=worldwide-pollution&rows=100&format=json"
MONGO_COLLECTION = "raw_pollution"

def ingest_pollution_api(ti):
    response = requests.get(POLLUTION_API_URL)
    if response.status_code == 200:
        data = response.json()
        
        # La data está en data['records'], lista de observaciones
        records = data.get('records', [])
        
        inserted_ids = insert_documents(MONGO_COLLECTION, records)
        
        ti.xcom_push(key="pollution_records_count", value=len(inserted_ids))
    else:
        raise Exception(f"Failed to fetch Pollution data, status code {response.status_code}")

default_args = {
    'start_date': datetime(2025, 1, 1),
}

with DAG(
    dag_id="ingestion_pollution",
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=["ingestion"]
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_pollution_api_task",
        python_callable=ingest_pollution_api,
    )
