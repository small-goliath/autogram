pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'autogram'
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_LATEST = 'latest'

        DEPLOY_HOST = '${SERVER_IP}'
        DEPLOY_PORT = '40102'
        PROJECT_DIR = '/home/dotori/services/autogram'

        // Jenkins credentials ID (SSH key for deployment server)
        // Create this in Jenkins: Manage Jenkins -> Credentials -> Add Credentials
        DEPLOY_CREDENTIALS = 'autogram-deploy-server'
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
                        docker compose version

                        echo "Node version:"
                        node --version || echo "Node not found in Jenkins"

                        echo "Python version:"
                        python3 --version || echo "Python not found in Jenkins"
                    '''
                }
            }
        }

        stage('Test SSH Credentials') {
            steps {
                script {
                    echo "Testing SSH credentials..."
                    try {
                        withCredentials([sshUserPrivateKey(credentialsId: 'autogram-deploy-server', keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                            sh """
                                echo "Credentials loaded successfully!"
                                echo "SSH User: \$SSH_USER"
                                echo "Testing SSH connection..."
                                ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$SSH_USER@${DEPLOY_HOST} 'echo "SSH connection successful!"'
                            """
                        }
                    } catch (Exception e) {
                        echo "CREDENTIAL TEST FAILED: ${e.message}"
                        echo "Please check:"
                        echo "1. Credential ID is exactly 'autogram-deploy-server'"
                        echo "2. Credential is in 'Global credentials (unrestricted)' scope"
                        echo "3. Credential type is 'SSH Username with private key'"
                        error("Credentials test failed - stopping pipeline")
                    }
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

                        # Run basic container test
                        docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} node --version
                        docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} python3 --version
                    """
                }
            }
        }

        stage('Stop Old Container') {
            steps {
                script {
                    echo "Stopping old containers on deployment server..."
                    withCredentials([sshUserPrivateKey(credentialsId: DEPLOY_CREDENTIALS, keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                        sh """
                            ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$SSH_USER@${DEPLOY_HOST} '
                                cd ${PROJECT_DIR} || exit 0

                                if [ -f docker-compose.yml ]; then
                                    echo "Stopping existing containers..."
                                    docker compose down || true
                                else
                                    echo "No docker-compose.yml found, skipping..."
                                fi
                            '
                        """
                    }
                }
            }
        }

        stage('Deploy to Server') {
            steps {
                script {
                    echo "Deploying to ${DEPLOY_HOST}..."
                    withCredentials([sshUserPrivateKey(credentialsId: DEPLOY_CREDENTIALS, keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                        sh """
                            # Create project directory if not exists
                            ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$SSH_USER@${DEPLOY_HOST} '
                                mkdir -p ${PROJECT_DIR}
                                mkdir -p ${PROJECT_DIR}/data
                                mkdir -p ${PROJECT_DIR}/logs
                            '

                            # Copy docker-compose.yml and necessary files
                            scp -i \$SSH_KEY -o StrictHostKeyChecking=no \
                                docker-compose.yml \
                                \$SSH_USER@${DEPLOY_HOST}:${PROJECT_DIR}/

                            # Copy .env file if exists
                            if [ -f .env.production ]; then
                                scp -i \$SSH_KEY -o StrictHostKeyChecking=no \
                                    .env.production \
                                    \$SSH_USER@${DEPLOY_HOST}:${PROJECT_DIR}/.env
                            fi
                        """
                    }
                }
            }
        }

        stage('Save and Load Docker Image') {
            steps {
                script {
                    echo "Transferring Docker image to deployment server..."
                    sh """
                        # Save Docker image to tar file
                        docker save ${DOCKER_IMAGE}:${DOCKER_TAG} | gzip > /tmp/${DOCKER_IMAGE}-${DOCKER_TAG}.tar.gz
                    """

                    withCredentials([sshUserPrivateKey(credentialsId: DEPLOY_CREDENTIALS, keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                        sh """
                            # Transfer image to server
                            scp -i \$SSH_KEY -o StrictHostKeyChecking=no \
                                /tmp/${DOCKER_IMAGE}-${DOCKER_TAG}.tar.gz \
                                \$SSH_USER@${DEPLOY_HOST}:/tmp/

                            # Load image on server
                            ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$SSH_USER@${DEPLOY_HOST} '
                                echo "Loading Docker image..."
                                docker load < /tmp/${DOCKER_IMAGE}-${DOCKER_TAG}.tar.gz

                                # Tag as latest
                                docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:${DOCKER_LATEST}

                                # Clean up
                                rm -f /tmp/${DOCKER_IMAGE}-${DOCKER_TAG}.tar.gz

                                echo "Available images:"
                                docker images | grep ${DOCKER_IMAGE}
                            '
                        """
                    }

                    sh "rm -f /tmp/${DOCKER_IMAGE}-${DOCKER_TAG}.tar.gz"
                }
            }
        }

        stage('Start New Container') {
            steps {
                script {
                    echo "Starting new container..."
                    withCredentials([sshUserPrivateKey(credentialsId: DEPLOY_CREDENTIALS, keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                        sh """
                            ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$SSH_USER@${DEPLOY_HOST} '
                                cd ${PROJECT_DIR}

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
                            '
                        """
                    }
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    echo "Performing health check..."
                    withCredentials([sshUserPrivateKey(credentialsId: DEPLOY_CREDENTIALS, keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                        sh """
                            ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$SSH_USER@${DEPLOY_HOST} '
                                # Wait for application to be ready
                                for i in {1..30}; do
                                    if curl -f http://localhost:${DEPLOY_PORT}/ > /dev/null 2>&1; then
                                        echo "Application is healthy!"
                                        exit 0
                                    fi
                                    echo "Waiting for application to be ready... (\$i/30)"
                                    sleep 2
                                done

                                echo "Health check failed!"
                                docker compose logs --tail=100
                                exit 1
                            '
                        """
                    }
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

                    withCredentials([sshUserPrivateKey(credentialsId: DEPLOY_CREDENTIALS, keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                        sh """
                            ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$SSH_USER@${DEPLOY_HOST} '
                                # Keep only last 3 tagged images
                                docker images ${DOCKER_IMAGE} --format "{{.Tag}}" | \
                                    grep -E "^[0-9]+\$" | \
                                    sort -rn | \
                                    tail -n +4 | \
                                    xargs -I {} docker rmi ${DOCKER_IMAGE}:{} || true

                                # Remove dangling images
                                docker image prune -f
                            '
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Deployment successful!"
            echo "Application is running at: http://${DEPLOY_HOST}:${DEPLOY_PORT}"
            echo "Public URL: https://autogram.kro.kr"
        }

        failure {
            echo "Deployment failed!"

            script {
                try {
                    withCredentials([sshUserPrivateKey(credentialsId: DEPLOY_CREDENTIALS, keyFileVariable: 'SSH_KEY', usernameVariable: 'SSH_USER')]) {
                        sh """
                            ssh -i \$SSH_KEY -o StrictHostKeyChecking=no \$SSH_USER@${DEPLOY_HOST} '
                                cd ${PROJECT_DIR}
                                echo "Container status:"
                                docker compose ps
                                echo "Recent logs:"
                                docker compose logs --tail=100
                            ' || true
                        """
                    }
                } catch (Exception e) {
                    echo "Failed to get deployment logs: ${e.message}"
                }
            }
        }

        always {
            echo "Pipeline finished"

            // Clean up workspace
            cleanWs(
                deleteDirs: true,
                disableDeferredWipeout: true,
                patterns: [[pattern: 'node_modules', type: 'INCLUDE']]
            )
        }
    }
}
