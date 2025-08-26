# AWS Multi-Agent Infrastructure Management System

A sophisticated multi-agent system built with the **agents-as-tools pattern** for AWS infrastructure management and network troubleshooting. The system intelligently routes customer requests to specialized agents for AWS resource information retrieval and network connectivity diagnostics.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Agent                       │
│              (Intelligent Request Router)                   │
└─────────────────┬───────────────────────┬───────────────────┘
                  │                       │
         ┌────────▼────────┐     ┌────────▼────────────────┐
         │ AWS Resource    │     │ Network Troubleshoot    │
         │ Agent (Tool)    │     │ Agent (Tool)           │
         └─────────────────┘     └─────────────────────────┘
```

### Core Components

- **Orchestrator Agent**: Main router that analyzes requests and routes them to appropriate tools
- **AWS Resource Agent**: Retrieves AWS service information (EC2, S3, EFS, Load Balancers, etc.)
- **Network Troubleshoot Agent**: Diagnoses connectivity issues and provides solutions
- **Extensible Design**: Easy to add new agents as tools

## 🚀 Features

### AWS Resource Management (Open & Flexible)
The system now supports **any AWS service** with intelligent service detection:

#### **Compute Services**
- **EC2 Instances**: Complete instance management with intelligent filtering
- **Lambda Functions**: Serverless function information and statistics

#### **Networking Services**  
- **VPC**: Virtual Private Cloud information and configurations
- **Subnets**: Subnet details across availability zones
- **Security Groups**: Firewall rules and security analysis
- **Load Balancers**: ALB, NLB, and Classic ELB management
- **NAT Gateways**: Network address translation resources
- **Internet Gateways**: Internet connectivity resources
- **Route Tables**: Network routing configurations

#### **Storage Services**
- **S3 Buckets**: Object storage bucket information
- **EBS Volumes**: Block storage volume details
- **EFS Filesystems**: Elastic file system information  
- **Snapshots**: EBS snapshot management

#### **Database Services**
- **RDS Instances**: Relational database information

#### **Smart Query Features**
- **Dynamic Service Detection**: Automatically detects which AWS service you're asking about
- **Flexible Filtering**: Filter by state, type, or any resource attribute
- **Count Queries**: "How many [service] do I have?"
- **Breakdown Queries**: "Show the count of each instance type"
- **Natural Language**: Ask questions naturally without rigid syntax

### Network Troubleshooting
- **EC2 Connectivity**: Diagnose instance connectivity issues
- **Load Balancer Issues**: Troubleshoot ALB/NLB connection problems
- **Storage Connectivity**: EFS mount and S3 access diagnostics
- **DNS Resolution**: DNS lookup and resolution testing
- **Port Connectivity**: Test specific port accessibility
- **Security Analysis**: Security group rule analysis

### 🧠 Enhanced Open Discussion Agent
- **Universal Question Handling**: Can answer ANY question, not just AWS-specific
- **AWS Best Practices**: Security, cost optimization, architecture guidance
- **Cloud Architecture**: Infrastructure design and planning advice
- **DevOps & Automation**: CI/CD, Infrastructure as Code, deployment strategies
- **Troubleshooting Guidance**: Step-by-step problem resolution help
- **Programming Assistance**: Scripting, automation, and development support
- **General Knowledge**: Technology concepts, processes, explanations
- **Intelligent Fallback**: Automatically used when specialized agents can't help
- **Response Validation**: Checks if specialized responses are relevant to user questions
- **Learning System**: Improves routing decisions based on success/failure patterns
- **Context Awareness**: Maintains conversation context for better responses

### System Features
- **Intelligent Routing**: Advanced keyword-based intent analysis with confidence scoring
- **Smart Fallback Logic**: Automatic routing to General LLM when specialized agents fail
- **Response Validation**: Validates relevance of specialized agent responses
- **Learning & Feedback**: Continuously improves routing decisions
- **Interactive CLI**: User-friendly command-line interface
- **JSON API Ready**: Structured responses for API integration
- **Robust Error Handling**: Graceful fallbacks and error recovery
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## 📋 Prerequisites

- **Python 3.7+**
- **AWS CLI configured** with appropriate credentials
- **AWS IAM permissions** for the services you want to query
- **Network connectivity** for troubleshooting features

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd aws-multi-agent-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure AWS Credentials

#### Option A: AWS CLI Configuration
```bash
aws configure
```

#### Option B: Environment Variables
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

#### Option C: IAM Role (for EC2 instances)
Attach an IAM role with appropriate permissions to your EC2 instance.

### 4. Required AWS IAM Permissions

Create an IAM policy with the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeVpcs",
                "ec2:DescribeSubnets",
                "s3:ListAllMyBuckets",
                "elasticloadbalancing:DescribeLoadBalancers",
                "elasticloadbalancing:DescribeTargetGroups",
                "efs:DescribeFileSystems",
                "efs:DescribeMountTargets",
                "cloudwatch:ListMetrics",
                "cloudtrail:DescribeTrails"
            ],
            "Resource": "*"
        }
    ]
}
```

## 🎯 Usage

### Command Line Interface

#### 1. Interactive Mode
```bash
python main.py
```

#### 2. Direct Queries

**Basic AWS Resource Queries:**
```bash
python main.py "Show me all EC2 instances"
python main.py "List S3 buckets"
python main.py "Get load balancer information"
python main.py "Display EFS filesystems"
python main.py "Show security group details"
```

**Smart Filtering Queries:**
```bash
# Count queries
python main.py "How many EC2 instances are running?"
python main.py "Count my stopped instances"
python main.py "How many micro instances do I have?"

# State-based filtering
python main.py "Show me running instances"
python main.py "List stopped servers"
python main.py "Display pending instances"

# Instance type filtering
python main.py "Show me t3.medium instances"
python main.py "List all micro instances"
python main.py "Get large instances"

# Combined filtering
python main.py "How many running micro instances?"
python main.py "Show me stopped t2.small instances"

# Breakdown and aggregation queries
python main.py "Show the count of each instance type"
python main.py "Breakdown by instance type"
python main.py "How many of each instance type do I have?"
python main.py "Breakdown by state"
python main.py "Count instances by type"
```

**Network Troubleshooting:**
```bash
python main.py "Diagnose EC2 connectivity issues"
python main.py "Troubleshoot load balancer connection problems"
python main.py "Check EFS mount connectivity"
python main.py "Diagnose S3 access issues"
```

**System Information:**
```bash
python main.py "help"
python main.py "what can you do"
```

### Example Interactions

#### AWS Resource Query
```bash
$ python main.py "Show me EC2 instances"

✅ Query processed successfully
🎯 Routed to: aws_resource_tool
🎯 Confidence: 1.00

📊 Results:
Found 3 EC2 instances:
  • i-1234567890abcdef0 (running) - t3.medium
  • i-0987654321fedcba0 (stopped) - t2.micro
  • i-abcdef1234567890f (running) - m5.large
```

#### Network Troubleshooting
```bash
$ python main.py "Diagnose connectivity issues"

✅ Query processed successfully
🎯 Routed to: network_troubleshoot_tool
🎯 Confidence: 0.95

📊 Results:
  Instance: i-1234567890abcdef0
    • public_ip_ping: success
    • port_22_connectivity: open
    • port_80_connectivity: closed
```

## 🔧 Configuration

### Environment Variables
```bash
# AWS Configuration
export AWS_REGION=us-east-1
export AWS_PROFILE=default

# Logging Level
export LOG_LEVEL=INFO
```

### Configuration Files

#### `config/settings.py`
- AWS region and profile settings
- Supported AWS services list
- Network troubleshooting categories
- Agent configuration parameters

## 📁 Project Structure

```
aws-multi-agent-system/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── main.py                     # Main entry point
├── agents/
│   ├── __init__.py
│   ├── orchestrator_agent.py   # Main orchestrator
│   ├── aws_resource_agent.py   # AWS resource retrieval
│   └── network_troubleshoot_agent.py  # Network diagnostics
├── utils/
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class
│   ├── aws_client.py          # AWS service clients
│   └── network_utils.py       # Network utilities
└── config/
    └── settings.py            # Configuration settings
```

## 🔌 API Integration

The system returns structured JSON responses, making it easy to integrate with REST APIs:

```python
from agents.orchestrator_agent import OrchestratorAgent

# Initialize the system
orchestrator = OrchestratorAgent()

# Process a query
result = orchestrator.run("Show me EC2 instances")
parsed_result = json.loads(result)

# Use the structured response
if parsed_result.get('success', True):
    tool_result = parsed_result['tool_result']
    # Process the tool result...
```

## 🚀 Extending the System

### Adding a New Agent

1. **Create the Agent Class**:
```python
from utils.base_agent import Agent

class MyNewAgent(Agent):
    def __init__(self):
        super().__init__(
            name="My New Agent",
            description="Description of what this agent does"
        )
    
    def run(self, input_data: str) -> str:
        # Implement your agent logic
        result = {"message": "Hello from new agent"}
        return json.dumps(result, indent=2)
```

2. **Register with Orchestrator**:
```python
# In orchestrator_agent.py
from agents.my_new_agent import MyNewAgent

# Add to __init__ method
self.my_new_agent = MyNewAgent()

# Add to tools dictionary
self.tools['my_new_tool'] = {
    'agent': self.my_new_agent,
    'description': 'Description of the new tool',
    'keywords': ['keyword1', 'keyword2', 'keyword3']
}
```

### Adding New AWS Services

1. **Update AWS Client** (`utils/aws_client.py`):
```python
def get_new_service_resources(self):
    """Get new AWS service information."""
    try:
        client = self.get_client('new-service')
        response = client.describe_resources()
        return response['Resources']
    except ClientError as e:
        logger.error(f"Error retrieving new service resources: {e}")
        return []
```

2. **Update Agent Logic** (`agents/aws_resource_agent.py`):
```python
def get_new_service_resources(self):
    """Get new service resources."""
    try:
        resources = self.aws_client.get_new_service_resources()
        return {
            'service': 'new-service',
            'resources': resources,
            'count': len(resources)
        }
    except Exception as e:
        return {'error': str(e), 'service': 'new-service'}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. AWS Credentials Not Found
```bash
Error: Unable to locate credentials
```
**Solution**: Configure AWS credentials using `aws configure` or environment variables.

#### 2. Permission Denied
```bash
Error: User is not authorized to perform: ec2:DescribeInstances
```
**Solution**: Add the required IAM permissions to your AWS user/role.

#### 3. Network Connectivity Issues
```bash
Error: ping3 module not found
```
**Solution**: The system will fallback to system ping. Install ping3 for better functionality:
```bash
pip install ping3
```

#### 4. DNS Resolution Failures
```bash
Error: dnspython module not found
```
**Solution**: The system will fallback to socket.gethostbyname. Install dnspython for advanced DNS features:
```bash
pip install dnspython
```

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
python main.py "your query"
```

Check the log file:
```bash
tail -f multi_agent_system.log
```

## 📊 Performance Considerations

- **AWS API Rate Limits**: The system respects AWS API rate limits
- **Concurrent Requests**: Agents can be called concurrently for better performance
- **Caching**: Consider implementing caching for frequently accessed resources
- **Timeout Handling**: Network operations have configurable timeouts

## 🔒 Security Best Practices

1. **Least Privilege**: Use IAM roles with minimal required permissions
2. **Credential Management**: Never hardcode AWS credentials
3. **Network Security**: Run in secure network environments
4. **Logging**: Monitor and audit system usage
5. **Input Validation**: The system validates and sanitizes inputs

## 📈 Monitoring and Logging

The system provides comprehensive logging:

- **Application Logs**: `multi_agent_system.log`
- **Agent-specific Logs**: Each agent has its own logger
- **AWS API Calls**: Boto3 logging for AWS interactions
- **Performance Metrics**: Request routing and processing times

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Create an issue with detailed information
4. Include system information and error messages

---

**Built with ❤️ using the agents-as-tools pattern for scalable multi-agent systems.**