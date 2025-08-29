#!/bin/bash

# Kill any existing Python processes running the agent server
pkill -f "python.*main.py"

# Kill any process using port 8080
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# Wait a moment for processes to terminate
sleep 3

# Activate virtual environment and start the server
echo "Starting AWS Cloud Agent Server..."
cd ..
source .venv/bin/activate
cd server
python main.py
