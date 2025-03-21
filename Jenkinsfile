pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Cleanup Application Containers') {
            steps {
                script {
                    // Stop and remove only application containers
                    sh '''
                        docker-compose stop flask-app frontend
                        docker-compose rm -f flask-app frontend
                        
                        # Remove application images to force rebuild
                        docker rmi -f $(docker images | grep 'flask-app' | awk '{print $3}') || true
                        docker rmi -f $(docker images | grep 'todo-frontend' | awk '{print $3}') || true
                    '''
                }
            }
        }

        stage('Start MySQL') {
            steps {
                script {
                    // Start only MySQL if not running
                    sh '''
                        if [ -z "$(docker ps -q -f name=mysql-db)" ]; then
                            docker-compose up -d db
                            # Wait for MySQL to initialize
                            sleep 60
                            echo 'Waited 1 minute for MySQL to start'
                        else
                            echo 'MySQL already running, skipping startup'
                        fi
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
                // Only stop application containers on failure, not monitoring
                sh '''
                    docker-compose stop flask-app frontend
                    docker-compose rm -f flask-app frontend
                '''
            }
            echo 'Deployment failed'
        }
        success {
            echo 'Deployment successful'
        }
    }
}