pipeline {
    agent any

    stages {

        stage('Git Check') {
            steps {
                echo 'Jenkins Pipeline Running'
            }
        }

        stage('Docker Check') {
            steps {
                sh 'docker ps'
            }
        }

    }
}