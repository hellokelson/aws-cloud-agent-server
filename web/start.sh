#!/bin/bash

# Activate the parent project's virtual environment
source ../.venv/bin/activate

# Install web portal dependencies in virtual environment
pip install --force-reinstall -r requirements.txt

# Start the web portal
echo "Starting AWS Assistant Web Portal on http://localhost:3000"
echo "Make sure main.py AgentCore is running on http://localhost:8080"
python app.py
