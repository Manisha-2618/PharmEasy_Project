"""
Helper script to initialize and seed a MySQL database when MySQL server is running.
Usage:
    python init_mysql.py
"""

import sys
import os
import pymysql
from config import Config

def init_mysql():
    print(f"Connecting to MySQL server at {Config.MYSQL_HOST}:{Config.MYSQL_PORT}...")
    try:
        # Connect without database first to create it
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            charset='utf8mb4',
            autocommit=True
        )
        cursor = conn.cursor()
        print(f"Creating database '{Config.MYSQL_DB}' if not exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DB}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE `{Config.MYSQL_DB}`")

        # Execute schema
        schema_path = os.path.join(Config.BASE_DIR, 'database', 'schema.sql')
        print(f"Applying schema from {schema_path}...")
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            for stmt in sql_content.split(';'):
                stmt = stmt.strip()
                if stmt and not stmt.lower().startswith('create database') and not stmt.lower().startswith('use '):
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        print(f"Notice on statement: {e}")
        
        conn.close()
        print("MySQL schema applied successfully!")

        # Now run seed data into MySQL
        print("Seeding MySQL tables...")
        # Temporarily force MySQL engine in seed
        from database.seed_data import seed_all
        seed_all()
        print("MySQL database setup & seed completed successfully!")
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        print("\nNote: Make sure your MySQL service (e.g., XAMPP, WAMP, or MySQL Windows Service) is started.")

if __name__ == '__main__':
    init_mysql()

