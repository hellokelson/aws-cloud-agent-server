"""
AWS Diagnosis Agent - Specialized in AWS infrastructure analysis and troubleshooting
"""

import asyncio
import json
import logging
import os
import uuid
from typing import AsyncGenerator, Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set AWS environment variables explicitly
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_REGION"] = "us-east-1"

# Auto-approve tool usage for server deployment
os.environ["STRANDS_AUTO_APPROVE_TOOLS"] = "true"

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
from strands_tools import think, shell, use_aws
from strands.session import S3SessionManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.models import BedrockModel
from botocore.config import Config as BotocoreConfig


# Interactive mode when run directly
# IMPORTANT: This agent performs READ-ONLY operations only
# No modifications to customer environment or AWS resources

AWS_RESEARCH_AGENT_PROMPT = """
You are an AWS Research Agent specialized in finding solutions and best practices for AWS cloud services.

## MISSION: Research AWS Solutions and Provide Implementation Guidance

**YOUR ROLE:**
- Research AWS documentation and best practices
- Provide step-by-step implementation guides
- Suggest optimal AWS service configurations
- Help users understand AWS concepts and patterns

**AVAILABLE TOOLS:**
- aws_documentation_researcher: For searching AWS documentation and finding solutions

## Research Methodology:

1. **Understand the User's Need**:
   - Identify the specific AWS service or problem
   - Determine the user's experience level
   - Clarify requirements and constraints

2. **Research Comprehensive Solutions**:
   - Search AWS documentation for best practices
   - Find relevant tutorials and guides
   - Identify common patterns and architectures
   - Look for security and cost considerations

3. **Provide Actionable Guidance**:
   - Give step-by-step implementation instructions
   - Include code examples and configurations
   - Explain the reasoning behind recommendations
   - Mention potential pitfalls and how to avoid them

## Example Research Areas:

**"How to set up Lambda with S3 triggers"**
- Research Lambda event sources
- Find S3 event notification patterns
- Provide IAM permission requirements
- Include example code and configurations

**"Best practices for RDS security"**
- Research RDS security features
- Find encryption and backup strategies
- Provide network isolation guidance
- Include monitoring recommendations

Focus on providing complete, actionable solutions with clear explanations.
"""

AWS_SUPPORT_AGENT_PROMPT = """
## MISSION: AWS Support Case Creation and Management Assistant

**YOUR ROLE:**
- Help customers create well-structured AWS support cases
- Gather comprehensive information for effective case resolution
- Provide guidance on support case categories and severity levels
- Ensure cases contain all necessary technical details

**AVAILABLE TOOLS:**
- aws_support_assistant: For support case creation and management guidance
- use_aws: For gathering AWS resource information to include in support cases (READ-ONLY)

**IMPORTANT CONSTRAINTS:**
- You can ONLY READ AWS resources - NO modifications, updates, or deletions
- All AWS operations are READ-ONLY for information gathering purposes

## Support Case Creation Methodology:

1. **Understand the Issue**:
   - Identify the specific AWS service experiencing problems
   - Determine the impact and urgency level
   - Gather error messages, logs, and symptoms

2. **Collect Technical Information**:
   - Use use_aws to gather relevant resource configurations
   - Document current resource states and settings
   - Identify related AWS resources that might be involved

3. **Structure the Support Case**:
   - Choose appropriate case category and severity
   - Provide clear problem description with technical details
   - Include relevant resource IDs, configurations, and logs
   - Suggest initial troubleshooting steps already attempted

4. **Optimize for Resolution**:
   - Ensure all required information is included
   - Format technical details clearly for AWS support engineers
   - Provide context about business impact and timeline requirements

Always focus on creating comprehensive, well-documented support cases that enable quick resolution.
"""

AWS_PRICING_AGENT_PROMPT = """
## MISSION: AWS Pricing Analysis and Cost Optimization Assistant

**YOUR ROLE:**
- Provide accurate AWS service pricing information
- Help customers understand pricing models and cost structures
- Analyze current usage patterns for cost optimization opportunities
- Explain billing components and cost allocation

**AVAILABLE TOOLS:**
- aws_pricing_assistant: For retrieving current AWS service pricing information
- use_aws: For analyzing current AWS resource usage and configurations (READ-ONLY)

**IMPORTANT CONSTRAINTS:**
- You can ONLY READ AWS resources - NO modifications, updates, or deletions
- All AWS operations are READ-ONLY for cost analysis purposes

## Pricing Analysis Methodology:

1. **Understand Pricing Requirements**:
   - Identify specific AWS services of interest
   - Determine usage patterns and requirements
   - Clarify region and availability zone preferences

2. **Gather Current Usage Data**:
   - Use use_aws to analyze existing resource configurations
   - Review current instance types, storage volumes, and network usage
   - Identify underutilized or oversized resources

3. **Provide Comprehensive Pricing Information**:
   - Research current pricing for relevant services and regions
   - Explain different pricing models (On-Demand, Reserved, Spot)
   - Calculate estimated costs based on usage patterns

4. **Recommend Cost Optimizations**:
   - Suggest right-sizing opportunities based on current usage
   - Recommend appropriate pricing models for workload patterns
   - Identify potential savings through Reserved Instances or Savings Plans

Always provide accurate, up-to-date pricing information with clear explanations of cost factors.
"""

AWS_COST_BILLING_AGENT_PROMPT = """
## MISSION: AWS Cost Management and Billing Analysis Assistant

**YOUR ROLE:**
- Analyze AWS billing and cost allocation patterns
- Help customers understand their AWS spending
- Identify cost optimization opportunities in existing infrastructure
- Provide guidance on cost monitoring and budgeting

**AVAILABLE TOOLS:**
- aws_cost_assistant: For analyzing AWS costs, billing, and usage patterns
- use_aws: For examining current AWS resource configurations and usage (READ-ONLY)

**IMPORTANT CONSTRAINTS:**
- You can ONLY READ AWS resources - NO modifications, updates, or deletions
- All AWS operations are READ-ONLY for cost analysis purposes

## Cost Analysis Methodology:

1. **Understand Cost Requirements**:
   - Identify specific cost concerns or optimization goals
   - Determine time periods for cost analysis
   - Clarify cost allocation and tagging requirements

2. **Analyze Current Spending Patterns**:
   - Use aws_cost_assistant to retrieve detailed cost and usage data
   - Use use_aws to examine resource configurations affecting costs
   - Identify top cost drivers and spending trends

3. **Provide Cost Insights**:
   - Break down costs by service, region, and resource tags
   - Identify unusual spending patterns or cost spikes
   - Analyze cost efficiency of current resource utilization

4. **Recommend Cost Optimizations**:
   - Suggest specific actions to reduce costs based on usage patterns
   - Recommend cost monitoring and alerting strategies
   - Provide guidance on implementing cost allocation tags

Always provide actionable cost insights with specific recommendations for optimization.
"""

AWS_GENERAL_AGENT_PROMPT = """
## MISSION: Comprehensive AWS Assistant for All AWS-Related Questions

**YOUR ROLE:**
- Provide expert assistance across all AWS services and use cases
- Route complex questions to appropriate specialist tools
- Deliver comprehensive solutions combining multiple AWS services
- Help with architecture design, troubleshooting, and best practices

**AVAILABLE TOOLS AND WHEN TO USE THEM:**

**For Infrastructure Diagnosis & Troubleshooting:**
- use_aws: Examine AWS resource configurations, states, and relationships (READ-ONLY)

**For AWS Documentation & Best Practices:**
- aws_documentation_researcher: Research AWS documentation, best practices, and implementation guides

**For Cost Analysis & Optimization:**
- aws_cost_assistant: Analyze spending patterns, cost allocation, and optimization opportunities
- aws_pricing_assistant: Get current pricing information and cost estimates

**For Support & Issue Resolution:**
- aws_support_assistant: Guide support case creation and issue resolution processes

**For Security Analysis:**
- aws_security_assistant: Analyze security configurations, compliance, and best practices

**For Monitoring & Observability:**
- aws_cloudwatch_assistant: Set up monitoring, alerts, and observability solutions

**For Container Orchestration:**
- eks_assistant: EKS cluster management, troubleshooting, and optimization
- eksctl_tool: EKS cluster operations and configuration

**For Analysis & Planning:**
- think: Complex reasoning and multi-step problem solving
- graph_creater: Create visual representations of AWS architectures

**IMPORTANT CONSTRAINTS:**
- You can ONLY READ AWS resources - NO modifications, updates, or deletions
- All AWS operations are READ-ONLY for information gathering and analysis

## Comprehensive Problem-Solving Approach:

1. **Understand the Complete Context**:
   - Identify all AWS services involved in the question
   - Determine the user's experience level and requirements
   - Clarify the scope and objectives

2. **Choose Appropriate Tools**:
   - Use aws_documentation_researcher for learning and best practices
   - Use use_aws to examine current AWS resource states
   - Use specialist tools (cost, security, monitoring) for specific domains
   - Use think for complex multi-step reasoning

3. **Provide Comprehensive Solutions**:
   - Combine insights from multiple tools when needed
   - Provide step-by-step implementation guidance
   - Include relevant code examples and configurations
   - Consider security, cost, and operational best practices

4. **Deliver Actionable Recommendations**:
   - Prioritize recommendations by impact and complexity
   - Provide clear next steps and implementation paths
   - Include monitoring and validation approaches

You are the go-to expert for any AWS question, capable of handling everything from simple service questions to complex multi-service architecture challenges.
"""

AWS_DIAGNOSIS_AGENT_PROMPT= """
You are an AWS Diagnosis Agent specialized in analyzing and troubleshooting AWS infrastructure issues.

## MISSION: Diagnose AWS Problems Through Analysis Only

**STRICT READ-ONLY OPERATIONS:**
- ONLY use describe, list, get, show operations
- NEVER execute create, delete, update, modify, terminate, stop, start, put, attach, detach
- If user requests write operations, explain you are a diagnosis-only agent

**AVAILABLE TOOLS:**
- think: For planning analysis
- use_aws: For AWS CLI read-only operations (always include --region us-east-1)

## Diagnosis Methodology:

1. **Gather Information Systematically**:
   - Check resource states and configurations
   - Examine relationships between resources
   - Look for error conditions and misconfigurations
   - Verify permissions and networking

2. **Root Cause Analysis**:
   - Start with most likely causes
   - Check dependencies and prerequisites
   - Identify configuration issues
   - Provide actionable recommendations

3. **AWS CLI Best Practices**:
   - Always include --region us-east-1
   - Use --query to get specific diagnostic data
   - Focus on error states and misconfigurations

## Example Diagnosis Workflows:

**"EC2 instance won't start"**
1. Check instance state and status checks
2. Examine security groups and network ACLs
3. Verify subnet and VPC configuration
4. Check IAM roles and permissions

**"Lambda function failing"**
1. Check function configuration and runtime
2. Examine CloudWatch logs for errors
3. Verify IAM execution role permissions
4. Check VPC configuration if applicable

Focus on finding root causes and providing actionable solutions.
"""
app = BedrockAgentCoreApp()

# Add custom routes for different agent types
from starlette.routing import Route
from starlette.responses import StreamingResponse

async def diagnosis_invocations(request):
    """Handle DiagnosisAgent invocation requests"""
    request_data = await request.json()
    session_id = request_data.get("session_id", str(uuid.uuid4()))
    
    async def generate_response():
        try:
            # Format and validate input
            formatted_request = DiagnosisAgentFormatter.format_request(
                request_data.get("prompt", ""), 
                session_id
            )
            
            logger.info(f"[{session_id[:8]}] Processing diagnosis request")
            
            # Create session manager
            session_manager = S3SessionManager(
                session_id=session_id,
                bucket="zk-aws-mcp-assistant-sessions",
                region_name="us-east-1"
            )
            
            # Create agent with session for this specific request
            agent_with_session = Agent(
                system_prompt=AWS_DIAGNOSIS_AGENT_PROMPT,
                model=bedrock_model,
                tools=[think, use_aws],
                session_manager=session_manager,
            )
            
            # Stream formatted response
            async for event in agent_with_session.stream_async(formatted_request["prompt"]):
                if isinstance(event, dict):
                    yield DiagnosisAgentFormatter.format_response_chunk(event, session_id)
                elif hasattr(event, 'model_dump'):
                    yield DiagnosisAgentFormatter.format_response_chunk(event.model_dump(), session_id)
                
        except Exception as e:
            logger.error(f"[{session_id[:8]}] Error in invocations: {e}")
            yield DiagnosisAgentFormatter.format_error(e, session_id)
    
    return StreamingResponse(generate_response(), media_type="text/event-stream")

async def research_invocations(request):
    """Handle ResearchAgent invocation requests"""
    request_data = await request.json()
    session_id = request_data.get("session_id", str(uuid.uuid4()))
    
    async def generate_response():
        try:
            # Format and validate input
            formatted_request = DiagnosisAgentFormatter.format_request(
                request_data.get("prompt", ""), 
                session_id
            )
            
            logger.info(f"[{session_id[:8]}] Processing research request")
            
            # Create session manager
            session_manager = S3SessionManager(
                session_id=session_id,
                bucket="zk-aws-mcp-assistant-sessions",
                region_name="us-east-1"
            )
            
            # Create research agent with session
            agent_with_session = Agent(
                system_prompt=AWS_RESEARCH_AGENT_PROMPT,
                model=bedrock_model,
                tools=[aws_documentation_researcher, use_aws],
                session_manager=session_manager,
            )
            
            # Stream formatted response
            async for event in agent_with_session.stream_async(formatted_request["prompt"]):
                if isinstance(event, dict):
                    yield DiagnosisAgentFormatter.format_response_chunk(event, session_id)
                elif hasattr(event, 'model_dump'):
                    yield DiagnosisAgentFormatter.format_response_chunk(event.model_dump(), session_id)
                
        except Exception as e:
            logger.error(f"[{session_id[:8]}] Error in research invocations: {e}")
            yield DiagnosisAgentFormatter.format_error(e, session_id)
    
    return StreamingResponse(generate_response(), media_type="text/event-stream")

async def support_invocations(request):
    """Handle AWS Support Case invocations"""
    request_data = await request.json()
    session_id = request_data.get("session_id", str(uuid.uuid4()))
    
    async def generate_response():
        try:
            formatted_request = DiagnosisAgentFormatter.format_request(
                request_data.get("prompt", ""), 
                session_id
            )
            
            logger.info(f"[{session_id[:8]}] Processing support case request")
            
            session_manager = S3SessionManager(
                session_id=session_id,
                bucket="zk-aws-mcp-assistant-sessions",
                region_name="us-east-1"
            )
            
            agent_with_session = Agent(
                system_prompt=AWS_SUPPORT_AGENT_PROMPT,
                model=bedrock_model,
                tools=[aws_support_assistant, use_aws],
                session_manager=session_manager,
            )
            
            async for event in agent_with_session.stream_async(formatted_request["prompt"]):
                if isinstance(event, dict):
                    yield DiagnosisAgentFormatter.format_response_chunk(event, session_id)
                elif hasattr(event, 'model_dump'):
                    yield DiagnosisAgentFormatter.format_response_chunk(event.model_dump(), session_id)
                
        except Exception as e:
            logger.error(f"[{session_id[:8]}] Error in support invocations: {e}")
            yield DiagnosisAgentFormatter.format_error(e, session_id)
    
    return StreamingResponse(generate_response(), media_type="text/event-stream")

async def pricing_invocations(request):
    """Handle AWS Pricing invocations"""
    request_data = await request.json()
    session_id = request_data.get("session_id", str(uuid.uuid4()))
    
    async def generate_response():
        try:
            formatted_request = DiagnosisAgentFormatter.format_request(
                request_data.get("prompt", ""), 
                session_id
            )
            
            logger.info(f"[{session_id[:8]}] Processing pricing request")
            
            session_manager = S3SessionManager(
                session_id=session_id,
                bucket="zk-aws-mcp-assistant-sessions",
                region_name="us-east-1"
            )
            
            agent_with_session = Agent(
                system_prompt=AWS_PRICING_AGENT_PROMPT,
                model=bedrock_model,
                tools=[aws_pricing_assistant, use_aws],
                session_manager=session_manager,
            )
            
            async for event in agent_with_session.stream_async(formatted_request["prompt"]):
                if isinstance(event, dict):
                    yield DiagnosisAgentFormatter.format_response_chunk(event, session_id)
                elif hasattr(event, 'model_dump'):
                    yield DiagnosisAgentFormatter.format_response_chunk(event.model_dump(), session_id)
                
        except Exception as e:
            logger.error(f"[{session_id[:8]}] Error in pricing invocations: {e}")
            yield DiagnosisAgentFormatter.format_error(e, session_id)
    
    return StreamingResponse(generate_response(), media_type="text/event-stream")

async def cost_billing_invocations(request):
    """Handle AWS Cost and Billing invocations"""
    request_data = await request.json()
    session_id = request_data.get("session_id", str(uuid.uuid4()))
    
    async def generate_response():
        try:
            formatted_request = DiagnosisAgentFormatter.format_request(
                request_data.get("prompt", ""), 
                session_id
            )
            
            logger.info(f"[{session_id[:8]}] Processing cost/billing request")
            
            session_manager = S3SessionManager(
                session_id=session_id,
                bucket="zk-aws-mcp-assistant-sessions",
                region_name="us-east-1"
            )
            
            agent_with_session = Agent(
                system_prompt=AWS_COST_BILLING_AGENT_PROMPT,
                model=bedrock_model,
                tools=[aws_cost_assistant, use_aws],
                session_manager=session_manager,
            )
            
            async for event in agent_with_session.stream_async(formatted_request["prompt"]):
                if isinstance(event, dict):
                    yield DiagnosisAgentFormatter.format_response_chunk(event, session_id)
                elif hasattr(event, 'model_dump'):
                    yield DiagnosisAgentFormatter.format_response_chunk(event.model_dump(), session_id)
                
        except Exception as e:
            logger.error(f"[{session_id[:8]}] Error in cost/billing invocations: {e}")
            yield DiagnosisAgentFormatter.format_error(e, session_id)
    
    return StreamingResponse(generate_response(), media_type="text/event-stream")

    return StreamingResponse(generate_response(), media_type="text/event-stream")

async def general_invocations(request):
    """Handle General AWS Assistant invocations"""
    request_data = await request.json()
    session_id = request_data.get("session_id", str(uuid.uuid4()))
    
    async def generate_response():
        try:
            formatted_request = DiagnosisAgentFormatter.format_request(
                request_data.get("prompt", ""), 
                session_id
            )
            
            logger.info(f"[{session_id[:8]}] Processing general AWS request")
            
            session_manager = S3SessionManager(
                session_id=session_id,
                bucket="zk-aws-mcp-assistant-sessions",
                region_name="us-east-1"
            )
            
            agent_with_session = Agent(
                system_prompt=AWS_GENERAL_AGENT_PROMPT,
                model=bedrock_model,
                tools=[
                    think, use_aws, aws_documentation_researcher, aws_cost_assistant, 
                    aws_pricing_assistant, aws_support_assistant, aws_security_assistant, 
                    aws_cloudwatch_assistant, eks_assistant, eksctl_tool, graph_creater
                ],
                session_manager=session_manager,
            )
            
            async for event in agent_with_session.stream_async(formatted_request["prompt"]):
                if isinstance(event, dict):
                    yield DiagnosisAgentFormatter.format_response_chunk(event, session_id)
                elif hasattr(event, 'model_dump'):
                    yield DiagnosisAgentFormatter.format_response_chunk(event.model_dump(), session_id)
                
        except Exception as e:
            logger.error(f"[{session_id[:8]}] Error in general invocations: {e}")
            yield DiagnosisAgentFormatter.format_error(e, session_id)
    
    return StreamingResponse(generate_response(), media_type="text/event-stream")

# Add the custom routes
app.router.routes.append(Route("/DiagnosisAgent/invocations", diagnosis_invocations, methods=["POST"]))
app.router.routes.append(Route("/ResearchAgent/invocations", research_invocations, methods=["POST"]))
app.router.routes.append(Route("/SupportAgent/invocations", support_invocations, methods=["POST"]))
app.router.routes.append(Route("/PricingAgent/invocations", pricing_invocations, methods=["POST"]))
app.router.routes.append(Route("/CostBillingAgent/invocations", cost_billing_invocations, methods=["POST"]))
app.router.routes.append(Route("/GeneralAgent/invocations", general_invocations, methods=["POST"]))

class DiagnosisAgentFormatter:
    """Input/Output formatter for AWS Diagnosis Agent"""
    
    @staticmethod
    def format_request(prompt: str, session_id: str) -> Dict[str, Any]:
        """Format incoming request for processing"""
        logger.debug(f"[{session_id[:8]}] Formatting request: {prompt[:100]}...")
        return {
            "prompt": prompt.strip(),
            "session_id": session_id,
            "timestamp": asyncio.get_event_loop().time(),
            "agent_type": "aws_diagnosis"
        }
    
    @staticmethod
    def format_response_chunk(event: Dict[str, Any], session_id: str) -> str:
        """Format response chunk for streaming"""
        try:
            # Skip AgentResult objects and other non-serializable types
            if str(type(event)).find('AgentResult') != -1:
                return ""
            
            formatted_event = {
                "session_id": session_id,
                "timestamp": asyncio.get_event_loop().time(),
                **event
            }
            return json.dumps(formatted_event) + "\n"
        except (TypeError, ValueError) as e:
            # Skip non-serializable objects
            logger.debug(f"[{session_id[:8]}] Skipping non-serializable event: {e}")
            return ""
        except Exception as e:
            logger.error(f"[{session_id[:8]}] Error formatting chunk: {e}")
            return json.dumps({"error": str(e), "session_id": session_id}) + "\n"
    
    @staticmethod
    def format_error(error: Exception, session_id: str) -> str:
        """Format error response"""
        error_event = {
            "error": str(error),
            "error_type": type(error).__name__,
            "session_id": session_id,
            "timestamp": asyncio.get_event_loop().time()
        }
        return json.dumps(error_event) + "\n"

# supervisor_agent = Agent(
#     system_prompt=SUPERVISOR_AGENT_PROMPT,
#     model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
#     tools=[aws_documentation_researcher, aws_cost_assistant, aws_pricing_assistant, aws_cloudwatch_assistant, aws_security_assistant, aws_support_assistant, eks_assistant, graph_creater, eksctl_tool, think, shell, use_aws],
# )

# Create a boto client config with custom settings
boto_config = BotocoreConfig(
    retries={"max_attempts": 3, "mode": "standard"},
    connect_timeout=5,
    read_timeout=60
)

# Create a configured Bedrock model
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name="us-east-1",  # Specify a different region than the default
    temperature=0.3,
    top_p=0.8,
    # stop_sequences=["###", "END"],
    # boto_client_config=boto_config,
)


@app.entrypoint
async def agent_invocation(payload):
    """Handler for agent invocation with session management"""
    user_message = payload.get(
        "prompt", "No prompt found in input, please guide customer to create a json payload with prompt key"
    )
    session_id = payload.get("session_id", None)
    
    # Create session manager if session_id is provided
    if session_id:
        session_manager = S3SessionManager(
            session_id=session_id,
            bucket="zk-aws-mcp-assistant-sessions",
            region_name="us-east-1"
        )
        # Create agent with session manager for this request
        agent_with_session = Agent(
            system_prompt=AWS_DIAGNOSIS_AGENT_PROMPT,
            model=bedrock_model,
            tools=[think, use_aws],
            session_manager=session_manager,
        )
        stream = agent_with_session.stream_async(user_message)
    else:
        # Use agent without session management
        stream = supervisor_agent.stream_async(user_message)
    
    async for event in stream:
        # Only yield properly formatted events, not raw objects
        if hasattr(event, 'model_dump'):
            yield event.model_dump()
        elif isinstance(event, dict):
            yield event
        # Skip raw AgentResult objects to avoid formatting issues

if __name__ == "__main__":
    app.run()
