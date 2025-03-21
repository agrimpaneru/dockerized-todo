pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Cleanup Application and Database Containers') {
            steps {
                script {
                    // Stop and remove application and database containers
                    sh '''
                        docker-compose stop flask-app frontend db
                        docker-compose rm -f flask-app frontend db
                        
                        # Remove application and database images to force rebuild
                        docker rmi -f $(docker images | grep 'flask-app' | awk '{print $3}') || true
                        docker rmi -f $(docker images | grep 'todo-frontend' | awk '{print $3}') || true
                        docker rmi -f $(docker images | grep 'mysql:8.0' | awk '{print $3}') || true
                        
                        # Optionally remove the database volume to start completely fresh
                        docker volume rm $(docker volume ls -q | grep db_data) || true
                    '''
                }
            }
        }

        stage('Start Fresh Database') {
            steps {
                script {
                    // Start a fresh MySQL instance
                    sh '''
                        docker-compose up -d db
                        # Wait for MySQL to initialize
                        sleep 60
                        echo 'Waited 1 minute for fresh MySQL to start'
                    '''
                }
            }
        }

        stage('Build and Start Application') {
            steps {
                script {
                    // Force rebuild of application services
                    sh 'docker-compose build --no-cache flask-app frontend'
                    
                    // Start application services
                    sh 'docker-compose up -d flask-app frontend'
                }
            }
        }

        stage('Ensure Monitoring') {
            steps {
                script {
                    // Start monitoring services only if they're not running
                    sh '''
                        if [ -z "$(docker ps -q -f name=prometheus)" ]; then
                            docker-compose up -d prometheus
                        fi
                        
                        if [ -z "$(docker ps -q -f name=cadvisor)" ]; then
                            docker-compose up -d cadvisor
                        fi
                        
                        if [ -z "$(docker ps -q -f name=grafana)" ]; then
                            docker-compose up -d grafana
                        fi
                    '''
                }
            }
        }
    }

    post {
        failure {
            script {
                // Only stop application and database containers on failure, not monitoring
                sh '''
                    docker-compose stop flask-app frontend db
                    docker-compose rm -f flask-app frontend db
                '''
            }
            echo 'Deployment failed'
        }
        success {
            echo 'Deployment successful'
        }
    }
}