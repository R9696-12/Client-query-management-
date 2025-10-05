import mysql.connector
from mysql.connector import Error
import pandas as pd
import hashlib
from datetime import datetime

def get_connection():
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='query_management_db',
            user='root', 
            password='Ravi@123' 
        )
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def create_tables():
    
    conn = get_connection()
    if conn is not None:
        cursor = conn.cursor()
        
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(255) PRIMARY KEY,
                hashed_password TEXT NOT NULL,
                role ENUM('Client', 'Support') NOT NULL
            )
        """)
        
       
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                query_id INT AUTO_INCREMENT PRIMARY KEY,
                client_email VARCHAR(255) NOT NULL,
                client_mobile VARCHAR(20) NOT NULL,
                query_heading VARCHAR(255) NOT NULL,
                query_description TEXT NOT NULL,
                status ENUM('Opened', 'Closed') NOT NULL,
                date_raised DATETIME NOT NULL,
                date_closed DATETIME
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password, role):
   
    conn = get_connection()
    if conn is not None:
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        try:
            cursor.execute("INSERT INTO users (username, hashed_password, role) VALUES (%s, %s, %s)",
                           (username, hashed_password, role))
            conn.commit()
            return True
        except Error as e:
            print(f"Error adding user: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

def authenticate_user(username, password):
   
    conn = get_connection()
    if conn is not None:
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        try:
            cursor.execute("SELECT role FROM users WHERE username = %s AND hashed_password = %s",
                           (username, hashed_password))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Authentication error: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

def add_query(client_email, client_mobile, query_heading, query_description):
   
    conn = get_connection()
    if conn is not None:
        cursor = conn.cursor()
        query = """INSERT INTO queries (client_email, client_mobile, query_heading, query_description, status, date_raised) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        try:
            cursor.execute(query, (client_email, client_mobile, query_heading, query_description, 'Opened', datetime.now()))
            conn.commit()
            return True
        except Error as e:
            print(f"Error adding query: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

def get_all_queries():
    
    conn = get_connection()
    if conn is not None:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM queries ORDER BY date_raised DESC")
        queries = cursor.fetchall()
        cursor.close()
        conn.close()
        return queries
    return []

def update_query_status(query_id, status, date_closed):
    
    conn = get_connection()
    if conn is not None:
        cursor = conn.cursor()
        query = "UPDATE queries SET status = %s, date_closed = %s WHERE query_id = %s"
        try:
            cursor.execute(query, (status, date_closed, query_id))
            conn.commit()
            return True
        except Error as e:
            print(f"Error updating query status: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
            
def get_query_data(status_filter):
    
    conn = get_connection()
    if conn is not None:
        cursor = conn.cursor(dictionary=True)
        if status_filter == 'All':
            cursor.execute("SELECT * FROM queries ORDER BY date_raised DESC")
        else:
            cursor.execute("SELECT * FROM queries WHERE status = %s ORDER BY date_raised DESC", (status_filter,))
        records = cursor.fetchall()
        cursor.close()
        conn.close()
        return pd.DataFrame(records)
    return pd.DataFrame()