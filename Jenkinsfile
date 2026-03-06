pipeline {
    agent any

    environment {
        APP_SERVER = "ec2-user@54.252.156.1"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/hyeegood/spring-vue-cicd-test.git'
            }
        }

        stage('Frontend Build') {
            steps {
                sh '''
                docker run --rm -v "${WORKSPACE}:/workspace" -w /workspace/frontend node:20-alpine sh -c "npm install && npm run build"
                '''
            }
        }

        stage('Copy Frontend') {
            steps {
                sh '''
                mkdir -p backend/src/main/resources/static
                rm -rf backend/src/main/resources/static/*
                cp -r frontend/dist/* backend/src/main/resources/static/
                '''
            }
        }

        stage('Backend Build') {
            steps {
                dir('backend') {
                    sh 'chmod +x gradlew'
                    sh './gradlew build'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t cicd-test .'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                docker save cicd-test | ssh -i /var/jenkins_home/dev-ec2-key.pem $APP_SERVER docker load

                ssh -i /var/jenkins_home/dev-ec2-key.pem $APP_SERVER "
                    docker stop cicd-test || true
                    docker rm cicd-test || true
                    docker run -d -p 8080:8080 --name cicd-test cicd-test
                "
                '''
            }
        }

    }
}