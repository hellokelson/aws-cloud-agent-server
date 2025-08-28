"""
# 🌐 AWS Assistant Agent for AgentCore

A multi-agent system specialized in AWS assistance using MCP and AgentCore Runtime.
This version is optimized for deployment to Amazon Bedrock AgentCore with streaming support.

## Features

- Multi-agent architecture with specialized tools
- AgentCore integration with streaming responses
- MCP server integration for AWS services
- Optimized for serverless deployment

## Usage

Local testing:
```bash
python agentcore_main.py
```

Deploy to AgentCore:
```bash
python deploy_agentcore.py
```
"""

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands_tools import think, use_aws
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp

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

# Supervisor agent prompt
SUPERVISOR_AGENT_PROMPT = """
You are an AWS Assistant with access to specialized agents and tools. Your role is to intelligently analyze queries and select the most appropriate tool based on the specific problem, not follow a rigid hierarchy.

## Core Thinking Principles:

1. **Analysis-First Approach**: Understand what the query is actually asking for before selecting tools
2. **Problem-Solution Matching**: Match the specific problem type to the tool that can best solve it
3. **Efficiency Over Hierarchy**: Choose the most direct path to the answer, not the "most specialized" tool
4. **Logical Tool Progression**: If multiple tools are needed, use them in logical order with clear reasoning

## Decision-Making Framework:

1. **Analyze the Query Type**: 
   - Resource inventory/listing (how many, what do I have, list my...)
   - Performance metrics/monitoring (CPU usage, error rates, trends...)
   - Cost/billing information (how much am I spending, cost analysis...)
   - Configuration/security analysis (settings, permissions, compliance...)
   - Documentation/learning (what is, how does, explain...)

2. **Match Problem to Tool Capability**:
   - Don't force a specialist tool if it can't solve the specific problem
   - Use the most direct tool that can provide the answer
   - Consider if the query needs multiple tools working together

3. **Execute with Clear Reasoning**:
   - Explain why you chose each tool
   - If a tool fails, explain why and choose the next logical option
   - Give up gracefully if no tool can solve the problem after 2-3 attempts

Execute operations directly when they are read-only and safe. Always explain your tool selection reasoning.
"""

# Initialize AgentCore app
app = BedrockAgentCoreApp()

# Create conversation manager with sliding window
conversation_manager = SlidingWindowConversationManager(
    window_size=30,  # Keep last 30 messages for context
    should_truncate_results=True
)

# Initialize Bedrock model
bedrock_model = BedrockModel(model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0")

# Create supervisor agent
supervisor_agent = Agent(
    model=bedrock_model,
    system_prompt=SUPERVISOR_AGENT_PROMPT,
    conversation_manager=conversation_manager,
    tools=[
        aws_documentation_researcher, 
        aws_cost_assistant, 
        aws_pricing_assistant, 
        aws_cloudwatch_assistant, 
        aws_security_assistant, 
        aws_support_assistant, 
        eks_assistant, 
        graph_creater, 
        eksctl_tool, 
        think, 
        use_aws
    ],
)

@app.entrypoint
async def agent_invocation(payload, context=None):
    """Handler for agent invocation with streaming support"""
    user_message = payload.get(
        "prompt", "No prompt found in input, please provide a prompt key in your JSON payload"
    )
    
    # Log context for debugging
    if context:
        print("AgentCore Context:", context)
    
    # Use streaming response
    stream = supervisor_agent.stream_async(user_message)
    async for event in stream:
        print(f"Streaming event: {event}")
        yield event

if __name__ == "__main__":
    app.run()
