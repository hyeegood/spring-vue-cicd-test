pipeline {
    agent any

    environment {
        APP_SERVER = "ec2-user@54.252.156.1"
        SSH_KEY = "/var/jenkins_home/dev-ec2-key.pem"
        IMAGE_NAME = "cicd-test"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/hyeegood/spring-vue-cicd-test.git'
            }
        }

        stage('Frontend Build') {
            steps {
                dir('stock-platform/frontend-vue') {
                    sh '''
                    npm install
                    npm run build
                    '''
                }
            }
        }

        stage('Copy Frontend to Spring Static') {
            steps {
                sh '''
                rm -rf backend/src/main/resources/static/*
                cp -r stock-platform/frontend-vue/dist/* backend/src/main/resources/static/
                '''
            }
        }

        stage('Backend Build') {
            steps {
                dir('backend') {
                    sh '''
                    chmod +x gradlew
                    ./gradlew clean build -x test
                    '''
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                docker build -t $IMAGE_NAME .
                '''
            }
        }

        stage('Deploy to EC2') {
            steps {
                sh '''
                docker save $IMAGE_NAME | ssh -i $SSH_KEY $APP_SERVER docker load

                ssh -i $SSH_KEY $APP_SERVER "
                    docker stop $IMAGE_NAME || true
                    docker rm $IMAGE_NAME || true
                    docker run -d -p 8080:8080 --name $IMAGE_NAME $IMAGE_NAME
                "
                '''
            }
        }

    }

    post {
        success {
            echo "Deploy success"
        }
        failure {
            echo "Deploy failed"
        }
    }
}