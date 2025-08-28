import subprocess
import json
from strands import tool


@tool
def eksctl_tool(command: str) -> str:
    """
    Execute read-only eksctl commands for EKS cluster management.
    
    This tool provides access to eksctl functionality with safety constraints:
    - Only read-only operations are allowed (get, describe, list)
    - No cluster creation, deletion, or modification operations
    - Provides detailed EKS cluster information and status
    
    Args:
        command: The eksctl command to execute (without 'eksctl' prefix)
                Examples: "get clusters", "get nodegroups --cluster my-cluster"
    
    Returns:
        The output from the eksctl command or error information
    """
    
    # Safety check - only allow read-only operations
    read_only_commands = ['get', 'describe', 'list', 'version', 'help']
    command_parts = command.strip().split()
    
    if not command_parts:
        return "Error: No command provided. Use commands like 'get clusters' or 'get nodegroups --cluster cluster-name'"
    
    first_command = command_parts[0].lower()
    if first_command not in read_only_commands:
        return f"Error: Command '{first_command}' is not allowed. Only read-only operations are permitted: {', '.join(read_only_commands)}"
    
    # Construct the full eksctl command
    full_command = ['eksctl'] + command_parts
    
    try:
        # Execute the command with timeout
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if not output:
                return f"Command executed successfully but returned no output.\nCommand: eksctl {command}"
            return f"Command: eksctl {command}\n\nOutput:\n{output}"
        else:
            error_output = result.stderr.strip()
            return f"Command failed: eksctl {command}\n\nError:\n{error_output}"
            
    except subprocess.TimeoutExpired:
        return f"Command timed out after 60 seconds: eksctl {command}"
    except FileNotFoundError:
        return "Error: eksctl is not installed or not found in PATH. Please install eksctl first."
    except Exception as e:
        return f"Error executing eksctl command: {str(e)}"


if __name__ == "__main__":
    # Test the tool
    print(eksctl_tool("get clusters"))
