#!/usr/bin/env python3
"""
Local testing script for AWS Assistant AgentCore integration

This script allows you to test the AgentCore-compatible agent locally
before deploying to Amazon Bedrock AgentCore Runtime.
"""

import asyncio
import json
import requests
import subprocess
import time
import sys
from typing import Dict, Any

def start_local_server():
    """Start the local AgentCore server"""
    print("🚀 Starting local AgentCore server...")
    process = subprocess.Popen(
        [sys.executable, "agentcore_main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(5)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8080/ping", timeout=5)
        if response.status_code == 200:
            print("✅ Local server started successfully")
            return process
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            process.terminate()
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to local server: {e}")
        process.terminate()
        return None

def test_agent(payload: Dict[str, Any]) -> bool:
    """Test the agent with a given payload"""
    try:
        response = requests.post(
            "http://localhost:8080/invocations",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ Test successful!")
            print(f"Response: {response.text[:500]}...")
            return True
        else:
            print(f"❌ Test failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def run_tests():
    """Run a series of tests"""
    test_cases = [
        {
            "name": "Documentation Query",
            "payload": {"prompt": "What is AWS Lambda?"}
        },
        {
            "name": "Cost Query",
            "payload": {"prompt": "What's my AWS spending this month?"}
        },
        {
            "name": "Security Query", 
            "payload": {"prompt": "Review my AWS security posture"}
        },
        {
            "name": "CloudWatch Query",
            "payload": {"prompt": "Show me CPU utilization for my EC2 instances"}
        }
    ]
    
    print(f"\n🧪 Running {len(test_cases)} test cases...\n")
    
    passed = 0
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}/{len(test_cases)}: {test_case['name']}")
        print(f"Query: {test_case['payload']['prompt']}")
        
        if test_agent(test_case['payload']):
            passed += 1
            print("✅ PASSED\n")
        else:
            print("❌ FAILED\n")
    
    print(f"📊 Test Results: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def main():
    """Main testing function"""
    print("🧪 AWS Assistant AgentCore Local Testing")
    print("=" * 50)
    
    # Start local server
    server_process = start_local_server()
    if not server_process:
        print("❌ Failed to start local server")
        return False
    
    try:
        # Run tests
        success = run_tests()
        
        if success:
            print("🎉 All tests passed! Agent is ready for deployment.")
        else:
            print("⚠️ Some tests failed. Please check the implementation.")
        
        return success
        
    finally:
        # Clean up
        print("🧹 Cleaning up...")
        server_process.terminate()
        server_process.wait()
        print("✅ Local server stopped")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
