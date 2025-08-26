"""AWS client utilities for resource management."""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Dict, List, Any, Optional
import logging
from config.settings import AWS_REGION, AWS_PROFILE

logger = logging.getLogger(__name__)

class AWSClientManager:
    """Manages AWS service clients and common operations."""
    
    def __init__(self, region: str = AWS_REGION, profile: str = AWS_PROFILE):
        self.region = region
        self.profile = profile
        self._clients = {}
        
    def get_client(self, service_name: str):
        """Get or create AWS service client."""
        if service_name not in self._clients:
            try:
                session = boto3.Session(profile_name=self.profile)
                self._clients[service_name] = session.client(service_name, region_name=self.region)
            except (ClientError, NoCredentialsError) as e:
                logger.error(f"Failed to create {service_name} client: {e}")
                raise
        return self._clients[service_name]
    
    def get_ec2_instances(self, instance_ids: Optional[List[str]] = None) -> List[Dict]:
        """Retrieve EC2 instance information."""
        try:
            ec2 = self.get_client('ec2')
            if instance_ids:
                response = ec2.describe_instances(InstanceIds=instance_ids)
            else:
                response = ec2.describe_instances()
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'InstanceId': instance['InstanceId'],
                        'State': instance['State']['Name'],
                        'InstanceType': instance['InstanceType'],
                        'PublicIpAddress': instance.get('PublicIpAddress'),
                        'PrivateIpAddress': instance.get('PrivateIpAddress'),
                        'VpcId': instance.get('VpcId'),
                        'SubnetId': instance.get('SubnetId'),
                        'SecurityGroups': [sg['GroupId'] for sg in instance.get('SecurityGroups', [])]
                    })
            return instances
        except ClientError as e:
            logger.error(f"Error retrieving EC2 instances: {e}")
            return []
    
    def get_security_groups(self, group_ids: Optional[List[str]] = None) -> List[Dict]:
        """Retrieve security group information."""
        try:
            ec2 = self.get_client('ec2')
            if group_ids:
                response = ec2.describe_security_groups(GroupIds=group_ids)
            else:
                response = ec2.describe_security_groups()
            
            return response['SecurityGroups']
        except ClientError as e:
            logger.error(f"Error retrieving security groups: {e}")
            return []
    
    def get_load_balancers(self) -> Dict[str, List]:
        """Retrieve load balancer information (ALB/NLB and Classic)."""
        try:
            # Get ALB/NLB
            elbv2 = self.get_client('elbv2')
            alb_nlb_response = elbv2.describe_load_balancers()
            
            # Get Classic ELB
            elb = self.get_client('elb')
            classic_response = elb.describe_load_balancers()
            
            return {
                'application_network': alb_nlb_response['LoadBalancers'],
                'classic': classic_response['LoadBalancerDescriptions']
            }
        except ClientError as e:
            logger.error(f"Error retrieving load balancers: {e}")
            return {'application_network': [], 'classic': []}
    
    def get_s3_buckets(self) -> List[Dict]:
        """Retrieve S3 bucket information."""
        try:
            s3 = self.get_client('s3')
            response = s3.list_buckets()
            return response['Buckets']
        except ClientError as e:
            logger.error(f"Error retrieving S3 buckets: {e}")
            return []
    
    def get_efs_filesystems(self) -> List[Dict]:
        """Retrieve EFS filesystem information."""
        try:
            efs = self.get_client('efs')
            response = efs.describe_file_systems()
            return response['FileSystems']
        except ClientError as e:
            logger.error(f"Error retrieving EFS filesystems: {e}")
            return []
    
    def get_vpcs(self) -> List[Dict]:
        """Retrieve VPC information."""
        try:
            ec2 = self.get_client('ec2')
            response = ec2.describe_vpcs()
            return response['Vpcs']
        except ClientError as e:
            logger.error(f"Error retrieving VPCs: {e}")
            return []
    
    def get_subnets(self) -> List[Dict]:
        """Retrieve subnet information."""
        try:
            ec2 = self.get_client('ec2')
            response = ec2.describe_subnets()
            return response['Subnets']
        except ClientError as e:
            logger.error(f"Error retrieving subnets: {e}")
            return []
    
    def get_route_tables(self) -> List[Dict]:
        """Retrieve route table information."""
        try:
            ec2 = self.get_client('ec2')
            response = ec2.describe_route_tables()
            return response['RouteTables']
        except ClientError as e:
            logger.error(f"Error retrieving route tables: {e}")
            return []
    
    def get_internet_gateways(self) -> List[Dict]:
        """Retrieve internet gateway information."""
        try:
            ec2 = self.get_client('ec2')
            response = ec2.describe_internet_gateways()
            return response['InternetGateways']
        except ClientError as e:
            logger.error(f"Error retrieving internet gateways: {e}")
            return []
    
    def get_nat_gateways(self) -> List[Dict]:
        """Retrieve NAT gateway information."""
        try:
            ec2 = self.get_client('ec2')
            response = ec2.describe_nat_gateways()
            return response['NatGateways']
        except ClientError as e:
            logger.error(f"Error retrieving NAT gateways: {e}")
            return []
    
    def get_volumes(self) -> List[Dict]:
        """Retrieve EBS volume information."""
        try:
            ec2 = self.get_client('ec2')
            response = ec2.describe_volumes()
            return response['Volumes']
        except ClientError as e:
            logger.error(f"Error retrieving EBS volumes: {e}")
            return []
    
    def get_snapshots(self, owner_ids: Optional[List[str]] = None) -> List[Dict]:
        """Retrieve EBS snapshot information."""
        try:
            ec2 = self.get_client('ec2')
            if owner_ids:
                response = ec2.describe_snapshots(OwnerIds=owner_ids)
            else:
                response = ec2.describe_snapshots(OwnerIds=['self'])
            return response['Snapshots']
        except ClientError as e:
            logger.error(f"Error retrieving EBS snapshots: {e}")
            return []
    
    def get_rds_instances(self) -> List[Dict]:
        """Retrieve RDS instance information."""
        try:
            rds = self.get_client('rds')
            response = rds.describe_db_instances()
            return response['DBInstances']
        except ClientError as e:
            logger.error(f"Error retrieving RDS instances: {e}")
            return []
    
    def get_lambda_functions(self) -> List[Dict]:
        """Retrieve Lambda function information."""
        try:
            lambda_client = self.get_client('lambda')
            response = lambda_client.list_functions()
            return response['Functions']
        except ClientError as e:
            logger.error(f"Error retrieving Lambda functions: {e}")
            return []
    
    def generic_aws_describe(self, service: str, operation: str, response_key: str = None) -> List[Dict]:
        """Generic method to call any AWS describe operation."""
        try:
            client = self.get_client(service)
            
            # Get the operation method
            if hasattr(client, operation):
                operation_method = getattr(client, operation)
                response = operation_method()
                
                # Try to extract the relevant data
                if response_key and response_key in response:
                    return response[response_key]
                else:
                    # Try common response keys
                    common_keys = [
                        'Items', 'Resources', 'Results', 'Data', 'Objects',
                        'Instances', 'Functions', 'Buckets', 'Volumes', 'Vpcs',
                        'Subnets', 'SecurityGroups', 'LoadBalancers', 'Clusters'
                    ]
                    for key in common_keys:
                        if key in response:
                            return response[key]
                    
                    # If no common key found, return the whole response
                    return [response] if isinstance(response, dict) else response
            else:
                logger.error(f"Operation {operation} not found for service {service}")
                return []
                
        except ClientError as e:
            logger.error(f"Error calling {service}.{operation}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error calling {service}.{operation}: {e}")
            return []