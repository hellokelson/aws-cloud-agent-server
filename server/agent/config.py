# Configuration constants for AWS Cloud Agent Server

# AWS Configuration
AWS_REGION = "us-east-1"

# Model Configuration
BEDROCK_MODEL_ID = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
# 3.7 4.0 gpt opensource 120b deepseek r1

MODEL_TEMPERATURE = 0.3

# S3 Configuration
S3_SESSION_BUCKET = "zk-aws-mcp-assistant-sessions"

# Server Configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080
WEB_UI_PORT = 80

# Tool Configuration
STRANDS_AUTO_APPROVE_TOOLS = "true"
