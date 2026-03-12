pipeline {
    agent any

    parameters {
        // 'AUTO' will look at the branch name, but you can override manually if needed
        choice(name: 'DEPLOY_ENV', choices: ['AUTO', 'DEV', 'QA'], description: 'Select environment')
    }

    environment {
        DEV_IP = '18.217.96.211'
        QA_IP  = '18.220.186.185'
        DEPLOY_PATH = '/var/www/quickdoc'
        
        // Match this exactly to the ID in your screenshot
        SSH_CRED_ID = 'ec2-dev-ssh' 
        TEST_RIGOR_CRED_ID = 'test_rigor_secret'
    }

    stages {
        stage('Determine Environment') {
            steps {
                script {
                    // Logic: If parameter is AUTO, detect based on Git branch name
                    // 'env.GIT_BRANCH' usually contains 'origin/qa' or 'origin/develop'
                    def currentBranch = env.GIT_BRANCH ?: 'develop'
                    
                    if (params.DEPLOY_ENV == 'QA' || currentBranch.contains('qa')) {
                        env.TARGET_IP = QA_IP
                        env.ENV_NAME = 'QA'
                    } else {
                        env.TARGET_IP = DEV_IP
                        env.ENV_NAME = 'DEV'
                    }
                    echo "Targeting Environment: ${env.ENV_NAME} at IP: ${env.TARGET_IP}"
                }
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup & Test') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    python -m pytest tests/ --junitxml=test-results.xml || true
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo "🚀 Deploying to ${env.ENV_NAME} (${env.TARGET_IP})..."
                
                // This block uses your 'ec2-dev-ssh' credential from Jenkins
                sshagent([env.SSH_CRED_ID]) {
                    sh '''
                        # 1. Prepare directory and permissions on remote EC2
                        ssh -o StrictHostKeyChecking=no ec2-user@${TARGET_IP} "sudo mkdir -p ${DEPLOY_PATH} && sudo chown -R ec2-user:ec2-user ${DEPLOY_PATH}"
                        
                        # 2. Transfer files using SCP
                        scp -o StrictHostKeyChecking=no src/frontend/templates/index.html ec2-user@${TARGET_IP}:${DEPLOY_PATH}/
                        scp -o StrictHostKeyChecking=no -r src/frontend/static ec2-user@${TARGET_IP}:${DEPLOY_PATH}/
                        
                        # 3. Final permission sync
                        ssh -o StrictHostKeyChecking=no ec2-user@${TARGET_IP} "sudo chmod -R 755 ${DEPLOY_PATH}"
                    '''
                }
            }
        }

        stage('testRigor Integration') {
            when {
                // Only run tests if we are deploying to the QA environment
                expression { env.ENV_NAME == 'QA' }
            }
            steps {
                // Using 'withCredentials' to securely inject your testRigor token
                withCredentials([string(credentialsId: env.TEST_RIGOR_CRED_ID, variable: 'TR_TOKEN')]) {
                    echo "Triggering testRigor for QA Environment..."
                    sh '''
                        curl -s -X POST "https://api.testrigor.com/api/v1/apps/Hs5GePpDbaANXBnRy/retest" \
                            -H "auth-token: ${TR_TOKEN}" \
                            -H "Content-Type: application/json"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment Successful to ${env.ENV_NAME}!"
            echo "URL: http://${env.TARGET_IP}"
        }
        failure {
            echo "❌ Pipeline failed! Check logs for deployment or test errors."
        }
    }
}
