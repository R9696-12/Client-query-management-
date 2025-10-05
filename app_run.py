import streamlit as st
import pandas as pd
from datetime import datetime
from database import *



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
    st.write("Manage client queries here.")

    
    status_filter = st.selectbox("Filter by Status", ["All", "Opened", "Closed"])
    
 
    df_queries = get_query_data(status_filter)

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