"""
# 🌐 AWS Documentaion Agent

A agent specialized in AWS docs research using MCP.

## What This Example Shows

This example demonstrates:
- Creating a research-oriented agent
- Storing research findings in memory for context preservation
- Using MCP server

Basic research query:
```
How to trigger AWS Lambda from S3?
```
"""

from tools.aws_cloudwatch_assistant import aws_cloudwatch_assistant
from tools.aws_cost_assistant import aws_cost_assistant
from tools.aws_documentation_researcher import aws_documentation_researcher
from tools.aws_pricing_assistant import aws_pricing_assistant
from tools.aws_security_assistant import aws_security_assistant
from tools.aws_support_assistant import aws_support_assistant
from tools.eks_assistant import eks_assistant
from tools.eksctl_tool import eksctl_tool
from tools.graph_creater import graph_creater
from strands import Agent
from strands_tools import think, shell, python_repl, use_aws

# Interactive mode when run directly
# IMPORTANT: This agent performs READ-ONLY operations only
# No modifications to customer environment or AWS resources

SUPERVISOR_AGENT_PROMPT = """
You are an AWS Assistant that intelligently analyzes queries and uses the most efficient approach.

## Core Strategy: THINK FIRST, THEN ACT

1. **Always use 'think' tool first** to analyze:
   - What specific information is needed?
   - What's the most efficient query approach?
   - What filters/parameters will minimize response size?
   - Which tool is best for this specific query?

2. **For AWS CLI queries, use smart parameters**:
   - Use --query to select only needed fields
   - Use --max-items to limit results 
   - Use filters to narrow scope
   - Example for EC2: --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name,LaunchTime,Tags[?Key==`Name`].Value|[0]]'

3. **Tool Selection Priority**:
   - Specific domain tools first (aws_cost_assistant, eks_assistant, etc.)
   - use_aws for general AWS queries with smart parameters
   - shell for complex CLI operations
   - python_repl for data processing

4. **Response Size Management**:
   - Always aim for concise, targeted queries
   - If response might be large, use --query to extract key fields only
   - Use --max-items 20-50 for list operations
   - Focus on answering the specific question, not dumping all data

5. **Retry Logic** (max 3 attempts):
   - If first approach fails, think about alternative parameters
   - Try different tool if needed
   - Report clear failure after 3 attempts

## Example Workflow for "list EC2 instances":
1. think: "User wants EC2 list, I should use --query to get key fields only"
2. use_aws with: --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name,LaunchTime]' --max-items 50
3. Provide structured summary

Always start with 'think' to plan your approach efficiently.
"""

supervisor_agent = Agent(
    system_prompt=SUPERVISOR_AGENT_PROMPT,
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    tools=[aws_documentation_researcher, aws_cost_assistant, aws_pricing_assistant, aws_cloudwatch_assistant, aws_security_assistant, aws_support_assistant, eks_assistant, graph_creater, eksctl_tool, think, python_repl, shell, use_aws],
)

# Example usage
if __name__ == "__main__":
    print("\n📁 AWS Agent\n")
    print("Ask a question about AWS or query your AWS spend.\n\n")
    
    print("You can try following queries:")
    print("- Explain AWS Lambda triggers")
    print("- What's my AWS spending this month?")
    print("- Create a graph of my service costs")
    print("- How much does a t3.medium EC2 instance cost per month?")
    print("- Compare pricing between us-east-1 and us-west-2 for RDS")
    print("- What's the cost difference between On-Demand and Reserved Instances?")
    print("- Show me AWS Free Tier limits for EC2")
    print("- Show me CPU utilization for my EC2 instances")
    print("- What CloudWatch alarms are currently firing?")
    print("- Search my application logs for errors in the last hour")
    print("- Show me memory usage trends for my RDS database")
    print("- Assess the security posture of my AWS account")
    print("- Review my IAM policies for security best practices")
    print("- Check my data protection and encryption settings")
    print("- Evaluate my network security configuration")
    print("- What are my current AWS support cases?")
    print("- Show me Trusted Advisor recommendations")
    print("- What's the status of AWS services in my region?")
    print("- What EKS clusters do I have running?")
    print("- Show me the node groups in my EKS cluster")
    print("- What add-ons are installed on my EKS cluster?")
    print("- Use eksctl to list my EKS clusters")
    print("- Show me EKS cluster details using eksctl")
    print("- Analyze the health of my Kubernetes workloads")
    print("- Analyze if instance i-12345 can connect to instance i-67890")
    print("- Can AMI ami-12345 be used to launch i7i instances? (uses dry-run)")
    print("- Test if I can create a security group with specific rules (dry-run)")
    print("- List all running EC2 instances in us-east-1")
    print("- Show me the configuration of security group sg-12345")
    print("- What IAM roles are attached to my EC2 instances?")
    print("- Analyze my VPC network configuration")
    print("- Check the status of my RDS databases")
    print("Type 'exit' to quit.")

    # Interactive loop
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() == "exit":
                print("\nGoodbye! 👋")
                break

            # Validate input is not empty
            if not user_input.strip():
                print("Please enter a valid question.")
                continue

            # Process the request
            print("\n🤖 Processing your request...\n")
            
            response = supervisor_agent(user_input)

            # Validate response is not empty
            content = str(response).strip()
            if not content:
                print("I apologize, but I received an empty response. Please try rephrasing your question.")
                continue
                
            print(content)

        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            error_msg = str(e)
            print(f"\nAn error occurred: {error_msg}")
            
            # Provide more specific guidance based on error type
            if "throttlingException" in error_msg or "Too many requests" in error_msg:
                print("This is an AWS API throttling error. The system made too many requests too quickly.")
                print("Please wait a moment before trying again. Consider:")
                print("- Using more specific queries to reduce API calls")
                print("- Asking about one service/region at a time")
                print("- Waiting 30-60 seconds before retrying")
            elif "ValidationException" in error_msg and "blank" in error_msg:
                print("This appears to be a message formatting issue. The agent may have generated an empty response.")
                print("Try asking a simpler question or rephrase your query.")
            elif "MCP" in error_msg or "server" in error_msg.lower():
                print("This appears to be an MCP server connection issue.")
                print("Please ensure the required MCP servers are running properly.")
            else:
                print("Please try asking a different question.")
                
            # Add debug info for troubleshooting
            print(f"Debug info: Error type: {type(e).__name__}")
