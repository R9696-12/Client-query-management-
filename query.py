import pandas as pd
from datetime import datetime
from database import get_connection, create_tables  # Changed to absolute import

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
            
if __name__ == "__main__":
    load_data_from_csv()
