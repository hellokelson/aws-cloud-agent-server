from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient


@tool
def eks_assistant(query: str) -> str:
    """
    Process and respond to Amazon EKS (Elastic Kubernetes Service) related queries using EKS MCP server.
    
    This tool leverages the awslabs.eks-mcp-server which provides comprehensive EKS management capabilities:
    - EKS cluster discovery and management
    - CloudFormation stack operations for EKS
    - Kubernetes API access and resource management
    - EKS troubleshooting and diagnostics
    - Node group and Fargate profile operations
    - EKS add-ons management
    - Kubernetes workload analysis and monitoring

    Args:
        query: The user's EKS related question

    Returns:
        A helpful response addressing the EKS query using EKS MCP server capabilities
    """

    formatted_query = f"Analyze and respond to this Amazon EKS question, providing clear explanations and actionable guidance. Use the available EKS MCP server tools to gather comprehensive information: {query}"
    response = str()

    try:
        eks_mcp_server = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="uvx", args=["awslabs.eks-mcp-server@latest"]
                )
            )
        )

        with eks_mcp_server:

            tools = eks_mcp_server.list_tools_sync()
            # Create the EKS agent with specific capabilities
            eks_agent = Agent(
                system_prompt="""You are an Amazon EKS (Elastic Kubernetes Service) specialist with access to the EKS MCP server tools. Your role is to:
                
                1. Analyze EKS-related questions and determine the best EKS MCP server tools to use
                2. Leverage the available EKS MCP server capabilities including:
                   - manage_eks_stacks: For CloudFormation-based EKS cluster operations (create, update, delete, describe)
                   - list_api_versions: For Kubernetes API discovery and cluster connectivity testing
                   - search_eks_troubleshoot_guide: For EKS troubleshooting guidance and best practices
                   - get_kubernetes_resources: For querying Kubernetes resources within clusters
                   - Other EKS-specific tools provided by the MCP server
                
                3. For cluster discovery and listing:
                   - Use the available MCP server tools creatively to discover EKS resources
                   - Try different approaches with the provided tools to gather cluster information
                   - Use CloudFormation stack management to find EKS-related stacks
                   - Use Kubernetes API tools to test cluster connectivity
                
                4. Provide comprehensive EKS guidance including:
                   - Cluster lifecycle management through CloudFormation
                   - Kubernetes resource management and monitoring
                   - EKS troubleshooting using the built-in troubleshooting guide
                   - Best practices for EKS operations
                   - Security and networking configurations
                
                5. When encountering errors or limitations:
                   - Explain what the EKS MCP server tools can and cannot do
                   - Provide alternative approaches using available tools
                   - Offer guidance on EKS best practices and troubleshooting
                
                IMPORTANT: Use only the EKS MCP server tools provided. Do not suggest external AWS CLI commands.
                Focus on leveraging the full capabilities of the EKS MCP server for comprehensive EKS management.
                
                Provide your complete response directly - do not create any files.
                """,
                tools=tools,
            )
            response = str(eks_agent(formatted_query))
            print("\n\n")

        if len(response) > 0:
            return response

        return "I apologize, but I couldn't access EKS information for your query using the EKS MCP server. This might be due to insufficient permissions, connectivity issues with the EKS MCP server, or the EKS service being unavailable in your region. Please verify your EKS permissions and try again."

    except Exception as e:
        error_msg = str(e)
        if "AccessDenied" in error_msg or "UnauthorizedOperation" in error_msg:
            return f"Error accessing Amazon EKS through MCP server: {error_msg}. Please ensure you have the necessary EKS permissions (eks:*, cloudformation:*, sts:AssumeRole) and that EKS is available in your current region."
        elif "ClusterNotFound" in error_msg or "ResourceNotFound" in error_msg:
            return f"EKS resource not found via MCP server: {error_msg}. The EKS MCP server may require existing clusters or CloudFormation stacks to discover resources. Consider creating an EKS cluster first or check if you have existing EKS CloudFormation stacks."
        elif "ConnectionError" in error_msg or "MCP" in error_msg:
            return f"EKS MCP server connection error: {error_msg}. Please ensure the EKS MCP server is properly installed and accessible."
        else:
            return f"Error processing your EKS query through MCP server: {error_msg}. Please check your AWS credentials, region settings, and EKS MCP server availability."


if __name__ == "__main__":
    eks_assistant("How many EKS clusters do I have?")
