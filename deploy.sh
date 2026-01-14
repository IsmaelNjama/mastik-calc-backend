#!/bin/bash

# Configuration
AWS_REGION="us-east-1"
FUNCTION_NAME="mastik-calculator"
ECR_REPO_NAME="mastik-calculator"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "Building and deploying Lambda function..."

# Build Docker image
docker build -f Dockerfile.lambda -t $FUNCTION_NAME .

# Create ECR repository if it doesn't exist
aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION 2>/dev/null || \
aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION

# Get ECR login token
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Tag and push image
# docker tag $FUNCTION_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest
# docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
IMAGE_TAG="$TIMESTAMP"
docker tag $FUNCTION_NAME:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$IMAGE_TAG
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$IMAGE_TAG
IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$IMAGE_TAG"

# Deploy/Update via CloudFormation
STACK_NAME="mastik-calculator-stack"

if aws cloudformation describe-stacks --stack-name $STACK_NAME --region $AWS_REGION 2>/dev/null; then
    echo "Updating CloudFormation stack..."
    aws cloudformation update-stack \
        --stack-name $STACK_NAME \
        --template-body file://cloudformation.yml \
        --parameters ParameterKey=ImageUri,ParameterValue=$IMAGE_URI \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $AWS_REGION
else
    echo "Creating CloudFormation stack..."
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://cloudformation.yml \
        --parameters ParameterKey=ImageUri,ParameterValue=$IMAGE_URI \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $AWS_REGION
fi

echo "Deployment complete!"