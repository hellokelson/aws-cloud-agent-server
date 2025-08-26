"""AWS Resource Agent - Retrieves AWS service resource information."""

from utils.base_agent import Agent
from typing import Dict, List, Any, Optional
import json
import logging
import re
from utils.aws_client import AWSClientManager
from config.settings import SUPPORTED_AWS_SERVICES

logger = logging.getLogger(__name__)

class AWSResourceAgent(Agent):
    """Agent specialized in retrieving AWS resource information and attributes."""
    
    def __init__(self):
        super().__init__(
            name="AWS Resource Agent",
            description="Dynamically retrieves information for any AWS service and resource type"
        )
        self.aws_client = AWSClientManager()
        
        # Define comprehensive AWS service mappings
        self.service_mappings = {
            # EC2 and Compute
            'ec2': {'keywords': ['ec2', 'instance', 'server', 'compute'], 'methods': ['get_ec2_instances']},
            'lambda': {'keywords': ['lambda', 'function', 'serverless'], 'methods': ['get_lambda_functions']},
            
            # Networking
            'vpc': {'keywords': ['vpc', 'virtual private cloud', 'network'], 'methods': ['get_vpcs']},
            'subnet': {'keywords': ['subnet', 'subnets'], 'methods': ['get_subnets']},
            'security_group': {'keywords': ['security group', 'sg', 'firewall'], 'methods': ['get_security_groups']},
            'route_table': {'keywords': ['route table', 'routing'], 'methods': ['get_route_tables']},
            'internet_gateway': {'keywords': ['internet gateway', 'igw'], 'methods': ['get_internet_gateways']},
            'nat_gateway': {'keywords': ['nat gateway', 'nat'], 'methods': ['get_nat_gateways']},
            
            # Load Balancing
            'load_balancer': {'keywords': ['load balancer', 'alb', 'nlb', 'elb'], 'methods': ['get_load_balancers']},
            
            # Storage
            's3': {'keywords': ['s3', 'bucket', 'object storage'], 'methods': ['get_s3_buckets']},
            'ebs': {'keywords': ['ebs', 'volume', 'disk'], 'methods': ['get_volumes']},
            'snapshot': {'keywords': ['snapshot', 'backup'], 'methods': ['get_snapshots']},
            'efs': {'keywords': ['efs', 'file system', 'filesystem'], 'methods': ['get_efs_filesystems']},
            
            # Database
            'rds': {'keywords': ['rds', 'database', 'db'], 'methods': ['get_rds_instances']},
        }
        
        # Define filter patterns for intelligent query parsing
        self.filter_patterns = {
            'state': {
                'running': ['running', 'active', 'up', 'available'],
                'stopped': ['stopped', 'down', 'inactive'],
                'pending': ['pending', 'starting'],
                'terminated': ['terminated', 'deleted'],
                'stopping': ['stopping', 'shutting down']
            },
            'instance_type': {
                'micro': ['micro', 't2.micro', 't3.micro'],
                'small': ['small', 't2.small', 't3.small'],
                'medium': ['medium', 't2.medium', 't3.medium'],
                'large': ['large', 't2.large', 't3.large'],
                'xlarge': ['xlarge', 'xl']
            },
            'count_keywords': ['how many', 'count', 'number of', 'total'],
            'list_keywords': ['list', 'show', 'display', 'get'],
            'breakdown_keywords': ['breakdown', 'each', 'by type', 'per type', 'group by', 'summary']
        }
    
    def parse_query_filters(self, query: str) -> Dict[str, Any]:
        """Parse query to extract filters and conditions."""
        query_lower = query.lower()
        filters = {
            'state': None,
            'instance_type': None,
            'count_only': False,
            'breakdown_by': None,
            'specific_filters': []
        }
        
        # Check if this is a count query
        if any(keyword in query_lower for keyword in self.filter_patterns['count_keywords']):
            filters['count_only'] = True
        
        # Check if this is a breakdown query
        if any(keyword in query_lower for keyword in self.filter_patterns['breakdown_keywords']):
            filters['breakdown_by'] = 'instance_type'  # Default breakdown
            filters['count_only'] = True  # Breakdown queries are inherently count queries
            
            # Determine what to break down by
            if any(keyword in query_lower for keyword in ['instance type', 'type']):
                filters['breakdown_by'] = 'instance_type'
            elif any(keyword in query_lower for keyword in ['state', 'status']):
                filters['breakdown_by'] = 'state'
            elif any(keyword in query_lower for keyword in ['region', 'az', 'availability zone']):
                filters['breakdown_by'] = 'availability_zone'
        
        # Extract state filters (only if not a breakdown query)
        if not filters.get('breakdown_by'):
            for state, keywords in self.filter_patterns['state'].items():
                if any(keyword in query_lower for keyword in keywords):
                    filters['state'] = state
                    break
        
        # Extract instance type filters (only if not a breakdown query)
        if not filters.get('breakdown_by'):
            for instance_type, keywords in self.filter_patterns['instance_type'].items():
                if any(keyword in query_lower for keyword in keywords):
                    filters['instance_type'] = instance_type
                    break
        
        # Extract specific instance type patterns (e.g., t3.medium, m5.large)
        instance_type_pattern = r'[tm]\d+\.[a-z]+'
        matches = re.findall(instance_type_pattern, query_lower)
        if matches and not filters.get('breakdown_by'):
            filters['specific_instance_type'] = matches[0]
        
        return filters

    def filter_ec2_instances(self, instances: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filter EC2 instances based on parsed filters."""
        filtered_instances = instances
        
        # Filter by state
        if filters.get('state'):
            filtered_instances = [
                instance for instance in filtered_instances
                if instance.get('State', '').lower() == filters['state']
            ]
        
        # Filter by instance type
        if filters.get('instance_type'):
            type_keywords = self.filter_patterns['instance_type'][filters['instance_type']]
            filtered_instances = [
                instance for instance in filtered_instances
                if any(keyword in instance.get('InstanceType', '').lower() for keyword in type_keywords)
            ]
        
        # Filter by specific instance type
        if filters.get('specific_instance_type'):
            filtered_instances = [
                instance for instance in filtered_instances
                if instance.get('InstanceType', '').lower() == filters['specific_instance_type']
            ]
        
        return filtered_instances

    def generate_breakdown(self, instances: List[Dict], breakdown_by: str) -> Dict[str, Any]:
        """Generate breakdown statistics for instances."""
        breakdown = {}
        
        if breakdown_by == 'instance_type':
            for instance in instances:
                instance_type = instance.get('InstanceType', 'unknown')
                breakdown[instance_type] = breakdown.get(instance_type, 0) + 1
        
        elif breakdown_by == 'state':
            for instance in instances:
                state = instance.get('State', 'unknown')
                breakdown[state] = breakdown.get(state, 0) + 1
        
        elif breakdown_by == 'availability_zone':
            for instance in instances:
                az = instance.get('Placement', {}).get('AvailabilityZone', 'unknown')
                breakdown[az] = breakdown.get(az, 0) + 1
        
        return breakdown

    def get_ec2_resources(self, instance_ids: Optional[List[str]] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get EC2 instances and related resources with optional filtering."""
        try:
            all_instances = self.aws_client.get_ec2_instances(instance_ids)
            instances = all_instances
            
            # Apply filters if provided (but not for breakdown queries)
            if filters and not filters.get('breakdown_by'):
                instances = self.filter_ec2_instances(instances, filters)
            
            # Get security groups for the instances
            sg_ids = []
            for instance in instances:
                sg_ids.extend(instance.get('SecurityGroups', []))
            
            security_groups = []
            if sg_ids:
                security_groups = self.aws_client.get_security_groups(list(set(sg_ids)))
            
            # Prepare response based on whether it's a breakdown query
            response = {
                'service': 'ec2',
                'instances': instances,
                'security_groups': security_groups,
                'count': len(instances)
            }
            
            # Add filter information to response
            if filters:
                response['applied_filters'] = {k: v for k, v in filters.items() if v is not None and v != False}
                
                # Handle breakdown queries
                if filters.get('breakdown_by'):
                    breakdown = self.generate_breakdown(all_instances, filters['breakdown_by'])
                    response['breakdown'] = breakdown
                    response['breakdown_by'] = filters['breakdown_by']
                    response['total_instances'] = len(all_instances)
                    
                    # For breakdown queries, we don't need the full instance list
                    response['instances'] = []
                else:
                    # Add state breakdown for better insights (non-breakdown queries)
                    state_breakdown = {}
                    for instance in all_instances:
                        state = instance.get('State', 'unknown')
                        state_breakdown[state] = state_breakdown.get(state, 0) + 1
                    response['state_breakdown'] = state_breakdown
            
            return response
            
        except Exception as e:
            logger.error(f"Error retrieving EC2 resources: {e}")
            return {'error': str(e), 'service': 'ec2'}
    
    def get_s3_resources(self) -> Dict[str, Any]:
        """Get S3 bucket information."""
        try:
            buckets = self.aws_client.get_s3_buckets()
            return {
                'service': 's3',
                'buckets': buckets,
                'count': len(buckets)
            }
        except Exception as e:
            logger.error(f"Error retrieving S3 resources: {e}")
            return {'error': str(e), 'service': 's3'}
    
    def get_load_balancer_resources(self) -> Dict[str, Any]:
        """Get load balancer information."""
        try:
            load_balancers = self.aws_client.get_load_balancers()
            return {
                'service': 'load_balancers',
                'application_network_lbs': load_balancers['application_network'],
                'classic_lbs': load_balancers['classic'],
                'alb_nlb_count': len(load_balancers['application_network']),
                'classic_count': len(load_balancers['classic'])
            }
        except Exception as e:
            logger.error(f"Error retrieving load balancer resources: {e}")
            return {'error': str(e), 'service': 'load_balancers'}
    
    def get_efs_resources(self) -> Dict[str, Any]:
        """Get EFS filesystem information."""
        try:
            filesystems = self.aws_client.get_efs_filesystems()
            return {
                'service': 'efs',
                'filesystems': filesystems,
                'count': len(filesystems)
            }
        except Exception as e:
            logger.error(f"Error retrieving EFS resources: {e}")
            return {'error': str(e), 'service': 'efs'}
    
    def get_security_group_details(self, group_ids: List[str]) -> Dict[str, Any]:
        """Get detailed security group information."""
        try:
            security_groups = self.aws_client.get_security_groups(group_ids)
            return {
                'service': 'security_groups',
                'security_groups': security_groups,
                'count': len(security_groups)
            }
        except Exception as e:
            logger.error(f"Error retrieving security group details: {e}")
            return {'error': str(e), 'service': 'security_groups'}
    
    def detect_service_from_query(self, query: str) -> Optional[str]:
        """Detect which AWS service is being requested from the query."""
        query_lower = query.lower()
        
        # Score each service based on keyword matches
        service_scores = {}
        for service, config in self.service_mappings.items():
            score = 0
            for keyword in config['keywords']:
                if keyword in query_lower:
                    score += 1
            if score > 0:
                service_scores[service] = score
        
        # Return the service with the highest score
        if service_scores:
            return max(service_scores.keys(), key=lambda x: service_scores[x])
        
        return None
    
    def get_generic_aws_resources(self, service: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generic method to get AWS resources for any service."""
        try:
            if service not in self.service_mappings:
                return {
                    'error': f'Service {service} not supported yet',
                    'service': service,
                    'suggestion': 'Try: ' + ', '.join(self.service_mappings.keys())
                }
            
            config = self.service_mappings[service]
            methods = config['methods']
            
            # Try each method until one works
            for method_name in methods:
                if hasattr(self.aws_client, method_name):
                    method = getattr(self.aws_client, method_name)
                    try:
                        if service == 'ec2' and filters:
                            # Special handling for EC2 with filters
                            return self.get_ec2_resources(filters=filters)
                        else:
                            # Generic resource retrieval
                            resources = method()
                            
                            # Apply basic filtering if needed
                            if filters and filters.get('count_only'):
                                return {
                                    'service': service,
                                    'count': len(resources),
                                    'query_interpretation': {
                                        'detected_service': service,
                                        'applied_filters': filters
                                    }
                                }
                            
                            return {
                                'service': service,
                                'resources': resources,
                                'count': len(resources)
                            }
                    except Exception as e:
                        logger.warning(f"Method {method_name} failed for {service}: {e}")
                        continue
            
            # If no method worked, return error
            return {
                'error': f'Failed to retrieve {service} resources',
                'service': service
            }
            
        except Exception as e:
            logger.error(f"Error retrieving {service} resources: {e}")
            return {'error': str(e), 'service': service}
    
    def get_vpc_resources(self) -> Dict[str, Any]:
        """Get VPC information."""
        try:
            vpcs = self.aws_client.get_vpcs()
            return {
                'service': 'vpc',
                'vpcs': vpcs,
                'count': len(vpcs)
            }
        except Exception as e:
            logger.error(f"Error retrieving VPC resources: {e}")
            return {'error': str(e), 'service': 'vpc'}
    
    def get_subnet_resources(self) -> Dict[str, Any]:
        """Get subnet information."""
        try:
            subnets = self.aws_client.get_subnets()
            return {
                'service': 'subnet',
                'subnets': subnets,
                'count': len(subnets)
            }
        except Exception as e:
            logger.error(f"Error retrieving subnet resources: {e}")
            return {'error': str(e), 'service': 'subnet'}
    
    def get_volume_resources(self) -> Dict[str, Any]:
        """Get EBS volume information."""
        try:
            volumes = self.aws_client.get_volumes()
            return {
                'service': 'ebs',
                'volumes': volumes,
                'count': len(volumes)
            }
        except Exception as e:
            logger.error(f"Error retrieving EBS volume resources: {e}")
            return {'error': str(e), 'service': 'ebs'}
    
    def get_lambda_resources(self) -> Dict[str, Any]:
        """Get Lambda function information."""
        try:
            functions = self.aws_client.get_lambda_functions()
            return {
                'service': 'lambda',
                'functions': functions,
                'count': len(functions)
            }
        except Exception as e:
            logger.error(f"Error retrieving Lambda resources: {e}")
            return {'error': str(e), 'service': 'lambda'}
    
    def get_rds_resources(self) -> Dict[str, Any]:
        """Get RDS instance information."""
        try:
            instances = self.aws_client.get_rds_instances()
            return {
                'service': 'rds',
                'instances': instances,
                'count': len(instances)
            }
        except Exception as e:
            logger.error(f"Error retrieving RDS resources: {e}")
            return {'error': str(e), 'service': 'rds'}
    
    def process_request(self, request: str) -> Dict[str, Any]:
        """Process AWS resource information requests with intelligent service detection."""
        request_lower = request.lower()
        
        # Parse query for filters and conditions
        filters = self.parse_query_filters(request)
        
        # Use dynamic service detection
        detected_service = self.detect_service_from_query(request)
        
        # If breakdown query without explicit service, default to EC2
        if filters.get('breakdown_by') and not detected_service:
            detected_service = 'ec2'
        
        if detected_service:
            # Use the generic resource retrieval method
            result = self.get_generic_aws_resources(detected_service, filters)
            
            # Add query interpretation
            result['query_interpretation'] = {
                'original_query': request,
                'detected_service': detected_service,
                'detected_filters': filters
            }
            
            # Handle special response formats for specific query types
            if filters.get('breakdown_by') and 'breakdown' in result:
                return {
                    'service': detected_service,
                    'query': request,
                    'breakdown': result['breakdown'],
                    'breakdown_by': result['breakdown_by'],
                    'total_instances': result.get('total_instances', result.get('count', 0)),
                    'query_interpretation': result['query_interpretation']
                }
            
            elif filters.get('count_only') and not filters.get('breakdown_by'):
                count_response = {
                    'service': detected_service,
                    'query': request,
                    'count': result.get('count', 0),
                    'query_interpretation': result['query_interpretation']
                }
                
                # Add additional breakdown info if available
                if 'state_breakdown' in result:
                    count_response['state_breakdown'] = result['state_breakdown']
                
                return count_response
            
            return result
        
        else:
            # No service detected - provide helpful guidance
            return {
                'message': 'I can help you query any AWS service! Please specify which AWS resource you want to query.',
                'supported_services': list(self.service_mappings.keys()),
                'examples': [
                    # EC2 examples
                    'How many EC2 instances do I have?',
                    'Show me running instances',
                    'Breakdown by instance type',
                    
                    # VPC examples  
                    'How many VPCs do I have?',
                    'List my VPCs',
                    'Show me subnets',
                    
                    # Storage examples
                    'Count my S3 buckets',
                    'How many EBS volumes?',
                    'List EFS filesystems',
                    
                    # Database examples
                    'Show me RDS instances',
                    'How many databases?',
                    
                    # Compute examples
                    'List Lambda functions',
                    'How many serverless functions?',
                    
                    # Networking examples
                    'Show security groups',
                    'List load balancers',
                    'How many NAT gateways?'
                ],
                'service_categories': {
                    'Compute': ['ec2', 'lambda'],
                    'Networking': ['vpc', 'subnet', 'security_group', 'load_balancer', 'nat_gateway', 'internet_gateway'],
                    'Storage': ['s3', 'ebs', 'efs', 'snapshot'],
                    'Database': ['rds']
                },
                'tip': 'Try asking about any AWS service like: "How many [service] do I have?" or "Show me [service]"'
            }
    
    def run(self, input_data: str) -> str:
        """Main entry point for the agent."""
        try:
            result = self.process_request(input_data)
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"AWS Resource Agent error: {e}")
            return json.dumps({
                'error': f'AWS Resource Agent encountered an error: {str(e)}',
                'input': input_data
            }, indent=2)