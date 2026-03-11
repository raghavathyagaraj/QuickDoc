pipeline {
    agent any
    
    environment {
        DEV_EC2_IP = '172.31.14.22'
        QA_EC2_IP = '172.31.7.234'
        DEPLOY_PATH = '/var/www/quickdoc'
        SSH_KEY = '/var/lib/jenkins/.ssh/id_rsa'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "Branch: ${env.BRANCH_NAME}"
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
                echo "Build Number: ${BUILD_NUMBER}"
                echo 'Preparing files for deployment...'
                echo 'Build complete'
            }
        }
        
        stage('Deploy to DEV') {
            when {
<<<<<<< HEAD
                branch 'dev'
=======
                branch 'develop'
>>>>>>> 315a180 (Updated Jenkinsfile with DEV and QA pipeline)
            }
            steps {
                echo '=========================================='
                echo 'Deploying to DEV Environment'
                echo '=========================================='
                sh """
                    ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ec2-user@${DEV_EC2_IP} 'sudo mkdir -p ${DEPLOY_PATH} && sudo chown -R ec2-user:ec2-user ${DEPLOY_PATH}'
                    scp -i ${SSH_KEY} -o StrictHostKeyChecking=no -r src/* ec2-user@${DEV_EC2_IP}:${DEPLOY_PATH}/
                    scp -i ${SSH_KEY} -o StrictHostKeyChecking=no requirements.txt ec2-user@${DEV_EC2_IP}:${DEPLOY_PATH}/
                    ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ec2-user@${DEV_EC2_IP} '
                        cd ${DEPLOY_PATH}
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                        sudo systemctl restart nginx
                    '
                """
                echo 'DEV deployment successful!'
            }
        }
        
        stage('Deploy to QA') {
            when {
                branch 'qa'
            }
            steps {
                echo '=========================================='
                echo 'Deploying to QA Environment'
                echo '=========================================='
                sh """
                    ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ec2-user@${QA_EC2_IP} 'sudo mkdir -p ${DEPLOY_PATH} && sudo chown -R ec2-user:ec2-user ${DEPLOY_PATH}'
                    scp -i ${SSH_KEY} -o StrictHostKeyChecking=no -r src/* ec2-user@${QA_EC2_IP}:${DEPLOY_PATH}/
                    scp -i ${SSH_KEY} -o StrictHostKeyChecking=no requirements.txt ec2-user@${QA_EC2_IP}:${DEPLOY_PATH}/
                    ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ec2-user@${QA_EC2_IP} '
                        cd ${DEPLOY_PATH}
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                        sudo systemctl restart nginx
                    '
                """
                echo 'QA deployment successful!'
            }
        }
    }
    
    post {
        success {
            echo '=========================================='
            echo 'Pipeline completed successfully!'
            echo '=========================================='
        }
        failure {
            echo '=========================================='
            echo 'Pipeline FAILED! Check logs above.'
            echo '=========================================='
        }
    }
}
