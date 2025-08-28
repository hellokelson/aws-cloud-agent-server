from flask import Flask, render_template, request, jsonify, Response
import requests
import json
import boto3
import uuid
from datetime import datetime
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
AGENTCORE_URL = "http://localhost:8080"
S3_BUCKET = "zk-aws-mcp-assistant-sessions"
AWS_REGION = "us-east-1"

# Initialize S3 client
s3_client = boto3.client('s3', region_name=AWS_REGION)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all chat sessions from S3"""
    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix='sessions/')
        sessions = []
        
        if 'Contents' in response:
            for obj in response['Contents']:
                if obj['Key'].endswith('.json'):
                    session_id = obj['Key'].split('/')[-1].replace('.json', '')
                    # Get session metadata
                    try:
                        session_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=obj['Key'])
                        session_data = json.loads(session_obj['Body'].read())
                        title = session_data.get('title', 'Untitled Session')
                        sessions.append({
                            'id': session_id,
                            'title': title,
                            'last_modified': obj['LastModified'].isoformat()
                        })
                    except Exception as e:
                        logger.error(f"Error reading session {session_id}: {e}")
        
        return jsonify(sessions)
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        return jsonify([])

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get specific session details"""
    try:
        key = f'sessions/{session_id}.json'
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=key)
        session_data = json.loads(response['Body'].read())
        return jsonify(session_data)
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        return jsonify({'error': 'Session not found'}), 404

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Delete a session"""
    try:
        key = f'sessions/{session_id}.json'
        s3_client.delete_object(Bucket=S3_BUCKET, Key=key)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        return jsonify({'error': 'Failed to delete session'}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Send message to agent and stream response"""
    data = request.json
    message = data.get('message', '')
    session_id = data.get('session_id', str(uuid.uuid4()))
    agent_type = data.get('agent_type', 'DiagnosisAgent')
    
    def generate():
        try:
            # Determine the correct endpoint based on agent type
            endpoint = f"{AGENTCORE_URL}/{agent_type}/invocations"
            
            payload = {
                'prompt': message,
                'session_id': session_id
            }
            
            # Stream response from AgentCore
            response = requests.post(
                endpoint,
                json=payload,
                stream=True,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        yield f"data: {line.decode('utf-8')}\n\n"
            else:
                error_data = {
                    'type': 'error',
                    'content': f'Agent request failed: {response.status_code}',
                    'session_id': session_id
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            error_data = {
                'type': 'error',
                'content': f'Connection error: {str(e)}',
                'session_id': session_id
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
