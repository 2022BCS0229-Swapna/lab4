pipeline {
    agent any

    environment {
        IMAGE_NAME = "2022bcs0229swapna/wine-infer"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
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
                    def metrics = readJSON file: 'app/artifacts/metrics.json'
                    env.CURRENT_ACCURACY = metrics.accuracy.toString()
                    echo "Current Accuracy: ${env.CURRENT_ACCURACY}"
                }
            }
        }

        stage('Compare Accuracy') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'best-accuracy', variable: 'BEST_ACCURACY')]) {
                        if (env.CURRENT_ACCURACY.toFloat() > BEST_ACCURACY.toFloat()) {
                            env.MODEL_IMPROVED = "true"
                            echo "Model improved"
                        } else {
                            env.MODEL_IMPROVED = "false"
                            echo "Model did not improve"
                        }
                    }
                }
            }
        }

        stage('Build Docker Image') {
            when {
                expression { env.MODEL_IMPROVED == "true" }
            }
            steps {
                script {
                    docker.build("${IMAGE_NAME}:${BUILD_NUMBER}")
                }
            }
        }

        stage('Push Docker Image') {
            when {
                expression { env.MODEL_IMPROVED == "true" }
            }
            steps {
                script {
                    docker.withRegistry('', 'dockerhub-creds') {
                        docker.image("${IMAGE_NAME}:${BUILD_NUMBER}").push()
                        docker.image("${IMAGE_NAME}:${BUILD_NUMBER}").push("latest")
                    }
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'app/artifacts/**', fingerprint: true
        }
    }
}
