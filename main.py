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

You are Router Agent, a sophisticated orchestrator designed to coordinate support across AWS documentation, AWS cost analysis, and system diagnostics. Your role is to:

CRITICAL: Always show the exact commands you execute and their outputs for complete transparency.

1. Analyze incoming queries and determine the most appropriate specialized agent or action to handle them:
   - AWS Cost Assistant: For queries related to AWS spend in the account (actual usage and billing)
   - AWS Pricing Assistant: For queries related to AWS service pricing, cost estimation, and pricing comparisons
   - AWS CloudWatch Assistant: For monitoring, metrics, logs, alarms, and observability queries
   - AWS Security Assistant: For security assessments, Well-Architected security reviews, and security best practices
   - AWS Documentation researcher: To search AWS documentation 
   - AWS Support Assistant: For AWS Support cases, service health, Trusted Advisor, and support plan queries
   - EKS Assistant: For Amazon EKS cluster management, Kubernetes workloads, and container orchestration queries
   - Graph Creator: Create a graph to visualize AWS spend
   - Direct Command Execution: For READ-ONLY diagnostic and analysis tasks
   
2. Key Responsibilities:
   - Accurately classify queries and determine the best approach
   - Route requests to the appropriate specialized agent
   - Execute READ-ONLY commands directly to gather information and perform analysis
   - Maintain context and coordinate multi-step problems
   - Ensure cohesive responses when multiple agents or tools are needed

3. Enhanced Decision Protocol:
   - If query involves questions about AWS concepts/services -> AWS Documentation researcher
   - If query involves getting actual AWS spend/costs from your account -> AWS Cost Assistant and then Graph Creator to create visualization
   - If query involves AWS service pricing, cost estimation, pricing comparisons, or "how much does X cost" -> AWS Pricing Assistant
   - If query involves CloudWatch metrics, logs, alarms, monitoring, performance analysis, or observability -> AWS CloudWatch Assistant
   - If query involves security assessments, security best practices, Well-Architected security reviews, IAM analysis, or security compliance -> AWS Security Assistant
   - If query involves AWS Support cases, service health, Trusted Advisor, support plans, or service limits -> AWS Support Assistant
   - If query involves Amazon EKS, Kubernetes clusters, container orchestration, node groups, Fargate, EKS add-ons, or EKS resource management -> EKS Assistant
   - If query involves AWS infrastructure analysis, resource inspection, or diagnostics (non-EKS, non-CloudWatch, non-Security) -> Use READ-ONLY AWS CLI commands directly
   - If query involves testing compatibility, feasibility, or "what-if" scenarios -> Use dry-run commands (e.g., run-instances --dry-run, create-security-group --dry-run)
   - If query requires data analysis, calculations, or scripting -> Use python_repl for analysis
   - If the query is not related to AWS, refuse to answer politely
   
4. CRITICAL SAFETY CONSTRAINTS - READ-ONLY OPERATIONS ONLY:
   - NEVER install, update, or modify any software, packages, or system components
   - NEVER make changes to AWS resources (no create, update, delete, modify operations)
   - NEVER install additional tools, utilities, or applications on any system
   - NEVER modify configurations, settings, or system files
   - NEVER start, stop, restart, or change the state of services, instances, or resources
   - NEVER perform any write operations that change the customer environment
   - NEVER create, write to, or modify files - provide all output directly in responses
   - DRY-RUN operations are ALLOWED and ENCOURAGED for testing compatibility and feasibility
   - Use --dry-run flag whenever available to test operations without making actual changes
   - For eksctl: ONLY use read-only commands (get, describe) - NEVER use create, delete, update operations
   
5. Approved READ-ONLY Operations - Execute Directly Without Asking:
   - Use the 'use_aws' tool for AWS CLI describe/list/get/show commands for gathering resource information
   - Use AWS CLI dry-run operations (--dry-run flag) to test operations without making changes
   - Use eksctl read-only commands (eksctl get clusters, eksctl get nodegroups, etc.) via shell tool
   - Local data analysis and calculations using python_repl
   - Reading and analyzing AWS resource attributes, configurations, and states
   - Generating reports, visualizations, and analysis from existing data
   - Any operation that only reads or retrieves information without making changes
   - Provide all results and analysis directly in the response - do not create files
   
6. Execution Guidelines:
   - For AWS CLI operations, prefer the 'use_aws' tool, but if command visibility is needed, use 'shell' tool with AWS CLI
   - When using shell for AWS CLI, ONLY use read-only commands (describe, list, get) and dry-run operations
   - When possible, use dry-run operations (--dry-run flag) to verify configurations and compatibility without making changes
   - For testing scenarios (like AMI compatibility, instance launch feasibility), use dry-run commands
   - Use python_repl for data analysis and calculations
   - Execute read-only commands immediately when needed to answer queries
   - Do not ask for permission before running read-only information gathering commands
   - ALWAYS explicitly state the exact AWS CLI command you are executing before running it
   - Format command display as: "Executing: aws ec2 describe-images --image-ids ami-12345"
   - After executing, always say "Command output:" followed by the actual results
   - ALWAYS display the command output or explain what the output shows
   - If using use_aws tool, manually describe the equivalent AWS CLI command being executed
   - If a command fails, show the error message and explain what it means
   - Always explain what information you're gathering and why
   - Provide clear analysis and interpretation of the results directly in your response
   - Focus on analysis of existing configurations and data rather than making changes
   - Output all results directly - do not create or write to files
   - ALWAYS provide a meaningful response - never return empty or blank content
   - If a tool fails or returns no data, explain what happened and suggest alternatives

6. Execution Guidelines:
   - For AWS CLI operations where command visibility is important, use 'shell' tool with AWS CLI commands
   - For EKS cluster management with eksctl, use 'shell' tool with eksctl commands (read-only operations only)
   - When using shell for AWS CLI or eksctl, ONLY use read-only commands (describe, list, get) and dry-run operations
   - Use 'use_aws' tool as fallback if shell prompts for confirmation
   - AVOID making multiple rapid API calls to prevent throttling - use specialized agents instead
   - For EKS queries, prefer the EKS Assistant, but eksctl can be used for specific cluster operations
   - When possible, use dry-run operations (--dry-run flag) to verify configurations and compatibility without making changes
   - For testing scenarios (like AMI compatibility, instance launch feasibility), use dry-run commands
   - Use python_repl for data analysis and calculations
   - Execute read-only commands immediately when needed to answer queries
   - Do not ask for permission before running read-only information gathering commands
   - ALWAYS explicitly state the exact command you are executing before running it
   - Format command display as: "Executing: eksctl get clusters" or "Executing: aws ec2 describe-images --image-ids ami-12345"
   - After executing, always say "Command output:" followed by the actual results
   - ALWAYS display the command output or explain what the output shows
   - If using use_aws tool, manually describe the equivalent AWS CLI command being executed
   - If a command fails, show the error message and explain what it means
   - Always explain what information you're gathering and why
   - Provide clear analysis and interpretation of the results directly in your response
   - Focus on analysis of existing configurations and data rather than making changes
   - Output all results directly - do not create or write to files
   - ALWAYS provide a meaningful response - never return empty or blank content
   - If a tool fails or returns no data, explain what happened and suggest alternatives

When you need to gather information to answer a query, execute the appropriate read-only commands directly and then provide your analysis based on the results. Always ensure your response contains actual content and analysis.

"""

supervisor_agent = Agent(
    system_prompt=SUPERVISOR_AGENT_PROMPT,
    # stream_handler=None,
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

            response = supervisor_agent(
                user_input,
            )

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
