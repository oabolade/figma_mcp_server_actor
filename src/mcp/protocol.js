/**
 * MCP Protocol Handlers
 * Implements Model Context Protocol JSON-RPC 2.0 methods
 */

class MCPProtocol {
  constructor(tools, resources, prompts) {
    this.tools = tools || new Map();
    this.resources = resources || new Map();
    this.prompts = prompts || new Map();
    this.initialized = false;
    this.serverInfo = {
      name: "figma-mcp-server",
      version: "0.0.1",
    };
  }

  /**
   * Initialize the MCP protocol session
   * @param {Object} _params - Initialize parameters
   * @returns {Object} Initialize result
   */
  async initialize(_params) {
    if (this.initialized) {
      throw new Error("Protocol already initialized");
    }

    this.initialized = true;

    return {
      protocolVersion: "2024-11-05",
      capabilities: {
        tools: {},
        resources: {},
        prompts: {},
      },
      serverInfo: this.serverInfo,
    };
  }

  /**
   * List all available tools
   * @returns {Object} Tools list
   */
  async listTools() {
    const toolsList = Array.from(this.tools.values()).map((tool) => ({
      name: tool.name,
      description: tool.description,
      inputSchema: tool.inputSchema,
    }));

    return {
      tools: toolsList,
    };
  }

  /**
   * Call a tool by name
   * @param {string} name - Tool name
   * @param {Object} arguments_ - Tool arguments
   * @returns {Object} Tool result
   */
  async callTool(name, arguments_) {
    if (!this.tools.has(name)) {
      throw new Error(`Tool not found: ${name}`);
    }

    const tool = this.tools.get(name);

    try {
      const result = await tool.handler(arguments_);
      return {
        content: [
          {
            type: "text",
            text:
              typeof result === "string"
                ? result
                : JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Error: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }

  /**
   * List all available resources
   * @returns {Object} Resources list
   */
  async listResources() {
    const resourcesList = Array.from(this.resources.values()).map(
      (resource) => ({
        uri: resource.uri,
        name: resource.name,
        description: resource.description,
        mimeType: resource.mimeType,
      }),
    );

    return {
      resources: resourcesList,
    };
  }

  /**
   * Read a resource by URI
   * @param {string} uri - Resource URI
   * @returns {Object} Resource content
   */
  async readResource(uri) {
    if (!this.resources.has(uri)) {
      throw new Error(`Resource not found: ${uri}`);
    }

    const resource = this.resources.get(uri);

    try {
      const content = await resource.handler(uri);
      return {
        contents: [
          {
            uri,
            mimeType: resource.mimeType || "application/json",
            text:
              typeof content === "string"
                ? content
                : JSON.stringify(content, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to read resource ${uri}: ${error.message}`);
    }
  }

  /**
   * List all available prompts
   * @returns {Object} Prompts list
   */
  async listPrompts() {
    const promptsList = Array.from(this.prompts.values()).map((prompt) => ({
      name: prompt.name,
      description: prompt.description,
      arguments: prompt.arguments || [],
    }));

    return {
      prompts: promptsList,
    };
  }

  /**
   * Get a prompt by name
   * @param {string} name - Prompt name
   * @param {Object} arguments_ - Prompt arguments
   * @returns {Object} Prompt result
   */
  async getPrompt(name, arguments_ = {}) {
    if (!this.prompts.has(name)) {
      throw new Error(`Prompt not found: ${name}`);
    }

    const prompt = this.prompts.get(name);

    try {
      const result = await prompt.handler(arguments_);
      return {
        description: result.description || prompt.description,
        messages: result.messages || [],
      };
    } catch (error) {
      throw new Error(`Failed to get prompt ${name}: ${error.message}`);
    }
  }

  /**
   * Register a tool
   * @param {string} name - Tool name
   * @param {Object} tool - Tool definition
   */
  registerTool(name, tool) {
    this.tools.set(name, {
      name,
      description: tool.description,
      inputSchema: tool.inputSchema,
      handler: tool.handler,
    });
  }

  /**
   * Register a resource
   * @param {string} uri - Resource URI
   * @param {Object} resource - Resource definition
   */
  registerResource(uri, resource) {
    this.resources.set(uri, {
      uri,
      name: resource.name,
      description: resource.description,
      mimeType: resource.mimeType || "application/json",
      handler: resource.handler,
    });
  }

  /**
   * Register a prompt
   * @param {string} name - Prompt name
   * @param {Object} prompt - Prompt definition
   */
  registerPrompt(name, prompt) {
    this.prompts.set(name, {
      name,
      description: prompt.description,
      arguments: prompt.arguments || [],
      handler: prompt.handler,
    });
  }
}

export { MCPProtocol };
