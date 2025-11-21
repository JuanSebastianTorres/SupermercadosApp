from pymongo import MongoClient

MONGO_URI = "mongodb://mongo:JaYxMtWeozSLgENuyZEfCrkToSvqpjOF@yamanote.proxy.rlwy.net:56843"
DB_NAME = "SupermercadosApp"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def get_db():
    return db
