#!/usr/bin/env python3
"""
Demo script showing the Open Discussion Agent capabilities.
This demonstrates how the system now handles ANY question through intelligent routing.
"""

import json
from agents.orchestrator_agent import OrchestratorAgent

def demo_query(orchestrator, query, description):
    """Demo a single query with explanation."""
    print(f"\n🎯 {description}")
    print(f"📝 Query: '{query}'")
    print("-" * 60)
    
    result = orchestrator.run(query)
    parsed = json.loads(result)
    
    # Show routing decision
    if 'orchestrator_analysis' in parsed:
        analysis = parsed['orchestrator_analysis']
        tool = analysis.get('selected_tool', 'unknown')
        is_fallback = analysis.get('is_fallback', False)
        confidence = analysis.get('confidence', 0)
        
        if is_fallback:
            print(f"🧠 ROUTED TO: General LLM Agent (Open Discussion)")
            print(f"📋 Reason: {analysis.get('fallback_reason', 'Unknown')}")
        else:
            print(f"🎯 ROUTED TO: {tool} (Specialized Agent)")
            print(f"🎯 Confidence: {confidence:.2f}")
        
        # Show response preview
        if 'tool_result' in parsed:
            tool_result = parsed['tool_result']
            if 'response' in tool_result:
                response = tool_result['response']
                print(f"💬 Response Preview: {response[:200]}...")
            elif 'count' in tool_result:
                print(f"📊 Result: Found {tool_result['count']} items")
    
    print(f"✅ Success: {parsed.get('success', False)}")
    return parsed

def main():
    """Demonstrate the open discussion agent capabilities."""
    print("🚀 Open Discussion Agent Demo")
    print("=" * 60)
    print("This shows how the system can now handle ANY question!")
    print("It intelligently routes to specialized agents OR falls back to LLM.")
    
    orchestrator = OrchestratorAgent()
    
    # 1. Specialized Agent Examples (should NOT fallback)
    print("\n" + "="*60)
    print("🎯 SPECIALIZED AGENT EXAMPLES")
    print("These should route to specialized agents:")
    print("="*60)
    
    demo_query(orchestrator, "how many VPCs do I have", 
               "AWS Resource Query - Should use AWS Resource Agent")
    
    demo_query(orchestrator, "diagnose connectivity issues", 
               "Network Query - Should use Network Troubleshoot Agent")
    
    # 2. Open Discussion Examples (should fallback to LLM)
    print("\n" + "="*60)
    print("🧠 OPEN DISCUSSION AGENT EXAMPLES")
    print("These should fallback to the General LLM Agent:")
    print("="*60)
    
    demo_query(orchestrator, "What are AWS security best practices?", 
               "AWS Best Practices - Should use General LLM Agent")
    
    demo_query(orchestrator, "How do I optimize costs in the cloud?", 
               "Cost Optimization - Should use General LLM Agent")
    
    demo_query(orchestrator, "What is the difference between ALB and NLB?", 
               "Technical Explanation - Should use General LLM Agent")
    
    demo_query(orchestrator, "How do I implement CI/CD for AWS deployments?", 
               "DevOps Question - Should use General LLM Agent")
    
    demo_query(orchestrator, "Explain microservices architecture", 
               "Architecture Question - Should use General LLM Agent")
    
    demo_query(orchestrator, "What are the benefits of containerization?", 
               "Technology Question - Should use General LLM Agent")
    
    demo_query(orchestrator, "How does DNS work?", 
               "General Tech Question - Should use General LLM Agent")
    
    demo_query(orchestrator, "What is the meaning of life?", 
               "Philosophical Question - Should use General LLM Agent")
    
    # 3. Edge Cases (should handle gracefully)
    print("\n" + "="*60)
    print("🔧 EDGE CASE EXAMPLES")
    print("These test the system's robustness:")
    print("="*60)
    
    demo_query(orchestrator, "vpc security group lambda optimization best practices", 
               "Mixed Keywords - Should intelligently choose best agent")
    
    demo_query(orchestrator, "help me with something but I don't know what", 
               "Vague Request - Should fallback to LLM gracefully")
    
    # 4. System Analysis
    print("\n" + "="*60)
    print("📊 SYSTEM ANALYSIS")
    print("="*60)
    
    print("\n🔍 Analyzing routing patterns...")
    analysis = orchestrator.run("analyze routing")
    parsed_analysis = json.loads(analysis)
    
    if 'total_requests' in parsed_analysis:
        print(f"📈 Total Requests: {parsed_analysis['total_requests']}")
        print(f"✅ Success Rate: {parsed_analysis['success_rate']:.2%}")
        print(f"🔄 Fallback Rate: {parsed_analysis['fallback_rate']:.2%}")
        
        if parsed_analysis.get('agent_usage'):
            print("\n🤖 Agent Usage:")
            for agent, stats in parsed_analysis['agent_usage'].items():
                success_rate = stats['success_count'] / stats['count'] if stats['count'] > 0 else 0
                print(f"   • {agent}: {stats['count']} requests ({success_rate:.1%} success)")
    
    # 5. Summary
    print("\n" + "="*60)
    print("🎉 DEMO COMPLETE - KEY ACHIEVEMENTS")
    print("="*60)
    print("✅ System can handle ANY question (not just AWS-specific)")
    print("✅ Intelligent routing to specialized agents when appropriate")
    print("✅ Automatic fallback to General LLM Agent when needed")
    print("✅ Response validation and relevance checking")
    print("✅ Learning from routing decisions for continuous improvement")
    print("✅ Graceful error handling and recovery")
    print("✅ Context-aware conversations")
    print("\n🚀 The system is now truly OPEN and UNLIMITED!")
    print("   You can ask about AWS, DevOps, programming, architecture,")
    print("   best practices, troubleshooting, or even general questions!")

if __name__ == "__main__":
    main()