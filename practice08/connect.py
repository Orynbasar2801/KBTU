import psycopg2
from config import db_params

def get_connection():
    return psycopg2.connect(**db_params)