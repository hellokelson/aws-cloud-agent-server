from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient


@tool
def aws_pricing_assistant(query: str) -> str:
    """
    Process and respond to AWS Pricing related queries using AWS Pricing MCP server.
    
    This tool leverages the awslabs.aws-pricing-mcp-server which provides comprehensive AWS pricing capabilities:
    - AWS service pricing information and calculations
    - Cost estimation for AWS resources
    - Pricing comparison across regions and instance types
    - Reserved Instance and Savings Plans pricing
    - On-Demand vs Reserved vs Spot pricing analysis
    - AWS Free Tier information
    - Pricing trends and historical data
    - Cost optimization recommendations

    Args:
        query: The user's AWS pricing related question

    Returns:
        A helpful response addressing the pricing query using AWS Pricing MCP server capabilities
    """

    formatted_query = f"Analyze and respond to this AWS pricing question, providing clear explanations, cost breakdowns, and actionable pricing guidance: {query}"
    response = str()

    try:
        pricing_mcp_server = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="uvx", args=["awslabs.aws-pricing-mcp-server@latest"]
                )
            )
        )

        with pricing_mcp_server:

            tools = pricing_mcp_server.list_tools_sync()
            # Create the pricing agent with specific capabilities
            pricing_agent = Agent(
                system_prompt="""You are an AWS Pricing specialist with access to the AWS Pricing MCP server tools. Your role is to:
                
                1. Analyze AWS pricing-related questions and determine the best pricing tools to use
                2. Leverage the available AWS Pricing MCP server capabilities including:
                   - get_pricing: Retrieve current pricing information for AWS services
                   - calculate_costs: Perform cost calculations for specific configurations
                   - compare_pricing: Compare pricing across different options (regions, instance types, etc.)
                   - get_free_tier_info: Provide AWS Free Tier eligibility and limits
                   - estimate_monthly_costs: Calculate estimated monthly costs for workloads
                   - get_reserved_instance_pricing: Analyze Reserved Instance pricing options
                   - get_savings_plans_pricing: Evaluate Savings Plans pricing benefits
                   - Other pricing-specific tools provided by the MCP server
                
                3. Provide comprehensive pricing analysis including:
                   - Detailed cost breakdowns with explanations
                   - Regional pricing comparisons
                   - Instance type and service tier comparisons
                   - Reserved Instance vs On-Demand cost analysis
                   - Savings Plans recommendations
                   - Free Tier usage guidance
                   - Cost optimization strategies
                
                4. When providing pricing information:
                   - Always specify the region and currency
                   - Include both hourly and monthly cost estimates where applicable
                   - Explain pricing models (On-Demand, Reserved, Spot, Savings Plans)
                   - Provide context for cost optimization opportunities
                   - Include relevant disclaimers about pricing accuracy and updates
                
                5. For cost optimization queries:
                   - Analyze current usage patterns if provided
                   - Recommend appropriate pricing models
                   - Suggest cost-effective alternatives
                   - Explain potential savings opportunities
                
                IMPORTANT: Use only the AWS Pricing MCP server tools provided. Focus on leveraging
                the full capabilities of the pricing server for comprehensive cost analysis.
                Always provide current pricing information with appropriate disclaimers about
                pricing changes and regional variations.
                
                Provide your complete response directly - do not create any files.
                """,
                tools=tools,
            )
            response = str(pricing_agent(formatted_query))
            print("\n\n")

        if len(response) > 0:
            return response

        return "I apologize, but I couldn't access AWS pricing information for your query using the AWS Pricing MCP server. This might be due to connectivity issues with the pricing service or the specific pricing data being unavailable. Please try rephrasing your question or check if the AWS Pricing API is accessible."

    except Exception as e:
        error_msg = str(e)
        if "AccessDenied" in error_msg or "UnauthorizedOperation" in error_msg:
            return f"Error accessing AWS Pricing through MCP server: {error_msg}. Please ensure you have internet connectivity to access AWS pricing APIs. Note that AWS Pricing API typically doesn't require AWS credentials for public pricing information."
        elif "ServiceUnavailable" in error_msg or "ThrottlingException" in error_msg:
            return f"AWS Pricing service temporarily unavailable: {error_msg}. The AWS Pricing API may be experiencing high load. Please try again in a few moments."
        elif "ConnectionError" in error_msg or "MCP" in error_msg:
            return f"AWS Pricing MCP server connection error: {error_msg}. Please ensure the AWS Pricing MCP server is properly installed and accessible."
        elif "InvalidParameter" in error_msg or "ValidationException" in error_msg:
            return f"Invalid pricing query parameters: {error_msg}. Please check your service names, regions, or instance types and try again with valid AWS service identifiers."
        else:
            return f"Error processing your pricing query through MCP server: {error_msg}. Please check your internet connection and try again. If the issue persists, the AWS Pricing API may be temporarily unavailable."


if __name__ == "__main__":
    aws_pricing_assistant("What's the cost of running a t3.medium EC2 instance in us-east-1?")
