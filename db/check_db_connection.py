import os

import psycopg
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Read the database URL without displaying it
database_url = os.getenv("SUPABASE_DATABASE_URL")

if not database_url:
    print("ERROR: SUPABASE_DATABASE_URL is not configured.")
else:
    try:
        # Open a connection and run a simple test query
        with psycopg.connect(database_url, connect_timeout=10) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                result = cursor.fetchone()

        print("SUCCESS: Connected to PostgreSQL.")
        print("Database version:", result[0].split(",")[0])

    except Exception as error:
        print("ERROR: Database connection failed.")
        print("Error type:", type(error).__name__)
        print("Error details:", str(error))