#!/bin/bash

echo "Cleaning up Lambda resources..."

# Delete Lambda function
aws lambda delete-function --function-name mastik-calculator

# Delete ECR repository and images
aws ecr delete-repository --repository-name mastik-calculator --force

# Delete IAM role and policies
aws iam detach-role-policy --role-name lambda-execution-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam detach-role-policy --role-name lambda-execution-role --policy-arn arn:aws:iam::198968105483:policy/LambdaECRPolicy
aws iam delete-role --role-name lambda-execution-role
aws iam delete-policy --policy-arn arn:aws:iam::198968105483:policy/LambdaECRPolicy

echo "Cleanup complete!"