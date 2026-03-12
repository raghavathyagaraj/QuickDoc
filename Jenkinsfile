pipeline {
    agent any

    parameters {
        choice(name: 'DEPLOY_ENV', choices: ['AUTO', 'DEV', 'QA'], description: 'Select environment')
    }

    environment {
        DEV_IP = '18.217.96.211'
        QA_IP  = '18.220.186.185'
        DEPLOY_PATH = '/var/www/quickdoc'
        SSH_KEY_PATH = '/Users/raghavathyagaraj/Downloads/quick-doc-dev.pem'
        
        TEST_RIGOR_CRED_ID = 'test_rigor_secret'
        // This is the ID of the secret text where you pasted your Slack Webhook URL
        SLACK_URL_ID = 'slack-webhook-url'
    }

    stages {
        stage('Determine Environment') {
            steps {
                script {
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
                sh '''
                    ssh -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} ec2-user@${TARGET_IP} "sudo mkdir -p ${DEPLOY_PATH} && sudo chown -R ec2-user:ec2-user ${DEPLOY_PATH}"
                    scp -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} src/frontend/templates/index.html ec2-user@${TARGET_IP}:${DEPLOY_PATH}/
                    scp -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} -r src/frontend/static ec2-user@${TARGET_IP}:${DEPLOY_PATH}/
                    ssh -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} ec2-user@${TARGET_IP} "sudo chmod -R 755 ${DEPLOY_PATH}"
                '''
            }
        }

        stage('testRigor Integration') {
            when {
                expression { env.ENV_NAME == 'QA' }
            }
            steps {
                withCredentials([string(credentialsId: env.TEST_RIGOR_CRED_ID, variable: 'TR_TOKEN')]) {
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
            echo "✅ Deployment Successful!"
            withCredentials([string(credentialsId: "${env.SLACK_URL_ID}", variable: 'SLACK_WEBHOOK')]) {
                sh '''
                    curl -X POST -H 'Content-type: application/json' --data "{
                        'text': '✅ *QuickDoc Deployment Success!*\\n*Env:* ${ENV_NAME}\\n*Build:* #${BUILD_NUMBER}\\n*URL:* http://${TARGET_IP}'
                    }" $SLACK_WEBHOOK
                '''
            }
        }
        failure {
            echo "❌ Pipeline failed!"
            withCredentials([string(credentialsId: "${env.SLACK_URL_ID}", variable: 'SLACK_WEBHOOK')]) {
                sh '''
                    curl -X POST -H 'Content-type: application/json' --data "{
                        'text': '❌ *QuickDoc Build Failed!*\\n*Project:* ${JOB_NAME}\\n*Build:* #${BUILD_NUMBER}'
                    }" $SLACK_WEBHOOK
                '''
            }
        }
    }
}
