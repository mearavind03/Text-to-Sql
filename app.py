from dotenv import load_dotenv 
import streamlit as st
import os
import sqlite3
import google.generativeai as genai


load_dotenv()  

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("Google API Key not found! Make sure it's set in the environment.")
else:
    genai.configure(api_key=API_KEY)


def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"{prompt}\nQuestion: {question}")  
        return response.text.strip()  
    except Exception as e:
        return f"Error generating SQL query: {str(e)}"


def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        return [("Error executing query:", str(e))]  


prompt = """
You are an expert in converting English questions to SQL queries!  
The SQL database is named STUDENT and has the following columns: NAME, CLASS, SECTION, and MARKS.

For example:

Example 1: "How many entries of records are present?"  
The SQL command will be: SELECT COUNT(*) FROM STUDENT;

Example 2: "Tell me all the students studying in the Data Science class."  
The SQL command will be: SELECT * FROM STUDENT WHERE CLASS = "Data Science";

Example 3: "How many students are in Section A?"  
The SQL command will be: SELECT COUNT(*) FROM STUDENT WHERE SECTION = "A";

Example 4: "Show me the names of students who scored more than 80 marks."  
The SQL command will be: SELECT NAME FROM STUDENT WHERE MARKS > 80;

Example 5: "Give me the details of students in Class 10, Section B."  
The SQL command will be: SELECT * FROM STUDENT WHERE CLASS = "10" AND SECTION = "B";

Example 6: "Who are the top 3 students with the highest marks?"  
The SQL command will be: SELECT * FROM STUDENT ORDER BY MARKS DESC LIMIT 3;

Example 7: "What is the average mark of all students?"  
The SQL command will be: SELECT AVG(MARKS) FROM STUDENT;

Example 8: "List all distinct classes available in the database."  
The SQL command will be: SELECT DISTINCT CLASS FROM STUDENT;

Example 9: "How many students scored between 50 and 75 marks?"  
The SQL command will be: SELECT COUNT(*) FROM STUDENT WHERE MARKS BETWEEN 50 AND 75;

Example 10: "Show the names and marks of students in descending order of marks."  
The SQL command will be: SELECT NAME, MARKS FROM STUDENT ORDER BY MARKS DESC;

The SQL code should not include the word "SQL" at the beginning or end.
"""


st.set_page_config(page_title="Retrieve Any SQL Query")
st.header("Gemini App to Retrieve SQL Data")


question = st.text_input("Enter your question:", key="input")
submit = st.button("Generate SQL Query")


if submit:
    sql_query = get_gemini_response(question, prompt) 

    
    if "Error generating SQL query" in sql_query:
        st.error(sql_query)
    else:
        st.subheader("Generated SQL Query:")
        st.code(sql_query, language="sql")  

    
        data = read_sql_query(sql_query, "student.db")  

        st.subheader("Query Results:")
        if data and "Error executing query" not in str(data):
            st.dataframe(data)  
        else:
            st.error("Invalid SQL Query or Database Error!")

