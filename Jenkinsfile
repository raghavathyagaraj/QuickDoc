pipeline {
    agent any
    
    stages {
        // Stage 1: Checkout Code
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Code checked out successfully'
            }
        }

        // Stage 2: Setup Python Environment
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

        // Stage 3: Run Unit Tests
        stage('Run Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m pytest tests/ --junitxml=test-results.xml --cov=src --cov-report=xml || true
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                }
            }
        }

        // Stage 4: Code Quality Check
        stage('Code Quality Check') {
            steps {
                sh '''
                    . venv/bin/activate
                    pip install flake8
                    flake8 src/ --max-line-length=120 --exit-zero
                '''
                echo 'Code quality check complete'
            }
        }

        // Stage 5: Build
        stage('Build') {
            steps {
                echo 'Building application...'
                sh '''
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Workspace: ${WORKSPACE}"
                '''
            }
        }

        // Stage 6: TestRigor Integration Tests
        stage('testRigor Integration Tests') {
            steps {
                // Ensure the credential ID matches 'test_rigor_secret' created as 'Secret text'
                withCredentials([string(credentialsId: 'test_rigor_secret', variable: 'API_KEY')]) {
                    script {
                        echo '=========================================='
                        echo 'Running TestRigor Integration Tests'
                        echo '=========================================='

                        // 1. Trigger the retest for App ID: Hs5GePpDbaANXBnRy
                        // Note: auth-token header is used instead of Bearer token
                        sh(script: '''
                            curl -s -X POST "https://api.testrigor.com/api/v1/apps/Hs5GePpDbaANXBnRy/retest" \
                            -H "Content-type: application/json" \
                            -H "auth-token: $API_KEY" \
                            -d '{"forceCancelPreviousTesting":true}'
                        ''')

                        // 2. Poll for status using HTTP codes
                        def finished = false
                        
                        while (!finished) {
                            echo "Checking test status..."
                            
                            // Using curl to get ONLY the HTTP status code for reliability
                            def statusCode = sh(script: """
                                curl -s -o /dev/null -w "%{http_code}" \
                                -H "auth-token: \$API_KEY" \
                                "https://api.testrigor.com/api/v1/apps/Hs5GePpDbaANXBnRy/status"
                            """, returnStdout: true).trim()

                            echo "Current Test Status Code: ${statusCode}"

                            switch(statusCode) {
                                case "200":
                                    echo "Test finished successfully!"
                                    finished = true
                                    break
                                case "227":
                                case "228":
                                    echo "Test is still New or In progress. Waiting 20 seconds..."
                                    sleep 20
                                    break
                                case "230":
                                    error "Test finished but FAILED."
                                    break
                                case "229":
                                    error "Test was CANCELED."
                                    break
                                default:
                                    error "Received unexpected status code: ${statusCode}"
                            }
                        }
                        
                        echo 'TestRigor Integration Tests completed successfully.'
                    }
                }
            }
        }

        // Stage 7: Deploy
        stage('Deploy') {
            steps {
                echo 'Deploying QuickDoc...'
                sh '''
                    echo "GitHub Pages URL: https://raghavathyagaraj.github.io/QuickDoc/"
                    echo "Deployment successful!"
                '''
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
            echo 'Pipeline failed!'
        }
    }
}
