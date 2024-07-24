import os
import psycopg2
from psycopg2.extras import DictCursor

DATABASE_URL = os.getenv('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)

def create_tables():
    with conn.cursor() as cur:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS federations (
            fed_id SERIAL PRIMARY KEY,
            fed_name VARCHAR(255) NOT NULL,
            owner_id INTEGER NOT NULL,
            fadmins INTEGER[],
            banned_users INTEGER[]
        );
        ''')
        conn.commit()
