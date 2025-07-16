import pymongo
import os
from dotenv import load_dotenv
from pymongoose import methods

load_dotenv()

def get_mongo_connection():
    connection_string = os.getenv("mongodb://portago-UAT:Idzh4PLGpZ2vOO8KRY0E@mongo.allence.cloud/portago-UAT")
    client = pymongo.MongoClient(connection_string)
    db = client.get_default_database()  # Récupère la base par défaut dans l'URL
    return db

mongo_client = get_mongo_connection()
methods.database = mongo_client 
