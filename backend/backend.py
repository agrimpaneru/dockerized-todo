from flask import Flask, render_template, request, jsonify
import mysql.connector
import os
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
db_host = os.getenv('MYSQL_HOST', 'db-service')  # Default is localhost if not set
db_user = os.getenv('MYSQL_USER', 'root')  # Default is root if not set
db_password = os.getenv('MYSQL_PASSWORD', 'password')  # Default is password if not set
db_name = os.getenv('MYSQL_DATABASE', 'todo_db')

# Configure MySQL Database
conn = mysql.connector.connect(
    host=db_host,
    user='root',  # Change as per your MySQL credentials
    password='password',  # Change as per your MySQL credentials
    database='todo_db'
)
cursor = conn.cursor()
cursor.execute("USE todo_db;")

# Create tasks table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task TEXT NOT NULL
)
''')
conn.commit()

@app.route('/')
def index():
    return ("hell")

@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    task = data.get('task')
    print(task)
    cursor.execute("INSERT INTO tasks (task) VALUES (%s)", (task,))
    conn.commit()
    return jsonify({"message": "Task added successfully!"})

@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    return jsonify(tasks)

@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    return jsonify({"message": "Task deleted successfully!"})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)
