"""Configuration settings for the multi-agent system."""

import os
from typing import Dict, Any

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
AWS_PROFILE = os.getenv('AWS_PROFILE', 'default')

# Agent Configuration
AGENT_CONFIG = {
    'orchestrator': {
        'name': 'AWS Infrastructure Orchestrator',
        'description': 'Routes requests to appropriate specialized agents'
    },
    'aws_resource': {
        'name': 'AWS Resource Agent',
        'description': 'Retrieves AWS resource information and attributes'
    },
    'network_troubleshoot': {
        'name': 'Network Troubleshoot Agent',
        'description': 'Diagnoses and provides solutions for network connectivity issues'
    }
}

# Supported AWS Services
SUPPORTED_AWS_SERVICES = [
    'ec2', 's3', 'ebs', 'vpc', 'nlb', 'alb', 'elb', 
    'eks', 'cloudwatch', 'cloudtrail', 'efs', 
    'security-groups', 'subnets', 'route-tables'
]

# Network troubleshooting categories
NETWORK_CATEGORIES = [
    'ec2-connectivity', 'load-balancer-issues', 
    'storage-connectivity', 'dns-resolution', 
    'security-group-rules', 'routing-issues'
]