# Figma MCP Server

A Model Context Protocol (MCP) server Actor for Apify that enables AI assistants and applications to interact with Figma designs and projects using natural language commands. This Actor creates a secure bridge between AI models and the Figma API, allowing users to query design information, extract asset details, modify design elements, and retrieve project metadata without manually navigating the Figma interface.

## Overview

The Figma MCP Server Actor establishes a long-running HTTP server that implements the Model Context Protocol, enabling seamless integration between AI assistants (like Claude Desktop, Cursor IDE, and custom AI workflows) and Figma's design platform. It provides a comprehensive set of tools, resources, and prompts for interacting with Figma files, components, assets, and projects.

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
- Supports **Server-Sent Events (SSE)** transport for real-time communication
- Provides RESTful endpoints for health checks and MCP protocol communication
- Maintains persistent connections for interactive AI assistant workflows
- Supports both Personal Access Token (PAT) and OAuth 2.0 authentication

### Transport Protocols

The server supports two transport mechanisms:

1. **HTTP POST** (`/mcp`) - Standard JSON-RPC 2.0 over HTTP
2. **Server-Sent Events (SSE)** (`/mcp/sse`) - Real-time bidirectional communication via SSE

The SSE transport is recommended for AI clients like Cursor IDE and Claude Desktop as it provides better real-time communication and connection management.

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

   Or use the local test server:

   ```bash
   node src/main-local.js
   ```

2. **Verify the server is running:**

   ```bash
   curl http://localhost:4321/health
   ```

3. **Test the MCP endpoint:**
   ```bash
   curl -X POST http://localhost:4321/mcp \
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
| `port`                  | integer | 4321    | HTTP server port number (overridden by Apify)      |
| `oauthClientId`         | string  | -       | OAuth 2.0 client ID (optional, for future use)     |
| `oauthClientSecret`     | string  | -       | OAuth 2.0 client secret (optional, for future use) |
| `maxConcurrentRequests` | integer | 10      | Maximum concurrent requests (1-100)                |
| `enableCaching`         | boolean | true    | Enable response caching for Figma API requests     |

### Environment Variables

You can also set the Figma access token via environment variable:

```bash
export FIGMA_ACCESS_TOKEN="your-token-here"
```

## Integration with AI Assistants

### 🎯 Cursor IDE

Cursor IDE supports MCP servers via SSE transport. Follow these steps to connect:

#### Step 1: Deploy and Start the Actor

1. **Deploy the Actor to Apify:**
   ```bash
   apify login
   apify push
   ```

2. **Start a new Actor run in Apify Console:**
   - Go to https://console.apify.com/actors/uyMWRGrQEwz1bA8Mc
   - Click "Start" or "Run"
   - Use input: `{"figmaAccessToken": "your-figma-token"}`
   - Select **"Start Web Server"** method
   - Wait for "Server is running in long-running mode..." in logs

3. **Get the Container URL:**
   - In the Actor run details page, copy the **Container URL** (e.g., `https://xxxxx.runs.apify.net`)

#### Step 2: Configure Cursor IDE

1. **Locate your Cursor MCP configuration file:**
   - **macOS**: `~/.cursor/mcp.json`
   - **Windows**: `%APPDATA%\Cursor\mcp.json`
   - **Linux**: `~/.config/Cursor/mcp.json`

2. **Add the Figma MCP server configuration:**

   ```json
   {
     "mcpServers": {
       "figma-mcp-standby": {
         "url": "https://<CONTAINER-ID>.runs.apify.net/mcp/sse",
         "env": {
           "APIFY_TOKEN": "your-apify-api-token"
         }
       }
     }
   }
   ```

   **Important:** Replace:
   - `<CONTAINER-ID>` with your actual Apify container ID from Step 1
   - `your-apify-api-token` with your Apify API token (optional, but recommended for authentication)

3. **Save the configuration file**

#### Step 3: Restart Cursor IDE

⚠️ **Critical:** You **must fully restart** Cursor IDE for the changes to take effect:

1. **macOS**: Press `Cmd+Q` to fully quit Cursor (not just close the window)
2. **Windows**: Close all Cursor windows and ensure it's not running in the background
3. **Linux**: Fully quit Cursor from the application menu

4. **Wait 5-10 seconds**, then reopen Cursor IDE

5. **Verify the connection:**
   - Go to **Settings** → **MCP**
   - Look for `figma-mcp-standby` in the list
   - It should show a **green status** indicating it's connected

#### Step 4: Test the Connection

Once connected, you can test the Figma MCP tools by asking Cursor:

- "What Figma MCP tools are available?"
- "Analyze Figma file [FILE_KEY]"
- "List components in Figma file [FILE_KEY]"
- "Export node [NODE_ID] from Figma file [FILE_KEY]"

#### Automated Configuration Update (Optional)

For convenience, you can use the provided script to automatically update your Cursor config when starting a new Actor run:

```bash
cd /path/to/figma_mcp_actor
export APIFY_TOKEN="your-apify-api-token"
./update-mcp-config.sh
```

This script will:
- Find the latest running Actor run
- Extract the container URL
- Update your `~/.cursor/mcp.json` automatically
- Create a backup of your existing config

### 🎯 Claude Desktop

Claude Desktop supports MCP servers via HTTP transport. Follow these steps:

#### Step 1: Deploy and Start the Actor

1. **Deploy the Actor to Apify** (same as Cursor IDE Step 1)

2. **Start a new Actor run** and get the Container URL

#### Step 2: Configure Claude Desktop

1. **Locate your Claude Desktop configuration file:**
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Add the Figma MCP server configuration:**

   ```json
   {
     "mcpServers": {
       "figma-standby": {
         "command": "npx",
         "args": [
        "-y",
        "mcp-remote",
        "https://x3i5l99zpsyz.runs.apify.net/mcp/sse?token=your apify api token"
      ]
       }
     }
   }
   ```

   **Note:** Claude Desktop uses HTTP transport (`/mcp` endpoint), not SSE.

3. **Save the configuration file**

#### Step 3: Restart Claude Desktop

⚠️ **Critical:** You **must fully restart** Claude Desktop:

1. **macOS**: Press `Cmd+Q` to fully quit Claude Desktop
2. **Windows**: Close all Claude Desktop windows
3. **Linux**: Fully quit Claude Desktop from the application menu

4. **Wait 5-10 seconds**, then reopen Claude Desktop

5. **Verify the connection:**
   - Check Claude Desktop settings or logs for MCP server status
   - The Figma MCP server should appear in the available MCP servers list

## Important Limitations & Troubleshooting

### ⚠️ Ephemeral Container URLs

**The Challenge:**
- Apify assigns a **unique container URL** for each Actor run
- When you start a new run, you get a new container URL
- AI clients (Cursor IDE, Claude Desktop) **cache the connection URL**
- If the URL changes, the client continues using the old cached URL, causing connection failures

**The Solution:**

1. **Every time you start a new Actor run:**
   - Update your MCP configuration file (`mcp.json` or `claude_desktop_config.json`) with the new container URL
   - **Fully restart** the AI client application

2. **Use the automated update script** (for Cursor IDE):
   ```bash
   ./update-mcp-config.sh
   ```

3. **Keep Actor runs running** as long as you need the connection (don't stop them unless necessary)

### 🔄 Connection Issues

#### Problem: "Connection failed" or "Server not found"

**Solutions:**

1. **Verify the Actor is still running:**
   - Check Apify Console → Actor runs
   - Ensure status is **RUNNING** (not READY, SUCCEEDED, or FAILED)

2. **Check the container URL:**
   - Go to Actor run details in Apify Console
   - Verify the Container URL matches what's in your config file
   - Test the URL manually: `curl https://<container-url>/health`

3. **Clear client cache and restart:**
   - **Cursor IDE**: Fully quit (Cmd+Q), wait 10 seconds, reopen
   - **Claude Desktop**: Fully quit, wait 10 seconds, reopen
   - Sometimes you may need to toggle the MCP server OFF and ON in settings

4. **Verify configuration file syntax:**
   - Ensure JSON is valid (no trailing commas, proper quotes)
   - Check file path is correct for your OS

#### Problem: "Protocol already initialized" error

**Solution:**
- This is normal during reconnection attempts
- The server now supports idempotent initialization
- If you see this error repeatedly, fully restart the client

#### Problem: Tools not appearing in client

**Solutions:**

1. **Verify connection status:**
   - Check that the MCP server shows as "connected" (green status)

2. **Check client logs:**
   - **Cursor IDE**: View → Output → Select "MCP" from dropdown
   - Look for initialization errors or connection issues

3. **Reinitialize the connection:**
   - Toggle the MCP server OFF and ON in client settings
   - Or fully restart the client

4. **Verify Actor is still running:**
   - Container URLs expire when Actor runs stop
   - Start a new run if needed

### 🚀 Best Practices

1. **Keep Actor runs running** while actively using the MCP server
2. **Use the automated update script** when starting new runs (Cursor IDE)
3. **Always fully restart** the AI client after updating the config
4. **Monitor Actor run status** in Apify Console
5. **Plan for migration** to a stable URL host (Railway, Render, etc.) for production use

### 🔮 Future Improvements

For production use, consider migrating to a cloud service with stable URLs:

- **Railway** - Easy deployment with persistent URLs
- **Render** - Free tier available, stable URLs
- **Fly.io** - Global edge deployment
- **DigitalOcean App Platform** - Simple deployment

This would eliminate the need to update configs and restart clients each time.

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

Returns service information and available endpoints, including SSE endpoint information.

### MCP Protocol Endpoints

#### HTTP Transport

```
POST /mcp
```

Main endpoint for MCP JSON-RPC 2.0 protocol communication over HTTP.

#### SSE Transport

```
GET /mcp/sse
```

Establishes a Server-Sent Events connection for real-time bidirectional communication.

```
POST /mcp/messages
```

Sends JSON-RPC messages over an active SSE connection.

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
- Adjust `port` if needed (default: 4321, but Apify overrides this)
- Configure other optional parameters

### 4. Run the Actor

The Actor will start as a long-running server accessible via:

- **Container URL**: `https://<containerId>.runs.apify.net/`
- **Health Check**: `https://<containerId>.runs.apify.net/health`
- **MCP HTTP Endpoint**: `https://<containerId>.runs.apify.net/mcp`
- **MCP SSE Endpoint**: `https://<containerId>.runs.apify.net/mcp/sse`

**Important:** The container URL is unique per run and expires when the run stops.

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

### SSE Connection Issues

- Ensure you're using the `/mcp/sse` endpoint (not `/mcp`)
- Check that the Actor run is still RUNNING
- Verify the container URL is correct and accessible
- Check Cursor IDE logs for SSE-specific errors

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
│   ├── main.js                # Entry point (Apify)
│   ├── main-local.js          # Local test server
│   ├── mcp/                    # MCP protocol implementation
│   │   ├── server.js
│   │   ├── protocol.js
│   │   ├── handlers.js
│   │   └── sse-handlers.js     # SSE transport handlers
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
- **Ephemeral URLs**: Apify container URLs expire when runs stop, requiring config updates and client restarts

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
- Review [Model Context Protocol Specification](https://modelcontextprotocol.io)
- Open an issue in the repository

## Changelog

### Version 0.0.1

- Initial release
- Full MCP protocol implementation
- Figma API integration with PAT authentication
- 15+ tools for file analysis, component extraction, asset export, and comments
- Resource and prompt support
- Long-running HTTP server architecture
- **SSE transport support** for real-time communication
- Idempotent initialization for client reconnections

---

**Built with ❤️ using Apify Actors and Model Context Protocol**
