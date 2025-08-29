#!/usr/bin/env python3
"""
AWS Cloud Agent Server - Multi-Agent System for AWS Infrastructure Management

A comprehensive multi-agent system for AWS infrastructure management, troubleshooting, 
and optimization using Strands AI framework and Model Context Protocol (MCP) servers.
"""

import os
import uuid
import logging
from pathlib import Path

# Import configuration
from agent.config import (
    AWS_REGION, BEDROCK_MODEL_ID, MODEL_TEMPERATURE,
    S3_SESSION_BUCKET, SERVER_HOST, SERVER_PORT, STRANDS_AUTO_APPROVE_TOOLS
)

# Import prompts
from agent.prompts import (
    AWS_DIAGNOSIS_AGENT_PROMPT, AWS_RESEARCH_AGENT_PROMPT, AWS_SUPPORT_AGENT_PROMPT,
    AWS_PRICING_AGENT_PROMPT, AWS_COST_BILLING_AGENT_PROMPT, AWS_GENERAL_AGENT_PROMPT
)

# Import formatters
from agent.formatters import AgentFormatter

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set AWS environment variables
os.environ["AWS_REGION"] = AWS_REGION
os.environ["STRANDS_AUTO_APPROVE_TOOLS"] = STRANDS_AUTO_APPROVE_TOOLS

# Import tools
from tools.aws_cloudwatch_assistant import aws_cloudwatch_assistant
from tools.aws_cost_assistant import aws_cost_assistant
from tools.aws_documentation_researcher import aws_documentation_researcher
from tools.aws_pricing_assistant import aws_pricing_assistant
from tools.aws_security_assistant import aws_security_assistant
from tools.aws_support_assistant import aws_support_assistant
from tools.eks_assistant import eks_assistant
from tools.eksctl_tool import eksctl_tool
from tools.graph_creater import graph_creater

# Import Strands framework
from strands import Agent
from strands_tools import think, shell, use_aws
from strands.session import S3SessionManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.models import BedrockModel
from botocore.config import Config as BotocoreConfig

# Import Starlette components
from starlette.routing import Route
from starlette.responses import StreamingResponse, JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware


def create_bedrock_model():
    """Create and configure Bedrock model"""
    boto_config = BotocoreConfig(
        retries={"max_attempts": 5, "mode": "adaptive"},
        connect_timeout=30,
        read_timeout=300,
        max_pool_connections=50
    )
    
    return BedrockModel(
        model_id=BEDROCK_MODEL_ID,
        region_name=AWS_REGION,
        temperature=MODEL_TEMPERATURE,
        config=boto_config
    )


def create_session_manager(session_id: str):
    """Create S3 session manager"""
    return S3SessionManager(
        session_id=session_id,
        bucket=S3_SESSION_BUCKET,
        region_name=AWS_REGION
    )


# Initialize Bedrock model
bedrock_model = create_bedrock_model()

# Initialize BedrockAgentCoreApp
app = BedrockAgentCoreApp()


# Agent invocation handlers
async def diagnosis_invocations(request):
    """Handle DiagnosisAgent invocation requests"""
    request_data = await request.json()
    session_id = request_data.get("session_id", str(uuid.uuid4()))
    
    async def generate_response():
        try:
            formatted_request = AgentFormatter.format_request(
                request_data.get("prompt", ""), 
                session_id
            )
            
            logger.info(f"[{session_id[:8]}] Processing diagnosis request")
            
            session_manager = create_session_manager(session_id)
            
            agent_with_session = Agent(
                system_prompt=AWS_DIAGNOSIS_AGENT_PROMPT,
                model=bedrock_model,
                tools=[think, use_aws],
                session_manager=session_manager,
            )
            
            async for event in agent_with_session.stream_async(formatted_request["prompt"]):
                if isinstance(event, dict):
                    yield AgentFormatter.format_response_chunk(event, session_id)
                elif hasattr(event, 'model_dump'):
                    yield AgentFormatter.format_response_chunk(event.model_dump(), session_id)
                
        except Exception as e:
            logger.error(f"[{session_id[:8]}] Error in invocations: {e}")
            yield AgentFormatter.format_error(e, session_id)
    
    response = StreamingResponse(generate_response(), media_type="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


async def research_invocations(request):
    """Handle ResearchAgent invocation requests"""
    request_data = await request.json()
    session_id = request_data.get("session_id", str(uuid.uuid4()))
    
    async def generate_response():
        try:
            formatted_request = AgentFormatter.format_request(
                request_data.get("prompt", ""), 
                session_id
            )
            
            logger.info(f"[{session_id[:8]}] Processing research request")
            
            session_manager = create_session_manager(session_id)
            
            agent_with_session = Agent(
                system_prompt=AWS_RESEARCH_AGENT_PROMPT,
                model=bedrock_model,
                tools=[aws_documentation_researcher, use_aws],
                session_manager=session_manager,
            )
            
            async for event in agent_with_session.stream_async(formatted_request["prompt"]):
                if isinstance(event, dict):
                    yield AgentFormatter.format_response_chunk(event, session_id)
                elif hasattr(event, 'model_dump'):
                    yield AgentFormatter.format_response_chunk(event.model_dump(), session_id)
                
        except Exception as e:
            logger.error(f"[{session_id[:8]}] Error in research invocations: {e}")
            yield AgentFormatter.format_error(e, session_id)
    
    response = StreamingResponse(generate_response(), media_type="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


async def support_invocations(request):
    """Handle AWS Support Case invocations"""
    request_data = await request.json()
    session_id = request_data.get("session_id", str(uuid.uuid4()))
    
    async def generate_response():
        try:
            formatted_request = AgentFormatter.format_request(
                request_data.get("prompt", ""), 
                session_id
            )
            
            logger.info(f"[{session_id[:8]}] Processing support request")
            
            session_manager = create_session_manager(session_id)
            
            agent_with_session = Agent(
                system_prompt=AWS_SUPPORT_AGENT_PROMPT,
                model=bedrock_model,
                tools=[aws_support_assistant, use_aws],
                session_manager=session_manager,
            )
            
            async for event in agent_with_session.stream_async(formatted_request["prompt"]):
                if isinstance(event, dict):
                    yield AgentFormatter.format_response_chunk(event, session_id)
                elif hasattr(event, 'model_dump'):
                    yield AgentFormatter.format_response_chunk(event.model_dump(), session_id)
                
        except Exception as e:
            logger.error(f"[{session_id[:8]}] Error in support invocations: {e}")
            yield AgentFormatter.format_error(e, session_id)
    
    response = StreamingResponse(generate_response(), media_type="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


async def pricing_invocations(request):
    """Handle AWS Pricing invocations"""
    request_data = await request.json()
    session_id = request_data.get("session_id", str(uuid.uuid4()))
    
    async def generate_response():
        try:
            formatted_request = AgentFormatter.format_request(
                request_data.get("prompt", ""), 
                session_id
            )
            
            logger.info(f"[{session_id[:8]}] Processing pricing request")
            
            session_manager = create_session_manager(session_id)
            
            agent_with_session = Agent(
                system_prompt=AWS_PRICING_AGENT_PROMPT,
                model=bedrock_model,
                tools=[aws_pricing_assistant, use_aws],
                session_manager=session_manager,
            )
            
            async for event in agent_with_session.stream_async(formatted_request["prompt"]):
                if isinstance(event, dict):
                    yield AgentFormatter.format_response_chunk(event, session_id)
                elif hasattr(event, 'model_dump'):
                    yield AgentFormatter.format_response_chunk(event.model_dump(), session_id)
                
        except Exception as e:
            logger.error(f"[{session_id[:8]}] Error in pricing invocations: {e}")
            yield AgentFormatter.format_error(e, session_id)
    
    response = StreamingResponse(generate_response(), media_type="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


async def cost_billing_invocations(request):
    """Handle AWS Cost and Billing invocations"""
    request_data = await request.json()
    session_id = request_data.get("session_id", str(uuid.uuid4()))
    
    async def generate_response():
        try:
            formatted_request = AgentFormatter.format_request(
                request_data.get("prompt", ""), 
                session_id
            )
            
            logger.info(f"[{session_id[:8]}] Processing cost/billing request")
            
            session_manager = create_session_manager(session_id)
            
            agent_with_session = Agent(
                system_prompt=AWS_COST_BILLING_AGENT_PROMPT,
                model=bedrock_model,
                tools=[aws_cost_assistant, use_aws],
                session_manager=session_manager,
            )
            
            async for event in agent_with_session.stream_async(formatted_request["prompt"]):
                if isinstance(event, dict):
                    yield AgentFormatter.format_response_chunk(event, session_id)
                elif hasattr(event, 'model_dump'):
                    yield AgentFormatter.format_response_chunk(event.model_dump(), session_id)
                
        except Exception as e:
            logger.error(f"[{session_id[:8]}] Error in cost/billing invocations: {e}")
            yield AgentFormatter.format_error(e, session_id)
    
    response = StreamingResponse(generate_response(), media_type="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


async def general_invocations(request):
    """Handle General AWS Assistant invocations"""
    request_data = await request.json()
    session_id = request_data.get("session_id", str(uuid.uuid4()))
    
    async def generate_response():
        try:
            formatted_request = AgentFormatter.format_request(
                request_data.get("prompt", ""), 
                session_id
            )
            
            logger.info(f"[{session_id[:8]}] Processing general AWS request")
            
            session_manager = create_session_manager(session_id)
            
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
                    yield AgentFormatter.format_response_chunk(event, session_id)
                elif hasattr(event, 'model_dump'):
                    yield AgentFormatter.format_response_chunk(event.model_dump(), session_id)
                
        except Exception as e:
            error_msg = str(e)
            if "Connection was closed" in error_msg or "endpoint URL" in error_msg:
                error_msg = "Bedrock service connection issue. Please try again in a moment."
            logger.error(f"[{session_id[:8]}] Error in general invocations: {e}")
            yield AgentFormatter.format_error(Exception(error_msg), session_id)
    
    response = StreamingResponse(generate_response(), media_type="text/event-stream")
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


async def options_handler(request):
    """Handle CORS preflight OPTIONS requests"""
    response = JSONResponse({})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "86400"
    return response


async def health_check(request):
    """Health check endpoint"""
    response = JSONResponse({"status": "healthy"})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


# Register routes
app.router.routes.append(Route("/DiagnosisAgent/invocations", diagnosis_invocations, methods=["POST"]))
app.router.routes.append(Route("/DiagnosisAgent/invocations", options_handler, methods=["OPTIONS"]))
app.router.routes.append(Route("/ResearchAgent/invocations", research_invocations, methods=["POST"]))
app.router.routes.append(Route("/ResearchAgent/invocations", options_handler, methods=["OPTIONS"]))
app.router.routes.append(Route("/SupportAgent/invocations", support_invocations, methods=["POST"]))
app.router.routes.append(Route("/SupportAgent/invocations", options_handler, methods=["OPTIONS"]))
app.router.routes.append(Route("/PricingAgent/invocations", pricing_invocations, methods=["POST"]))
app.router.routes.append(Route("/PricingAgent/invocations", options_handler, methods=["OPTIONS"]))
app.router.routes.append(Route("/CostBillingAgent/invocations", cost_billing_invocations, methods=["POST"]))
app.router.routes.append(Route("/CostBillingAgent/invocations", options_handler, methods=["OPTIONS"]))
app.router.routes.append(Route("/GeneralAgent/invocations", general_invocations, methods=["POST"]))
app.router.routes.append(Route("/GeneralAgent/invocations", options_handler, methods=["OPTIONS"]))
app.router.routes.append(Route("/health", health_check, methods=["GET"]))

# Debug: Print all registered routes
print("Registered routes:")
for route in app.router.routes:
    print(f"  {route.path} - {route.methods}")


# Interactive mode when run directly
if __name__ == "__main__":
    print("Starting AWS Cloud Agent Server...")
    print(f"Server will be available at http://localhost:{SERVER_PORT}")
    
    # Run the web server
    app.run(host=SERVER_HOST, port=SERVER_PORT)
