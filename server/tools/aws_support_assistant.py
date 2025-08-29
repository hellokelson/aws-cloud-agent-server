from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient


@tool
def aws_support_assistant(query: str) -> str:
    """
    Process and respond to AWS Support related queries using AWS Support MCP server.
    
    This tool can help with:
    - AWS Support case management
    - Service health and status information
    - AWS Trusted Advisor recommendations
    - Support plan information
    - Service limit inquiries

    Args:
        query: The user's AWS Support related question

    Returns:
        A helpful response addressing the support query
    """

    formatted_query = f"Analyze and respond to this AWS Support question, providing clear explanations and actionable guidance: {query}"
    response = str()

    try:
        support_mcp_server = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="uvx", args=["awslabs.aws-support-mcp-server@latest"]
                )
            )
        )

        with support_mcp_server:

            tools = support_mcp_server.list_tools_sync()
            # Create the support agent with specific capabilities
            support_agent = Agent(
                system_prompt="""You are an AWS Support specialist with access to AWS Support tools. Your role is to:
                
                1. Analyze AWS Support related questions and determine the best approach
                2. Use AWS Support tools to gather relevant information about:
                   - Support cases and their status
                   - AWS service health and operational status
                   - Trusted Advisor recommendations and findings
                   - Support plan details and entitlements
                   - Service limits and quota information
                3. Provide clear, actionable guidance based on the support data
                4. Help users understand AWS Support processes and best practices
                5. Synthesize findings into comprehensive, helpful responses
                
                When using support tools, focus on providing accurate, up-to-date information
                that helps users resolve their AWS issues or understand their support options.
                
                Provide your complete response directly - do not create any files.
                """,
                tools=tools,
            )
            response = str(support_agent(formatted_query))
            print("\n\n")

        if len(response) > 0:
            return response

        return "I apologize, but I couldn't access AWS Support information for your query. This might be due to insufficient permissions or the support service being unavailable. Please try rephrasing your question or check your AWS Support plan access."

    except Exception as e:
        error_msg = str(e)
        if "SubscriptionRequiredException" in error_msg or "Premium Support Subscription is required" in error_msg:
            return """I see that your AWS account is using the Basic Support plan (free tier), which doesn't provide programmatic access to AWS Support APIs. 

## Creating a Support Case with Basic Support

Since you're on the Basic Support plan, you can still create support cases, but you'll need to use the AWS Console directly:

### Steps to Create a Support Case:

1. **Go to AWS Support Center**: https://console.aws.amazon.com/support/
2. **Click "Create case"**
3. **Choose your case type**:
   - **Account and billing support** (always available)
   - **Service limit increase** (always available)
   - **Technical support** (limited on Basic plan)

### What's Available on Basic Support:
- ✅ Account and billing support
- ✅ Service limit increase requests
- ✅ Access to AWS documentation and whitepapers
- ✅ AWS Personal Health Dashboard
- ✅ AWS Trusted Advisor (7 core checks)
- ❌ Technical support cases (requires paid plan)
- ❌ Programmatic API access (requires paid plan)

### If You Need Technical Support:
Consider upgrading to a paid support plan:
- **Developer Support** ($29/month): Basic technical support + API access
- **Business Support** ($100/month minimum): 24/7 technical support + full API access

### For Immediate Help:
- Check AWS documentation: https://docs.aws.amazon.com/
- Visit AWS re:Post community: https://repost.aws/
- Review AWS Personal Health Dashboard for service issues

Would you like me to help you with account/billing questions or service limit increases instead?"""
        elif "permission" in error_msg.lower() or "access" in error_msg.lower():
            return f"Error accessing AWS Support: {error_msg}. Please ensure you have the necessary AWS Support permissions and an active support plan."
        else:
            return f"Error processing your support query: {error_msg}"


if __name__ == "__main__":
    aws_support_assistant("What are my current AWS support cases?")
