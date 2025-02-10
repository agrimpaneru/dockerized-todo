import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',  # Change if using another user
        password='password',  # Change to your actual password
        database='todo_db'
    )
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    
    print("Connection successful! Tables in todo_db:")
    for table in cursor.fetchall():
        print(table)

    conn.close()
except mysql.connector.Error as err:
    print(f"Error: {err}")
