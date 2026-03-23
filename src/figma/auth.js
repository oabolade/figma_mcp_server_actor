/**
 * Figma API Authentication Module
 * - Default: Personal Access Token (PAT) via X-Figma-Token
 * - Optional: OAuth 2.0 for team/shared files (Bearer), used when PAT is not set
 */

import crypto from "node:crypto";

import fetch from "node-fetch";

/** Single-session OAuth key (one linked Figma user per Actor run / KV store) */
export const OAUTH_SESSION_KEY = "__session__";

const FIGMA_OAUTH_AUTHORIZE = "https://www.figma.com/oauth";
const FIGMA_OAUTH_TOKEN = "https://api.figma.com/v1/oauth/token";
const FIGMA_OAUTH_REFRESH = "https://api.figma.com/v1/oauth/refresh";

/** Default scopes — must be a subset of scopes enabled on your OAuth app in Figma */
const DEFAULT_OAUTH_SCOPES =
  "file_content:read,file_content:write,file_comments:read,file_comments:write";

class FigmaAuth {
  constructor(config = {}) {
    this.pat = config.figmaAccessToken || process.env.FIGMA_ACCESS_TOKEN;
    this.oauthClientId =
      config.oauthClientId || process.env.FIGMA_OAUTH_CLIENT_ID;
    this.oauthClientSecret =
      config.oauthClientSecret || process.env.FIGMA_OAUTH_CLIENT_SECRET;
    this.oauthRedirectUri =
      config.oauthRedirectUri || process.env.FIGMA_OAUTH_REDIRECT_URI;
    this.oauthScopes =
      config.oauthScopes || process.env.FIGMA_OAUTH_SCOPES || DEFAULT_OAUTH_SCOPES;
    /** Optional: called after refresh so KV stays in sync (e.g. saveOAuthSessionToKv) */
    this.onOAuthPersist = config.onOAuthPersist ?? null;
    /** @type {Map<string, { accessToken: string, refreshToken?: string, expiresAt: number }>} */
    this.oauthTokens = new Map();
    /** CSRF state -> createdAt ms */
    this._oauthStates = new Map();
  }

  /**
   * PAT always wins when set (default access method).
   * Otherwise use stored OAuth session (Bearer).
   */
  getAuthHeaders(_userId = null) {
    if (this.pat) {
      return {
        "X-Figma-Token": this.pat,
      };
    }

    const token = this.oauthTokens.get(OAUTH_SESSION_KEY);
    if (token?.accessToken) {
      return {
        Authorization: `Bearer ${token.accessToken}`,
      };
    }

    throw new Error(
      "No Figma authentication: set figmaAccessToken (PAT), or complete OAuth at GET /oauth/authorize (when PAT is unset and OAuth app is configured).",
    );
  }

  /**
   * True if PAT is set, or a usable OAuth session exists in memory.
   */
  isAuthenticated() {
    if (this.pat) return true;
    const t = this.oauthTokens.get(OAUTH_SESSION_KEY);
    return Boolean(t?.accessToken);
  }

  /**
   * True if OAuth app credentials are configured (allows starting server to run OAuth flow).
   */
  hasOAuthAppCredentials() {
    return Boolean(this.oauthClientId && this.oauthClientSecret);
  }

  /**
   * Restore session from persisted JSON (e.g. Apify KV).
   * @param {{ accessToken: string, refreshToken?: string, expiresAt: number }} payload
   */
  restoreOAuthSession(payload) {
    if (!payload?.accessToken) return;
    this.oauthTokens.set(OAUTH_SESSION_KEY, {
      accessToken: payload.accessToken,
      refreshToken: payload.refreshToken,
      expiresAt: payload.expiresAt ?? Date.now() + 90 * 24 * 60 * 60 * 1000,
    });
  }

  /** @returns {{ accessToken: string, refreshToken?: string, expiresAt: number } | null} */
  getOAuthSessionForStorage() {
    return this.oauthTokens.get(OAUTH_SESSION_KEY) ?? null;
  }

  /**
   * @param {string} _userId - kept for API compatibility; session is always OAUTH_SESSION_KEY
   * @param {Object} tokenData - Figma token response
   */
  setOAuthToken(_userId, tokenData) {
    const expiresIn = Number(tokenData.expires_in) || 7776000; // ~90d default
    this.oauthTokens.set(OAUTH_SESSION_KEY, {
      accessToken: tokenData.access_token,
      refreshToken: tokenData.refresh_token,
      expiresAt: Date.now() + expiresIn * 1000,
    });
  }

  getOAuthAuthorizationUrl(redirectUri, state) {
    if (!this.oauthClientId) {
      throw new Error("OAuth client ID not configured");
    }

    const params = new URLSearchParams({
      client_id: this.oauthClientId,
      redirect_uri: redirectUri,
      response_type: "code",
      scope: this.oauthScopes,
      state,
    });

    return `${FIGMA_OAUTH_AUTHORIZE}?${params.toString()}`;
  }

  /**
   * @param {string} code
   * @param {string} redirectUri - must match Figma app + token request exactly
   * @returns {Promise<Object>} Raw Figma JSON (access_token, refresh_token, expires_in, ...)
   */
  async exchangeCodeForToken(code, redirectUri) {
    if (!this.oauthClientId || !this.oauthClientSecret) {
      throw new Error("OAuth credentials not configured");
    }

    const basic = Buffer.from(
      `${this.oauthClientId}:${this.oauthClientSecret}`,
    ).toString("base64");

    const body = new URLSearchParams({
      redirect_uri: redirectUri,
      code,
      grant_type: "authorization_code",
    });

    const response = await fetch(FIGMA_OAUTH_TOKEN, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Authorization: `Basic ${basic}`,
      },
      body: body.toString(),
    });

    const text = await response.text();
    if (!response.ok) {
      throw new Error(
        `Figma OAuth token exchange failed: ${response.status} ${text}`,
      );
    }

    return JSON.parse(text);
  }

  /**
   * Refresh access token (Figma invalidates previous access token on refresh).
   */
  async refreshAccessToken() {
    const session = this.oauthTokens.get(OAUTH_SESSION_KEY);
    if (!session?.refreshToken) {
      throw new Error("No refresh token; re-authorize via GET /oauth/authorize");
    }
    if (!this.oauthClientId || !this.oauthClientSecret) {
      throw new Error("OAuth credentials not configured");
    }

    const basic = Buffer.from(
      `${this.oauthClientId}:${this.oauthClientSecret}`,
    ).toString("base64");

    const body = new URLSearchParams({
      refresh_token: session.refreshToken,
    });

    const response = await fetch(FIGMA_OAUTH_REFRESH, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        Authorization: `Basic ${basic}`,
      },
      body: body.toString(),
    });

    const text = await response.text();
    if (!response.ok) {
      throw new Error(
        `Figma OAuth refresh failed: ${response.status} ${text}`,
      );
    }

    const data = JSON.parse(text);
    const expiresIn = Number(data.expires_in) || 7776000;
    this.oauthTokens.set(OAUTH_SESSION_KEY, {
      accessToken: data.access_token,
      refreshToken: session.refreshToken,
      expiresAt: Date.now() + expiresIn * 1000,
    });
    if (typeof this.onOAuthPersist === "function") {
      await this.onOAuthPersist();
    }
    return data;
  }

  /**
   * If using OAuth (no PAT), refresh access token when near expiry.
   * No-op when PAT is set.
   */
  async ensureAccessToken() {
    if (this.pat) return;

    const session = this.oauthTokens.get(OAUTH_SESSION_KEY);
    if (!session?.accessToken) return;

    const bufferMs = 120_000; // 2 minutes
    if (session.expiresAt > Date.now() + bufferMs) return;

    if (session.refreshToken) {
      await this.refreshAccessToken();
    }
  }

  generateOAuthState() {
    const state = crypto.randomBytes(24).toString("hex");
    this._oauthStates.set(state, Date.now());
    // prune old states (> 10 min)
    const cutoff = Date.now() - 10 * 60 * 1000;
    for (const [s, t] of this._oauthStates) {
      if (t < cutoff) this._oauthStates.delete(s);
    }
    return state;
  }

  consumeOAuthState(state) {
    if (!state || !this._oauthStates.has(state)) {
      return false;
    }
    this._oauthStates.delete(state);
    return true;
  }
}

export { FigmaAuth };
