from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient


@tool
def aws_documentation_researcher(query: str) -> str:
    """
    Research AWS documentation to answer queries.

    Args:
        query: The user's AWS-related question

    Returns:
        A comprehensive response based on AWS documentation
    """

    formatted_query = f"Research and provide a detailed answer to this AWS question: {query}"
    response = str()

    try:
        # Use the working AWS documentation MCP server
        documentation_mcp_server = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="uvx", args=["awslabs.aws-documentation-mcp-server@latest"]
                )
            )
        )

        with documentation_mcp_server:
            tools = documentation_mcp_server.list_tools_sync()
            
            # Create the research agent with AWS documentation capabilities
            research_agent = Agent(
                system_prompt="""You are an AWS expert researcher with access to comprehensive AWS documentation.
                
                Your approach:
                1. Use available AWS documentation tools to search for relevant information
                2. Find accurate, up-to-date AWS documentation and best practices
                3. Provide detailed explanations with practical examples
                4. Include relevant AWS service configurations and code samples
                5. Cite AWS documentation sources when available
                
                Focus on providing actionable, accurate information based on official AWS resources.
                Always structure your response clearly with headings, examples, and step-by-step guidance where appropriate.
                """,
                tools=tools,
            )
            response = str(research_agent(formatted_query))

        if len(response) > 0:
            return response

        return "I apologize, but I couldn't find relevant AWS documentation for your question. Could you please rephrase or provide more specific details?"

    except Exception as e:
        return f"Error accessing AWS documentation: {str(e)}"


if __name__ == "__main__":
    aws_documentation_researcher("What is Amazon EKS and how do I get started?")
