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
                        if [ -f docker-compose.yml ]; then
                            echo "Stopping existing containers..."
                            docker compose down || true
                        else
                            echo "No docker-compose.yml found, skipping..."
                        fi
                    """
                }
            }
        }

        stage('Prepare Environment') {
            steps {
                script {
                    echo "Preparing environment in workspace..."
                    sh """
                        # Ensure directories exist
                        mkdir -p data
                        mkdir -p logs

                        # Copy .env file if exists
                        if [ -f .env.production ]; then
                            cp -f .env.production .env
                            echo "✅ Copied .env.production to .env"
                        else
                            echo "⚠️  No .env.production file found"
                        fi

                        echo "✅ Environment prepared"
                        echo "Working directory: \$(pwd)"
                        ls -la
                    """
                }
            }
        }

        stage('Start New Container') {
            steps {
                script {
                    echo "Starting new container..."
                    sh """
                        # Start container
                        docker compose up -d

                        # Wait for container to be healthy
                        echo "Waiting for container to be healthy..."
                        sleep 10

                        # Check container status
                        docker compose ps

                        # Check logs
                        echo "Container logs:"
                        docker compose logs --tail=50
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
                        docker compose logs --tail=100
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
                        docker compose ps || true
                        echo "Recent logs:"
                        docker compose logs --tail=100 || true
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
