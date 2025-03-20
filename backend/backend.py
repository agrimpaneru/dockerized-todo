from flask import Flask, request, jsonify
import mysql.connector
import os
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database configuration
db_host = os.getenv('MYSQL_HOST', 'db-service')
db_user = os.getenv('MYSQL_USER', 'root')
db_password = os.getenv('MYSQL_PASSWORD', 'password')
db_name = os.getenv('MYSQL_DATABASE', 'todo_db')

# Configure MySQL Database
def get_db_connection():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

# Initialize database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create enhanced tasks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        task TEXT NOT NULL,
        category VARCHAR(50),
        priority VARCHAR(20) DEFAULT 'medium',
        due_date DATE,
        completed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

# Initialize database on startup
init_db()

@app.route('/')
def index():
    return jsonify({"status": "API is running", "version": "1.0"})

@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    task = data.get('task')
    category = data.get('category', '')
    priority = data.get('priority', 'medium')
    due_date = data.get('dueDate')
    
    if not task:
        return jsonify({"error": "Task description is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO tasks (task, category, priority, due_date) VALUES (%s, %s, %s, %s)",
            (task, category, priority, due_date)
        )
        conn.commit()
        return jsonify({"message": "Task added successfully!", "id": cursor.lastrowid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM tasks ORDER BY due_date ASC")
        tasks = cursor.fetchall()
        # Convert datetime objects to string for JSON serialization
        for task in tasks:
            if task['due_date']:
                task['due_date'] = task['due_date'].isoformat()
            if task['created_at']:
                task['created_at'] = task['created_at'].isoformat()
        return jsonify(tasks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/update_task_status/<int:task_id>', methods=['PUT'])
def update_task_status(task_id):
    data = request.json
    completed = data.get('completed', False)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE tasks SET completed = %s WHERE id = %s",
            (completed, task_id)
        )
        conn.commit()
        
        if cursor.rowcount:
            return jsonify({"message": "Task status updated successfully!"})
        else:
            return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        
        if cursor.rowcount:
            return jsonify({"message": "Task deleted successfully!"})
        else:
            return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/tasks/stats', methods=['GET'])
def get_task_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get total tasks
        cursor.execute("SELECT COUNT(*) as total FROM tasks")
        total = cursor.fetchone()['total']
        
        # Get completed tasks
        cursor.execute("SELECT COUNT(*) as completed FROM tasks WHERE completed = TRUE")
        completed = cursor.fetchone()['completed']
        
        # Get overdue tasks
        cursor.execute("SELECT COUNT(*) as overdue FROM tasks WHERE due_date < CURDATE() AND completed = FALSE")
        overdue = cursor.fetchone()['overdue']
        
        # Get tasks by priority
        cursor.execute("SELECT priority, COUNT(*) as count FROM tasks GROUP BY priority")
        priority_stats = cursor.fetchall()
        
        # Get tasks by category
        cursor.execute("SELECT category, COUNT(*) as count FROM tasks WHERE category != '' GROUP BY category")
        category_stats = cursor.fetchall()
        
        return jsonify({
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "overdue": overdue,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
            "by_priority": priority_stats,
            "by_category": category_stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)