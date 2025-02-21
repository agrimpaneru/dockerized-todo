# Visit this site for this project
For more information, visit [Agrim Paneru's Website](https://agrimpaneru.com.np/blog/jenkins-webhooks-cicd/).
# To-Do List Application

This is a simple To-Do List application built using Flask for the backend, MySQL for the database, and Nginx for serving the frontend.

## Project Structure
```
.
├── backend
│   ├── backend.py         # Flask backend application
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Dockerfile for Flask app
├── frontend
│   ├── index.html         # Frontend HTML file
│   ├── Dockerfile         # Dockerfile for Nginx
├── docker-compose.yml     # Docker Compose configuration file
├── README.md              # Project documentation
```

## Features
- Add tasks to the to-do list
- View all tasks
- Delete tasks
- Dockerized for easy deployment
- Uses MySQL for data persistence

## Prerequisites
- Docker & Docker Compose installed on your system

## Getting Started

### 1. Clone the Repository
```sh
git clone https://github.com/your-username/todo-app.git
cd todo-app
```

### 2. Build and Run the Containers
```sh
docker-compose up --build
```
This command will build and start all the services defined in `docker-compose.yml`.

### 3. Access the Application
- Backend API: `http://localhost:5000`
- Frontend: `http://localhost:8000`
- MySQL: `localhost:3306` (username: `root`, password: `password`)

## API Endpoints

### 1. Add a Task
**Endpoint:** `POST /add_task`
```json
{
  "task": "Buy groceries"
}
```

### 2. Get All Tasks
**Endpoint:** `GET /get_tasks`

### 3. Delete a Task
**Endpoint:** `DELETE /delete_task/{task_id}`

## Stopping the Application
To stop all running containers, use:
```sh
docker-compose down
```

