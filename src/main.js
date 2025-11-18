/**
 * Figma MCP Server Actor - Main Entry Point
 * Long-running HTTP server implementing Model Context Protocol
 */

import { Actor } from 'apify';
import express from 'express';
import { createMCPHandler } from './mcp/handlers.js';
import MCPServer from './mcp/server.js';
import MCPProtocol from './mcp/protocol.js';
import FigmaClient from './figma/client.js';
import FigmaAuth from './figma/auth.js';

// Import tools, resources, and prompts
import { registerFileAnalysisTools } from './tools/file-analysis.js';
import { registerComponentExtractionTools } from './tools/component-extraction.js';
import { registerAssetExportTools } from './tools/asset-export.js';
import { registerCommentTools } from './tools/comments.js';
import { registerDesignModificationTools } from './tools/design-modification.js';
import { registerFigmaResources } from './resources/figma-resources.js';
import { registerFigmaPrompts } from './prompts/figma-prompts.js';

await Actor.init();

// Get input configuration
const input = (await Actor.getInput()) ?? {};
const {
    figmaAccessToken,
    port = 8080,
    oauthClientId,
    oauthClientSecret,
    maxConcurrentRequests = 10,
    enableCaching = true,
} = input;

// Get web server port from Apify configuration (takes precedence)
const webServerPort = Actor.configuration?.web_server_port || port;

// Initialize Figma authentication and client
const auth = new FigmaAuth({
    figmaAccessToken,
    oauthClientId,
    oauthClientSecret,
});

if (!auth.isAuthenticated()) {
    throw new Error('Figma authentication required. Please provide figmaAccessToken in input.');
}

const figmaClient = new FigmaClient(auth);
figmaClient.setCacheEnabled(enableCaching);

// Initialize MCP protocol and server
const protocol = new MCPProtocol();
const mcpServer = new MCPServer(protocol);

// Register all tools
registerFileAnalysisTools(protocol, figmaClient);
registerComponentExtractionTools(protocol, figmaClient);
registerAssetExportTools(protocol, figmaClient);
registerCommentTools(protocol, figmaClient);
registerDesignModificationTools(protocol, figmaClient);

// Register all resources
registerFigmaResources(protocol, figmaClient);

// Register all prompts
registerFigmaPrompts(protocol, figmaClient);

// Create Express app
const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        service: 'figma-mcp-server',
        version: '0.0.1',
        authenticated: auth.isAuthenticated(),
        timestamp: new Date().toISOString(),
    });
});

// Root endpoint info
app.get('/', (req, res) => {
    res.json({
        service: 'Figma MCP Server',
        version: '0.0.1',
        endpoints: {
            mcp: '/mcp',
            health: '/health',
        },
        protocol: 'Model Context Protocol (MCP)',
        transport: 'JSON-RPC 2.0 over HTTP',
    });
});

// MCP JSON-RPC endpoint
app.post('/mcp', createMCPHandler(mcpServer));

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Express error:', err);
    res.status(500).json({
        error: 'Internal server error',
        message: err.message,
    });
});

// Start HTTP server
const server = app.listen(webServerPort, '0.0.0.0', () => {
    console.log(`Figma MCP Server listening on port ${webServerPort}`);
    console.log(`Health check: http://localhost:${webServerPort}/health`);
    console.log(`MCP endpoint: http://localhost:${webServerPort}/mcp`);
    console.log('Server is running in long-running mode...');
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully...');
    server.close(() => {
        console.log('HTTP server closed');
        Actor.exit();
    });
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully...');
    server.close(() => {
        console.log('HTTP server closed');
        Actor.exit();
    });
});

// Keep the process alive (long-running mode)
// The server will continue running until explicitly stopped


