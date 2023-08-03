import psycopg2
from pymongo import MongoClient
from config import config
# PostgreSQL configuration
pg_config = {
    'dbname': config['db_name'],
    'user': config['db_user'],
    'password': config['db_pwd'],
    'host': config['db_host'],
}

# MongoDB configuration
mongo_client = MongoClient(config['mongo_url'])
mongo_db = mongo_client[config['db_name']]

def create_postgres_connection():
    try:
        connection = psycopg2.connect(**pg_config)
        return connection
    except Exception as e:
        raise ConnectionError("Failed to connect to PostgreSQL")

def create_mongo_connection():
    try:
        return mongo_db
    except Exception as e:
        raise ConnectionError("Failed to connect to MongoDB")
