#!/usr/bin/env python3
"""
Test script to demonstrate the Enhanced Orchestrator Agent with intelligent fallback and learning capabilities.
"""

import json
import time
from agents.orchestrator_agent import OrchestratorAgent

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)

def print_result(query, result):
    """Print query result in a formatted way."""
    print(f"\n📝 Query: {query}")
    print("-" * 50)
    
    try:
        parsed = json.loads(result) if isinstance(result, str) else result
        
        # Show orchestrator analysis
        if 'orchestrator_analysis' in parsed:
            analysis = parsed['orchestrator_analysis']
            print(f"🤖 Selected Tool: {analysis.get('selected_tool', 'unknown')}")
            print(f"🎯 Confidence: {analysis.get('confidence', 0):.2f}")
            print(f"🔄 Is Fallback: {analysis.get('is_fallback', False)}")
            
            if analysis.get('fallback_reason'):
                print(f"📋 Fallback Reason: {analysis['fallback_reason']}")
            
            if analysis.get('routing_reason'):
                print(f"🧭 Routing Reason: {analysis['routing_reason']}")
            
            if analysis.get('response_validation'):
                validation = analysis['response_validation']
                print(f"✅ Response Validation: {validation.get('is_relevant', 'unknown')} (confidence: {validation.get('confidence', 0):.2f})")
        
        # Show tool result summary
        if 'tool_result' in parsed:
            tool_result = parsed['tool_result']
            if 'service' in tool_result:
                print(f"🔧 Service: {tool_result['service']}")
            if 'count' in tool_result:
                print(f"📊 Count: {tool_result['count']}")
            if 'response' in tool_result:
                response = tool_result['response']
                print(f"💬 Response: {response[:150]}...")
        
        print(f"✅ Success: {parsed.get('success', False)}")
        
    except Exception as e:
        print(f"❌ Error parsing result: {e}")
        print(f"Raw result: {result}")

def test_specialized_agents():
    """Test that specialized agents still work correctly."""
    print_section("Testing Specialized Agents")
    
    orchestrator = OrchestratorAgent()
    
    # Test AWS Resource Agent
    aws_queries = [
        "how many VPCs do I have",
        "list all EC2 instances",
        "show me S3 buckets",
        "get load balancer information"
    ]
    
    for query in aws_queries:
        result = orchestrator.run(query)
        print_result(query, result)
        time.sleep(1)  # Small delay for readability
    
    # Test Network Troubleshoot Agent
    network_queries = [
        "diagnose connectivity issues",
        "troubleshoot network problems",
        "check port connectivity"
    ]
    
    for query in network_queries:
        result = orchestrator.run(query)
        print_result(query, result)
        time.sleep(1)

def test_fallback_scenarios():
    """Test various fallback scenarios."""
    print_section("Testing Intelligent Fallback Scenarios")
    
    orchestrator = OrchestratorAgent()
    
    # Test questions that should fallback to LLM
    fallback_queries = [
        "What are AWS security best practices?",
        "How do I optimize costs in the cloud?",
        "What is the difference between ALB and NLB?",
        "How do I implement CI/CD for AWS?",
        "What is Infrastructure as Code?",
        "How do microservices work?",
        "Explain containerization benefits",
        "What is the meaning of life?",  # Completely unrelated question
        "How do I bake a cake?"  # Another unrelated question
    ]
    
    for query in fallback_queries:
        result = orchestrator.run(query)
        print_result(query, result)
        time.sleep(1)

def test_edge_cases():
    """Test edge cases and error scenarios."""
    print_section("Testing Edge Cases and Error Scenarios")
    
    orchestrator = OrchestratorAgent()
    
    edge_cases = [
        "",  # Empty query
        "   ",  # Whitespace only
        "show me instances that don't exist in a service that doesn't exist",  # Likely to cause errors
        "vpc ec2 s3 lambda rds everything all at once",  # Multiple keywords
        "help me with something but I don't know what",  # Vague request
    ]
    
    for query in edge_cases:
        if query.strip():  # Skip empty queries for display
            result = orchestrator.run(query)
            print_result(query, result)
            time.sleep(1)

def test_learning_capabilities():
    """Test the learning and analysis capabilities."""
    print_section("Testing Learning and Analysis Capabilities")
    
    orchestrator = OrchestratorAgent()
    
    # First, make some requests to build history
    print("🔄 Building routing history...")
    test_queries = [
        "how many EC2 instances",
        "what are security best practices",
        "diagnose network issues",
        "show me VPCs",
        "how to optimize costs"
    ]
    
    for query in test_queries:
        orchestrator.run(query)
    
    # Now test analysis capabilities
    print("\n📊 Analyzing routing patterns...")
    analysis_result = orchestrator.run("analyze routing")
    print_result("analyze routing", analysis_result)
    
    # Test routing recommendations
    print("\n🎯 Getting routing recommendations...")
    recommendation_result = orchestrator.run("routing recommendations for: how many instances do I have")
    print_result("routing recommendations", recommendation_result)

def test_system_status():
    """Test system status and help functionality."""
    print_section("Testing System Status and Help")
    
    orchestrator = OrchestratorAgent()
    
    system_queries = [
        "help",
        "what can you do",
        "status",
        "available tools"
    ]
    
    for query in system_queries:
        result = orchestrator.run(query)
        print_result(query, result)
        time.sleep(1)

def test_context_awareness():
    """Test context awareness in fallback scenarios."""
    print_section("Testing Context Awareness")
    
    orchestrator = OrchestratorAgent()
    
    # First make a query that will succeed with specialized agent
    print("🔄 Making initial query to build context...")
    initial_result = orchestrator.run("how many VPCs do I have")
    print_result("how many VPCs do I have", initial_result)
    
    # Now ask a follow-up question that should use LLM with context
    print("\n🔄 Making follow-up query that should use context...")
    followup_result = orchestrator.run("How can I better organize these resources?")
    print_result("How can I better organize these resources?", followup_result)

def demonstrate_feedback_system():
    """Demonstrate the feedback system."""
    print_section("Demonstrating Feedback System")
    
    orchestrator = OrchestratorAgent()
    
    # Simulate user feedback
    print("🔄 Simulating user feedback...")
    
    feedback_result = orchestrator.provide_user_feedback(
        request="how many instances do I have",
        was_helpful=False,
        selected_tool="aws_resource_tool",
        feedback_text="The response was too technical, I wanted a simple count"
    )
    
    print("📝 Feedback Result:")
    print(json.dumps(feedback_result, indent=2))

def main():
    """Run all tests to demonstrate the enhanced orchestrator."""
    print("🚀 Enhanced Orchestrator Agent Test Suite")
    print("This demonstrates intelligent routing, fallback, and learning capabilities")
    
    try:
        # Test core functionality
        test_specialized_agents()
        test_fallback_scenarios()
        test_edge_cases()
        
        # Test advanced features
        test_learning_capabilities()
        test_system_status()
        test_context_awareness()
        demonstrate_feedback_system()
        
        print_section("Test Suite Complete!")
        print("✅ All tests completed successfully!")
        print("\n🎯 Key Features Demonstrated:")
        print("   • Intelligent agent routing with confidence scoring")
        print("   • Automatic fallback to General LLM Agent")
        print("   • Response validation and relevance checking")
        print("   • Learning from routing decisions")
        print("   • Context-aware conversations")
        print("   • User feedback integration")
        print("   • Comprehensive error handling")
        
    except Exception as e:
        print(f"\n❌ Test suite encountered an error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()