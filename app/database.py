from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

_client = None
_db = None
# MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority

def db_connect():
    global _client, _db

    if _db is None:
        MONGO_URI = os.getenv("MONGO_URI")
        _client = MongoClient(MONGO_URI)
        _db = _client["amazon_sales_db"]

    return _db


def get_collection(name: str):
    db = db_connect()
    return db[name]
