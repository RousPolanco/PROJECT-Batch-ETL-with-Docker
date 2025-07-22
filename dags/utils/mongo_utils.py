from pymongo import MongoClient
import os

MONGO_HOST = os.getenv("MONGO_HOST", "mongodb")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_DB = os.getenv("MONGO_DB", "ProjectETL")  

def get_mongo_client():
    try:
        client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
        return client
    except Exception as e:
        print("Error connecting to MongoDB:", e)
        raise

def get_collection(APIS):
    client = get_mongo_client()
    db = client[MONGO_DB]
    return db[APIS]

def insert_documents(APIS, data):
    if not isinstance(data, list):
        data = [data]
    collection = get_collection(APIS)
    result = collection.insert_many(data)
    return result.inserted_ids

def get_all_documents(APIS):
    collection = get_collection(APIS)
    return list(collection.find())


