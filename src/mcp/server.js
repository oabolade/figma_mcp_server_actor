/**
 * MCP JSON-RPC 2.0 Server
 * Handles JSON-RPC requests and routes them to protocol handlers
 */

import MCPProtocol from './protocol.js';

class MCPServer {
    constructor(protocol) {
        this.protocol = protocol || new MCPProtocol();
        this.sessions = new Map();
    }

    /**
     * Handle a JSON-RPC request
     * @param {Object} request - JSON-RPC request object
     * @returns {Promise<Object>} JSON-RPC response
     */
    async handleRequest(request) {
        const { jsonrpc, id, method, params } = request;

        // Validate JSON-RPC version
        if (jsonrpc !== '2.0') {
            return {
                jsonrpc: '2.0',
                id,
                error: {
                    code: -32600,
                    message: 'Invalid Request',
                    data: 'jsonrpc must be "2.0"',
                },
            };
        }

        // Handle notifications (requests without id)
        if (id === undefined) {
            // Process notification but don't return response
            try {
                await this._processMethod(method, params);
            } catch (error) {
                // Log but don't respond to notifications
                console.error('Notification error:', error);
            }
            return null;
        }

        try {
            const result = await this._processMethod(method, params);
            
            return {
                jsonrpc: '2.0',
                id,
                result,
            };
        } catch (error) {
            return {
                jsonrpc: '2.0',
                id,
                error: {
                    code: error.code || -32603,
                    message: error.message || 'Internal error',
                    data: error.data,
                },
            };
        }
    }

    /**
     * Process a method call
     * @private
     */
    async _processMethod(method, params) {
        switch (method) {
            case 'initialize':
                return await this.protocol.initialize(params || {});

            case 'tools/list':
                return await this.protocol.listTools();

            case 'tools/call':
                if (!params || !params.name) {
                    throw new Error('Tool name is required');
                }
                return await this.protocol.callTool(params.name, params.arguments || {});

            case 'resources/list':
                return await this.protocol.listResources();

            case 'resources/read':
                if (!params || !params.uri) {
                    throw new Error('Resource URI is required');
                }
                return await this.protocol.readResource(params.uri);

            case 'prompts/list':
                return await this.protocol.listPrompts();

            case 'prompts/get':
                if (!params || !params.name) {
                    throw new Error('Prompt name is required');
                }
                return await this.protocol.getPrompt(params.name, params.arguments || {});

            default:
                throw {
                    code: -32601,
                    message: 'Method not found',
                    data: `Unknown method: ${method}`,
                };
        }
    }

    /**
     * Handle batch requests
     * @param {Array} requests - Array of JSON-RPC requests
     * @returns {Promise<Array>} Array of JSON-RPC responses
     */
    async handleBatch(requests) {
        const responses = await Promise.all(
            requests.map(req => this.handleRequest(req))
        );
        return responses.filter(res => res !== null); // Filter out notification responses
    }
}

export default MCPServer;


