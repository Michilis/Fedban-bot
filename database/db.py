import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

# Establish the connection to the database
conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)

def create_tables():
    with conn.cursor() as cur:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS federations (
            fed_id VARCHAR PRIMARY KEY,
            fed_name VARCHAR(255) NOT NULL,
            owner_id INTEGER NOT NULL,
            fadmins INTEGER[],
            banned_users INTEGER[],
            chat_ids INTEGER[]
        );
        ''')
        conn.commit()

def fetch_one(query, params=None):
    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchone()

def fetch_all(query, params=None):
    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()

def execute_query(query, params=None):
    with conn.cursor() as cur:
        cur.execute(query, params)
        conn.commit()
