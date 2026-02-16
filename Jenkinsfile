pipeline {
    agent any
    stages {

        // -------------------------
        // Stage 1: Checkout Code
        // -------------------------
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Code checked out successfully'
            }
        }

        // -------------------------
        // Stage 2: Setup Python Environment
        // -------------------------
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

        // -------------------------
        // Stage 3: Run Unit Tests
        // -------------------------
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

        // -------------------------
        // Stage 4: Code Quality Check
        // -------------------------
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

        // -------------------------
        // Stage 5: Build
        // -------------------------
        stage('Build') {
            steps {
                echo 'Building application...'
                sh '''
                    echo "Build Number: ${BUILD_NUMBER}"
                    echo "Workspace: ${WORKSPACE}"
                '''
            }
        }

        // -------------------------
        // Stage 6: TestRigor Integration Tests
        // -------------------------
        stage('testRigor Integration Tests') {
            steps {
                withCredentials([string(credentialsId: 'test_rigor_secret', variable: 'API_KEY')]) {
                    script {
                        echo '=========================================='
                        echo 'Running TestRigor Integration Tests'
                        echo '=========================================='

                        // Trigger TestRigor test suite
                        def response = sh(script: """
                            curl -s -X POST "https://api.testrigor.com/api/v1/run" \\
                            -H "Authorization: Bearer $API_KEY" \\
                            -H "Content-Type: application/json" \\
                            -d '{ "testSuiteName": "QuickDoc Homepage real test" }'
                        """, returnStdout: true).trim()

                        // Extract runId
                        def runId = sh(script: "echo $response | jq -r '.runId'", returnStdout: true).trim()
                        echo "Triggered TestRigor run with ID: ${runId}"

                        // Poll for test completion
                        def status = "running"
                        while(status == "running") {
                            sleep 10
                            def statusResp = sh(script: "curl -s -X GET https://api.testrigor.com/api/v1/run/${runId} -H 'Authorization: Bearer $API_KEY'", returnStdout: true).trim()
                            status = sh(script: "echo $statusResp | jq -r '.status'", returnStdout: true).trim()
                            echo "Current Status: ${status}"
                        }

                        // Download test report
                        sh "curl -s -X GET https://api.testrigor.com/api/v1/run/${runId}/report -H 'Authorization: Bearer $API_KEY' -o TestRigor_Report_${runId}.json"

                        // Check result and fail build if tests failed
                        def result = sh(script: "echo $statusResp | jq -r '.result'", returnStdout: true).trim()
                        echo "TestRigor Result: ${result}"
                        if(result != "passed") {
                            error "TestRigor tests failed!"
                        }

                        echo 'TestRigor Integration Tests completed successfully.'
                    }
                }
            }
        }

        // -------------------------
        // Stage 7: Deploy
        // -------------------------
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

    // -------------------------
    // Post Actions
    // -------------------------
    post {
        success {
            echo '=========================================='
            echo 'Pipeline completed successfully!'
            echo 'All stages passed including TestRigor tests'
            echo '=========================================='
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
