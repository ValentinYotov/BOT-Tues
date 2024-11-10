import os

DATABASE = {
    'dbname': os.getenv('POSTGRES_DB', 'mydatabase'),
    'user': os.getenv('POSTGRES_USER', 'myuser'),
    'password': os.getenv('POSTGRES_PASSWORD', 'mypassword'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),  # Променяме хоста от 'db' на 'localhost'
    'port': '5432',
}