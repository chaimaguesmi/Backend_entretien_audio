import pymongo
import os
from dotenv import load_dotenv


def get_mongo_connection():
    load_dotenv()
    connection_string = os.getenv("MONGODB_URL")
    db_name = connection_string.split("@")[1].split("/")[1]
    return pymongo.MongoClient(connection_string)[db_name]


mongo_client = get_mongo_connection()
