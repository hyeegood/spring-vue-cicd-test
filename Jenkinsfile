pipeline {
    agent any

    environment {
        APP_SERVER = "ec2-user@54.252.156.1"
        // Vue 빌드 시 API 주소 (운영 FastAPI 떠 있는 호스트:포트). 8080은 Spring만 있으면 /api 없음 → 대시보드 빈 화면
        VITE_API_BASE = "http://54.252.156.1:8000"
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
                set -e
                # Vite는 빌드 시점에 VITE_* 를 번들에 넣음. 없으면 '' → 브라우저가 8080/api 호출 → Spring에는 해당 API 없음
                echo "VITE_API_BASE=${VITE_API_BASE}" > stock-platform/frontend-vue/.env.production

                CID=$(docker create -w /app node:20-alpine sh -c "npm install && npm run build")

                docker cp stock-platform/frontend-vue/. "$CID:/app/"

                docker start -a "$CID"

                docker cp "$CID:/app/dist" stock-platform/frontend-vue/

                docker rm "$CID" 2>/dev/null || true
                '''
            }
        }

        stage('Copy Frontend') {
            steps {
                sh '''
                mkdir -p backend/src/main/resources/static
                rm -rf backend/src/main/resources/static/*

                cp -r stock-platform/frontend-vue/dist/* backend/src/main/resources/static/
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