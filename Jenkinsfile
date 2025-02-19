pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    // Stop and remove existing containers
                    sh '''
                        docker-compose down
                        # Additional cleanup in case docker-compose down didn't work
                        docker rm -f mysql-db || true
                    '''
                }
            }
        }

        stage('Start MySQL') {
            steps {
                script {
                    // Start only MySQL
                    sh 'docker-compose up -d db'
                    
                    // Wait for 1 minute
                    sh 'sleep 60'
                    echo 'Waited 1 minute for MySQL to start'
                }
            }
        }

        stage('Start Other Services') {
            steps {
                script {
                    // Start remaining services
                    sh 'docker-compose up -d'
                }
            }
        }
    }

    post {
        failure {
            sh 'docker-compose down'
            echo 'Deployment failed'
        }
        success {
            echo 'Deployment successful'
        }
    }
}