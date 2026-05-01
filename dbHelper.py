import os
import psycopg2

# Database connection parameters from your Nix environment
DB_NAME = "aircraft_db"
DB_USER = "aircraft_db"

DB_HOST = os.environ.get("PGHOST", "127.0.0.1")
DB_PORT = os.environ.get("PGPORT", "5432")


def getConnection():
    return psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT,password=""
    )