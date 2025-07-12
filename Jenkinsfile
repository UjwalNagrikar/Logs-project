pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                script {
                    // Build the Docker images for the API and dashboard
                    sh 'docker-compose build'
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    // Run tests for the log parser and API
                    sh 'pytest tests/test_parser.py'
                    sh 'pytest tests/test_api.py'
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    // Deploy the application using Terraform
                    sh 'cd terraform && terraform init'
                    sh 'cd terraform && terraform apply -auto-approve'
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}