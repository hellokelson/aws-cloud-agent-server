# AWS Cloud Agent Server

A comprehensive multi-agent system for AWS infrastructure management, troubleshooting, and optimization using Strands AI framework and Model Context Protocol (MCP) servers.

## 🏗️ Architecture Overview

### Multi-Agent System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Portal (Port 3000)                  │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────────────┐ │
│  │General  │Diagnosis│Research │Support  │Pricing│Cost&Bill│ │
│  └─────────┴─────────┴─────────┴─────────┴─────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/CORS Requests
┌─────────────────────────▼───────────────────────────────────┐
│              Agent Core Server (Port 8080)                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │            Specialized Agent Endpoints                  │ │
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

## 🤖 Specialized AI Agents

### **General Agent** - Comprehensive AWS Assistant
- **Purpose**: All-in-one AWS expert for any question or task
- **Tools**: Complete toolkit including documentation, cost analysis, security, monitoring
- **Use Cases**: Architecture design, multi-service solutions, complex troubleshooting

### **Diagnosis Agent** - Infrastructure Troubleshooting
- **Purpose**: Analyze and diagnose AWS infrastructure issues
- **Tools**: `think`, `use_aws` (read-only analysis)
- **Use Cases**: Performance problems, connectivity issues, configuration analysis

### **Research Agent** - Documentation & Best Practices
- **Purpose**: Research AWS solutions and implementation guidance
- **Tools**: `aws_documentation_researcher`, `use_aws`
- **Use Cases**: Learning new services, finding best practices, implementation guides

### **Support Agent** - AWS Support Case Management
- **Purpose**: Help create well-structured AWS support cases
- **Tools**: `aws_support_assistant`, `use_aws`
- **Use Cases**: Support case creation, issue documentation, escalation guidance

### **Pricing Agent** - Cost Analysis & Optimization
- **Purpose**: AWS service pricing information and cost optimization
- **Tools**: `aws_pricing_assistant`, `use_aws`
- **Use Cases**: Cost estimates, pricing comparisons, optimization recommendations

### **Cost & Billing Agent** - Financial Management
- **Purpose**: Analyze AWS spending and billing patterns
- **Tools**: `aws_cost_assistant`, `use_aws`
- **Use Cases**: Bill analysis, cost allocation, spending optimization

## 🛠️ Key Features

### **Multi-Agent Architecture**
- **Specialized Expertise**: Each agent optimized for specific AWS domains
- **Tool Selection**: Intelligent routing to appropriate tools based on query context
- **Session Isolation**: Independent conversation sessions per agent type
- **Cross-Agent Switching**: Seamless switching between agent types in web UI

### **Real-Time Streaming**
- **Server-Sent Events**: Live response streaming for immediate feedback
- **Multiple Format Support**: Handles various response formats from Strands framework
- **Progress Indicators**: Visual feedback during response generation

### **Robust AWS Integration**
- **Read-Only Safety**: All AWS operations are strictly read-only for security
- **Comprehensive Coverage**: Support for 50+ AWS services through specialized tools
- **Session Persistence**: S3-based conversation history storage
- **Error Resilience**: Adaptive retry logic for AWS service connectivity

### **Professional Web Interface**
- **Multi-Tab Design**: Separate tabs for each agent type
- **Session Management**: Create, switch, and manage conversation sessions
- **Health Monitoring**: Real-time agent core connection status
- **Responsive Design**: Works on desktop and mobile devices

### **Enterprise-Ready**
- **CORS Support**: Proper cross-origin resource sharing configuration
- **Modular Architecture**: Clean separation of concerns for maintainability
- **Configuration Management**: Centralized configuration for different environments
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## 📁 Project Structure

```
aws-cloud-agent-server/
├── server/                     # Main server package
│   ├── main.py                # FastAPI server & agent orchestration
│   ├── restart.sh             # Server restart script
│   ├── agent/                 # Agent configuration & components
│   │   ├── config.py         # Configuration constants
│   │   ├── prompts.py        # Specialized agent system prompts
│   │   └── formatters.py     # Response formatting utilities
│   ├── tools/                # AWS tools & assistants
│   │   ├── aws_cost_assistant.py
│   │   ├── aws_pricing_assistant.py
│   │   ├── aws_support_assistant.py
│   │   ├── aws_security_assistant.py
│   │   ├── aws_cloudwatch_assistant.py
│   │   ├── aws_documentation_researcher.py
│   │   ├── eks_assistant.py
│   │   ├── eksctl_tool.py
│   │   └── graph_creater.py
│   └── deploy/               # Deployment scripts
│       └── deploy_agentcore.py
├── web/                      # Web portal
│   ├── app.py               # Flask web server
│   ├── start.sh             # Web server start script
│   └── templates/
│       └── index.html       # Multi-agent web interface
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🚀 Quick Start

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

# Set environment variables (optional - defaults provided)
export AWS_REGION=us-east-1
export STRANDS_AUTO_APPROVE_TOOLS=true
```

### Running the System

#### Start Agent Core Server (Port 8080)
```bash
cd server
./restart.sh
```

#### Start Web Portal (Port 3000)
```bash
cd web
./start.sh
```

#### Access the Application
- **Web Interface**: http://localhost:3000
- **Agent API**: http://localhost:8080
- **Health Check**: http://localhost:8080/health

## 🔧 Configuration

### Server Configuration (`server/agent/config.py`)
```python
# AWS Configuration
AWS_REGION = "us-east-1"

# Model Configuration
BEDROCK_MODEL_ID = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
MODEL_TEMPERATURE = 0.3

# S3 Configuration
S3_SESSION_BUCKET = "your-session-bucket"

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080
```

### Web Configuration (Embedded in `web/templates/index.html`)
```javascript
const WEB_CONFIG = {
    WEB_PORT: 3000,
    AGENT_SERVER_HOST: 'localhost',
    AGENT_SERVER_PORT: 8080
};
```

## 🔒 Security & Safety

### Read-Only Operations
- **Strict Policy**: All AWS operations are read-only for safety
- **No Modifications**: Agents cannot create, update, or delete AWS resources
- **Analysis Focus**: Emphasis on analysis, diagnosis, and recommendations

### Security Measures
- **IAM Permissions**: Uses existing AWS credentials with limited permissions
- **Session Isolation**: Each conversation maintains separate session state
- **Input Validation**: Basic input sanitization and validation
- **CORS Protection**: Proper cross-origin resource sharing configuration

### Recommended Security Practices
- Use IAM roles with minimal required permissions
- Implement request rate limiting in production
- Add audit logging for all AWS API calls
- Monitor for unusual access patterns
- Run in isolated environments for production use

## 🎯 Use Cases

### **Infrastructure Troubleshooting**
- Diagnose connectivity issues between VPCs
- Analyze performance bottlenecks in EC2 instances
- Investigate security group and NACL configurations
- Review load balancer health check failures

### **Cost Optimization**
- Analyze monthly AWS bills for cost drivers
- Identify underutilized resources for right-sizing
- Compare pricing options for Reserved Instances
- Evaluate Savings Plans opportunities

### **Architecture Design**
- Research best practices for multi-tier applications
- Design secure, scalable AWS architectures
- Plan disaster recovery strategies
- Evaluate service alternatives and trade-offs

### **Support & Documentation**
- Create detailed AWS support cases
- Find implementation guides for new services
- Research compliance and security requirements
- Get step-by-step deployment instructions

## 🔮 Future Enhancements

### **Enhanced Agent Orchestration**
- Multi-agent workflows for complex tasks
- Agent handoffs and collaboration
- Parallel processing capabilities
- Decision trees for smart routing

### **Advanced Features**
- Multi-cloud support (Azure, GCP)
- Custom integrations and plugins
- Workflow automation from conversations
- Organization-specific knowledge bases

### **Enterprise Integration**
- SSO authentication and authorization
- Role-based access control
- API key management
- Comprehensive audit trails

## 📊 Monitoring & Observability

### **Built-in Monitoring**
- Real-time health status indicators
- Agent performance metrics
- Session management and analytics
- Error tracking and alerting

### **Logging**
- Structured logging for all operations
- Request tracing through agent pipeline
- Performance monitoring and optimization
- Usage analytics and patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all agents maintain READ-ONLY constraints
5. Update documentation
6. Submit a pull request

## 📄 License

[Specify your license here]

---

**⚠️ Important**: This system provides READ-ONLY access to AWS resources. Always verify agent recommendations before implementing changes in production environments.

**🔗 Quick Links**:
- Web Interface: http://localhost:3000
- API Documentation: http://localhost:8080/health
- AWS Pricing Calculator: https://calculator.aws
