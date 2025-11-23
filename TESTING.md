# Testing Guide for Figma MCP Server

This guide shows you how to test the Figma MCP Server tools end-to-end without connecting to an LLM application.

## Testing Options

### Option 1: Local Testing (Recommended for Development) ⭐

**Best for:** Quick iteration, debugging, development

1. **Start the server locally:**
   ```bash
   apify run
   ```
   
   This will:
   - Load your Figma token from `storage/key_value_stores/default/INPUT.json`
   - Start the server on port 8080 (default)

2. **In a new terminal, run the test script:**
   ```bash
   ./test-mcp.sh
   ```

   Or test manually with curl commands (see examples below).

3. **Access the server:**
   - Health: `http://localhost:8080/health`
   - MCP endpoint: `http://localhost:8080/mcp`

---

### Option 2: Apify Platform Testing

**Best for:** Testing in production-like environment

1. **Deploy to Apify** (if not already deployed):
   ```bash
   apify push
   ```

2. **Start a run** from Apify Console:
   - Go to your Actor page
   - Click "Start" button
   - The Actor will start and provide a container URL

3. **Get the container URL:**
   - Format: `https://<containerId>.runs.apify.net/`
   - Found in the run logs or Console

4. **Test using the container URL:**
   ```bash
   ./test-mcp.sh <containerId>.runs.apify.net 80
   ```
   
   Or manually:
   ```bash
   curl https://<containerId>.runs.apify.net/health
   ```

**Note:** For Apify platform, the port is usually 80 (HTTP) or 443 (HTTPS).

---

## Manual Testing with curl

### 1. Health Check
```bash
curl http://localhost:8080/health
```

### 2. Initialize MCP Protocol
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
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }'
```

### 3. List All Tools
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

### 4. Call a Tool - Analyze File
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
        "fileKey": "YOUR_FIGMA_FILE_KEY"
      }
    }
  }'
```

### 5. Call a Tool - List Components
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "list_components",
      "arguments": {
        "fileKey": "YOUR_FIGMA_FILE_KEY"
      }
    }
  }'
```

### 6. Read a Resource
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 5,
    "method": "resources/read",
    "params": {
      "uri": "figma://file/YOUR_FIGMA_FILE_KEY"
    }
  }'
```

### 7. Get a Prompt
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "prompts/get",
    "params": {
      "name": "analyze_design_file",
      "arguments": {
        "fileKey": "YOUR_FIGMA_FILE_KEY"
      }
    }
  }'
```

---

## Available Tools to Test

### File Analysis Tools
- `analyze_file` - Analyze a Figma file structure
- `get_file_structure` - Get hierarchical file structure
- `extract_styles` - Extract design tokens and styles

### Component Extraction Tools
- `list_components` - List all components in a file
- `get_component_details` - Get detailed component information
- `find_component_usage` - Find component usage instances

### Asset Export Tools
- `export_node` - Export a specific node
- `export_multiple_nodes` - Export multiple nodes
- `export_file_pages` - Export all pages

### Comment Management Tools
- `get_comments` - Retrieve all comments
- `create_comment` - Create a new comment
- `resolve_comment` - Mark comment as resolved
- `delete_comment` - Delete a comment

### Design Modification Tools
- `update_node_properties` - Update node properties
- `get_node_for_modification` - Get node info for modification

---

## Example: Complete Test Flow

1. **Start the server:**
   ```bash
   apify run
   ```

2. **In another terminal, test step by step:**
   ```bash
   # Health check
   curl http://localhost:8080/health
   
   # Initialize
   curl -X POST http://localhost:8080/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
   
   # List tools
   curl -X POST http://localhost:8080/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
   
   # Call analyze_file (replace FILE_KEY with your Figma file key)
   curl -X POST http://localhost:8080/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"analyze_file","arguments":{"fileKey":"FILE_KEY"}}}'
   ```

---

## Using the Test Script

The provided `test-mcp.sh` script automates common tests:

```bash
# Test locally (default: localhost:8080)
./test-mcp.sh

# Test with custom host/port
./test-mcp.sh localhost 8080

# Test on Apify platform (using container URL)
./test-mcp.sh <containerId>.runs.apify.net 80

# Test with a specific Figma file

```

**Requirements:**
- `curl` - for HTTP requests
- `jq` - for JSON formatting (optional but recommended)
  ```bash
  # Install jq:
  # macOS: brew install jq
  # Linux: apt-get install jq or yum install jq
  ```

---

## Tips

1. **Use jq for better output:**
   ```bash
   curl ... | jq '.'
   ```

2. **Save responses for analysis:**
   ```bash
   curl ... > response.json
   ```

3. **Check logs:** When running locally with `apify run`, watch the terminal for server logs and errors.

4. **Get a Figma file key:**
   - Open any Figma file in your browser
   - The URL format is: `https://www.figma.com/file/FILE_KEY/...`
   - Copy the `FILE_KEY` part

---

## Troubleshooting

**Server not starting:**
- Check that `figmaAccessToken` is set in `storage/key_value_stores/default/INPUT.json`
- Verify the port (8080) is not already in use
- Check Node.js version >= 20.0.0

**401/403 errors:**
- Verify your Figma Personal Access Token is valid
- Check token permissions in Figma settings

**Connection refused (Apify platform):**
- Make sure the Actor run is in "RUNNING" status
- Wait a few seconds after starting the run for the server to start
- Check the run logs for the container URL


