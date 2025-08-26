"""Network utilities for troubleshooting connectivity issues."""

import socket
import subprocess
import json
from typing import Dict, List, Optional, Tuple, Any
import logging
import requests

# Try to import optional dependencies
try:
    from ping3 import ping
    PING3_AVAILABLE = True
except ImportError:
    PING3_AVAILABLE = False
    ping = None

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

logger = logging.getLogger(__name__)

class NetworkTroubleshooter:
    """Network troubleshooting utilities."""
    
    def __init__(self):
        self.timeout = 10
    
    def ping_host(self, host: str) -> Dict[str, Any]:
        """Ping a host and return connectivity status."""
        if not PING3_AVAILABLE:
            # Fallback to system ping command
            try:
                result = subprocess.run(['ping', '-c', '1', '-W', '3', host], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return {
                        'status': 'success',
                        'host': host,
                        'response_time': 'N/A',
                        'message': f'Host {host} is reachable (system ping)'
                    }
                else:
                    return {
                        'status': 'failed',
                        'host': host,
                        'response_time': None,
                        'message': f'Host {host} is not reachable (system ping)'
                    }
            except Exception as e:
                return {
                    'status': 'error',
                    'host': host,
                    'error': str(e),
                    'message': f'Error pinging {host}: {e}'
                }
        
        try:
            response_time = ping(host, timeout=self.timeout)
            if response_time is not None:
                return {
                    'status': 'success',
                    'host': host,
                    'response_time': response_time,
                    'message': f'Host {host} is reachable'
                }
            else:
                return {
                    'status': 'failed',
                    'host': host,
                    'response_time': None,
                    'message': f'Host {host} is not reachable'
                }
        except Exception as e:
            return {
                'status': 'error',
                'host': host,
                'error': str(e),
                'message': f'Error pinging {host}: {e}'
            }
    
    def check_port_connectivity(self, host: str, port: int) -> Dict[str, Any]:
        """Check if a specific port is open on a host."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                return {
                    'status': 'open',
                    'host': host,
                    'port': port,
                    'message': f'Port {port} is open on {host}'
                }
            else:
                return {
                    'status': 'closed',
                    'host': host,
                    'port': port,
                    'message': f'Port {port} is closed on {host}'
                }
        except Exception as e:
            return {
                'status': 'error',
                'host': host,
                'port': port,
                'error': str(e),
                'message': f'Error checking port {port} on {host}: {e}'
            }
    
    def resolve_dns(self, hostname: str) -> Dict[str, Any]:
        """Resolve DNS for a hostname."""
        if not DNS_AVAILABLE:
            # Fallback to socket.gethostbyname
            try:
                ip_address = socket.gethostbyname(hostname)
                return {
                    'status': 'success',
                    'hostname': hostname,
                    'ip_addresses': [ip_address],
                    'message': f'DNS resolution successful for {hostname} (socket fallback)'
                }
            except Exception as e:
                return {
                    'status': 'failed',
                    'hostname': hostname,
                    'error': str(e),
                    'message': f'DNS resolution failed for {hostname}: {e}'
                }
        
        try:
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(hostname, 'A')
            ip_addresses = [str(answer) for answer in answers]
            
            return {
                'status': 'success',
                'hostname': hostname,
                'ip_addresses': ip_addresses,
                'message': f'DNS resolution successful for {hostname}'
            }
        except Exception as e:
            return {
                'status': 'failed',
                'hostname': hostname,
                'error': str(e),
                'message': f'DNS resolution failed for {hostname}: {e}'
            }
    
    def trace_route(self, host: str) -> Dict[str, Any]:
        """Perform traceroute to a host."""
        try:
            # Use traceroute command (Linux/Mac) or tracert (Windows)
            cmd = ['traceroute', '-n', host]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'host': host,
                    'trace': result.stdout,
                    'message': f'Traceroute to {host} completed'
                }
            else:
                return {
                    'status': 'failed',
                    'host': host,
                    'error': result.stderr,
                    'message': f'Traceroute to {host} failed'
                }
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'host': host,
                'message': f'Traceroute to {host} timed out'
            }
        except Exception as e:
            return {
                'status': 'error',
                'host': host,
                'error': str(e),
                'message': f'Error running traceroute to {host}: {e}'
            }
    
    def diagnose_ec2_connectivity(self, instance_info: Dict) -> Dict[str, Any]:
        """Diagnose EC2 instance connectivity issues."""
        diagnostics = {
            'instance_id': instance_info.get('InstanceId'),
            'tests': []
        }
        
        # Check if instance is running
        if instance_info.get('State') != 'running':
            diagnostics['tests'].append({
                'test': 'instance_state',
                'status': 'warning',
                'message': f"Instance is in '{instance_info.get('State')}' state, not running"
            })
            return diagnostics
        
        # Test connectivity to public IP if available
        public_ip = instance_info.get('PublicIpAddress')
        if public_ip:
            ping_result = self.ping_host(public_ip)
            diagnostics['tests'].append({
                'test': 'public_ip_ping',
                'result': ping_result
            })
        
        # Test common ports (SSH, HTTP, HTTPS)
        common_ports = [22, 80, 443]
        for port in common_ports:
            if public_ip:
                port_result = self.check_port_connectivity(public_ip, port)
                diagnostics['tests'].append({
                    'test': f'port_{port}_connectivity',
                    'result': port_result
                })
        
        return diagnostics
    
    def diagnose_load_balancer_connectivity(self, lb_dns: str) -> Dict[str, Any]:
        """Diagnose load balancer connectivity issues."""
        diagnostics = {
            'load_balancer_dns': lb_dns,
            'tests': []
        }
        
        # DNS resolution
        dns_result = self.resolve_dns(lb_dns)
        diagnostics['tests'].append({
            'test': 'dns_resolution',
            'result': dns_result
        })
        
        # Ping test
        ping_result = self.ping_host(lb_dns)
        diagnostics['tests'].append({
            'test': 'ping_connectivity',
            'result': ping_result
        })
        
        # HTTP/HTTPS connectivity
        for port, protocol in [(80, 'http'), (443, 'https')]:
            port_result = self.check_port_connectivity(lb_dns, port)
            diagnostics['tests'].append({
                'test': f'{protocol}_port_connectivity',
                'result': port_result
            })
        
        return diagnostics