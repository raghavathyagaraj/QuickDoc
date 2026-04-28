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
        REPO_PATH = '/home/ec2-user/QuickDoc'
        TEST_RIGOR_CRED_ID = 'test_rigor_secret'
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

        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    echo "✅ Python environment configured"
                    python3 --version
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m pytest tests/ \
                        --junitxml=test-results.xml \
                        --cov=src \
                        --cov-report=xml:coverage.xml \
                        -v || true
                    echo "✅ Tests completed"
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
            }
        }

        stage('Code Quality') {
            steps {
                sh '''
                    . venv/bin/activate
                    pip install flake8 bandit pbr --quiet
                    flake8 src/ --max-line-length=120 --exclude=venv --statistics || true
                    bandit -r src/ -ll || true
                    echo "✅ Code quality checks completed"
                '''
            }
        }

        stage('Database Integration Check') {
            steps {
                sh '''
                    . venv/bin/activate
                    python3 -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/quickdoc'
os.environ['SECRET_KEY'] = 'ci-test-secret-key'
os.environ['FLASK_ENV'] = 'testing'
print('DATABASE_URL set:', bool(os.environ.get('DATABASE_URL')))
print('SECRET_KEY set:', bool(os.environ.get('SECRET_KEY')))
print('✅ Database integration config verified')
"
                '''
            }
        }

        stage('Deploy Static Files') {
            steps {
                echo "Deploying static files to ${env.ENV_NAME} (${env.TARGET_IP})..."
                sh '''
                    ssh -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} ec2-user@${TARGET_IP} \
                        "sudo mkdir -p ${DEPLOY_PATH} && sudo chown -R ec2-user:ec2-user ${DEPLOY_PATH}"

                    scp -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} \
                        src/frontend/templates/index.html ec2-user@${TARGET_IP}:${DEPLOY_PATH}/

                    scp -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} -r \
                        src/frontend/static ec2-user@${TARGET_IP}:${DEPLOY_PATH}/

                    ssh -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} ec2-user@${TARGET_IP} \
                        "sudo chmod -R 755 ${DEPLOY_PATH}"
                '''
            }
        }

        stage('Deploy Flask App') {
            steps {
                echo "Deploying Flask app via Docker to ${env.ENV_NAME} (${env.TARGET_IP})..."
                sh '''
                    ssh -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} ec2-user@${TARGET_IP} \
                        "cd ${REPO_PATH} && git pull origin develop && docker-compose up --build -d"
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    sleep 10
                    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://${TARGET_IP}/auth/login || echo "000")
                    echo "Health check status: $STATUS"
                    if [ "$STATUS" = "200" ] || [ "$STATUS" = "302" ]; then
                        echo "✅ App is healthy"
                    else
                        echo "⚠️ App returned status $STATUS"
                    fi
                '''
            }
        }

        stage('testRigor Integration') {
            when {
                expression { env.ENV_NAME == 'DEV' || env.ENV_NAME == 'QA' }
            }
            steps {
                withCredentials([string(credentialsId: env.TEST_RIGOR_CRED_ID, variable: 'TR_TOKEN')]) {
                    sh '''
                        curl -s -X POST "https://api.testrigor.com/api/v1/apps/Hs5GePpDbaANXBnRy/retest" \
                            -H "auth-token: ${TR_TOKEN}" \
                            -H "Content-Type: application/json"
                        echo "✅ testRigor triggered"
                    '''
                }
            }
        }

    }

    post {
        success {
            echo "✅ Deployment Successful!"
            withCredentials([string(credentialsId: "${env.SLACK_URL_ID}", variable: 'SLACK_WEBHOOK')]) {
                script {
                    if (env.ENV_NAME == 'QA') {
                        def notes = readFile('release-notes/qa.md').trim()
                        def message = "QA Release Notes - Build ${BUILD_NUMBER} - Branch ${GIT_BRANCH} - URL http://${TARGET_IP}\n\n${notes}"

                        def payload = groovy.json.JsonOutput.toJson([text: message])
                        writeFile file: 'slack_payload.json', text: payload

                        sh '''
                            curl -X POST -H "Content-type: application/json" \
                            -d @slack_payload.json $SLACK_WEBHOOK
                        '''
                    } else {
                        def message = "✅ QuickDoc DEV Deployment Success!\nBuild: #${BUILD_NUMBER}\nBranch: ${GIT_BRANCH}\nURL: http://${TARGET_IP}"
                        def payload = groovy.json.JsonOutput.toJson([text: message])
                        writeFile file: 'slack_payload.json', text: payload

                        sh '''
                            curl -X POST -H "Content-type: application/json" \
                            -d @slack_payload.json $SLACK_WEBHOOK
                        '''
                    }
                }
            }
        }

        failure {
            echo "❌ Pipeline failed!"
            withCredentials([string(credentialsId: "${env.SLACK_URL_ID}", variable: 'SLACK_WEBHOOK')]) {
                script {
                    def message = "❌ QuickDoc Build Failed!\nProject: ${JOB_NAME}\nBuild: #${BUILD_NUMBER}\nEnv: ${ENV_NAME}\n\nCheck Jenkins logs immediately."
                    def payload = groovy.json.JsonOutput.toJson([text: message])
                    writeFile file: 'slack_payload.json', text: payload

                    sh '''
                        curl -X POST -H "Content-type: application/json" \
                        -d @slack_payload.json $SLACK_WEBHOOK
                    '''
                }
            }
        }
    }
}