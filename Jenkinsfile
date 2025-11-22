pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'autogram'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_LATEST = 'latest'

        DEPLOY_PORT = '40102'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "Checking out code from repository..."
                    checkout scm

                    sh '''
                        echo "Branch: ${GIT_BRANCH}"
                        echo "Commit: ${GIT_COMMIT}"
                        git log -1 --pretty=format:"%h - %an, %ar : %s"
                    '''
                }
            }
        }

        stage('Environment Check') {
            steps {
                script {
                    echo "Checking build environment..."
                    sh '''
                        echo "Docker version:"
                        docker --version

                        echo "Docker Compose version:"
                        docker-compose --version 2>/dev/null || docker compose version 2>/dev/null || echo "Docker Compose not found on Jenkins server (OK - only needed on deployment server)"

                        echo "Node version:"
                        node --version || echo "Node not found in Jenkins"

                        echo "Python version:"
                        python3 --version || echo "Python not found in Jenkins"

                        echo "Current user:"
                        whoami

                        echo "Workspace directory:"
                        echo "${WORKSPACE}"
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: ${DOCKER_IMAGE}:${DOCKER_TAG}"
                    sh """
                        docker build \
                            --tag ${DOCKER_IMAGE}:${DOCKER_TAG} \
                            --tag ${DOCKER_IMAGE}:${DOCKER_LATEST} \
                            --build-arg BUILD_DATE=\$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
                            --build-arg VCS_REF=\${GIT_COMMIT} \
                            .
                    """

                    echo "Docker image built successfully"
                    sh "docker images | grep ${DOCKER_IMAGE}"
                }
            }
        }

        stage('Test Image') {
            steps {
                script {
                    echo "Testing Docker image..."
                    sh """
                        # Test if image exists
                        docker images ${DOCKER_IMAGE}:${DOCKER_TAG}

                        # Test node and python are available
                        docker run --rm --entrypoint node ${DOCKER_IMAGE}:${DOCKER_TAG} --version
                        docker run --rm --entrypoint python3 ${DOCKER_IMAGE}:${DOCKER_TAG} --version

                        echo "✅ Docker image tests passed"
                    """
                }
            }
        }

        stage('Stop Old Container') {
            steps {
                script {
                    echo "Stopping old containers..."
                    sh """
                        # Stop and remove container if exists
                        docker stop autogram 2>/dev/null || true
                        docker rm autogram 2>/dev/null || true
                        echo "✅ Old container stopped"
                    """
                }
            }
        }

        stage('Prepare Environment') {
            steps {
                script {
                    echo "Preparing environment in workspace..."

                    // Create .env file from Jenkins credentials
                    withCredentials([file(credentialsId: 'autogram-env-file', variable: 'ENV_FILE')]) {
                        sh """
                            # Ensure directories exist
                            mkdir -p data
                            mkdir -p logs
                            mkdir -p sessions

                            # Copy .env file from credentials
                            cp -f \${ENV_FILE} .env
                            echo "✅ Environment file created from Jenkins credentials"

                            echo "✅ Environment prepared"
                            echo "Working directory: \$(pwd)"
                            ls -la
                        """
                    }
                }
            }
        }

        stage('Start New Container') {
            steps {
                script {
                    echo "Starting new container..."
                    sh """
                        # Start container with docker run
                        if [ -f .env ]; then
                            echo "Using .env file"
                            docker run -d \\
                                --name autogram \\
                                --restart unless-stopped \\
                                -p ${DEPLOY_PORT}:3000 \\
                                --env-file .env \\
                                -v \$(pwd)/data:/app/data \\
                                -v \$(pwd)/logs:/app/logs \\
                                ${DOCKER_IMAGE}:${DOCKER_TAG}
                        else
                            echo "No .env file found, starting without env file"
                            docker run -d \\
                                --name autogram \\
                                --restart unless-stopped \\
                                -p ${DEPLOY_PORT}:3000 \\
                                -v \$(pwd)/data:/app/data \\
                                -v \$(pwd)/logs:/app/logs \\
                                ${DOCKER_IMAGE}:${DOCKER_TAG}
                        fi

                        # Wait for container to be healthy
                        echo "Waiting for container to be healthy..."
                        sleep 10

                        # Check container status
                        echo "Container status:"
                        docker ps --filter name=autogram

                        # Check logs
                        echo "Container logs:"
                        docker logs --tail=50 autogram
                    """
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    echo "Performing health check..."
                    sh """
                        # Wait for application to be ready
                        for i in {1..30}; do
                            if curl -f http://localhost:${DEPLOY_PORT}/ > /dev/null 2>&1; then
                                echo "✅ Application is healthy!"
                                exit 0
                            fi
                            echo "Waiting for application to be ready... (\$i/30)"
                            sleep 2
                        done

                        echo "❌ Health check failed!"
                        docker logs --tail=100 autogram
                        exit 1
                    """
                }
            }
        }

        stage('Cleanup Old Images') {
            steps {
                script {
                    echo "Cleaning up old Docker images..."
                    sh """
                        # Keep only last 3 tagged images
                        docker images ${DOCKER_IMAGE} --format "{{.Tag}}" | \
                            grep -E '^[0-9]+\$' | \
                            sort -rn | \
                            tail -n +4 | \
                            xargs -I {} docker rmi ${DOCKER_IMAGE}:{} || true

                        # Remove dangling images
                        docker image prune -f
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ Deployment successful!"
            echo "Workspace: ${WORKSPACE}"
            echo "Application is running at: http://localhost:${DEPLOY_PORT}"
            echo "Public URL: https://autogram.kro.kr"
        }

        failure {
            echo "❌ Deployment failed!"

            script {
                try {
                    sh """
                        echo "Container status:"
                        docker ps --filter name=autogram || true
                        echo "Recent logs:"
                        docker logs --tail=100 autogram || true
                    """
                } catch (Exception e) {
                    echo "Failed to get deployment logs: ${e.message}"
                }
            }
        }

        always {
            echo "Pipeline finished"

            cleanWs(
                deleteDirs: true,
                disableDeferredWipeout: true,
                patterns: [[pattern: 'node_modules', type: 'INCLUDE']]
            )
        }
    }
}
