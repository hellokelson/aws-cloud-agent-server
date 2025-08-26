#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced filtering capabilities
"""

from agents.aws_resource_agent import AWSResourceAgent

def test_query_parsing():
    """Test the query parsing functionality."""
    agent = AWSResourceAgent()
    
    test_queries = [
        "show me how many ec2 instances are running",
        "list stopped instances", 
        "count my micro instances",
        "show me t3.medium instances",
        "how many running servers do I have",
        "display all instances",
        "get pending instances"
    ]
    
    print("🧪 Testing Query Parsing and Filtering")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        filters = agent.parse_query_filters(query)
        print(f"🎯 Detected filters: {filters}")
        
        # Show what would be filtered
        active_filters = {k: v for k, v in filters.items() if v is not None and v != False}
        if active_filters:
            print(f"✅ Active filters: {active_filters}")
        else:
            print("ℹ️  No filters detected - will show all instances")

def test_instance_filtering():
    """Test instance filtering with mock data."""
    agent = AWSResourceAgent()
    
    # Mock EC2 instances data
    mock_instances = [
        {'InstanceId': 'i-1234567890abcdef0', 'State': 'running', 'InstanceType': 't3.medium'},
        {'InstanceId': 'i-0987654321fedcba0', 'State': 'stopped', 'InstanceType': 't2.micro'},
        {'InstanceId': 'i-abcdef1234567890f', 'State': 'running', 'InstanceType': 'm5.large'},
        {'InstanceId': 'i-fedcba0987654321a', 'State': 'pending', 'InstanceType': 't3.small'},
        {'InstanceId': 'i-1111222233334444b', 'State': 'running', 'InstanceType': 't2.micro'},
        {'InstanceId': 'i-2222333344445555c', 'State': 'running', 'InstanceType': 't3.medium'},
        {'InstanceId': 'i-3333444455556666d', 'State': 'stopped', 'InstanceType': 'm5.large'}
    ]
    
    print("\n\n🔬 Testing Instance Filtering")
    print("=" * 60)
    print(f"📊 Mock data: {len(mock_instances)} instances")
    for instance in mock_instances:
        print(f"  • {instance['InstanceId']} ({instance['State']}) - {instance['InstanceType']}")
    
    # Test different filters
    test_filters = [
        {'state': 'running'},
        {'state': 'stopped'},
        {'instance_type': 'micro'},
        {'state': 'running', 'instance_type': 'micro'},
        {'specific_instance_type': 't3.medium'}
    ]
    
    for filters in test_filters:
        print(f"\n🎯 Applying filters: {filters}")
        filtered = agent.filter_ec2_instances(mock_instances, filters)
        print(f"📈 Results: {len(filtered)} instances")
        for instance in filtered:
            print(f"  ✅ {instance['InstanceId']} ({instance['State']}) - {instance['InstanceType']}")

def test_breakdown_functionality():
    """Test breakdown functionality with mock data."""
    agent = AWSResourceAgent()
    
    # Mock EC2 instances data with more variety
    mock_instances = [
        {'InstanceId': 'i-1234567890abcdef0', 'State': 'running', 'InstanceType': 't3.medium'},
        {'InstanceId': 'i-0987654321fedcba0', 'State': 'stopped', 'InstanceType': 't2.micro'},
        {'InstanceId': 'i-abcdef1234567890f', 'State': 'running', 'InstanceType': 'm5.large'},
        {'InstanceId': 'i-fedcba0987654321a', 'State': 'pending', 'InstanceType': 't3.small'},
        {'InstanceId': 'i-1111222233334444b', 'State': 'running', 'InstanceType': 't2.micro'},
        {'InstanceId': 'i-2222333344445555c', 'State': 'running', 'InstanceType': 't3.medium'},
        {'InstanceId': 'i-3333444455556666d', 'State': 'stopped', 'InstanceType': 'm5.large'},
        {'InstanceId': 'i-4444555566667777e', 'State': 'running', 'InstanceType': 't3.large'},
        {'InstanceId': 'i-5555666677778888f', 'State': 'running', 'InstanceType': 't2.micro'}
    ]
    
    print("\n\n📊 Testing Breakdown Functionality")
    print("=" * 60)
    print(f"📊 Mock data: {len(mock_instances)} instances")
    
    # Test breakdown by instance type
    print("\n🔍 Testing breakdown by instance type:")
    breakdown_by_type = agent.generate_breakdown(mock_instances, 'instance_type')
    print("Instance Type Breakdown:")
    for instance_type, count in sorted(breakdown_by_type.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(mock_instances) * 100)
        print(f"  • {instance_type}: {count} instances ({percentage:.1f}%)")
    
    # Test breakdown by state
    print("\n🔍 Testing breakdown by state:")
    breakdown_by_state = agent.generate_breakdown(mock_instances, 'state')
    print("State Breakdown:")
    for state, count in sorted(breakdown_by_state.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(mock_instances) * 100)
        print(f"  • {state}: {count} instances ({percentage:.1f}%)")

def test_breakdown_queries():
    """Test breakdown query parsing."""
    agent = AWSResourceAgent()
    
    breakdown_queries = [
        "show the count of each instance type",
        "breakdown by instance type",
        "count instances by type",
        "show me instance type breakdown",
        "how many of each instance type do I have",
        "group instances by state",
        "breakdown by state"
    ]
    
    print("\n\n🧪 Testing Breakdown Query Parsing")
    print("=" * 60)
    
    for query in breakdown_queries:
        print(f"\n📝 Query: '{query}'")
        filters = agent.parse_query_filters(query)
        print(f"🎯 Detected filters: {filters}")
        
        if filters.get('breakdown_by'):
            print(f"✅ Breakdown detected: {filters['breakdown_by']}")
        else:
            print("❌ No breakdown detected")

if __name__ == "__main__":
    test_query_parsing()
    test_instance_filtering()
    test_breakdown_functionality()
    test_breakdown_queries()