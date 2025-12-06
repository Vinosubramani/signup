import psycopg2
from urllib.parse import urlparse

# Use the working non-pooling Supabase URL
DATABASE_URL = "postgres://postgres.zyudyulbspnaaxnfakde:I89APup0VpFtaSxw@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require"

# Parse the URL
result = urlparse(DATABASE_URL)

username = result.username
password = result.password
database = result.path[1:]  # skip leading '/'
hostname = result.hostname
port = result.port

try:
    # Connect to PostgreSQL
    connection = psycopg2.connect(
        user=username,
        password=password,
        host=hostname,
        port=port,
        database=database,
        sslmode='require'  # Supabase requires SSL
    )

    cursor = connection.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print("Connected successfully!")
    print("PostgreSQL version:", db_version)

except Exception as e:
    print("Error connecting to PostgreSQL:", e)

finally:
    if 'connection' in locals() and connection:
        cursor.close()
        connection.close()
        print("Connection closed.")
