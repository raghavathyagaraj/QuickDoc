pipeline {
    agent any

    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['DEV', 'QA'],
            description: 'Select environment to deploy'
        )
    }

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
            }
        }

        stage('Deploy') {
            steps {
                script {

                    if (params.ENVIRONMENT == 'DEV') {
                        TARGET_IP = env.DEV_EC2_IP
                    }

                    if (params.ENVIRONMENT == 'QA') {
                        TARGET_IP = env.QA_EC2_IP
                    }

                    echo "Deploying to ${params.ENVIRONMENT}"
                    echo "Target server: ${TARGET_IP}"

                    sh """
                        ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ec2-user@${TARGET_IP} 'sudo mkdir -p ${DEPLOY_PATH}'
                        scp -i ${SSH_KEY} -o StrictHostKeyChecking=no -r src/* ec2-user@${TARGET_IP}:${DEPLOY_PATH}/
                    """
                }
            }
        }
    }
}
