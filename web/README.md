# AWS Assistant Web Portal

A Cloudscape-based web interface for the AWS Assistant AgentCore.

## Features

- **Session Management**: View and manage chat sessions stored in S3
- **Real-time Chat**: Interactive chat interface with streaming responses
- **Session Persistence**: Continue conversations across sessions
- **Cloudscape Design**: AWS-native UI components and styling

## Setup

1. **Start AgentCore** (in main directory):
   ```bash
   python main.py
   ```
   This starts the AgentCore server on http://localhost:8080

2. **Start Web Portal**:
   ```bash
   cd web
   ./start.sh
   ```
   This starts the web portal on http://localhost:3000

## Usage

### Left Panel - Session List
- View all existing chat sessions
- Click on a session to load its conversation history
- Sessions are automatically titled based on the first message
- "New Chat" button creates a fresh session

### Right Panel - Chat Interface
- Type questions about AWS resources, costs, security, etc.
- Responses stream in real-time from the AgentCore
- Sessions are automatically saved to S3
- Chat history is preserved across browser sessions

## API Endpoints

- `GET /api/sessions` - List all sessions
- `GET /api/sessions/<id>` - Get session details
- `POST /api/chat` - Send message and stream response
- `DELETE /api/sessions/<id>` - Delete session

## Configuration

The web portal connects to:
- **AgentCore**: http://localhost:8080
- **S3 Bucket**: zk-aws-mcp-assistant-sessions
- **Region**: us-east-1

## Architecture

```
Browser ←→ Flask Web App ←→ AgentCore ←→ AWS Services
                ↓
            S3 Sessions
```

The web portal provides a user-friendly interface to the powerful multi-agent AWS assistant system.
