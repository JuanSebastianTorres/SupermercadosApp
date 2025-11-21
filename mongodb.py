# mongodb.py
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "SupermercadosApp")

_client = None
_db = None

def get_client():
    global _client
    if _client is None:
        if not MONGO_URI:
            raise RuntimeError("MONGO_URI no está definido")
        _client = MongoClient(MONGO_URI)
    return _client

def get_db():
    global _db
    if _db is None:
        client = get_client()
        _db = client[MONGO_DBNAME]
    return _db
