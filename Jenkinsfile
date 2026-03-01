pipeline {
    agent any
    
    environment {
        DEV_EC2_IP = '18.217.96.211'
        DEPLOY_PATH = '/var/www/quickdoc'
        SSH_KEY_PATH = '/Users/raghavathyagaraj/Downloads/quick-doc-dev.pem'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Code checked out successfully'
            }
        }
        
        stage('Setup Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
                echo 'Environment setup complete'
            }
        }
        
        stage('Run Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m pytest tests/ --junitxml=test-results.xml || true
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building application...'
                sh '''
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Preparing files for deployment..."
                '''
                echo 'Build complete'
            }
        }
        
        stage('testRigor Integration Tests') {
                steps {
                    echo "=========================================="
                    echo "Triggering testRigor Integration Tests"
                    echo "=========================================="
                    sh '''
                        response=$(curl -s -X POST "https://api.testrigor.com/api/v1/apps/YOUR_APP_ID/retest" \
                            -H "auth-token: UM2h1XU87swTe72ASAlskBlZGBlQWjxZqvWVe0R9kmQxkE5QSA9D" \
                            -H "Content-Type: application/json")
                        echo "TestRigor Response: $response"
                    '''
                    echo "=========================================="
                    echo "testRigor tests triggered! Check dashboard for results."
                    echo "=========================================="
                }
            }
        
        stage('Deploy to DEV') {
            steps {
                echo '=========================================='
                echo 'Deploying to AWS EC2 DEV Server'
                echo '=========================================='
                
                sh '''
                    echo "Deploying to: ${DEV_EC2_IP}"
                    
                    scp -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} src/frontend/templates/index.html ec2-user@${DEV_EC2_IP}:${DEPLOY_PATH}/
                    scp -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} -r src/frontend/static ec2-user@${DEV_EC2_IP}:${DEPLOY_PATH}/
                    
                    echo "=================================================="
                    echo "DEV Deployment Successful!"
                    echo "URL: http://${DEV_EC2_IP}"
                    echo "=================================================="
                '''
            }
        }
    }
    
    post {
        success {
            echo '=========================================='
            echo 'Pipeline completed successfully!'
            echo 'Homepage deployed to DEV: http://18.217.96.211'
            echo '=========================================='
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
