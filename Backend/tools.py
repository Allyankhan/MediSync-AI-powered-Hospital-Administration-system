from langchain_core.tools import tool
import sqlite3
import mysql.connector

from rag import get_rag_chain

from sql_tool import execute_sql
from weather_tool import search

rag_chain = get_rag_chain()


@tool
def hospital_rag(question:str):
    """
    Search hospital documents.
    """

    response = rag_chain.invoke(
        {
            "input":question
        }
    )

    return response["answer"]


@tool
def hospital_sql(sql_query: str):
    """
    Execute SQL query on hospital database.
    """
    try:
        # Try to execute the query normally
        result = execute_sql(sql_query)
        return str(result)
    except Exception as e:
   
        return f"SQL Error: {str(e)}\n\nHint: You likely guessed a column name wrong. Use the get_table_schema tool to find the correct columns, then rewrite your query."
@tool
def weather_tool(question: str):
    """
    Search web for weather related information
    """
    print(f"\n[DEBUG] The AI decided to trigger the weather_tool with this query: {question}\n")
    # DuckDuckGoSearchRun takes the query string and returns a result string
    response = search.invoke(question)
    return response
@tool
def get_table_schema(table_name: str):
    """
    Use this tool to find the exact column names of a table before writing an SQL query.
    """
    # Write a quick SQL query that returns the columns for the requested table
    query = f"DESCRIBE {table_name};"
    return str(execute_sql(query))

@tool


def book_appointment(patient_name: str, department: str, date: str, time: str):
    """
    Executes the database INSERT to book a medical appointment.
    CRITICAL INSTRUCTION: You MUST NOT call this tool unless the user has explicitly 
    provided ALL four required parameters (patient_name, department, date, time). 
    If any parameter is missing, DO NOT call this tool. Instead, ask the user to provide 
    the missing information. Do not assume or generate fake names or times.
    """
    try:
        # Connect to your XAMPP MySQL server
        conn = mysql.connector.connect(
            host="localhost",       
            user="root",            # Default XAMPP username
            password="",            # Default XAMPP password is empty
            database="hospital_ai"  # Make sure this matches your actual database name in phpMyAdmin!
        )
        cursor = conn.cursor()

        # Execute the INSERT query matching your new 'bookings' table
        insert_query = '''
            INSERT INTO bookings (patient_name, department, appointment_date, appointment_time)
            VALUES (%s, %s, %s, %s)
        '''
        
        cursor.execute(insert_query, (patient_name, department, date, time))

        # Commit the transaction to save changes
        conn.commit()
        return f"Success! Appointment confirmed for {patient_name} in the {department} department on {date} at {time}."

    except mysql.connector.Error as err:
        return f"Database Error: {err}"
        
    finally:
        # Always close the connection
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()