from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import mysql.connector
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://98.70.73.193:8000", "http://localhost:8000"]}}, supports_credentials=True)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins=["http://98.70.73.193:8000", "http://localhost:8000"])

# Database configuration
db_host = os.getenv('MYSQL_HOST', 'db-service')
db_user = os.getenv('MYSQL_USER', 'root')
db_password = os.getenv('MYSQL_PASSWORD', 'password')
db_name = os.getenv('MYSQL_DATABASE', 'todo_db')

def get_db_connection():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

# Initialize the database and create table if it doesn't exist
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tasks table with necessary fields
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        task TEXT NOT NULL,
        completed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    ''')
    
    # Check if the completed column exists, and add it if it doesn't
    try:
        cursor.execute("SELECT completed FROM tasks LIMIT 1")
    except mysql.connector.Error:
        cursor.execute("ALTER TABLE tasks ADD COLUMN completed BOOLEAN DEFAULT FALSE")
        cursor.execute("ALTER TABLE tasks ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        cursor.execute("ALTER TABLE tasks ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    
    conn.commit()
    cursor.close()
    conn.close()

# Initialize database on startup
init_db()

# Function to get all tasks
def get_all_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, task, completed FROM tasks ORDER BY created_at DESC")
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return tasks

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send all tasks to the newly connected client
    emit('tasks_update', get_all_tasks())

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# RESTful API endpoints
@app.route('/')
def index():
    return jsonify({"status": "Todo API is running"})

@app.route('/add_task', methods=['POST'])
def add_task():
    try:
        data = request.json
        task = data.get('task')
        completed = data.get('completed', False)
        
        if not task:
            return jsonify({"error": "Task content is required"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO tasks (task, completed) VALUES (%s, %s)", 
            (task, completed)
        )
        
        conn.commit()
        task_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        # Broadcast the updated task list to all connected clients
        socketio.emit('tasks_update', get_all_tasks())
        
        return jsonify({
            "message": "Task added successfully!",
            "task_id": task_id
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    try:
        tasks = get_all_tasks()
        return jsonify(tasks)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_task/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        data = request.json
        updates = []
        params = []
        
        if 'task' in data:
            updates.append("task = %s")
            params.append(data['task'])
        
        if 'completed' in data:
            updates.append("completed = %s")
            params.append(data['completed'])
        
        if not updates:
            return jsonify({"error": "No update data provided"}), 400
        
        params.append(task_id)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, params)
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Task not found"}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Broadcast the updated task list to all connected clients
        socketio.emit('tasks_update', get_all_tasks())
        
        return jsonify({"message": "Task updated successfully!"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_task/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        
        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({"error": "Task not found"}), 404
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Broadcast the updated task list to all connected clients
        socketio.emit('tasks_update', get_all_tasks())
        
        return jsonify({"message": "Task deleted successfully!"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear_completed', methods=['DELETE'])
def clear_completed():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE completed = TRUE")
        deleted_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Broadcast the updated task list to all connected clients
        socketio.emit('tasks_update', get_all_tasks())
        
        return jsonify({
            "message": f"Cleared {deleted_count} completed tasks",
            "count": deleted_count
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)