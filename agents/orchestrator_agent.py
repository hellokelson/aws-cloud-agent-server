"""Enhanced Orchestrator Agent - Routes requests with intelligent fallback and learning capabilities."""

from utils.base_agent import Agent
from typing import Dict, List, Any, Optional
import json
import logging
import os
from datetime import datetime
from agents.aws_resource_agent import AWSResourceAgent
from agents.network_troubleshoot_agent import NetworkTroubleshootAgent
from agents.general_llm_agent import GeneralLLMAgent
from config.settings import AGENT_CONFIG, SUPPORTED_AWS_SERVICES, NETWORK_CATEGORIES

logger = logging.getLogger(__name__)

class OrchestratorAgent(Agent):
    """Main orchestrator agent that routes requests to specialized agents."""
    
    def __init__(self):
        super().__init__(
            name="AWS Infrastructure Orchestrator",
            description="Routes customer requests to appropriate specialized agents for AWS resource information or network troubleshooting"
        )
        
        # Initialize specialized agents as tools
        self.aws_resource_agent = AWSResourceAgent()
        self.network_troubleshoot_agent = NetworkTroubleshootAgent()
        self.general_llm_agent = GeneralLLMAgent()
        
        # Define available tools
        self.tools = {
            'aws_resource_tool': {
                'agent': self.aws_resource_agent,
                'description': 'Retrieves AWS resource information and attributes',
                'keywords': ['ec2', 's3', 'ebs', 'vpc', 'nlb', 'alb', 'elb', 'eks', 
                           'cloudwatch', 'cloudtrail', 'efs', 'security', 'group', 
                           'instance', 'bucket', 'load', 'balancer', 'filesystem',
                           'resource', 'list', 'show', 'get', 'describe', 'info',
                           'breakdown', 'count', 'each', 'type', 'state', 'summary',
                           'how many', 'total', 'running', 'stopped', 'micro', 'small',
                           'subnet', 'lambda', 'function', 'rds', 'database', 'volume',
                           'snapshot', 'gateway', 'route', 'services', 'aws']
            },
            'network_troubleshoot_tool': {
                'agent': self.network_troubleshoot_agent,
                'description': 'Diagnoses and provides solutions for network connectivity issues',
                'keywords': ['connectivity', 'connection', 'network', 'troubleshoot', 
                           'diagnose', 'ping', 'port', 'dns', 'resolve', 'trace',
                           'issue', 'problem', 'error', 'fail', 'timeout', 'unreachable',
                           'mount', 'access', 'communication', 'ssh', 'http', 'https']
            },
            'general_llm_tool': {
                'agent': self.general_llm_agent,
                'description': 'Handles any question using advanced language model capabilities',
                'keywords': [],  # No specific keywords - this is the fallback agent
                'is_fallback': True
            }
        }
        
        # Configuration for routing decisions
        self.routing_config = {
            'min_confidence_threshold': 0.5,  # Minimum confidence to use specialized agent
            'min_keyword_matches': 2,  # Minimum keyword matches for specialized agent
            'enable_fallback': True,  # Whether to use general LLM as fallback
            'fallback_for_errors': True,  # Use fallback when specialized agents error
            'validate_responses': True,  # Validate if specialized agent responses are relevant
            'enable_learning': True  # Enable learning from routing mistakes
        }
        
        # Learning and feedback system
        self.feedback_log_file = 'orchestrator_feedback.json'
        self.routing_history = []
        self.load_feedback_history()
    
    def load_feedback_history(self):
        """Load previous feedback and routing history for learning."""
        try:
            if os.path.exists(self.feedback_log_file):
                with open(self.feedback_log_file, 'r') as f:
                    data = json.load(f)
                    self.routing_history = data.get('routing_history', [])
                    logger.info(f"Loaded {len(self.routing_history)} routing history entries")
        except Exception as e:
            logger.warning(f"Could not load feedback history: {e}")
            self.routing_history = []
    
    def save_feedback_history(self):
        """Save routing history and feedback for future learning."""
        try:
            data = {
                'routing_history': self.routing_history[-1000:],  # Keep last 1000 entries
                'last_updated': datetime.now().isoformat()
            }
            with open(self.feedback_log_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Could not save feedback history: {e}")
    
    def log_routing_decision(self, request: str, selected_tool: str, confidence: float, 
                           is_fallback: bool, success: bool, fallback_reason: str = None):
        """Log routing decisions for learning and improvement."""
        if not self.routing_config['enable_learning']:
            return
            
        entry = {
            'timestamp': datetime.now().isoformat(),
            'request': request,
            'selected_tool': selected_tool,
            'confidence': confidence,
            'is_fallback': is_fallback,
            'success': success,
            'fallback_reason': fallback_reason
        }
        
        self.routing_history.append(entry)
        
        # Save periodically
        if len(self.routing_history) % 10 == 0:
            self.save_feedback_history()
    
    def validate_response_relevance(self, request: str, response: Dict[str, Any], 
                                  selected_tool: str) -> Dict[str, Any]:
        """Validate if the specialized agent response is relevant to the user's question."""
        if not self.routing_config['validate_responses']:
            return {'is_relevant': True, 'confidence': 1.0}
        
        # Basic validation rules for different agent types
        validation_result = {'is_relevant': True, 'confidence': 1.0, 'reasons': []}
        
        try:
            if selected_tool == 'aws_resource_tool':
                # Check if AWS resource agent returned meaningful data
                if 'error' in response:
                    validation_result['is_relevant'] = False
                    validation_result['confidence'] = 0.0
                    validation_result['reasons'].append('Agent returned error')
                elif response.get('count') == 0 and 'how many' in request.lower():
                    # This might be valid (user has 0 resources)
                    validation_result['confidence'] = 0.8
                elif not response.get('service') and not response.get('resources'):
                    validation_result['is_relevant'] = False
                    validation_result['confidence'] = 0.2
                    validation_result['reasons'].append('No service or resources in response')
            
            elif selected_tool == 'network_troubleshoot_tool':
                # Check if network troubleshoot agent provided useful information
                if 'error' in response:
                    validation_result['is_relevant'] = False
                    validation_result['confidence'] = 0.0
                    validation_result['reasons'].append('Agent returned error')
                elif not response.get('diagnostics') and not response.get('recommendations'):
                    validation_result['is_relevant'] = False
                    validation_result['confidence'] = 0.3
                    validation_result['reasons'].append('No diagnostics or recommendations provided')
        
        except Exception as e:
            logger.warning(f"Error validating response relevance: {e}")
            validation_result['confidence'] = 0.5  # Uncertain
        
        return validation_result
    
    def analyze_request_intent(self, request: str) -> Dict[str, Any]:
        """Analyze the customer request to determine intent and appropriate tool."""
        request_lower = request.lower()
        
        # Score each specialized tool based on keyword matches (exclude fallback tools)
        tool_scores = {}
        specialized_tools = {k: v for k, v in self.tools.items() if not v.get('is_fallback', False)}
        
        for tool_name, tool_info in specialized_tools.items():
            score = 0
            matched_keywords = []
            
            for keyword in tool_info['keywords']:
                if keyword in request_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            tool_scores[tool_name] = {
                'score': score,
                'matched_keywords': matched_keywords,
                'description': tool_info['description']
            }
        
        # Determine the best specialized tool
        if tool_scores:
            best_tool = max(tool_scores.keys(), key=lambda x: tool_scores[x]['score'])
            best_score = tool_scores[best_tool]['score']
            
            # Calculate confidence
            total_score = sum(score['score'] for score in tool_scores.values())
            confidence = best_score / max(1, total_score) if total_score > 0 else 0
            
            # Check if confidence and keyword matches meet thresholds
            meets_confidence = confidence >= self.routing_config['min_confidence_threshold']
            meets_keyword_count = best_score >= self.routing_config['min_keyword_matches']
            
            if best_score > 0 and meets_confidence and meets_keyword_count:
                return {
                    'intent': 'specialized_tool',
                    'selected_tool': best_tool,
                    'confidence': confidence,
                    'tool_scores': tool_scores,
                    'analysis': f"Selected specialized tool {best_tool} with confidence {confidence:.2f} ({best_score} keyword matches)"
                }
        
        # If no specialized tool matches or confidence is too low, use fallback
        if self.routing_config['enable_fallback']:
            return {
                'intent': 'fallback_to_llm',
                'selected_tool': 'general_llm_tool',
                'confidence': 1.0,  # Always confident in fallback
                'tool_scores': tool_scores,
                'analysis': f"Using general LLM fallback - no specialized tool matched with sufficient confidence",
                'fallback_reason': 'low_confidence' if tool_scores else 'no_keywords_matched'
            }
        
        # If fallback is disabled, return unclear intent
        return {
            'intent': 'unclear',
            'confidence': 0,
            'message': 'Could not determine the intent of your request and fallback is disabled',
            'suggestions': self._get_usage_examples()
        }
    
    def route_request(self, request: str) -> Dict[str, Any]:
        """Route the request to the appropriate specialized agent with fallback support."""
        try:
            # Analyze the request intent
            intent_analysis = self.analyze_request_intent(request)
            
            if intent_analysis['intent'] == 'unclear':
                return intent_analysis
            
            selected_tool = intent_analysis['selected_tool']
            confidence = intent_analysis['confidence']
            is_fallback = intent_analysis['intent'] == 'fallback_to_llm'
            
            # Log the routing decision
            if is_fallback:
                logger.info(f"Using fallback LLM agent - reason: {intent_analysis.get('fallback_reason', 'unknown')}")
            else:
                logger.info(f"Routing request to {selected_tool} with confidence {confidence:.2f}")
            
            # Execute the selected tool
            agent = self.tools[selected_tool]['agent']
            
            try:
                result = agent.run(request)
                
                # Parse the result if it's a JSON string
                try:
                    parsed_result = json.loads(result)
                except json.JSONDecodeError:
                    parsed_result = {'raw_output': result}
                
                # Check if specialized agent returned an error and fallback is enabled
                if (not is_fallback and 
                    self.routing_config['fallback_for_errors'] and 
                    ('error' in parsed_result or parsed_result.get('success') == False)):
                    
                    logger.warning(f"Specialized agent {selected_tool} returned error, falling back to LLM")
                    self.log_routing_decision(request, selected_tool, confidence, False, False, 'agent_error')
                    return self._fallback_to_llm(request, {
                        'failed_agent': selected_tool,
                        'error': parsed_result.get('error', 'Unknown error'),
                        'original_result': parsed_result
                    })
                
                # Validate response relevance for specialized agents
                validation_result = None
                if not is_fallback and self.routing_config['validate_responses']:
                    validation_result = self.validate_response_relevance(request, parsed_result, selected_tool)
                    
                    # If response is not relevant, fallback to LLM
                    if not validation_result['is_relevant'] and self.routing_config['enable_fallback']:
                        logger.warning(f"Specialized agent {selected_tool} response not relevant (confidence: {validation_result['confidence']:.2f}), falling back to LLM")
                        logger.info(f"Validation reasons: {validation_result.get('reasons', [])}")
                        
                        self.log_routing_decision(request, selected_tool, confidence, False, False, 'irrelevant_response')
                        return self._fallback_to_llm(request, {
                            'failed_agent': selected_tool,
                            'validation_failure': validation_result,
                            'original_result': parsed_result,
                            'reason': 'Response not relevant to user question'
                        })
                
                # Log successful routing decision
                self.log_routing_decision(request, selected_tool, confidence, is_fallback, True)
                
                # Prepare successful response
                response = {
                    'orchestrator_analysis': {
                        'selected_tool': selected_tool,
                        'confidence': confidence,
                        'is_fallback': is_fallback
                    },
                    'tool_result': parsed_result,
                    'success': True
                }
                
                # Add validation info if available
                if validation_result:
                    response['orchestrator_analysis']['response_validation'] = validation_result
                
                # Add routing reason based on type
                if is_fallback:
                    response['orchestrator_analysis']['fallback_reason'] = intent_analysis.get('fallback_reason')
                    response['orchestrator_analysis']['routing_reason'] = "Fallback to general LLM agent"
                else:
                    matched_keywords = intent_analysis.get('tool_scores', {}).get(selected_tool, {}).get('matched_keywords', [])
                    response['orchestrator_analysis']['routing_reason'] = f"Matched keywords: {matched_keywords}"
                
                return response
                
            except Exception as agent_error:
                logger.error(f"Agent {selected_tool} execution failed: {agent_error}")
                
                # If specialized agent fails and fallback is enabled, use LLM
                if not is_fallback and self.routing_config['fallback_for_errors']:
                    logger.info("Falling back to LLM due to agent execution error")
                    return self._fallback_to_llm(request, {
                        'failed_agent': selected_tool,
                        'execution_error': str(agent_error)
                    })
                else:
                    # If fallback agent fails or fallback is disabled, return error
                    return {
                        'error': f'Agent {selected_tool} execution failed: {str(agent_error)}',
                        'request': request,
                        'success': False
                    }
            
        except Exception as e:
            logger.error(f"Error in routing logic: {e}")
            
            # Try fallback even for routing errors
            if self.routing_config['fallback_for_errors']:
                logger.info("Falling back to LLM due to routing error")
                return self._fallback_to_llm(request, {
                    'routing_error': str(e)
                })
            
            return {
                'error': f'Orchestrator encountered an error: {str(e)}',
                'request': request,
                'success': False
            }
    
    def _fallback_to_llm(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fallback to the general LLM agent with context."""
        try:
            # Prepare input with context for the LLM agent
            llm_input = {
                'question': request,
                'context': context
            }
            
            result = self.general_llm_agent.run(json.dumps(llm_input))
            
            try:
                parsed_result = json.loads(result)
            except json.JSONDecodeError:
                parsed_result = {'raw_output': result}
            
            return {
                'orchestrator_analysis': {
                    'selected_tool': 'general_llm_tool',
                    'confidence': 1.0,
                    'is_fallback': True,
                    'fallback_reason': 'agent_error' if context else 'low_confidence',
                    'routing_reason': 'Fallback to general LLM agent',
                    'context_provided': context is not None
                },
                'tool_result': parsed_result,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Fallback LLM agent also failed: {e}")
            return {
                'error': f'All agents failed. Last error: {str(e)}',
                'request': request,
                'success': False,
                'fallback_attempted': True
            }
    
    def _get_usage_examples(self) -> Dict[str, List[str]]:
        """Get usage examples for each tool."""
        return {
            'aws_resource_queries': [
                'Show me all EC2 instances',
                'List S3 buckets',
                'Get load balancer information',
                'Display EFS filesystems',
                'Show security group details',
                'What EC2 instances are running?',
                'Get information about my VPC resources'
            ],
            'network_troubleshooting': [
                'Diagnose EC2 connectivity issues',
                'Troubleshoot load balancer connection problems',
                'Check EFS mount connectivity',
                'Diagnose S3 access issues',
                'Why can\'t I connect to my EC2 instance?',
                'Load balancer is not responding',
                'EFS mount is failing'
            ]
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get the status of all available tools and agents."""
        status = {
            'orchestrator': {
                'name': self.name,
                'status': 'active',
                'available_tools': len(self.tools)
            },
            'tools': {}
        }
        
        for tool_name, tool_info in self.tools.items():
            try:
                # Test if the agent is responsive
                agent = tool_info['agent']
                status['tools'][tool_name] = {
                    'name': agent.name,
                    'description': tool_info['description'],
                    'status': 'active',
                    'keywords_count': len(tool_info['keywords'])
                }
            except Exception as e:
                status['tools'][tool_name] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        return status
    
    def process_request(self, request: str) -> Dict[str, Any]:
        """Process incoming requests and route them appropriately."""
        request_lower = request.lower()
        
        # Handle system/meta requests
        if any(keyword in request_lower for keyword in ['help', 'status', 'available', 'what can you do']):
            return {
                'system_info': {
                    'name': self.name,
                    'description': self.description,
                    'available_tools': [
                        {
                            'name': tool_info['agent'].name,
                            'description': tool_info['description']
                        }
                        for tool_info in self.tools.values()
                    ],
                    'supported_aws_services': SUPPORTED_AWS_SERVICES,
                    'network_categories': NETWORK_CATEGORIES
                },
                'usage_examples': self._get_usage_examples(),
                'system_status': self.get_system_status()
            }
        
        # Route the request to appropriate tool
        return self.route_request(request)
    
    def analyze_routing_patterns(self) -> Dict[str, Any]:
        """Analyze routing history to identify patterns and improvement opportunities."""
        if not self.routing_history:
            return {'message': 'No routing history available'}
        
        analysis = {
            'total_requests': len(self.routing_history),
            'success_rate': 0,
            'fallback_rate': 0,
            'agent_usage': {},
            'common_failures': {},
            'improvement_suggestions': []
        }
        
        successful_requests = 0
        fallback_requests = 0
        
        for entry in self.routing_history:
            # Count successes
            if entry['success']:
                successful_requests += 1
            
            # Count fallbacks
            if entry['is_fallback']:
                fallback_requests += 1
            
            # Count agent usage
            tool = entry['selected_tool']
            if tool not in analysis['agent_usage']:
                analysis['agent_usage'][tool] = {'count': 0, 'success_count': 0}
            analysis['agent_usage'][tool]['count'] += 1
            if entry['success']:
                analysis['agent_usage'][tool]['success_count'] += 1
            
            # Track failure reasons
            if not entry['success'] and entry.get('fallback_reason'):
                reason = entry['fallback_reason']
                if reason not in analysis['common_failures']:
                    analysis['common_failures'][reason] = 0
                analysis['common_failures'][reason] += 1
        
        # Calculate rates
        analysis['success_rate'] = successful_requests / len(self.routing_history)
        analysis['fallback_rate'] = fallback_requests / len(self.routing_history)
        
        # Generate improvement suggestions
        if analysis['fallback_rate'] > 0.3:
            analysis['improvement_suggestions'].append(
                "High fallback rate detected. Consider expanding specialized agent keywords or improving routing logic."
            )
        
        if 'irrelevant_response' in analysis['common_failures']:
            analysis['improvement_suggestions'].append(
                "Frequent irrelevant responses detected. Consider improving response validation or agent capabilities."
            )
        
        return analysis
    
    def get_routing_recommendations(self, request: str) -> Dict[str, Any]:
        """Get recommendations for improving routing for similar requests."""
        similar_requests = []
        
        # Find similar requests in history
        request_words = set(request.lower().split())
        for entry in self.routing_history[-100:]:  # Check last 100 entries
            entry_words = set(entry['request'].lower().split())
            similarity = len(request_words.intersection(entry_words)) / len(request_words.union(entry_words))
            
            if similarity > 0.3:  # 30% similarity threshold
                similar_requests.append({
                    'request': entry['request'],
                    'similarity': similarity,
                    'selected_tool': entry['selected_tool'],
                    'success': entry['success'],
                    'is_fallback': entry['is_fallback']
                })
        
        # Sort by similarity
        similar_requests.sort(key=lambda x: x['similarity'], reverse=True)
        
        recommendations = {
            'similar_requests_found': len(similar_requests),
            'top_similar': similar_requests[:5],
            'recommendations': []
        }
        
        if similar_requests:
            # Analyze patterns in similar requests
            successful_tools = [req['selected_tool'] for req in similar_requests if req['success']]
            if successful_tools:
                most_successful = max(set(successful_tools), key=successful_tools.count)
                recommendations['recommendations'].append(
                    f"Similar requests were most successful with: {most_successful}"
                )
        
        return recommendations
    
    def provide_user_feedback(self, request: str, was_helpful: bool, 
                            selected_tool: str, feedback_text: str = None) -> Dict[str, Any]:
        """Allow users to provide feedback on routing decisions."""
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'request': request,
            'selected_tool': selected_tool,
            'was_helpful': was_helpful,
            'feedback_text': feedback_text,
            'type': 'user_feedback'
        }
        
        self.routing_history.append(feedback_entry)
        self.save_feedback_history()
        
        # If feedback was negative, provide suggestions
        suggestions = []
        if not was_helpful:
            suggestions.append("Thank you for the feedback. We'll use this to improve routing decisions.")
            
            # Suggest alternative agents
            available_agents = [tool for tool in self.tools.keys() if tool != selected_tool]
            if available_agents:
                suggestions.append(f"You might try asking your question differently, or we can route to: {', '.join(available_agents)}")
        
        return {
            'feedback_recorded': True,
            'suggestions': suggestions,
            'message': 'Thank you for your feedback! This helps improve the system.'
        }
    
    def run(self, input_data: str) -> str:
        """Main entry point for the orchestrator agent."""
        try:
            # Check for special commands
            if input_data.lower().startswith('analyze routing'):
                result = self.analyze_routing_patterns()
            elif input_data.lower().startswith('routing recommendations'):
                # Extract the actual request from the command
                request = input_data.replace('routing recommendations for:', '').strip()
                result = self.get_routing_recommendations(request)
            else:
                result = self.process_request(input_data)
            
            return json.dumps(result, indent=2, default=str)
        except Exception as e:
            logger.error(f"Orchestrator Agent error: {e}")
            return json.dumps({
                'error': f'Orchestrator Agent encountered an error: {str(e)}',
                'input': input_data,
                'success': False
            }, indent=2)