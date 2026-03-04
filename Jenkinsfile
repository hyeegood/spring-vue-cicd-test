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

        stage('Backend Build') {
            steps {
                dir('backend') {
                    sh './gradlew build'
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t cicd-test .'
            }
        }

        stage('Deploy to App Server') {
            steps {
                sh """
                docker save cicd-test | ssh $APP_SERVER docker load
                ssh $APP_SERVER '
                docker stop cicd-test || true
                docker rm cicd-test || true
                docker run -d -p 8080:8080 --name cicd-test cicd-test
                '
                """
            }
        }

    }
}