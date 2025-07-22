from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
from utils.mongo_utils import insert_documents

# Constants
COVID_API_URL = "https://disease.sh/v3/covid-19/historical/all?lastdays=all"
MONGO_COLLECTION = "raw_covid"

def ingest_covid_api(ti):
    response = requests.get(COVID_API_URL)
    if response.status_code == 200:
        data = response.json()
        
        # Data comes as a dict with keys like 'cases', 'deaths', 'recovered'
        # We transform it to a list of dicts with date and values for easier Mongo insert
        
        transformed_data = []
        dates = data.get('cases', {}).keys()
        for date in dates:
            transformed_data.append({
                "date": date,
                "cases": data['cases'].get(date),
                "deaths": data['deaths'].get(date),
                "recovered": data['recovered'].get(date)
            })
        
        # Insert into MongoDB collection raw_covid
        inserted_ids = insert_documents(MONGO_COLLECTION, transformed_data)
        
        # Push number of records inserted to XCom
        ti.xcom_push(key="covid_records_count", value=len(inserted_ids))
    else:
        raise Exception(f"Failed to fetch COVID data, status code {response.status_code}")

default_args = {
    'start_date': datetime(2025, 1, 1),
}

with DAG(
    dag_id="ingestion_covid",
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=["ingestion"]
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_covid_api_task",
        python_callable=ingest_covid_api,
    )
