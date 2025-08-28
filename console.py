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

from tools.aws_documentation_researcher import aws_documentation_researcher
from tools.aws_pricing_assistant import aws_pricing_assistant
from strands import Agent
from strands_tools import think, use_aws
from strands.models import BedrockModel
from botocore.config import Config as BotocoreConfig

# Interactive mode when run directly
# IMPORTANT: This agent performs READ-ONLY operations only
# No modifications to customer environment or AWS resources

SUPERVISOR_AGENT_PROMPT = """
You are an AWS Assistant that intelligently analyzes queries and uses the most efficient approach.

## Core Strategy: ANSWER EFFICIENTLY AND FAST

1. **Tool Selection - BE SELECTIVE FOR SPEED**:
   - **For account queries** (my instances, my resources): Use use_aws ONLY
   - **For pricing questions**: Use aws_pricing_assistant ONLY  
   - **For general AWS knowledge**: Use aws_documentation_researcher ONLY
   - **NEVER use documentation researcher for account-specific queries**
   - **For "cheapest instance" questions: Get instances with use_aws, then use pricing assistant**

2. **AWS CLI Best Practices - MINIMIZE DATA**:
   - **Always use --query to return only needed fields**
   - **Use filters to reduce array size before processing**
   - **For counts: use length() function in --query**
   - Example: --query 'length(Reservations[*].Instances[*])'
   - Example: --query 'Reservations[*].Instances[*].[InstanceId,InstanceType]'

3. **CRITICAL: Answer only what's requested**:
   - If user asks "how many", provide ONLY the count
   - DO NOT add extra analysis unless specifically requested
   - DO NOT use slow tools unless absolutely necessary
   - Answer the question and STOP

## Example Workflows:

**"How many EC2 instances are running?"**
1. use_aws: ec2 describe-instances --filters Name=instance-state-name,Values=running --query 'length(Reservations[*].Instances[*])'
2. Answer: "You have X running EC2 instances." STOP.

**"Which running instance is cheapest?"**
1. use_aws: Get instance types with --query 'Reservations[*].Instances[*].InstanceType'
2. aws_pricing_assistant: Compare pricing for those types
3. Answer which is cheapest. STOP.

**"How do I configure Lambda?"** (General knowledge)
1. aws_documentation_researcher: Search Lambda configuration
2. Provide guide. STOP.

Use tools efficiently - avoid slow MCP servers for simple account queries.
"""

# supervisor_agent = Agent(
#     system_prompt=SUPERVISOR_AGENT_PROMPT,
#     model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
#     tools=[aws_documentation_researcher, aws_cost_assistant, aws_pricing_assistant, aws_cloudwatch_assistant, aws_security_assistant, aws_support_assistant, eks_assistant, graph_creater, eksctl_tool, think, python_repl, shell, use_aws],
# )

# Create a boto client config with custom settings
boto_config = BotocoreConfig(
    retries={"max_attempts": 3, "mode": "standard"},
    connect_timeout=5,
    read_timeout=60
)

# Create a configured Bedrock model
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    region_name="us-east-1",  # Specify a different region than the default
    temperature=0.3,
    top_p=0.8,
    stop_sequences=["###", "END"],
    boto_client_config=boto_config,
)


supervisor_agent = Agent(
    system_prompt=SUPERVISOR_AGENT_PROMPT,
    model=bedrock_model,
    tools=[aws_documentation_researcher, aws_pricing_assistant, think, use_aws],
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
