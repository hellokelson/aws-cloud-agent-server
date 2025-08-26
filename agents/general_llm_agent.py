"""General Purpose LLM Agent - Handles any question using LLM capabilities."""

from utils.base_agent import Agent
from typing import Dict, List, Any, Optional
import json
import logging
import requests
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class GeneralLLMAgent(Agent):
    """General purpose agent that can handle any question using LLM capabilities."""
    
    def __init__(self):
        super().__init__(
            name="General Purpose LLM Agent",
            description="Handles any question or request using advanced language model capabilities when specialized agents cannot help"
        )
        
        # Configuration for different LLM providers
        self.llm_config = {
            'openai': {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'model': 'gpt-3.5-turbo',
                'endpoint': 'https://api.openai.com/v1/chat/completions'
            },
            'anthropic': {
                'api_key': os.getenv('ANTHROPIC_API_KEY'),
                'model': 'claude-3-sonnet-20240229',
                'endpoint': 'https://api.anthropic.com/v1/messages'
            },
            'local': {
                'endpoint': os.getenv('LOCAL_LLM_ENDPOINT', 'http://localhost:11434/api/generate'),
                'model': os.getenv('LOCAL_LLM_MODEL', 'llama2')
            }
        }
        
        # Determine which LLM provider to use
        self.provider = self._detect_available_provider()
        
    def _detect_available_provider(self) -> str:
        """Detect which LLM provider is available."""
        # Check for OpenAI API key
        if self.llm_config['openai']['api_key']:
            return 'openai'
        
        # Check for Anthropic API key
        if self.llm_config['anthropic']['api_key']:
            return 'anthropic'
        
        # Check for local LLM endpoint
        try:
            local_endpoint = self.llm_config['local']['endpoint']
            response = requests.get(local_endpoint.replace('/api/generate', '/api/tags'), timeout=5)
            if response.status_code == 200:
                return 'local'
        except:
            pass
        
        # Fallback to mock mode
        return 'mock'
    
    def _call_openai(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Call OpenAI API."""
        try:
            headers = {
                'Authorization': f"Bearer {self.llm_config['openai']['api_key']}",
                'Content-Type': 'application/json'
            }
            
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt(context)
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            data = {
                'model': self.llm_config['openai']['model'],
                'messages': messages,
                'max_tokens': 1000,
                'temperature': 0.7
            }
            
            response = requests.post(
                self.llm_config['openai']['endpoint'],
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return self._fallback_response(prompt, context)
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return self._fallback_response(prompt, context)
    
    def _call_anthropic(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Call Anthropic Claude API."""
        try:
            headers = {
                'x-api-key': self.llm_config['anthropic']['api_key'],
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            data = {
                'model': self.llm_config['anthropic']['model'],
                'max_tokens': 1000,
                'messages': [
                    {
                        'role': 'user',
                        'content': f"{self._get_system_prompt(context)}\n\nUser question: {prompt}"
                    }
                ]
            }
            
            response = requests.post(
                self.llm_config['anthropic']['endpoint'],
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['content'][0]['text']
            else:
                logger.error(f"Anthropic API error: {response.status_code} - {response.text}")
                return self._fallback_response(prompt, context)
                
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {e}")
            return self._fallback_response(prompt, context)
    
    def _call_local_llm(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Call local LLM (like Ollama)."""
        try:
            data = {
                'model': self.llm_config['local']['model'],
                'prompt': f"{self._get_system_prompt(context)}\n\nUser question: {prompt}\n\nResponse:",
                'stream': False
            }
            
            response = requests.post(
                self.llm_config['local']['endpoint'],
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', self._fallback_response(prompt, context))
            else:
                logger.error(f"Local LLM error: {response.status_code} - {response.text}")
                return self._fallback_response(prompt, context)
                
        except Exception as e:
            logger.error(f"Error calling local LLM: {e}")
            return self._fallback_response(prompt, context)
    
    def _get_system_prompt(self, context: Dict[str, Any] = None) -> str:
        """Get system prompt for the LLM."""
        base_prompt = """You are a helpful AI assistant integrated into an AWS multi-agent infrastructure management system. 

Your role is to handle any question or request that the specialized agents (AWS Resource Agent, Network Troubleshoot Agent) cannot handle.

You can help with:
- General AWS questions and explanations
- Cloud architecture advice and best practices
- Troubleshooting guidance and recommendations
- Infrastructure planning and design
- Security best practices
- Cost optimization suggestions
- DevOps and automation guidance
- Programming and scripting help
- General technical questions
- Any other questions the user might have

Be helpful, accurate, and provide practical advice. If you're not certain about something, say so and suggest where the user might find more authoritative information.

Current date and time: {datetime}
""".format(datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        if context:
            base_prompt += f"\n\nContext from previous interactions:\n{json.dumps(context, indent=2)}"
        
        return base_prompt
    
    def _fallback_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Provide a fallback response when LLM APIs are not available."""
        return f"""I understand you're asking: "{prompt}"

I'm a general-purpose AI assistant, but I don't currently have access to external LLM services. However, I can still help you with:

**AWS-Related Questions:**
- I can guide you to the appropriate AWS documentation
- Suggest best practices for common scenarios
- Help you understand AWS service relationships
- Provide troubleshooting steps

**General Guidance:**
- For AWS service details, try the AWS CLI: `aws [service] help`
- For infrastructure questions, check AWS Well-Architected Framework
- For troubleshooting, consider AWS CloudTrail and CloudWatch logs

**To enable full LLM capabilities:**
1. Set OPENAI_API_KEY environment variable for OpenAI
2. Set ANTHROPIC_API_KEY environment variable for Claude
3. Set up a local LLM like Ollama at LOCAL_LLM_ENDPOINT

Would you like me to help you with any specific AWS-related task that our specialized agents can handle?"""
    
    def process_question(self, question: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process any question using LLM capabilities."""
        try:
            logger.info(f"Processing general question with {self.provider} provider: {question}")
            
            # Call the appropriate LLM provider
            if self.provider == 'openai':
                response = self._call_openai(question, context)
            elif self.provider == 'anthropic':
                response = self._call_anthropic(question, context)
            elif self.provider == 'local':
                response = self._call_local_llm(question, context)
            else:
                response = self._fallback_response(question, context)
            
            return {
                'service': 'general_llm',
                'question': question,
                'response': response,
                'provider': self.provider,
                'context_used': context is not None,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return {
                'service': 'general_llm',
                'question': question,
                'error': str(e),
                'response': self._fallback_response(question, context),
                'provider': 'fallback'
            }
    
    def run(self, input_data: str) -> str:
        """Main entry point for the general LLM agent."""
        try:
            # Try to parse input as JSON for context
            context = None
            question = input_data
            
            try:
                parsed_input = json.loads(input_data)
                if isinstance(parsed_input, dict):
                    question = parsed_input.get('question', input_data)
                    context = parsed_input.get('context')
            except:
                # Input is just a plain string question
                pass
            
            result = self.process_question(question, context)
            return json.dumps(result, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"General LLM Agent error: {e}")
            return json.dumps({
                'error': f'General LLM Agent encountered an error: {str(e)}',
                'input': input_data,
                'service': 'general_llm'
            }, indent=2)