pipeline {
    agent any
    
    parameters {
        // Allows you to choose the environment when you click 'Build with Parameters'
        choice(name: 'DEPLOY_ENV', choices: ['DEV', 'QA'], description: 'Select the environment to deploy to')
    }
    
    environment {
        // Your existing Dev IP and your new QA IP
        DEV_EC2_IP = '18.217.96.211'
        QA_EC2_IP = '18.220.186.185'
        
        DEPLOY_PATH = '/var/www/quickdoc'
        SSH_KEY_PATH = '/Users/raghavathyagaraj/Downloads/quick-doc-dev.pem'
        
        // This logic determines which IP to use based on the parameter selected
        TARGET_IP = "${params.DEPLOY_ENV == 'QA' ? QA_EC2_IP : DEV_EC2_IP}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "Code checked out successfully for ${params.DEPLOY_ENV} environment"
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
        
        stage('Deploy') {
            steps {
                echo "=========================================="
                echo "Deploying to AWS EC2 ${params.DEPLOY_ENV} Server"
                echo "Target IP: ${TARGET_IP}"
                echo "=========================================="
                
                sh '''
                    # Copy files to the target IP (Dev or QA)
                    scp -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} src/frontend/templates/index.html ec2-user@${TARGET_IP}:${DEPLOY_PATH}/
                    scp -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} -r src/frontend/static ec2-user@${TARGET_IP}:${DEPLOY_PATH}/
                '''
            }
        }
        
        stage('testRigor Integration Tests') {
            // We only trigger this if we are deploying to QA (optional logic)
            when {
                expression { params.DEPLOY_ENV == 'QA' }
            }
            steps {
                echo "Triggering testRigor for QA..."
                sh '''
                    curl -s -X POST "https://api.testrigor.com/api/v1/apps/Hs5GePpDbaANXBnRy/retest" \
                        -H "auth-token: UM2h1XU87swTe72ASAlskBlZGBlQWjxZqvWVe0R9kmQxkE5QSA9D" \
                        -H "Content-Type: application/json"
                '''
            }
        }
    }
    
    post {
        success {
            echo "=========================================="
            echo "Pipeline completed successfully for ${params.DEPLOY_ENV}!"
            echo "URL: http://${TARGET_IP}"
            echo "=========================================="
        }
        failure {
            echo "Pipeline failed for ${params.DEPLOY_ENV}!"
        }
    }
}
