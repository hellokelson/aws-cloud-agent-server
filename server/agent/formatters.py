# Response formatters for AWS Cloud Agent Server

import json
import asyncio


class AgentFormatter:
    """Input/Output formatter for AWS Agents"""
    
    @staticmethod
    def format_request(prompt: str, session_id: str) -> dict:
        """Format incoming request for the agent"""
        return {
            "prompt": prompt,
            "session_id": session_id,
            "timestamp": asyncio.get_event_loop().time()
        }
    
    @staticmethod
    def format_response_chunk(event_data: dict, session_id: str) -> str:
        """Format streaming response chunks"""
        # Ensure event_data is serializable
        if hasattr(event_data, 'model_dump'):
            event_data = event_data.model_dump()
        elif not isinstance(event_data, dict):
            event_data = {"content": str(event_data)}
        
        # Remove non-serializable objects
        serializable_data = {}
        for key, value in event_data.items():
            try:
                json.dumps(value)  # Test if serializable
                serializable_data[key] = value
            except (TypeError, ValueError):
                serializable_data[key] = str(value)  # Convert to string if not serializable
        
        formatted_event = {
            "event": serializable_data,
            "session_id": session_id,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        try:
            return f"data: {json.dumps(formatted_event)}\n\n"
        except (TypeError, ValueError) as e:
            # Fallback for any remaining serialization issues
            error_event = {
                "error": f"Serialization error: {str(e)}",
                "session_id": session_id,
                "timestamp": asyncio.get_event_loop().time()
            }
            return f"data: {json.dumps(error_event)}\n\n"
    
    @staticmethod
    def format_error(error: Exception, session_id: str) -> str:
        """Format error responses"""
        error_event = {
            "error": str(error),
            "error_type": type(error).__name__,
            "session_id": session_id,
            "timestamp": asyncio.get_event_loop().time()
        }
        return f"data: {json.dumps(error_event)}\n\n"
