import os
from pymongo import MongoClient

def get_mongo_client():
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise RuntimeError("MONGO_URI is not set. Put it in .env or Docker env.")
    return MongoClient(uri, connectTimeoutMS=20000, serverSelectionTimeoutMS=20000)

