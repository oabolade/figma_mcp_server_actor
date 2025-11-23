# Figma MCP Server

A Model Context Protocol (MCP) server Actor for Apify that enables AI assistants and applications to interact with Figma designs and projects using natural language commands. This Actor creates a secure bridge between AI models and the Figma API, allowing users to query design information, extract asset details, modify design elements, and retrieve project metadata without manually navigating the Figma interface.

## Overview

The Figma MCP Server Actor establishes a long-running HTTP server that implements the Model Context Protocol, enabling seamless integration between AI assistants (like Claude, ChatGPT, and custom AI workflows) and Figma's design platform. It provides a comprehensive set of tools, resources, and prompts for interacting with Figma files, components, assets, and projects.

## Key Features

### 🎨 **Real-time Design File Analysis**

- Analyze Figma file structure and extract metadata
- Extract design tokens, styles, and component information
- Get hierarchical file structures with customizable depth

### 🧩 **Component Extraction & Management**

- List all components and component sets in a file
- Get detailed component information including properties and variants
- Find component usage patterns across files

### 📦 **Automated Asset Export**

- Export design assets in multiple formats (PNG, SVG, PDF, JPG)
- Batch export multiple nodes or entire pages
- Configurable scale factors for different display densities

### 💬 **Collaborative Comment Management**

- Retrieve comments from Figma files
- Create new comments at specific positions or nodes
- Manage feedback and annotations programmatically

### 🔧 **Design Element Modification**

- Get node information for modification planning
- Support for design updates (via Plugin API integration)

### 📊 **Project & Team Management**

- Access project metadata and file listings
- Retrieve team projects and organizational information

## Architecture

This Actor runs as a **long-running HTTP server** that:

- Implements the Model Context Protocol (MCP) JSON-RPC 2.0 specification
- Provides RESTful endpoints for health checks and MCP protocol communication
- Maintains persistent connections for interactive AI assistant workflows
- Supports both Personal Access Token (PAT) and OAuth 2.0 authentication

## Getting Started

### Prerequisites

- Node.js >= 20.0.0
- Apify account ([Sign up here](https://apify.com))
- Figma account with API access
- Figma Personal Access Token ([Generate here](https://www.figma.com/developers/api#access-tokens))

### Installation

1. **Clone or download this Actor**

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Configure your Figma access token:**

   Create `storage/key_value_stores/default/INPUT.json`:

   ```json
   {
     "figmaAccessToken": "your-figma-personal-access-token",
     "port": 8080
   }
   ```

### Local Development

1. **Run the Actor locally:**

   ```bash
   apify run
   ```

2. **Verify the server is running:**

   ```bash
   curl http://localhost:8080/health
   ```

3. **Test the MCP endpoint:**
   ```bash
   curl -X POST http://localhost:8080/mcp \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": 1,
       "method": "initialize",
       "params": {}
     }'
   ```

## Configuration

### Input Parameters

| Parameter               | Type    | Default | Description                                        |
| ----------------------- | ------- | ------- | -------------------------------------------------- |
| `figmaAccessToken`      | string  | -       | Personal Access Token for Figma API authentication |
| `port`                  | integer | 8080    | HTTP server port number                            |
| `oauthClientId`         | string  | -       | OAuth 2.0 client ID (optional, for future use)     |
| `oauthClientSecret`     | string  | -       | OAuth 2.0 client secret (optional, for future use) |
| `maxConcurrentRequests` | integer | 10      | Maximum concurrent requests (1-100)                |
| `enableCaching`         | boolean | true    | Enable response caching for Figma API requests     |

### Environment Variables

You can also set the Figma access token via environment variable:

```bash
export FIGMA_ACCESS_TOKEN="your-token-here"
```

## MCP Protocol Implementation

This Actor implements the full Model Context Protocol specification, including:

### Tools

The server provides 15+ MCP tools organized into categories:

#### File Analysis Tools

- `analyze_file` - Analyze a Figma file structure and extract metadata
- `get_file_structure` - Get hierarchical file structure with customizable depth
- `extract_styles` - Extract design tokens, styles, and design system information

#### Component Extraction Tools

- `list_components` - List all components available in a Figma file
- `get_component_details` - Get detailed information about a specific component
- `find_component_usage` - Find all instances where a component is used

#### Asset Export Tools

- `export_node` - Export a specific node as PNG, SVG, PDF, or JPG
- `export_multiple_nodes` - Export multiple nodes in batch
- `export_file_pages` - Export all pages from a Figma file

#### Comment Management Tools

- `get_comments` - Retrieve all comments from a Figma file
- `create_comment` - Create a new comment at a position or node
- `resolve_comment` - Mark a comment as resolved
- `delete_comment` - Delete a comment

#### Design Modification Tools

- `update_node_properties` - Update properties of a design node
- `get_node_for_modification` - Get detailed node information for modification planning

### Resources

The server exposes read-only resources for accessing Figma data:

- `figma://file/{fileKey}` - File metadata and structure
- `figma://components/{fileKey}` - Component library
- `figma://styles/{fileKey}` - Design tokens and styles
- `figma://project/{projectId}` - Project information
- `figma://team/{teamId}/projects` - Team projects list

### Prompts

Pre-configured prompts for common workflows:

- `analyze_design_file` - Guide for analyzing Figma design files
- `extract_components` - Guide for extracting and documenting components
- `export_assets` - Best practices for asset export
- `check_design_system` - Design system consistency checks
- `manage_feedback` - Comment and feedback management guidance

## Usage Examples

### Example 1: Initialize MCP Connection

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "example-client",
        "version": "1.0.0"
      }
    }
  }'
```

### Example 2: List Available Tools

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

### Example 3: Analyze a Figma File

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "analyze_file",
      "arguments": {
        "fileKey": "your-figma-file-key"
      }
    }
  }'
```

### Example 4: Export a Component as PNG

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "export_node",
      "arguments": {
        "fileKey": "your-figma-file-key",
        "nodeId": "node-id-to-export",
        "format": "PNG",
        "scale": 2
      }
    }
  }'
```

### Example 5: Read a Resource

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "resources/read",
    "params": {
      "uri": "figma://file/your-figma-file-key"
    }
  }'
```

## API Endpoints

### Health Check

```
GET /health
```

Returns server status and health information.

**Response:**

```json
{
  "status": "ok",
  "service": "figma-mcp-server",
  "version": "0.0.1",
  "authenticated": true,
  "timestamp": "2024-11-15T12:00:00.000Z"
}
```

### Root Endpoint

```
GET /
```

Returns service information and available endpoints.

### MCP Protocol Endpoint

```
POST /mcp
```

Main endpoint for MCP JSON-RPC 2.0 protocol communication.

## Deployment to Apify Platform

### 1. Login to Apify

```bash
apify login
```

### 2. Push the Actor

```bash
apify push
```

### 3. Configure Input

After deployment, configure the Actor input in the Apify Console:

- Set your `figmaAccessToken`
- Adjust `port` if needed (default: 8080)
- Configure other optional parameters

### 4. Run the Actor

The Actor will start as a long-running server accessible via:

- **Container URL**: `https://<containerId>.runs.apify.net/`
- **Health Check**: `https://<containerId>.runs.apify.net/health`
- **MCP Endpoint**: `https://<containerId>.runs.apify.net/mcp`

## Integration with AI Assistants

### Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "figma": {
      "url": "https://<containerId>.runs.apify.net/mcp",
      "transport": "http"
    }
  }
}
```

### Custom Integration

The server implements the standard MCP protocol, making it compatible with any MCP client:

```javascript
// Example MCP client usage
const response = await fetch("https://your-actor-url/mcp", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: {
      name: "analyze_file",
      arguments: { fileKey: "your-file-key" },
    },
  }),
});
```

## Authentication

### Personal Access Token (Current)

1. Go to [Figma Settings](https://www.figma.com/settings)
2. Navigate to **Personal access tokens**
3. Click **Generate new token**
4. Copy the token and use it in the Actor input

### OAuth 2.0 (Planned)

OAuth 2.0 support is planned for multi-user scenarios. The structure is in place, and implementation will be added in a future update.

## Error Handling

The server implements comprehensive error handling:

- **Invalid requests**: Returns JSON-RPC 2.0 error responses
- **Authentication errors**: Clear error messages for missing or invalid tokens
- **Figma API errors**: Propagates API errors with context
- **Network errors**: Graceful handling of connection issues

## Rate Limiting

The Figma API has rate limits. The Actor includes:

- Response caching (configurable, enabled by default)
- Request queuing for concurrent requests
- Configurable `maxConcurrentRequests` parameter

## Troubleshooting

### Server Not Starting

- Verify Node.js version >= 20.0.0
- Check that the port is not already in use
- Ensure `figmaAccessToken` is provided in input

### Authentication Errors

- Verify your Figma Personal Access Token is valid
- Check token permissions in Figma settings
- Ensure token hasn't expired

### MCP Protocol Errors

- Verify JSON-RPC 2.0 format is correct
- Check that required parameters are provided
- Review error messages in response

## Development

### Project Structure

```
figma_mcp_actor/
├── .actor/
│   ├── actor.json              # Actor configuration
│   ├── input_schema.json       # Input schema
│   ├── output_schema.json      # Output schema
│   └── dataset_schema.json    # Dataset schema
├── src/
│   ├── main.js                # Entry point
│   ├── mcp/                    # MCP protocol implementation
│   │   ├── server.js
│   │   ├── protocol.js
│   │   └── handlers.js
│   ├── figma/                  # Figma API integration
│   │   ├── client.js
│   │   └── auth.js
│   ├── tools/                  # MCP tools
│   ├── resources/              # MCP resources
│   └── prompts/                # MCP prompts
├── Dockerfile
├── package.json
└── README.md
```

### Running Tests

```bash
npm test
```

### Code Formatting

```bash
npm run format
```

### Linting

```bash
npm run lint
npm run lint:fix
```

## Limitations

- **Design Modification**: Full design modification requires Figma Plugin API (REST API has limited write capabilities)
- **Comment Resolution**: Some comment operations may require Plugin API integration
- **OAuth 2.0**: Currently supports Personal Access Tokens; OAuth 2.0 support is planned

## Contributing

Contributions are welcome! Please ensure:

- Code follows the existing style
- Tests are added for new features
- Documentation is updated

## License

ISC

## Support

For issues, questions, or contributions:

- Check the [Apify Documentation](https://docs.apify.com)
- Review [Figma API Documentation](https://www.figma.com/developers/api)
- Open an issue in the repository [Github Repo](https://github.com/oabolade/figma_mcp_server_actor)

## Changelog

### Version 0.0.1

- Initial release
- Full MCP protocol implementation
- Figma API integration with PAT authentication
- 15+ tools for file analysis, component extraction, asset export, and comments
- Resource and prompt support
- Long-running HTTP server architecture

---

**Built with ❤️ using Apify Actors and Model Context Protocol**
