from mcp import StdioServerParameters, stdio_client
from strands import Agent, tool
from strands.tools.mcp import MCPClient


@tool
def aws_security_assistant(query: str) -> str:
    """
    Process and respond to AWS Security Assessment related queries using Well-Architected Security MCP server.
    
    This tool leverages the awslabs.well-architected-security-mcp-server which provides comprehensive security assessment capabilities:
    - AWS Well-Architected Security Pillar assessments
    - Security best practices analysis and recommendations
    - AWS security configuration reviews
    - Compliance and governance assessments
    - Security risk identification and mitigation
    - Identity and Access Management (IAM) analysis
    - Data protection and encryption assessments
    - Network security evaluations
    - Incident response and detective controls review

    Args:
        query: The user's AWS security assessment related question

    Returns:
        A helpful response addressing the security query using Well-Architected Security MCP server capabilities
    """

    formatted_query = f"Analyze and respond to this AWS security question, providing clear security assessments, best practices recommendations, and actionable security guidance based on AWS Well-Architected Framework: {query}"
    response = str()

    try:
        security_mcp_server = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="uvx", args=["awslabs.well-architected-security-mcp-server@latest"]
                )
            )
        )

        with security_mcp_server:

            tools = security_mcp_server.list_tools_sync()
            # Create the security assessment agent with specific capabilities
            security_agent = Agent(
                system_prompt="""You are an AWS Security Assessment specialist with access to the Well-Architected Security MCP server tools. Your role is to:
                
                1. Analyze AWS security-related questions and determine the best security assessment tools to use
                2. Leverage the available Well-Architected Security MCP server capabilities including:
                   - assess_security_pillar: Perform comprehensive security pillar assessments
                   - analyze_iam_policies: Review IAM policies and permissions
                   - evaluate_data_protection: Assess data encryption and protection measures
                   - review_network_security: Analyze network security configurations
                   - check_detective_controls: Evaluate logging and monitoring setup
                   - assess_incident_response: Review incident response capabilities
                   - evaluate_identity_foundation: Analyze identity and access management
                   - check_compliance_frameworks: Assess compliance with security standards
                   - Other security-specific tools provided by the MCP server
                
                3. Provide comprehensive security assessments including:
                   - Well-Architected Security Pillar analysis
                   - Security best practices recommendations
                   - Risk identification and prioritization
                   - Remediation guidance and action plans
                   - Compliance gap analysis
                   - Security configuration reviews
                   - Identity and access management optimization
                   - Data protection and encryption strategies
                
                4. When conducting security assessments:
                   - Follow AWS Well-Architected Security Pillar principles
                   - Provide risk-based prioritization of findings
                   - Explain security implications and business impact
                   - Recommend specific AWS security services and features
                   - Include implementation guidance and best practices
                   - Consider compliance requirements and frameworks
                   - Address both preventive and detective controls
                
                5. For security recommendations:
                   - Prioritize high-risk security gaps
                   - Provide step-by-step remediation guidance
                   - Recommend appropriate AWS security tools and services
                   - Include cost considerations for security improvements
                   - Suggest security automation opportunities
                   - Address security monitoring and alerting
                
                6. Security assessment areas to cover:
                   - Identity and Access Management (IAM)
                   - Detective Controls (logging, monitoring, alerting)
                   - Infrastructure Protection (network security, host security)
                   - Data Protection in Transit and at Rest
                   - Incident Response capabilities
                   - Application Security
                   - Compliance and Governance
                
                7. When encountering security issues:
                   - Explain the security risk and potential impact
                   - Provide immediate mitigation steps if critical
                   - Recommend long-term security improvements
                   - Suggest security training and awareness needs
                
                IMPORTANT: Use only the Well-Architected Security MCP server tools provided. Focus on 
                leveraging the full capabilities of the security server for comprehensive security assessments.
                Always provide actionable security recommendations based on AWS security best practices
                and the Well-Architected Framework.
                
                Provide your complete response directly - do not create any files.
                """,
                tools=tools,
            )
            response = str(security_agent(formatted_query))
            print("\n\n")

        if len(response) > 0:
            return response

        return "I apologize, but I couldn't access AWS security assessment information for your query using the Well-Architected Security MCP server. This might be due to insufficient permissions for security analysis, connectivity issues, or the specific security resources being unavailable. Please verify your AWS permissions for security services and try again."

    except Exception as e:
        error_msg = str(e)
        if "AccessDenied" in error_msg or "UnauthorizedOperation" in error_msg:
            return f"Error accessing AWS Security services through MCP server: {error_msg}. Please ensure you have the necessary permissions for security analysis (iam:*, cloudtrail:*, config:*, securityhub:*, guardduty:*, etc.) and that security services are available in your current region."
        elif "ResourceNotFound" in error_msg or "InvalidParameterValue" in error_msg:
            return f"Security resource not found: {error_msg}. Please verify that the specified security resources, policies, or configurations exist in your account and region. Some security assessments may require specific AWS services to be enabled."
        elif "ThrottlingException" in error_msg or "LimitExceeded" in error_msg:
            return f"AWS Security API throttling: {error_msg}. The security assessment APIs are being rate limited. Please wait a moment and try again with a more specific security query."
        elif "ConnectionError" in error_msg or "MCP" in error_msg:
            return f"Well-Architected Security MCP server connection error: {error_msg}. Please ensure the Well-Architected Security MCP server is properly installed and accessible."
        elif "ServiceNotEnabled" in error_msg or "FeatureNotAvailable" in error_msg:
            return f"AWS Security service not enabled: {error_msg}. Some security assessments require specific AWS security services (Security Hub, GuardDuty, Config, etc.) to be enabled in your account."
        else:
            return f"Error processing your security assessment query through MCP server: {error_msg}. Please check your AWS credentials, region settings, and security service availability. Some security assessments may require additional AWS service configurations."


if __name__ == "__main__":
    aws_security_assistant("Assess the security posture of my AWS account")
