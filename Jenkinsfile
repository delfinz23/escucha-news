pipeline {
    agent any
    stages {
        
        stage('Docker stop escuchanews 60') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh "ssh root@10.22.1.60 podman stop escuchanews"
                }
            }
        }
        stage('Docker rm escuchanews 60') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                    sh "ssh root@10.22.1.60 podman rm escuchanews"
                    sh "ssh root@10.22.1.60 podman rmi 10.118.1.80/datascience/escuchanew:0.0.1"
                }
            }
        }
        stage('Docker Start escuchanews 60') {
            steps {
                sh 'ssh root@10.22.1.60 podman run -d --name escuchanews --restart unless-stopped 10.118.1.80/datacience/escuchanew:0.0.1'  
			}
		}
    }
}