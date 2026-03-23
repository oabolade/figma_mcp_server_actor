/**
 * Figma MCP Server Actor - Main Entry Point
 * Long-running HTTP server implementing Model Context Protocol
 *
 * Auth: PAT (default) or OAuth 2.0 when PAT is omitted — for team / shared files.
 */

import { Actor } from "apify";
import express from "express";

import { FigmaAuth, OAUTH_SESSION_KEY } from "./figma/auth.js";
import { FigmaClient } from "./figma/client.js";
import { createMCPHandler } from "./mcp/handlers.js";
import { MCPProtocol } from "./mcp/protocol.js";
import { MCPServer } from "./mcp/server.js";
import { loadOAuthSessionFromKv, saveOAuthSessionToKv } from "./oauth/persist.js";
import { registerFigmaPrompts } from "./prompts/figma-prompts.js";
import { registerFigmaResources } from "./resources/figma-resources.js";
import { registerAssetExportTools } from "./tools/asset-export.js";
import { registerCommentTools } from "./tools/comments.js";
import { registerComponentExtractionTools } from "./tools/component-extraction.js";
import { registerDesignModificationTools } from "./tools/design-modification.js";
import { registerFileAnalysisTools } from "./tools/file-analysis.js";

await Actor.init();

const input = (await Actor.getInput()) ?? {};
const {
  figmaAccessToken,
  port = 8080,
  oauthClientId,
  oauthClientSecret,
  oauthRedirectUri,
  oauthScopes,
  enableCaching = true,
} = input;

const webServerPort = Actor.configuration?.web_server_port || port;

const hasPat = Boolean(figmaAccessToken || process.env.FIGMA_ACCESS_TOKEN);
const hasOAuthApp = Boolean(oauthClientId && oauthClientSecret);

if (!hasPat && !hasOAuthApp) {
  throw new Error(
    "Figma auth: provide figmaAccessToken (PAT, recommended default), or oauthClientId + oauthClientSecret for OAuth-only mode with team files.",
  );
}

const authHolder = { auth: /** @type {FigmaAuth | null} */ (null) };
authHolder.auth = new FigmaAuth({
  figmaAccessToken,
  oauthClientId,
  oauthClientSecret,
  oauthRedirectUri,
  oauthScopes,
  onOAuthPersist: async () => {
    await saveOAuthSessionToKv(authHolder.auth);
  },
});
const { auth } = authHolder;

await loadOAuthSessionFromKv(auth);

if (!auth.isAuthenticated()) {
  // eslint-disable-next-line no-console
  console.warn(
    "[Figma MCP] No PAT and no stored OAuth session yet. Start OAuth: GET /oauth/authorize (after setting oauthRedirectUri in input).",
  );
}

const figmaClient = new FigmaClient(auth);
figmaClient.setCacheEnabled(enableCaching);

const protocol = new MCPProtocol();
const mcpServer = new MCPServer(protocol);

registerFileAnalysisTools(protocol, figmaClient);
registerComponentExtractionTools(protocol, figmaClient);
registerAssetExportTools(protocol, figmaClient);
registerCommentTools(protocol, figmaClient);
registerDesignModificationTools(protocol, figmaClient);
registerFigmaResources(protocol, figmaClient);
registerFigmaPrompts(protocol, figmaClient);

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get("/health", (_req, res) => {
  let mode = "pending_oauth";
  if (auth.pat) mode = "pat";
  else if (auth.isAuthenticated()) mode = "oauth";
  res.json({
    status: "ok",
    service: "figma-mcp-server",
    version: "0.0.1",
    auth_mode: mode,
    figma_authenticated: auth.isAuthenticated(),
    timestamp: new Date().toISOString(),
  });
});

app.get("/", (req, res) => {
  res.json({
    service: "Figma MCP Server",
    version: "0.0.1",
    endpoints: {
      mcp: "/mcp",
      health: "/health",
      oauth_authorize: "/oauth/authorize",
      oauth_callback: "/oauth/callback",
    },
    auth: {
      default: "PAT (figmaAccessToken)",
      optional_oauth:
        "Omit PAT and set oauthClientId, oauthClientSecret, oauthRedirectUri; then visit /oauth/authorize",
    },
    protocol: "Model Context Protocol (MCP)",
    transport: "JSON-RPC 2.0 over HTTP",
  });
});

app.get("/oauth/authorize", (_req, res) => {
  try {
    if (auth.pat) {
      res
        .status(400)
        .type("text")
        .send(
          "PAT is configured — OAuth is disabled. Remove figmaAccessToken to use OAuth for team projects.",
        );
      return;
    }
    if (!auth.hasOAuthAppCredentials()) {
      res.status(400).type("text").send("OAuth app credentials not configured.");
      return;
    }
    if (!auth.oauthRedirectUri) {
      res
        .status(400)
        .type("text")
        .send(
          "Set oauthRedirectUri in Actor input to match a redirect URL in your Figma OAuth app, e.g. https://<run>.runs.apify.net/oauth/callback",
        );
      return;
    }
    const state = auth.generateOAuthState();
    const url = auth.getOAuthAuthorizationUrl(auth.oauthRedirectUri, state);
    res.redirect(302, url);
  } catch (err) {
    res.status(500).type("text").send(err.message);
  }
});

app.get("/oauth/callback", async (req, res) => {
  try {
    if (auth.pat) {
      res.status(400).type("text").send("PAT is configured.");
      return;
    }
    const { code, state, error, error_description: errorDesc } = req.query;
    if (error) {
      res
        .status(400)
        .type("text")
        .send(`OAuth error: ${error} ${errorDesc || ""}`);
      return;
    }
    if (!code || !state) {
      res.status(400).type("text").send("Missing code or state.");
      return;
    }
    if (!auth.consumeOAuthState(String(state))) {
      res
        .status(400)
        .type("text")
        .send("Invalid or expired state; try /oauth/authorize again.");
      return;
    }
    if (!auth.oauthRedirectUri) {
      res.status(500).type("text").send("oauthRedirectUri not configured.");
      return;
    }
    const tokenData = await auth.exchangeCodeForToken(
      String(code),
      auth.oauthRedirectUri,
    );
    auth.setOAuthToken(OAUTH_SESSION_KEY, tokenData);
    await saveOAuthSessionToKv(auth);
    res
      .status(200)
      .type("text")
      .send(
        "Figma connected. You can close this tab. OAuth session is saved to the Actor key-value store for this run.",
      );
  } catch (err) {
    res.status(500).type("text").send(err.message);
  }
});

app.post("/mcp", createMCPHandler(mcpServer));

app.use((err, req, res, _next) => {
  // eslint-disable-next-line no-console
  console.error("Express error:", err);
  res.status(500).json({
    error: "Internal server error",
    message: err.message,
  });
});

const server = app.listen(webServerPort, "0.0.0.0", () => {
  // eslint-disable-next-line no-console
  console.log(`Figma MCP Server listening on port ${webServerPort}`);
  // eslint-disable-next-line no-console
  console.log(`Health: http://localhost:${webServerPort}/health`);
  // eslint-disable-next-line no-console
  console.log(`MCP: http://localhost:${webServerPort}/mcp`);
});

process.on("SIGTERM", () => {
  // eslint-disable-next-line no-console
  console.log("SIGTERM received, shutting down gracefully...");
  server.close(() => {
    // eslint-disable-next-line no-console
    console.log("HTTP server closed");
    Actor.exit();
  });
});

process.on("SIGINT", () => {
  // eslint-disable-next-line no-console
  console.log("SIGINT received, shutting down gracefully...");
  server.close(() => {
    // eslint-disable-next-line no-console
    console.log("HTTP server closed");
    Actor.exit();
  });
});
