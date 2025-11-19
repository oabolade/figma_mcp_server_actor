/**
 * MCP Request Handlers
 * HTTP request/response handling for MCP server
 */

/**
 * Create Express middleware for MCP JSON-RPC endpoint
 * @param {import('./server.js').MCPServer} mcpServer - MCP server instance
 * @returns {Function} Express middleware
 */
export function createMCPHandler(mcpServer) {
  return async (req, res) => {
    // Set CORS headers
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type");

    // Handle preflight requests
    if (req.method === "OPTIONS") {
      return res.status(200).end();
    }

    // Only accept POST requests
    if (req.method !== "POST") {
      return res.status(405).json({
        error: "Method not allowed",
      });
    }

    // Parse request body
    const { body: request } = req;

    try {
      // Handle batch requests
      if (Array.isArray(request)) {
        const responses = await mcpServer.handleBatch(request);
        return res.json(responses.length > 0 ? responses : null);
      }

      // Handle single request
      const response = await mcpServer.handleRequest(request);

      // Notifications don't return a response
      if (response === null) {
        return res.status(200).end();
      }

      return res.json(response);
    } catch (error) {
      return res.status(500).json({
        jsonrpc: "2.0",
        error: {
          code: -32603,
          message: "Internal error",
          data: error.message,
        },
      });
    }
  };
}
