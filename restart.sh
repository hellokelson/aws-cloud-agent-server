#!/bin/bash
# Kill existing process on port 8080
lsof -ti :8080 | xargs kill -9 2>/dev/null
# Start main.py with virtual environment
cd /Users/zhangkap/aws/sourcecode/aws-cloud-agent-server
source .venv/bin/activate
python main.py
