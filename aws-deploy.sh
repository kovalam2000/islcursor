#!/bin/bash

# AWS Satellite Interlink Application Deployment Script
# This script deploys the application to AWS ECS with Fargate

set -e

# Configuration
APP_NAME="satellite-interlink"
AWS_REGION="us-east-1"
ECR_REPOSITORY_NAME="satellite-interlink"
CLUSTER_NAME="satellite-interlink-cluster"
SERVICE_NAME="satellite-interlink-service"
TASK_DEFINITION_NAME="satellite-interlink-task"

echo "🚀 Starting deployment of Satellite Interlink Application to AWS..."

# Check if AWS CLI is installed and configured
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t $APP_NAME .

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# Create ECR repository if it doesn't exist
echo "📦 Creating ECR repository..."
aws ecr create-repository --repository-name $ECR_REPOSITORY_NAME --region $AWS_REGION 2>/dev/null || echo "Repository already exists"

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

# Tag and push image
echo "📤 Tagging and pushing Docker image..."
docker tag $APP_NAME:latest $ECR_URI/$ECR_REPOSITORY_NAME:latest
docker push $ECR_URI/$ECR_REPOSITORY_NAME:latest

# Create ECS cluster if it doesn't exist
echo "🏗️ Creating ECS cluster..."
aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $AWS_REGION 2>/dev/null || echo "Cluster already exists"

# Create task definition
echo "📋 Creating ECS task definition..."
cat > task-definition.json << EOF
{
    "family": "$TASK_DEFINITION_NAME",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "cpu": "512",
    "memory": "1024",
    "executionRoleArn": "arn:aws:iam::$AWS_ACCOUNT_ID:role/ecsTaskExecutionRole",
    "containerDefinitions": [
        {
            "name": "$APP_NAME",
            "image": "$ECR_URI/$ECR_REPOSITORY_NAME:latest",
            "portMappings": [
                {
                    "containerPort": 5000,
                    "protocol": "tcp"
                }
            ],
            "essential": true,
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "/ecs/$APP_NAME",
                    "awslogs-region": "$AWS_REGION",
                    "awslogs-stream-prefix": "ecs"
                }
            },
            "healthCheck": {
                "command": ["CMD-SHELL", "curl -f http://localhost:5000/ || exit 1"],
                "interval": 30,
                "timeout": 5,
                "retries": 3,
                "startPeriod": 60
            }
        }
    ]
}
EOF

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json --region $AWS_REGION

# Get default VPC and subnets
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=is-default,Values=true" --query 'Vpcs[0].VpcId' --output text --region $AWS_REGION)
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query 'Subnets[*].SubnetId' --output text --region $AWS_REGION | tr '\t' ',')

# Create security group if it doesn't exist
SECURITY_GROUP_NAME="satellite-interlink-sg"
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters "Name=group-name,Values=$SECURITY_GROUP_NAME" --query 'SecurityGroups[0].GroupId' --output text --region $AWS_REGION 2>/dev/null || echo "none")

if [ "$SECURITY_GROUP_ID" = "none" ] || [ "$SECURITY_GROUP_ID" = "None" ]; then
    echo "🔒 Creating security group..."
    SECURITY_GROUP_ID=$(aws ec2 create-security-group --group-name $SECURITY_GROUP_NAME --description "Security group for Satellite Interlink app" --vpc-id $VPC_ID --region $AWS_REGION --query 'GroupId' --output text)
    
    # Add inbound rule for port 5000
    aws ec2 authorize-security-group-ingress --group-id $SECURITY_GROUP_ID --protocol tcp --port 5000 --cidr 0.0.0.0/0 --region $AWS_REGION
fi

# Create service
echo "🚀 Creating ECS service..."
aws ecs create-service \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --task-definition $TASK_DEFINITION_NAME \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
    --region $AWS_REGION 2>/dev/null || echo "Service already exists"

# Wait for service to be stable
echo "⏳ Waiting for service to be stable..."
aws ecs wait services-stable --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION

# Get service details
SERVICE_DETAILS=$(aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $AWS_REGION)
TASK_ARN=$(echo $SERVICE_DETAILS | jq -r '.services[0].deployments[0].taskDefinition')

echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Deployment Summary:"
echo "   Application: $APP_NAME"
echo "   ECS Cluster: $CLUSTER_NAME"
echo "   Service: $SERVICE_NAME"
echo "   Task Definition: $TASK_ARN"
echo "   Security Group: $SECURITY_GROUP_ID"
echo ""
echo "🌐 To access your application:"
echo "   1. Go to the ECS console in AWS"
echo "   2. Navigate to the service: $SERVICE_NAME"
echo "   3. Click on the running task"
echo "   4. Note the public IP address"
echo "   5. Access via: http://<PUBLIC_IP>:5000"
echo ""
echo "🔍 Monitor your application:"
echo "   - ECS Console: https://console.aws.amazon.com/ecs/home?region=$AWS_REGION"
echo "   - CloudWatch Logs: /ecs/$APP_NAME"

# Clean up temporary files
rm -f task-definition.json

echo ""
echo "🎉 Deployment script completed!"
