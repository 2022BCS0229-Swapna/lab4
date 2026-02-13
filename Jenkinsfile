pipeline {
    agent any

    environment {
        DOCKER_CREDS = credentials('dockerhub-creds')
        BEST_ACC = credentials('best-accuracy')
    }

    stages {

        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                apt-get update
                apt-get install -y python3-venv python3-pip
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                sh '''
                . venv/bin/activate
                python scripts/train.py
                '''
            }
        }

        stage('Read Accuracy') {
            steps {
                script {
                    def json = readFile('app/artifacts/metrics.json')
                    def matcher = json =~ /"accuracy"\s*:\s*([0-9.]+)/
                    env.CURR_ACC = matcher[0][1]
                    echo "Current Accuracy: ${env.CURR_ACC}"
                }
            }
        }


        stage('Compare Accuracy') {
            steps {
                script {
                    if (env.CURR_ACC.toFloat() > env.BEST_ACC.toFloat()) {
                        env.BUILD_IMAGE = "true"
                        echo "Model improved"
                    } else {
                        env.BUILD_IMAGE = "false"
                        echo "Model did not improve"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when { expression { env.BUILD_IMAGE == "true" } }
            steps {
                sh '''
                docker login -u $DOCKER_CREDS_USR -p $DOCKER_CREDS_PSW
                docker build -t $DOCKER_CREDS_USR/wine:${BUILD_NUMBER} .
                docker tag $DOCKER_CREDS_USR/wine:${BUILD_NUMBER} $DOCKER_CREDS_USR/wine:latest
                '''
            }
        }

        stage('Push Docker Image') {
            when { expression { env.BUILD_IMAGE == "true" } }
            steps {
                sh '''
                docker push $DOCKER_CREDS_USR/wine:${BUILD_NUMBER}
                docker push $DOCKER_CREDS_USR/wine:latest
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'app/artifacts/**', fingerprint: true
        }
    }
}
