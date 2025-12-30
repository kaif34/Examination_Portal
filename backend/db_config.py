import os
from flask_mysqldb import MySQL
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def init_mysql(app):
    # Use os.getenv to read from .env, with defaults if the file is missing
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
    
    # This reads the empty password from your .env file
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', '') 
    
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'entrance_database')
    
    mysql = MySQL(app)
    return mysql