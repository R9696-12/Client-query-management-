import mysql.connector
from mysql.connector import Error
import pandas as pd
import hashlib
from database import get_connection, create_tables
from datetime import datetime
import streamlit as st
from database import *

# Streamlit frontend 1

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

#MySQL database connection and table creation 2


def load_data_from_csv(csv_filepath=r'C:\query management\synthetic_client_queries.csv'):
    """
    Reads data from a CSV file and loads it into the MySQL database.
    """
    try:
        df = pd.read_csv(csv_filepath)
        print(f"Successfully read {len(df)} rows from {csv_filepath}")
        # Strip whitespace and convert to title case to match ENUM values
        df['status'] = df['status'].str.strip().str.title()
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
       
       
    conn = get_connection()
    if conn is None:
        print("Failed to connect to the database. Exiting.")
        return

        cursor = conn.cursor()

        
        insert_query = """
        INSERT INTO queries (client_email, client_mobile, query_heading, query_description, status, date_raised, date_closed) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        # Prepare data for insertion
        data_to_insert = []
        for index, row in df.iterrows():
            created_time_str = row['date_raised']
            date_raised = datetime.strptime(created_time_str, '%m/%d/%Y')

            date_closed = None 
            if pd.notna(row['date_closed']) and str(row['date_closed']).strip() != '':
                closed_time_str = str(row['date_closed']).strip()
                try:
                   date_closed = datetime.strptime(closed_time_str, '%m/%d/%Y')
                except ValueError:
                   print(f"Warning: Skipping invalid closed date for row {index}: {closed_time_str}")
                   

            data_to_insert.append((
                row['client_email'],
                str(row['client_mobile']),  # Ensure mobile number is a string
                row['query_heading'],
                row['query_description'],
                row['status'],
                date_raised,
                date_closed
            ))
            
# CSV data loader 3


if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None


def show_login_page():
    st.title("Client Query Management System")
    st.subheader("Login / Register")

    choice = st.selectbox("Choose Action", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    

    if choice == "Register":
        role = st.selectbox("Role", ["Client", "Support"])
        if st.button("Register"):
            if add_user(username, password, role):
                st.success(f"User {username} registered successfully as {role}!")
            else:
                st.error("Registration failed. Username may already exist.")
    
    elif choice == "Login":
        if st.button("Login"):
            role = authenticate_user(username, password)
            
            if role:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.success(f"Logged in as {username} ({role})")
                st.rerun()
            else:
                st.error("Invalid Username or Password.")


def show_client_page():
    st.title("Submit a New Query")
    st.markdown("### 🧑‍💼 Logged in as Client")
    st.write("Please fill out the form below to submit your query")    

    with st.form(key='query_form'):
        client_email = st.text_input("Email ID")
        client_mobile = st.text_input("Mobile Number")
        query_heading = st.text_input("Query Heading")
        query_description = st.text_area("Query Description")
        submit_button = st.form_submit_button("Submit Query")

        if submit_button:
            if not all([client_email, client_mobile, query_heading, query_description]):
                st.error("Please fill in all the required fields.")
            else:
                

                if add_query(client_email, client_mobile, query_heading, query_description):
                    st.success("Your query has been submitted successfully!")
                else:
                    st.error("Failed to submit query. Please try again.")


def show_support_page():
    
    if 'success_message' in st.session_state and st.session_state.success_message:
        st.success(st.session_state.success_message)
        # Clear the message so it doesn't reappear on every refresh
        st.session_state.success_message = ""
        
    st.title("Support Team Dashboard")
    st.markdown("### 🧑‍💻 Logged in as Support")
    st.write("Manage client queries here.")

    
    status_filter = st.selectbox("Filter by Status", ["All", "Opened", "Closed"])
    
 
    df_queries = get_query_data(status_filter)
    if not df_queries.empty:
        total = len(df_queries)
        opened = len(df_queries[df_queries['status'] == 'Opened'])
        closed = len(df_queries[df_queries['status'] == 'Closed'])

        # Display 3 nice metrics side by side
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📋 Total Queries", total)
        with col2:
            st.metric("🟢 Opened", opened)
        with col3:
            st.metric("🔴 Closed", closed)

    st.subheader(f"{status_filter} Queries")
    
    if not df_queries.empty:
        
        st.dataframe(df_queries[['query_id', 'client_email', 'query_heading', 'status', 'date_raised', 'date_closed']])

        st.subheader("Manage Queries")
        
        open_queries = df_queries[df_queries['status'] == 'Opened']
        if not open_queries.empty:
            query_to_close = st.selectbox("Select a Query to Close", open_queries['query_id'])
            
            if st.button("Close Selected Query"):
                if update_query_status(query_to_close, 'Closed', datetime.now()):
                    st.session_state.success_message= f"Query {query_to_close} has been closed."
                    st.rerun()
                else:
                    st.error("Failed to close query.")
        else:
            st.info("No open queries to manage.")
        
        
        st.subheader("Query Details")
        selected_query_id = st.selectbox("View Details for Query ID", df_queries['query_id'])
        if selected_query_id:
            query_details = df_queries[df_queries['query_id'] == selected_query_id].iloc[0]
            st.write(f"**Query ID:** {query_details['query_id']}")
            st.write(f"**Email:** {query_details['client_email']}")
            st.write(f"**Mobile:** {query_details['client_mobile']}")
            st.write(f"**Heading:** {query_details['query_heading']}")
            st.write(f"**Description:** {query_details['query_description']}")
            st.write(f"**Status:** {query_details['status']}")
            st.write(f"**Created:** {query_details['date_raised']}")
            
            
    else:
        st.info("No queries found.")


def main():
    if not st.session_state.logged_in:
        show_login_page()
    else:
        st.sidebar.title(f"Welcome, {st.session_state.username}!")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.rerun()

        if st.session_state.role == "Client":
            show_client_page()
        elif st.session_state.role == "Support":
            show_support_page()

if __name__ == "__main__":
    
    create_tables() 
    main()
