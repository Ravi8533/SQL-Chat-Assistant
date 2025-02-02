import sqlite3
import re
from flask import Flask, request, jsonify, render_template
from urllib.parse import quote

# Initialize Flask app
app = Flask(__name__)

def create_database():
    #Creates SQLite database and tables
    conn = sqlite3.connect("company.db")
    cursor = conn.cursor()
    
    # Create Employees table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employees (
        ID INTEGER PRIMARY KEY,
        Name VARCHAR(100) NOT NULL,
        Department VARCHAR(50) NOT NULL,
        Salary INTEGER NOT NULL,
        Hire_Date DATE NOT NULL
    )
    """)
    
    # Create Departments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Departments (
        ID INTEGER PRIMARY KEY,
        Name VARCHAR(50) NOT NULL,
        Manager VARCHAR(100) NOT NULL
    )
    """)
    
    # Insert initial data
    cursor.executemany("INSERT OR IGNORE INTO Employees VALUES (?, ?, ?, ?, ?)", [
        (1, 'Alice', 'Sales', 50000, '2021-01-15'),
        (2, 'Bob', 'Engineering', 70000, '2020-06-10'),
        (3, 'Charlie', 'Marketing', 60000, '2022-03-20'),
        (4, 'Ravi', 'Analytics', 75000,'2023-26-09'),
        (5, 'Ravindra', 'Development', 90000,'2021-02-02'),
        (6, 'Ankit', 'Management', 85000,'2024-06-05')
    ])
    
    cursor.executemany("INSERT OR IGNORE INTO Departments VALUES (?, ?, ?)", [
        (1, 'Sales', 'Alice'),
        (2, 'Engineering', 'Bob'),
        (3, 'Marketing', 'Charlie'),
        (4, 'Analytics', 'Ravi'),
        (5, 'Development', 'Ravindra'),
        (6, 'Marketing', 'Ankit') 
    ])
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    # Renders the chat UI
    return render_template("index.html")

@app.route('/query', methods=['POST'])
def query_database():
    # Handles user queries and returns results from SQLite database
    data = request.json
    user_query = data.get("query", "")
    query_type, param = parse_query_type(user_query)
    response = get_response(query_type,param)
    return jsonify({"response": response})
   
def parse_query_type(user_query):
    #Parses natural language query using regex to extract query_type and parameters
    user_query = user_query.lower()
    
    patterns = {
        "employees_in": r"employees in the (\w+)",
        "manager_of": r"manager of the (\w+)",
        "hired_after": r"hired after (\d{4}-\d{2}-\d{2})",
        "salary_expense": r"total salary expense for the (\w+)"
    }
    
    for query_type, pattern in patterns.items():
        match = re.search(pattern, user_query)
        if match:
            return query_type, match.group(1)
    
    return None, None
 
def execute_query(query, isMultiple):
    conn = sqlite3.connect("company.db")
    cursor = conn.cursor()
    cursor.execute(query)
    if isMultiple:
        results = cursor.fetchall()
    else:
        results = cursor.fetchone()
    conn.close()
    return results
 
def get_response(query_type,param): 
    try:
        if query_type == "employees_in": 
            #case when need to find employees names in the given department
            query = 'SELECT Name FROM Employees WHERE Department = "{}"'.format(param.capitalize())
            results = execute_query(query, True)
            response = [row[0] for row in results] if results else ["No employees found"]
        
        elif query_type == "manager_of":
            #case when need to find Manager names in the given department
            query = 'SELECT Manager FROM Departments WHERE Name = "{}"'.format(param.capitalize())
            result = execute_query(query, False)
            response = result[0] if result else "No manager found"
        
        elif query_type == "hired_after":
            #case when need to find employees names hire after a particular date
            query = 'SELECT Name FROM Employees WHERE Hire_Date > "{}"'.format(param.capitalize())
            results = execute_query(query, True)
            response = [row[0] for row in results] if results else ["No employees found"]
        
        elif query_type == "salary_expense":
            #case when need to find employees Salary in the given department
            query = 'SELECT SUM(Salary) FROM Employees WHERE Department = "{}"'.format (param.capitalize())
            result = execute_query(query, False)
            response = f"Total salary expense: {result[0]}" if result[0] else "No data found"
        
        else:
            response = "Sorry, I don't understand that query."
    except Exception as e:
        response = f"Error processing query: {str(e)}"
    return response

if __name__ == '__main__':
    create_database()
    app.run(debug=True)
