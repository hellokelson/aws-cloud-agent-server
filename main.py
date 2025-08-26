#!/usr/bin/env python3
"""
Multi-Agent AWS Infrastructure Management System
Main entry point for the orchestrator agent with agents-as-tools pattern.
"""

import sys
import json
import logging
from typing import Optional
from agents.orchestrator_agent import OrchestratorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('multi_agent_system.log')
    ]
)

logger = logging.getLogger(__name__)

class MultiAgentSystem:
    """Main system class that manages the multi-agent infrastructure."""
    
    def __init__(self):
        """Initialize the multi-agent system."""
        try:
            self.orchestrator = OrchestratorAgent()
            logger.info("Multi-Agent System initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Multi-Agent System: {e}")
            raise
    
    def process_query(self, query: str) -> dict:
        """Process a user query through the orchestrator."""
        try:
            logger.info(f"Processing query: {query}")
            result = self.orchestrator.run(query)
            
            # Parse the JSON result
            if isinstance(result, str):
                result = json.loads(result)
            
            logger.info("Query processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'error': f'System error: {str(e)}',
                'query': query,
                'success': False
            }
    
    def interactive_mode(self):
        """Run the system in interactive mode."""
        print("🤖 AWS Multi-Agent Infrastructure System")
        print("=" * 50)
        print("Available commands:")
        print("  - Ask about AWS resources: 'Show me EC2 instances'")
        print("  - Troubleshoot network issues: 'Diagnose connectivity problems'")
        print("  - Get help: 'help' or 'what can you do'")
        print("  - Exit: 'quit' or 'exit'")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n💬 Enter your query: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                # Process the query
                result = self.process_query(user_input)
                
                # Display the result
                self._display_result(result)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _display_result(self, result: dict):
        """Display the result in a user-friendly format."""
        print("\n" + "=" * 50)
        
        if result.get('success', True):
            print("✅ Query processed successfully")
            
            # Display orchestrator analysis if available
            if 'orchestrator_analysis' in result:
                analysis = result['orchestrator_analysis']
                print(f"🎯 Routed to: {analysis['selected_tool']}")
                print(f"🎯 Confidence: {analysis['confidence']:.2f}")
                print(f"🎯 Reason: {analysis['routing_reason']}")
            
            # Display tool result
            if 'tool_result' in result:
                tool_result = result['tool_result']
                if 'error' in tool_result:
                    print(f"❌ Tool Error: {tool_result['error']}")
                else:
                    print("\n📊 Results:")
                    self._format_tool_result(tool_result)
            
            # Display system info if available
            elif 'system_info' in result:
                self._display_system_info(result)
        
        else:
            print("❌ Query failed")
            if 'error' in result:
                print(f"Error: {result['error']}")
        
        print("=" * 50)
    
    def _format_tool_result(self, tool_result: dict):
        """Format and display tool results."""
        service = tool_result.get('service', 'unknown')
        
        # Display query interpretation if available
        if 'query_interpretation' in tool_result:
            interpretation = tool_result['query_interpretation']
            print(f"🔍 Query: {interpretation['original_query']}")
            if 'detected_filters' in interpretation:
                filters = interpretation['detected_filters']
                active_filters = {k: v for k, v in filters.items() if v is not None and v != False}
                if active_filters:
                    print(f"🎯 Applied filters: {active_filters}")
        
        if service == 'ec2':
            count = tool_result.get('count', 0)
            instances = tool_result.get('instances', [])
            
            # Handle breakdown queries
            if 'breakdown' in tool_result:
                breakdown = tool_result['breakdown']
                breakdown_by = tool_result.get('breakdown_by', 'unknown')
                total_instances = tool_result.get('total_instances', 0)
                
                print(f"\n📊 EC2 Instance Breakdown by {breakdown_by.replace('_', ' ').title()}:")
                print(f"📈 Total instances: {total_instances}")
                print()
                
                # Sort breakdown by count (descending)
                sorted_breakdown = sorted(breakdown.items(), key=lambda x: x[1], reverse=True)
                
                for item, item_count in sorted_breakdown:
                    percentage = (item_count / total_instances * 100) if total_instances > 0 else 0
                    print(f"  • {item}: {item_count} instances ({percentage:.1f}%)")
                
                return  # Early return for breakdown queries
            
            # Show state breakdown if available
            if 'state_breakdown' in tool_result:
                print(f"\n📊 Instance State Breakdown:")
                for state, count_per_state in tool_result['state_breakdown'].items():
                    print(f"  • {state}: {count_per_state}")
            
            # If this was a count-only query, focus on the count
            if tool_result.get('query_interpretation', {}).get('detected_filters', {}).get('count_only'):
                applied_filters = tool_result.get('applied_filters', {})
                filter_desc = ""
                if applied_filters:
                    filter_parts = []
                    if 'state' in applied_filters:
                        filter_parts.append(f"{applied_filters['state']} state")
                    if 'instance_type' in applied_filters:
                        filter_parts.append(f"{applied_filters['instance_type']} type")
                    if 'specific_instance_type' in applied_filters:
                        filter_parts.append(f"{applied_filters['specific_instance_type']} instances")
                    filter_desc = f" ({', '.join(filter_parts)})" if filter_parts else ""
                
                print(f"\n✅ Answer: {count} EC2 instances{filter_desc}")
            else:
                print(f"\nFound {count} EC2 instances:")
                for instance in instances[:10]:  # Show first 10
                    print(f"  • {instance['InstanceId']} ({instance['State']}) - {instance['InstanceType']}")
                if len(instances) > 10:
                    print(f"  ... and {len(instances) - 10} more instances")
        
        elif service == 's3':
            buckets = tool_result.get('buckets', [])
            print(f"\nFound {len(buckets)} S3 buckets:")
            for bucket in buckets[:5]:  # Show first 5
                print(f"  • {bucket['Name']} (Created: {bucket['CreationDate']})")
            if len(buckets) > 5:
                print(f"  ... and {len(buckets) - 5} more buckets")
        
        elif service == 'load_balancers':
            alb_count = tool_result.get('alb_nlb_count', 0)
            classic_count = tool_result.get('classic_count', 0)
            print(f"\nFound {alb_count} ALB/NLB and {classic_count} Classic Load Balancers")
        
        elif service == 'efs':
            filesystems = tool_result.get('filesystems', [])
            print(f"\nFound {len(filesystems)} EFS filesystems:")
            for fs in filesystems[:5]:
                print(f"  • {fs['FileSystemId']} ({fs['LifeCycleState']})")
        
        elif service == 'vpc':
            vpcs = tool_result.get('vpcs', [])
            resources = tool_result.get('resources', vpcs)  # Handle generic response
            print(f"\nFound {len(resources)} VPCs:")
            for vpc in resources[:10]:
                vpc_id = vpc.get('VpcId', 'N/A')
                state = vpc.get('State', 'N/A')
                cidr = vpc.get('CidrBlock', 'N/A')
                is_default = vpc.get('IsDefault', False)
                default_text = " (Default)" if is_default else ""
                print(f"  • {vpc_id} ({state}) - {cidr}{default_text}")
        
        elif service == 'subnet':
            subnets = tool_result.get('subnets', [])
            resources = tool_result.get('resources', subnets)
            print(f"\nFound {len(resources)} Subnets:")
            for subnet in resources[:10]:
                subnet_id = subnet.get('SubnetId', 'N/A')
                state = subnet.get('State', 'N/A')
                cidr = subnet.get('CidrBlock', 'N/A')
                az = subnet.get('AvailabilityZone', 'N/A')
                print(f"  • {subnet_id} ({state}) - {cidr} in {az}")
        
        elif service == 'lambda':
            functions = tool_result.get('functions', [])
            resources = tool_result.get('resources', functions)
            print(f"\nFound {len(resources)} Lambda functions:")
            for func in resources[:10]:
                func_name = func.get('FunctionName', 'N/A')
                runtime = func.get('Runtime', 'N/A')
                last_modified = func.get('LastModified', 'N/A')
                print(f"  • {func_name} ({runtime}) - Modified: {last_modified}")
        
        elif service == 'rds':
            instances = tool_result.get('instances', [])
            resources = tool_result.get('resources', instances)
            print(f"\nFound {len(resources)} RDS instances:")
            for db in resources[:10]:
                db_id = db.get('DBInstanceIdentifier', 'N/A')
                status = db.get('DBInstanceStatus', 'N/A')
                engine = db.get('Engine', 'N/A')
                instance_class = db.get('DBInstanceClass', 'N/A')
                print(f"  • {db_id} ({status}) - {engine} on {instance_class}")
        
        elif service == 'ebs':
            volumes = tool_result.get('volumes', [])
            resources = tool_result.get('resources', volumes)
            print(f"\nFound {len(resources)} EBS volumes:")
            for vol in resources[:10]:
                vol_id = vol.get('VolumeId', 'N/A')
                state = vol.get('State', 'N/A')
                size = vol.get('Size', 'N/A')
                vol_type = vol.get('VolumeType', 'N/A')
                print(f"  • {vol_id} ({state}) - {size}GB {vol_type}")
        
        elif service == 'security_groups':
            security_groups = tool_result.get('security_groups', [])
            resources = tool_result.get('resources', security_groups)
            print(f"\nFound {len(resources)} Security Groups:")
            for sg in resources[:10]:
                sg_id = sg.get('GroupId', 'N/A')
                sg_name = sg.get('GroupName', 'N/A')
                description = sg.get('Description', 'N/A')
                print(f"  • {sg_id} ({sg_name}) - {description}")
        
        elif 'connectivity' in service:
            diagnostics = tool_result.get('diagnostics', {})
            if isinstance(diagnostics, list):
                for diag in diagnostics:
                    print(f"  Instance: {diag.get('instance_id', 'N/A')}")
                    tests = diag.get('tests', [])
                    for test in tests:
                        status = test.get('result', {}).get('status', 'unknown')
                        print(f"    • {test.get('test', 'Unknown test')}: {status}")
            else:
                print(f"  Target: {diagnostics.get('load_balancer_dns', 'N/A')}")
        
        elif service == 'general_llm':
            # Handle General LLM Agent responses
            response = tool_result.get('response', 'No response available')
            provider = tool_result.get('provider', 'unknown')
            question = tool_result.get('question', 'N/A')
            
            print(f"\n🤖 AI Assistant Response (via {provider}):")
            print(f"📝 Question: {question}")
            print(f"\n💬 Answer:")
            print(response)
            
            # Show context if it was used
            if tool_result.get('context_used'):
                print(f"\n🔍 Context from previous interactions was used")
        
        else:
            # Generic display for other results
            print(json.dumps(tool_result, indent=2, default=str))
    
    def _display_system_info(self, result: dict):
        """Display system information."""
        system_info = result.get('system_info', {})
        print(f"\n🤖 System: {system_info.get('name', 'Unknown')}")
        print(f"📝 Description: {system_info.get('description', 'N/A')}")
        
        print("\n🛠️  Available Tools:")
        for tool in system_info.get('available_tools', []):
            print(f"  • {tool['name']}: {tool['description']}")
        
        if 'usage_examples' in result:
            examples = result['usage_examples']
            print("\n💡 Usage Examples:")
            for category, example_list in examples.items():
                print(f"\n  {category.replace('_', ' ').title()}:")
                for example in example_list[:3]:  # Show first 3 examples
                    print(f"    - {example}")

def main():
    """Main function."""
    try:
        # Initialize the multi-agent system
        system = MultiAgentSystem()
        
        # Check if query is provided as command line argument
        if len(sys.argv) > 1:
            query = ' '.join(sys.argv[1:])
            result = system.process_query(query)
            print(json.dumps(result, indent=2, default=str))
        else:
            # Run in interactive mode
            system.interactive_mode()
            
    except Exception as e:
        logger.error(f"System startup failed: {e}")
        print(f"❌ Failed to start system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()