# AWS Cloud Agent Server

A comprehensive multi-agent system for AWS infrastructure management, troubleshooting, and optimization using Strands AI framework and Model Context Protocol (MCP) servers.

## Purpose

This project provides specialized AI agents for different aspects of AWS cloud management:

- **Diagnosis Agent**: Infrastructure troubleshooting and problem analysis
- **Research Agent**: AWS documentation research and best practices
- **Support Agent**: AWS support case creation and management
- **Pricing Agent**: Cost analysis and pricing optimization
- **Cost & Billing Agent**: Billing analysis and cost management
- **General Agent**: Comprehensive AWS assistant combining all capabilities

Each agent is designed with **READ-ONLY** access to AWS resources, ensuring safe operations while providing detailed analysis and recommendations.

## Architecture Design

### Multi-Agent Orchestration with Strands

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Portal UI                            │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────────────┐ │
│  │General  │Diagnosis│Research │Support  │Pricing│Cost&Bill│ │
│  └─────────┴─────────┴─────────┴─────────┴─────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/SSE Streaming
┌─────────────────────────▼───────────────────────────────────┐
│                FastAPI Server                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            Agent Router & Session Manager               │ │
│  │  /GeneralAgent/invocations                             │ │
│  │  /DiagnosisAgent/invocations                           │ │
│  │  /ResearchAgent/invocations                            │ │
│  │  /SupportAgent/invocations                             │ │
│  │  /PricingAgent/invocations                             │ │
│  │  /CostBillingAgent/invocations                         │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                 Strands Agent Framework                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Agent(system_prompt, model, tools, session_manager)   │ │
│  │  ├─ Claude 3.5 Sonnet (Bedrock)                       │ │
│  │  ├─ Specialized System Prompts                         │ │
│  │  ├─ Tool Selection & Orchestration                     │ │
│  │  └─ S3 Session Management                              │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Tool Ecosystem                           │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │   Core      │    MCP      │   AWS       │  Analysis   │  │
│  │   Tools     │   Servers   │   Tools     │   Tools     │  │
│  │             │             │             │             │  │
│  │ • think     │ • aws-doc   │ • use_aws   │ • graph     │  │
│  │ • shell     │ • knowledge │ • cost      │ • eksctl    │  │
│  │             │   -mcp      │ • pricing   │             │  │
│  │             │             │ • support   │             │  │
│  │             │             │ • security  │             │  │
│  │             │             │ • cloudwatch│             │  │
│  │             │             │ • eks       │             │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Agent Orchestration Strategy

1. **Specialized Agents**: Each agent has a specific domain expertise with tailored system prompts
2. **Tool Selection**: Agents intelligently choose appropriate tools based on query context
3. **Session Isolation**: Each agent type maintains separate conversation sessions
4. **Streaming Responses**: Real-time response streaming for better user experience
5. **READ-ONLY Operations**: All AWS operations are strictly read-only for safety

### Project Structure

```
aws-cloud-agent-server/
├── main.py                     # FastAPI server & agent orchestration
├── tools/                      # Specialized tool implementations
│   ├── aws_cost_assistant.py
│   ├── aws_pricing_assistant.py
│   ├── aws_support_assistant.py
│   ├── aws_security_assistant.py
│   ├── aws_cloudwatch_assistant.py
│   ├── aws_documentation_researcher.py
│   ├── eks_assistant.py
│   ├── eksctl_tool.py
│   └── graph_creater.py
├── web/
│   └── templates/
│       └── index.html          # Multi-tab web interface
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## How to Run

### Prerequisites

```bash
# Install Python 3.11+
# Install AWS CLI and configure credentials
aws configure

# Install uv for Python package management
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup & Installation

```bash
# Clone the repository
git clone <repository-url>
cd aws-cloud-agent-server

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Set environment variables
export AWS_DEFAULT_REGION=us-east-1
export AWS_REGION=us-east-1
export STRANDS_AUTO_APPROVE_TOOLS=true
```

### Running the Server

```bash
# Start the FastAPI server
python main.py

# Access the web interface
open http://localhost:8000
```

### Using the API

```bash
# Direct agent invocation
curl -X POST http://localhost:8000/GeneralAgent/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are my running EC2 instances?", "session_id": "test-session"}'
```

## How to Extend Agents

### Adding a New Specialized Agent

1. **Create Agent Prompt**:
```python
# In main.py
NEW_AGENT_PROMPT = """
## MISSION: Your Agent's Purpose

**YOUR ROLE:**
- Define the agent's responsibilities
- Specify the domain expertise

**AVAILABLE TOOLS:**
- tool_name: Description of when to use this tool
- use_aws: For AWS resource information (READ-ONLY)

**IMPORTANT CONSTRAINTS:**
- You can ONLY READ AWS resources - NO modifications
"""
```

2. **Create Agent Invocation**:
```python
async def new_agent_invocations(request):
    # Follow the pattern from existing agents
    agent_with_session = Agent(
        system_prompt=NEW_AGENT_PROMPT,
        model=bedrock_model,
        tools=[specialized_tool, use_aws],
        session_manager=session_manager,
    )
```

3. **Add Route**:
```python
app.router.routes.append(Route("/NewAgent/invocations", new_agent_invocations, methods=["POST"]))
```

4. **Update Web Interface**:
```html
<!-- Add tab in index.html -->
<button class="tab" onclick="switchTab('NewAgent')">New Agent</button>
<div id="NewAgent" class="tab-content">...</div>
```

### Creating Custom Tools

```python
# In tools/custom_tool.py
from strands import tool

@tool
def custom_aws_tool(query: str) -> str:
    """
    Description of what this tool does.
    
    Args:
        query: Input parameter description
        
    Returns:
        Response description
    """
    # Implement tool logic
    return result
```

## Security Considerations & Risks

### Current Security Measures

- **READ-ONLY Operations**: All AWS operations are strictly read-only
- **IAM Permissions**: Agents use existing AWS credentials with limited permissions
- **Session Isolation**: Each conversation maintains separate session state
- **Input Validation**: Basic input sanitization and validation

### Security Risks

1. **Credential Exposure**: AWS credentials are inherited from environment
2. **Information Disclosure**: Agents may expose sensitive AWS resource information
3. **Prompt Injection**: Malicious prompts could potentially manipulate agent behavior
4. **Resource Enumeration**: Agents can discover and list AWS resources
5. **Cost Impact**: Extensive AWS API calls may incur costs

### Recommended Mitigations

- Use IAM roles with minimal required permissions
- Implement request rate limiting
- Add audit logging for all AWS API calls
- Sanitize and validate all user inputs
- Consider running in isolated environments
- Monitor for unusual access patterns

## Future Roadmap

### Enhanced Agent Orchestration

- **Multi-Agent Workflows**: Coordinate multiple agents for complex tasks
- **Agent Handoffs**: Seamless transfer between specialized agents
- **Parallel Processing**: Concurrent agent execution for faster responses
- **Decision Trees**: Smart routing based on query classification

### Authentication & Authorization

- **MCP Server Auth**: Secure authentication between agents and MCP servers
- **Role-Based Access**: Different permission levels for different users
- **API Key Management**: Secure handling of external service credentials
- **Audit Trails**: Comprehensive logging of all agent interactions

### Observability & Monitoring

- **Agent Performance Metrics**: Response times, success rates, tool usage
- **Conversation Analytics**: User interaction patterns and satisfaction
- **Error Tracking**: Detailed error logging and alerting
- **Cost Monitoring**: Track AWS API usage and associated costs

### Feedback & Improvement Loop

- **Response Quality Scoring**: User feedback on agent responses
- **Conversation Mining**: Extract insights from successful interactions
- **Prompt Optimization**: Iterative improvement of system prompts
- **Tool Effectiveness**: Analyze which tools provide the most value

### Advanced Features

- **Multi-Cloud Support**: Extend beyond AWS to Azure, GCP
- **Custom Integrations**: Plugin system for organization-specific tools
- **Workflow Automation**: Convert conversations into executable workflows
- **Knowledge Base**: Build organization-specific knowledge from interactions

## Agent Core Integration

This project leverages AWS Bedrock Agent Core for:

- **Model Management**: Centralized LLM model configuration
- **Session Persistence**: S3-based conversation history storage
- **Streaming Responses**: Real-time response delivery
- **Error Handling**: Robust error management and recovery

### Observability Features

- **Request Tracing**: Track requests through the agent pipeline
- **Performance Monitoring**: Monitor response times and resource usage
- **Usage Analytics**: Understand agent utilization patterns
- **Quality Metrics**: Measure response accuracy and user satisfaction

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all agents maintain READ-ONLY constraints
5. Update documentation
6. Submit a pull request

## License

[Specify your license here]

---

**⚠️ Important**: This system provides READ-ONLY access to AWS resources. Always verify agent recommendations before implementing changes in production environments.
