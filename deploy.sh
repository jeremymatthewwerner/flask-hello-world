#!/bin/bash
set -e

# Store the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the infra directory for Pulumi commands
cd "${SCRIPT_DIR}/infra"

# Get the repository URL
REPO_URL=$(pulumi stack output repository_url)
echo "Repository URL: $REPO_URL"

# Authenticate with ECR
echo "Authenticating with ECR..."
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin $REPO_URL

# Change back to root directory for Docker commands
cd "${SCRIPT_DIR}"

# Build the image
echo "Building Docker image..."
docker build --platform linux/amd64 -t bouncing-circles .

# Tag the image
echo "Tagging image..."
docker tag bouncing-circles:latest $REPO_URL:latest

# Push to ECR
echo "Pushing to ECR..."
docker push $REPO_URL:latest

# Verify the push
echo "Verifying image push..."
aws ecr describe-images \
    --repository-name $(echo $REPO_URL | cut -d'/' -f2) \
    --region us-west-2 \
    --output json

# Force new deployment
echo "Forcing new deployment..."
aws ecs update-service \
    --cluster bouncing-circles-cluster-aa3c4a6 \
    --service bouncing-circles-service-7d1cc11 \
    --force-new-deployment \
    --region us-west-2 \
    --no-cli-pager

echo "Deployment initiated! It may take a few minutes for changes to propagate."

# Change back to infra directory for final Pulumi command
cd "${SCRIPT_DIR}/infra"
echo "Deployment complete! Your app should be available at: $(pulumi stack output alb_dns_name)" 