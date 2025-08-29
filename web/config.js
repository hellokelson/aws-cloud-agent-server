// Web portal configuration
const WEB_CONFIG = {
    // Web UI server port
    WEB_PORT: 80,
    
    // Agent Core server configuration
    AGENT_SERVER_HOST: 'localhost',
    AGENT_SERVER_PORT: 8080,
    
    // Full agent server URL
    get AGENT_SERVER_URL() {
        return `http://${this.AGENT_SERVER_HOST}:${this.AGENT_SERVER_PORT}`;
    }
};
