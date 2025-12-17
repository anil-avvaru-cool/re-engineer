import psycopg2
import numpy as np
import os
from dotenv import load_dotenv
from psycopg2 import Error
from psycopg2.extras import execute_batch

# CREATE EXTENSION vector;
# SELECT id,SUBSTRING(ni.chunk, 1, 200) AS short_chunk, embedding as dimension FROM issue_tracker ni
# ORDER BY embedding <=> '[5.99734336e-02,-1.30569497e-02]'
# LIMIT 5;
# drop table issue_tracker;
# CREATE TABLE issue_tracker (id bigserial PRIMARY KEY,chunk VARCHAR NOT NULL,embedding vector(768));
# CREATE INDEX ON issue_tracker USING hnsw (embedding vector_cosine_ops);

class PostgreSQLManager:
    def __init__(self, db_params):
        """
        Initializes the database connection.
        db_params should be a dictionary with keys like 'host', 'database', 'user', 'password', 'port'.
        """
        self.db_params = db_params
        self.connection = None

    def connect(self):
        """Establishes a connection to the PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(**self.db_params)
            self.connection.autocommit = False  # Disable autocommit for explicit transactions
            print("Database connection established successfully.")
        except Error as e:
            print(f"Error connecting to database: {e}")
            self.connection = None

    def disconnect(self):
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
            
    def execute_batch(self, insert_query, data_to_insert) -> bool:
        try:
            with self.connection.cursor() as cursor:
                psycopg2.extras.execute_batch(cursor, insert_query, data_to_insert)
                self.connection.commit()  # Commit changes for CUD operations
                return True
        except Error as e:
            self.connection.rollback()  # Rollback on error
            print(f"Database operation failed: {e}")
            return None
            
    def execute_select_count(self, select_query) -> int :
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(select_query)
                count_after = cursor.fetchone()[0]            
                return count_after
        except Error as e:
            self.connection.rollback()  # Rollback on error
            print(f"Database operation failed: {e}")
            return None

    def execute_query(self, query, params=None, fetch_result=False):
        """Helper method to execute a query and handle transactions."""
        if not self.connection:
            print("No database connection. Please connect first.")
            return None

        try:
            with self.connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                if fetch_result:
                    return cursor.fetchall()
                else:
                    self.connection.commit()  # Commit changes for CUD operations
                    return True
        except Error as e:
            self.connection.rollback()  # Rollback on error
            print(f"Database operation failed: {e}")
            return None

def save_relevant_chunks(recursive_chunks:list, embeddings_list:list, table_name:str) -> int:
    load_dotenv()
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    db_params = {
            "host": DB_HOST,
            "database": DB_NAME,
            "user": DB_USER,
            "password": DB_PASS,
            "port": DB_PORT
        }

    crud_manager = PostgreSQLManager(db_params)
    crud_manager.connect()

    data_to_insert = []
    for i in range(len(embeddings_list)):
        content = recursive_chunks[i]            
        embedding = embeddings_list[i]
        data_to_insert.append((content,embedding))

    if crud_manager.connection:        
        truncate_sql = f"truncate table {table_name};"
        crud_manager.execute_query(truncate_sql)
        
        insert_sql = f"INSERT INTO {table_name} (chunk, embedding) VALUES (%s, %s)"        
        crud_manager.execute_batch(insert_sql, data_to_insert)
        
        rows_inserted = crud_manager.execute_select_count(f"SELECT COUNT(*) FROM {table_name};")        
        crud_manager.disconnect()
        return rows_inserted