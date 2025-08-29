from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient


@tool
def aws_cloudwatch_assistant(query: str) -> str:
    """
    Process and respond to Amazon CloudWatch related queries using CloudWatch MCP server.
    
    This tool leverages the awslabs.cloudwatch-mcp-server which provides comprehensive CloudWatch capabilities:
    - CloudWatch metrics retrieval and analysis
    - CloudWatch logs querying and searching
    - CloudWatch alarms management and status
    - CloudWatch dashboards and widgets
    - CloudWatch Insights queries
    - Performance monitoring and troubleshooting
    - Resource utilization analysis
    - Application and infrastructure observability

    Args:
        query: The user's CloudWatch related question

    Returns:
        A helpful response addressing the CloudWatch query using CloudWatch MCP server capabilities
    """

    formatted_query = f"Analyze and respond to this Amazon CloudWatch question, providing clear explanations, metrics analysis, and actionable monitoring guidance: {query}"
    response = str()

    try:
        cloudwatch_mcp_server = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="uvx", args=["awslabs.cloudwatch-mcp-server@latest"]
                )
            )
        )

        with cloudwatch_mcp_server:

            tools = cloudwatch_mcp_server.list_tools_sync()
            # Create the CloudWatch agent with specific capabilities
            cloudwatch_agent = Agent(
                system_prompt="""You are an Amazon CloudWatch specialist with access to the CloudWatch MCP server tools. Your role is to:
                
                1. Analyze CloudWatch-related questions and determine the best CloudWatch tools to use
                2. Leverage the available CloudWatch MCP server capabilities including:
                   - get_metrics: Retrieve CloudWatch metrics for AWS resources
                   - query_logs: Search and analyze CloudWatch logs
                   - list_alarms: Get CloudWatch alarms and their status
                   - get_alarm_history: Analyze alarm state changes and history
                   - describe_dashboards: Access CloudWatch dashboard information
                   - run_insights_query: Execute CloudWatch Logs Insights queries
                   - get_metric_statistics: Retrieve statistical data for metrics
                   - list_log_groups: Discover available log groups
                   - Other CloudWatch-specific tools provided by the MCP server
                
                3. Provide comprehensive monitoring and observability analysis including:
                   - Performance metrics analysis and interpretation
                   - Log analysis and troubleshooting guidance
                   - Alarm configuration and status monitoring
                   - Resource utilization trends and patterns
                   - Application performance insights
                   - Infrastructure health monitoring
                   - Cost optimization through monitoring data
                
                4. When analyzing metrics and logs:
                   - Provide context for metric values and trends
                   - Explain what normal vs abnormal patterns look like
                   - Suggest appropriate time ranges for analysis
                   - Recommend relevant metrics to monitor
                   - Identify potential performance bottlenecks
                   - Provide actionable troubleshooting steps
                
                5. For monitoring setup and optimization:
                   - Recommend appropriate CloudWatch alarms
                   - Suggest useful CloudWatch dashboards
                   - Provide guidance on log retention and costs
                   - Recommend CloudWatch Insights queries
                   - Explain monitoring best practices
                
                6. When encountering errors or limitations:
                   - Explain what CloudWatch data is available
                   - Provide alternative approaches for monitoring
                   - Suggest manual CloudWatch console checks if needed
                   - Offer guidance on CloudWatch permissions and setup
                
                IMPORTANT: Use only the CloudWatch MCP server tools provided. Focus on leveraging
                the full capabilities of the CloudWatch server for comprehensive monitoring analysis.
                Always provide context for metrics and explain their significance for system health.
                
                Provide your complete response directly - do not create any files.
                """,
                tools=tools,
            )
            response = str(cloudwatch_agent(formatted_query))
            print("\n\n")

        if len(response) > 0:
            return response

        return "I apologize, but I couldn't access CloudWatch information for your query using the CloudWatch MCP server. This might be due to insufficient CloudWatch permissions, connectivity issues, or the specific metrics/logs being unavailable. Please verify your CloudWatch permissions and try again."

    except Exception as e:
        error_msg = str(e)
        if "AccessDenied" in error_msg or "UnauthorizedOperation" in error_msg:
            return f"Error accessing Amazon CloudWatch through MCP server: {error_msg}. Please ensure you have the necessary CloudWatch permissions (cloudwatch:GetMetricStatistics, logs:DescribeLogGroups, cloudwatch:DescribeAlarms, etc.) and that CloudWatch is available in your current region."
        elif "ResourceNotFound" in error_msg or "InvalidParameterValue" in error_msg:
            return f"CloudWatch resource not found: {error_msg}. Please verify that the specified metrics, log groups, or alarms exist in your account and region. Check the resource names and time ranges."
        elif "ThrottlingException" in error_msg or "LimitExceeded" in error_msg:
            return f"CloudWatch API throttling: {error_msg}. The CloudWatch API is being rate limited. Please wait a moment and try again with a more specific query or smaller time range."
        elif "ConnectionError" in error_msg or "MCP" in error_msg:
            return f"CloudWatch MCP server connection error: {error_msg}. Please ensure the CloudWatch MCP server is properly installed and accessible."
        elif "InvalidTimeRange" in error_msg or "InvalidMetricName" in error_msg:
            return f"Invalid CloudWatch query parameters: {error_msg}. Please check your metric names, time ranges, and dimensions. Ensure you're using valid AWS service metrics and time periods."
        else:
            return f"Error processing your CloudWatch query through MCP server: {error_msg}. Please check your AWS credentials, region settings, and CloudWatch service availability."


if __name__ == "__main__":
    aws_cloudwatch_assistant("Show me CPU utilization for my EC2 instances")
