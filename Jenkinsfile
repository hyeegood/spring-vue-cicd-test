pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git 'https://github.com/hyeegood/spring-vue-cicd-test.git'
            }
        }

        stage('Backend Build') {
            steps {
                dir('backend') {
                    sh './gradlew build'
                }
            }
        }

        stage('Frontend Build') {
            steps {
                dir('frontend') {
                    sh 'npm install'
                    sh 'npm run build'
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
                docker stop cicd-test || true
                docker rm cicd-test || true
                docker run -d -p 8081:8080 --name cicd-test cicd-test
                '''
            }
        }

    }
}