"""Network Troubleshoot Agent - Diagnoses and provides solutions for network connectivity issues."""

from utils.base_agent import Agent
from typing import Dict, List, Any, Optional
import json
import logging
from utils.network_utils import NetworkTroubleshooter
from utils.aws_client import AWSClientManager
from config.settings import NETWORK_CATEGORIES

logger = logging.getLogger(__name__)

class NetworkTroubleshootAgent(Agent):
    """Agent specialized in diagnosing network connectivity issues."""
    
    def __init__(self):
        super().__init__(
            name="Network Troubleshoot Agent",
            description="Diagnoses and provides solutions for network connectivity issues including EC2 communication, Load Balancer connections, and storage connectivity"
        )
        self.network_troubleshooter = NetworkTroubleshooter()
        self.aws_client = AWSClientManager()
    
    def diagnose_ec2_connectivity_issues(self, instance_id: Optional[str] = None) -> Dict[str, Any]:
        """Diagnose EC2 connectivity issues."""
        try:
            # Get EC2 instance information
            if instance_id:
                instances = self.aws_client.get_ec2_instances([instance_id])
            else:
                instances = self.aws_client.get_ec2_instances()
            
            if not instances:
                return {
                    'error': 'No EC2 instances found',
                    'suggestion': 'Please check if the instance ID is correct or if you have proper permissions'
                }
            
            diagnostics = []
            for instance in instances:
                instance_diagnostics = self.network_troubleshooter.diagnose_ec2_connectivity(instance)
                
                # Add security group analysis
                sg_ids = instance.get('SecurityGroups', [])
                if sg_ids:
                    security_groups = self.aws_client.get_security_groups(sg_ids)
                    instance_diagnostics['security_group_analysis'] = self._analyze_security_groups(security_groups)
                
                diagnostics.append(instance_diagnostics)
            
            return {
                'service': 'ec2_connectivity',
                'diagnostics': diagnostics,
                'recommendations': self._get_ec2_recommendations(diagnostics)
            }
        except Exception as e:
            logger.error(f"Error diagnosing EC2 connectivity: {e}")
            return {'error': str(e), 'service': 'ec2_connectivity'}
    
    def diagnose_load_balancer_issues(self, lb_dns: Optional[str] = None) -> Dict[str, Any]:
        """Diagnose load balancer connectivity issues."""
        try:
            if not lb_dns:
                # Get all load balancers
                load_balancers = self.aws_client.get_load_balancers()
                lb_list = []
                
                # Extract DNS names from ALB/NLB
                for lb in load_balancers['application_network']:
                    lb_list.append(lb['DNSName'])
                
                # Extract DNS names from Classic ELB
                for lb in load_balancers['classic']:
                    lb_list.append(lb['DNSName'])
                
                if not lb_list:
                    return {
                        'error': 'No load balancers found',
                        'suggestion': 'Please check if you have load balancers configured'
                    }
                
                # Diagnose first load balancer as example
                lb_dns = lb_list[0]
            
            diagnostics = self.network_troubleshooter.diagnose_load_balancer_connectivity(lb_dns)
            
            return {
                'service': 'load_balancer_connectivity',
                'diagnostics': diagnostics,
                'recommendations': self._get_load_balancer_recommendations(diagnostics)
            }
        except Exception as e:
            logger.error(f"Error diagnosing load balancer connectivity: {e}")
            return {'error': str(e), 'service': 'load_balancer_connectivity'}
    
    def diagnose_storage_connectivity(self, storage_type: str = 'efs') -> Dict[str, Any]:
        """Diagnose storage connectivity issues (EFS, S3)."""
        try:
            if storage_type.lower() == 'efs':
                filesystems = self.aws_client.get_efs_filesystems()
                if not filesystems:
                    return {
                        'error': 'No EFS filesystems found',
                        'suggestion': 'Please check if you have EFS filesystems configured'
                    }
                
                diagnostics = []
                for fs in filesystems:
                    fs_diagnostics = {
                        'filesystem_id': fs['FileSystemId'],
                        'state': fs['LifeCycleState'],
                        'performance_mode': fs['PerformanceMode'],
                        'throughput_mode': fs['ThroughputMode']
                    }
                    
                    # Check mount targets
                    try:
                        efs_client = self.aws_client.get_client('efs')
                        mount_targets = efs_client.describe_mount_targets(FileSystemId=fs['FileSystemId'])
                        fs_diagnostics['mount_targets'] = mount_targets['MountTargets']
                    except Exception as e:
                        fs_diagnostics['mount_targets_error'] = str(e)
                    
                    diagnostics.append(fs_diagnostics)
                
                return {
                    'service': 'efs_connectivity',
                    'diagnostics': diagnostics,
                    'recommendations': self._get_efs_recommendations(diagnostics)
                }
            
            elif storage_type.lower() == 's3':
                # For S3, we mainly check endpoint connectivity
                s3_endpoints = [
                    f's3.{self.aws_client.region}.amazonaws.com',
                    f's3-{self.aws_client.region}.amazonaws.com'
                ]
                
                diagnostics = []
                for endpoint in s3_endpoints:
                    endpoint_diagnostics = {
                        'endpoint': endpoint,
                        'connectivity': self.network_troubleshooter.ping_host(endpoint),
                        'dns_resolution': self.network_troubleshooter.resolve_dns(endpoint)
                    }
                    diagnostics.append(endpoint_diagnostics)
                
                return {
                    'service': 's3_connectivity',
                    'diagnostics': diagnostics,
                    'recommendations': self._get_s3_recommendations(diagnostics)
                }
        except Exception as e:
            logger.error(f"Error diagnosing storage connectivity: {e}")
            return {'error': str(e), 'service': 'storage_connectivity'}
    
    def _analyze_security_groups(self, security_groups: List[Dict]) -> Dict[str, Any]:
        """Analyze security group rules for potential issues."""
        analysis = {
            'total_groups': len(security_groups),
            'issues': [],
            'recommendations': []
        }
        
        for sg in security_groups:
            # Check for overly permissive rules
            for rule in sg.get('IpPermissions', []):
                for ip_range in rule.get('IpRanges', []):
                    if ip_range.get('CidrIp') == '0.0.0.0/0':
                        analysis['issues'].append({
                            'type': 'overly_permissive',
                            'security_group': sg['GroupId'],
                            'rule': rule,
                            'message': f"Security group {sg['GroupId']} allows traffic from anywhere (0.0.0.0/0)"
                        })
        
        return analysis
    
    def _get_ec2_recommendations(self, diagnostics: List[Dict]) -> List[str]:
        """Generate recommendations based on EC2 diagnostics."""
        recommendations = []
        
        for diag in diagnostics:
            for test in diag.get('tests', []):
                if test.get('result', {}).get('status') == 'failed':
                    if 'ping' in test.get('test', ''):
                        recommendations.append("Check security group rules to ensure ICMP traffic is allowed")
                    elif 'port' in test.get('test', ''):
                        port = test.get('test', '').split('_')[1]
                        recommendations.append(f"Check security group rules for port {port} and ensure the service is running")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _get_load_balancer_recommendations(self, diagnostics: Dict) -> List[str]:
        """Generate recommendations based on load balancer diagnostics."""
        recommendations = []
        
        for test in diagnostics.get('tests', []):
            if test.get('result', {}).get('status') == 'failed':
                if 'dns' in test.get('test', ''):
                    recommendations.append("Check DNS configuration and ensure the load balancer exists")
                elif 'connectivity' in test.get('test', ''):
                    recommendations.append("Check security group rules and network ACLs for the load balancer")
        
        return recommendations
    
    def _get_efs_recommendations(self, diagnostics: List[Dict]) -> List[str]:
        """Generate recommendations based on EFS diagnostics."""
        recommendations = []
        
        for diag in diagnostics:
            if diag.get('state') != 'available':
                recommendations.append(f"EFS filesystem {diag.get('filesystem_id')} is not in available state")
            
            if not diag.get('mount_targets'):
                recommendations.append(f"No mount targets found for EFS filesystem {diag.get('filesystem_id')}")
        
        return recommendations
    
    def _get_s3_recommendations(self, diagnostics: List[Dict]) -> List[str]:
        """Generate recommendations based on S3 diagnostics."""
        recommendations = []
        
        for diag in diagnostics:
            if diag.get('connectivity', {}).get('status') == 'failed':
                recommendations.append("Check internet connectivity and DNS resolution for S3 endpoints")
        
        return recommendations
    
    def process_request(self, request: str) -> Dict[str, Any]:
        """Process network troubleshooting requests."""
        request_lower = request.lower()
        
        # Determine the type of network issue
        if any(keyword in request_lower for keyword in ['ec2', 'instance', 'server', 'ssh', 'connect']):
            return self.diagnose_ec2_connectivity_issues()
        
        elif any(keyword in request_lower for keyword in ['load balancer', 'alb', 'nlb', 'elb', 'lb']):
            return self.diagnose_load_balancer_issues()
        
        elif any(keyword in request_lower for keyword in ['efs', 'file system', 'filesystem', 'mount']):
            return self.diagnose_storage_connectivity('efs')
        
        elif any(keyword in request_lower for keyword in ['s3', 'bucket', 'storage']):
            return self.diagnose_storage_connectivity('s3')
        
        else:
            return {
                'message': 'Please specify which network issue you want to diagnose',
                'supported_categories': NETWORK_CATEGORIES,
                'examples': [
                    'Diagnose EC2 connectivity issues',
                    'Check load balancer connectivity',
                    'Troubleshoot EFS mount issues',
                    'Check S3 connectivity problems'
                ]
            }
    
    def run(self, input_data: str) -> str:
        """Main entry point for the agent."""
        try:
            result = self.process_request(input_data)
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"Network Troubleshoot Agent error: {e}")
            return json.dumps({
                'error': f'Network Troubleshoot Agent encountered an error: {str(e)}',
                'input': input_data
            }, indent=2)