# Figma MCP Server (Apify Actor)

Model Context Protocol (MCP) server that exposes **Figma REST API** capabilities to AI assistants (Cursor, Claude, custom agents). Runs as a **long-running web server** on the [Apify](https://apify.com) platform (standby / container URL) or locally via `apify run`.

## Features

- **File analysis** — structure, metadata, styles, depth-limited trees  
- **Components** — list, details, usage  
- **Assets** — export nodes (PNG, SVG, PDF, JPG)  
- **Comments** — read and create  
- **Projects / teams** — listings and metadata  
- **MCP resources & prompts** for guided workflows  

## Authentication

### Personal Access Token (default)

Recommended for solo use. Set **`figmaAccessToken`** in Actor input (or `FIGMA_ACCESS_TOKEN` in env).

- Generate: [Figma → Settings → Security → Personal access tokens](https://www.figma.com/settings)  
- API header: `X-Figma-Token`  
- **When PAT is set, OAuth is disabled** for API calls (and `/oauth/*` routes return an error).

### OAuth 2.0 (optional — team / shared files)

Use when you **omit** `figmaAccessToken` and provide a Figma OAuth app:

| Input | Purpose |
|--------|---------|
| `oauthClientId` | From [Figma → Developers → Apps](https://www.figma.com/developers/apps) |
| `oauthClientSecret` | Same app |
| `oauthRedirectUri` | **Exact** redirect URL registered on the app, e.g. `https://<your-run>.runs.apify.net/oauth/callback` |
| `oauthScopes` | Optional; comma-separated scopes. Must be a subset of the app’s configured scopes. Defaults include `file_content:read`, `file_content:write`, `file_comments:read`, `file_comments:write`. |

**Flow**

1. Start the Actor with OAuth fields filled and **no** PAT.  
2. Open **`GET https://<container-url>/oauth/authorize`** in a browser (normal browser — not an embedded WebView; [Figma requirement](https://developers.figma.com/docs/rest-api/authentication/)).  
3. After consent, Figma redirects to **`/oauth/callback`**; tokens are stored in the run’s default **key-value store** (`FIGMA_OAUTH_SESSION`) and refreshed when near expiry.  

Token exchange uses Figma’s documented endpoints (`https://api.figma.com/v1/oauth/token` and `.../oauth/refresh`). Codes expire quickly — complete the redirect promptly.

## Requirements

- **Node.js** ≥ 20  
- **Apify account** (for cloud)  
- **Figma** PAT and/or OAuth app  

## Quick start (Apify Cloud)

```bash
npm install
apify login
apify push
```

In [Apify Console](https://console.apify.com), open the Actor, set input (at minimum `figmaAccessToken`), start with **web server / long-running** as required by your template, then use the **Container URL** from the run.

Deploy reference: `apify push` builds and publishes; see [Apify CLI](https://docs.apify.com/cli).

## Configuration (input)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `figmaAccessToken` | string | — | **PAT (recommended).** If set, used for all Figma API calls. |
| `port` | integer | `8080` | HTTP listen port (Apify may override via `web_server_port`). |
| `oauthClientId` | string | — | OAuth app client ID (only if not using PAT). |
| `oauthClientSecret` | string | — | OAuth app secret (secret input). |
| `oauthRedirectUri` | string | — | Must match Figma app redirect URI exactly. |
| `oauthScopes` | string | — | Optional scope override (comma-separated). |
| `maxConcurrentRequests` | integer | `10` | Reserved / future use. |
| `enableCaching` | boolean | `true` | Cache GET responses from Figma. |

Local / CLI input file example (`apify run`):

```json
{
  "figmaAccessToken": "figd_...",
  "port": 8080
}
```

## HTTP API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Service info and endpoint list |
| `GET` | `/health` | Liveness; includes `auth_mode`: `pat` \| `oauth` \| `pending_oauth`, `figma_authenticated` |
| `POST` | `/mcp` | **MCP JSON-RPC 2.0** (primary transport for this server) |
| `GET` | `/oauth/authorize` | Start OAuth (browser); disabled if PAT is set |
| `GET` | `/oauth/callback` | OAuth redirect handler |

**Apify MCP path:** `.actor/actor.json` sets `webServerMcpPath` to **`/mcp`**. Your MCP client URL is typically:

`https://<container-id>.runs.apify.net/mcp`

(Use the **Container URL** from the run page + `/mcp`.)

## Cursor IDE

1. Deploy and start the Actor; copy the run **Container URL** (while status is **RUNNING**).  
2. Edit **`~/.cursor/mcp.json`** (paths differ on Windows/Linux — see Cursor docs).  

Example (remote HTTP MCP — adjust to your Cursor version’s expected shape):

```json
{
  "mcpServers": {
    "figma-mcp-standby": {
      "url": "https://YOUR_RUN_ID.runs.apify.net/mcp"
    }
  }
}
```

**Notes**

- **`env.APIFY_TOKEN`** in `mcp.json` is **not** passed to this Node process; it does not replace Figma auth. Use **`figmaAccessToken`** (or OAuth) in **Actor input**.  
- Container URLs are **per run** and stop working when the run ends; update `mcp.json` and restart Cursor after a new run.  
- If connection fails, use **Cursor → Output → MCP** and `curl https://.../health`.  

## Claude Desktop / other clients

Use your client’s supported way to attach a **remote MCP** URL (e.g. `mcp-remote` pointing at `https://.../mcp`). Paths and query params depend on the client version.

## Local development

```bash
npm install
apify run
```

Or run the entry with Node if you inject env / input yourself:

```bash
export FIGMA_ACCESS_TOKEN="figd_..."
node src/main.js
```

Check health (port from logs or input):

```bash
curl -s http://localhost:8080/health | jq .
```

Sample MCP initialize:

```bash
curl -s -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'
```

## Project structure

```
figma_mcp_actor/
├── .actor/
│   ├── actor.json           # Apify Actor metadata (incl. webServerMcpPath: /mcp)
│   ├── input_schema.json
│   ├── output_schema.json
│   └── dataset_schema.json
├── src/
│   ├── main.js              # Express app, /mcp, /oauth/*, Apify bootstrap
│   ├── figma/
│   │   ├── auth.js          # PAT + OAuth token exchange, refresh, KV hook
│   │   └── client.js        # Figma REST wrapper
│   ├── oauth/
│   │   └── persist.js       # Apify KV: FIGMA_OAUTH_SESSION
│   ├── mcp/                 # Protocol, handlers, server
│   ├── tools/
│   ├── resources/
│   └── prompts/
├── Dockerfile
├── package.json
└── README.md
```

## MCP tools (overview)

Includes (names may vary slightly in code): file analysis (`analyze_file`, `get_file_structure`, …), components (`list_components`, …), export (`export_node`, …), comments (`get_comments`, `create_comment`, …), design modification helpers, plus **resources** (`figma://file/...`, etc.) and **prompts** for common tasks.

## Limitations

- **REST vs Plugin API** — deep design writes may need the Plugin API; this Actor uses REST where supported.  
- **Ephemeral Apify URLs** — each run has a new base URL unless you use a stable hosting pattern.  
- **OAuth** — single stored session per run (KV); not multi-user concurrent OAuth in one process.  

## Scripts

```bash
npm run lint
npm run lint:fix
npm run format
```

## License

ISC

## Changelog

### 0.2

- Optional **OAuth 2.0** (Figma authorization code + refresh); **PAT remains default** when set.  
- **`/oauth/authorize`** and **`/oauth/callback`**; session persisted in default KV (`FIGMA_OAUTH_SESSION`).  
- Input: `oauthRedirectUri`, `oauthScopes`.  
- Health JSON: `auth_mode`, `figma_authenticated`.  

### 0.1 / 0.0.1

- Initial MCP + Figma REST integration, PAT, long-running server, `/mcp` JSON-RPC.

---

**References:** [Apify Actors](https://docs.apify.com/platform/actors) · [Figma REST API](https://developers.figma.com/docs/rest-api/) · [Model Context Protocol](https://modelcontextprotocol.io)
