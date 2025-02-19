pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build and Start Services') {
            steps {
                script {
                    // Build all services
                    sh 'docker-compose build'
                    
                    // First start only the database
                    sh 'docker-compose up -d db'
                    
                    // Wait for MySQL to be healthy
                    sh '''
                        echo "Waiting for MySQL to be ready..."
                        attempt=1
                        max_attempts=30
                        until docker exec mysql-db mysqladmin ping -h localhost -u root -ppassword || [ $attempt -eq $max_attempts ]
                        do
                            echo "Waiting for MySQL to be ready... (Attempt $attempt/$max_attempts)"
                            sleep 10
                            attempt=$((attempt + 1))
                        done
                        
                        if [ $attempt -eq $max_attempts ]; then
                            echo "MySQL failed to become ready in time"
                            exit 1
                        fi
                        
                        echo "MySQL is ready!"
                    '''
                    
                    // Now start the remaining services
                    sh 'docker-compose up -d'
                }
            }
        }

        stage('Verify Services') {
            steps {
                script {
                    // Wait for Flask backend to be ready
                    sh '''
                        echo "Verifying Flask backend..."
                        attempt=1
                        max_attempts=10
                        until curl -s http://localhost:5000 || [ $attempt -eq $max_attempts ]
                        do
                            echo "Waiting for Flask backend... (Attempt $attempt/$max_attempts)"
                            sleep 5
                            attempt=$((attempt + 1))
                        done
                        
                        if [ $attempt -eq $max_attempts ]; then
                            echo "Flask backend failed to become ready"
                            exit 1
                        fi
                    '''
                    
                    // Verify frontend
                    sh '''
                        echo "Verifying frontend..."
                        attempt=1
                        max_attempts=10
                        until curl -s http://localhost:8000 || [ $attempt -eq $max_attempts ]
                        do
                            echo "Waiting for frontend... (Attempt $attempt/$max_attempts)"
                            sleep 5
                            attempt=$((attempt + 1))
                        done
                        
                        if [ $attempt -eq $max_attempts ]; then
                            echo "Frontend failed to become ready"
                            exit 1
                        fi
                    '''
                }
            }
        }
    }

    post {
        failure {
            script {
                sh '''
                    echo "Deployment failed. Printing logs..."
                    docker-compose logs
                    echo "Stopping all services..."
                    docker-compose down
                '''
            }
        }
        success {
            echo 'All services deployed and verified successfully!'
        }
        always {
            sh 'docker system prune -f'
        }
    }
}