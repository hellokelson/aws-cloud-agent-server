#!/usr/bin/env python3
"""
Deployment script for AWS Assistant to Amazon Bedrock AgentCore Runtime

This script handles:
1. Building Docker container
2. Pushing to ECR
3. Creating AgentCore Runtime
4. Deploying the agent

Prerequisites:
- AWS CLI configured
- Docker installed and running
- Appropriate IAM permissions
"""

import boto3
import json
import os
import subprocess
import sys
import time
from typing import Optional

class AgentCoreDeployer:
    def __init__(self, 
                 agent_name: str = "aws-assistant-mcp",
                 region: str = "us-east-1",
                 execution_role_arn: Optional[str] = None):
        self.agent_name = agent_name
        self.region = region
        self.execution_role_arn = execution_role_arn
        
        # Initialize AWS clients
        self.ecr_client = boto3.client('ecr', region_name=region)
        self.agentcore_client = boto3.client('bedrock-agentcore-control', region_name=region)
        self.sts_client = boto3.client('sts', region_name=region)
        
        # Get account ID
        self.account_id = self.sts_client.get_caller_identity()['Account']
        self.repository_name = f"{agent_name}-repo"
        self.image_uri = f"{self.account_id}.dkr.ecr.{region}.amazonaws.com/{self.repository_name}:latest"
    
    def create_ecr_repository(self):
        """Create ECR repository if it doesn't exist"""
        try:
            self.ecr_client.describe_repositories(repositoryNames=[self.repository_name])
            print(f"✅ ECR repository {self.repository_name} already exists")
        except self.ecr_client.exceptions.RepositoryNotFoundException:
            print(f"📦 Creating ECR repository: {self.repository_name}")
            self.ecr_client.create_repository(
                repositoryName=self.repository_name,
                imageScanningConfiguration={'scanOnPush': True}
            )
            print(f"✅ Created ECR repository: {self.repository_name}")
    
    def build_and_push_image(self):
        """Build Docker image and push to ECR"""
        print("🔨 Building Docker image...")
        
        # Create Dockerfile
        dockerfile_content = f"""
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml .
RUN pip install -e .

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "agentcore_main.py"]
"""
        
        with open("Dockerfile", "w") as f:
            f.write(dockerfile_content)
        
        # Build image
        build_cmd = ["docker", "build", "-t", self.agent_name, "."]
        result = subprocess.run(build_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Docker build failed: {result.stderr}")
            return False
        
        print("✅ Docker image built successfully")
        
        # Get ECR login token
        print("🔐 Getting ECR login token...")
        login_response = self.ecr_client.get_authorization_token()
        token = login_response['authorizationData'][0]['authorizationToken']
        endpoint = login_response['authorizationData'][0]['proxyEndpoint']
        
        # Docker login to ECR
        login_cmd = ["docker", "login", "--username", "AWS", "--password-stdin", endpoint]
        login_process = subprocess.run(login_cmd, input=token, text=True, capture_output=True)
        if login_process.returncode != 0:
            print(f"❌ ECR login failed: {login_process.stderr}")
            return False
        
        # Tag image
        tag_cmd = ["docker", "tag", self.agent_name, self.image_uri]
        subprocess.run(tag_cmd, check=True)
        
        # Push image
        print("📤 Pushing image to ECR...")
        push_cmd = ["docker", "push", self.image_uri]
        result = subprocess.run(push_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Docker push failed: {result.stderr}")
            return False
        
        print(f"✅ Image pushed successfully: {self.image_uri}")
        return True
    
    def create_execution_role(self):
        """Create IAM execution role if not provided"""
        if self.execution_role_arn:
            return self.execution_role_arn
        
        iam_client = boto3.client('iam', region_name=self.region)
        role_name = f"{self.agent_name}-execution-role"
        
        # Trust policy for AgentCore
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock-agentcore.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        # Basic execution policy
        execution_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogGroup",
                        "logs:CreateLogStream",
                        "logs:PutLogEvents",
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream",
                        "s3:GetObject",
                        "s3:PutObject",
                        "cloudwatch:GetMetricStatistics",
                        "cloudwatch:ListMetrics",
                        "ec2:DescribeInstances",
                        "rds:DescribeDBInstances"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        try:
            # Create role
            role_response = iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f"Execution role for {self.agent_name} AgentCore runtime"
            )
            role_arn = role_response['Role']['Arn']
            
            # Attach policy
            iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName=f"{role_name}-policy",
                PolicyDocument=json.dumps(execution_policy)
            )
            
            print(f"✅ Created execution role: {role_arn}")
            return role_arn
            
        except iam_client.exceptions.EntityAlreadyExistsException:
            role_response = iam_client.get_role(RoleName=role_name)
            role_arn = role_response['Role']['Arn']
            print(f"✅ Using existing execution role: {role_arn}")
            return role_arn
    
    def deploy_agent_runtime(self):
        """Deploy agent to AgentCore Runtime"""
        print("🚀 Deploying agent to AgentCore Runtime...")
        
        execution_role_arn = self.create_execution_role()
        
        try:
            response = self.agentcore_client.create_agent_runtime(
                agentRuntimeName=self.agent_name,
                agentRuntimeArtifact={
                    'containerConfiguration': {
                        'containerUri': self.image_uri
                    }
                },
                networkConfiguration={"networkMode": "PUBLIC"},
                roleArn=execution_role_arn
            )
            
            agent_runtime_arn = response['agentRuntimeArn']
            print(f"✅ Agent runtime created: {agent_runtime_arn}")
            
            # Wait for deployment to complete
            print("⏳ Waiting for deployment to complete...")
            while True:
                status_response = self.agentcore_client.get_agent_runtime(
                    agentRuntimeArn=agent_runtime_arn
                )
                status = status_response['agentRuntimeStatus']
                print(f"Status: {status}")
                
                if status == 'READY':
                    print("✅ Agent runtime is ready!")
                    break
                elif status in ['FAILED', 'STOPPED']:
                    print(f"❌ Deployment failed with status: {status}")
                    return None
                
                time.sleep(30)
            
            return agent_runtime_arn
            
        except Exception as e:
            print(f"❌ Failed to create agent runtime: {e}")
            return None
    
    def test_agent(self, agent_runtime_arn: str):
        """Test the deployed agent"""
        print("🧪 Testing deployed agent...")
        
        runtime_client = boto3.client('bedrock-agentcore', region_name=self.region)
        
        test_payload = json.dumps({
            "prompt": "What is AWS Lambda?"
        }).encode()
        
        try:
            response = runtime_client.invoke_agent_runtime(
                agentRuntimeArn=agent_runtime_arn,
                runtimeSessionId="test-session-123",
                payload=test_payload
            )
            
            result = response['payload'].read().decode()
            print(f"✅ Test successful! Response: {result[:200]}...")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    def deploy(self):
        """Full deployment process"""
        print(f"🚀 Starting deployment of {self.agent_name} to AgentCore Runtime")
        print(f"Region: {self.region}")
        print(f"Account: {self.account_id}")
        
        # Step 1: Create ECR repository
        self.create_ecr_repository()
        
        # Step 2: Build and push Docker image
        if not self.build_and_push_image():
            print("❌ Deployment failed at image build/push step")
            return False
        
        # Step 3: Deploy to AgentCore
        agent_runtime_arn = self.deploy_agent_runtime()
        if not agent_runtime_arn:
            print("❌ Deployment failed at AgentCore deployment step")
            return False
        
        # Step 4: Test the agent
        if self.test_agent(agent_runtime_arn):
            print(f"🎉 Deployment successful!")
            print(f"Agent Runtime ARN: {agent_runtime_arn}")
            print(f"You can now invoke your agent using the AWS SDK or CLI")
            return True
        else:
            print("⚠️ Deployment completed but test failed")
            return False

def main():
    """Main deployment function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy AWS Assistant to AgentCore")
    parser.add_argument("--agent-name", default="aws-assistant-mcp", help="Agent name")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    parser.add_argument("--execution-role-arn", help="IAM execution role ARN (optional)")
    
    args = parser.parse_args()
    
    deployer = AgentCoreDeployer(
        agent_name=args.agent_name,
        region=args.region,
        execution_role_arn=args.execution_role_arn
    )
    
    success = deployer.deploy()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
