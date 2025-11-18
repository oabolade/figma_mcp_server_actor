/**
 * Figma API Authentication Module
 * Supports Personal Access Token (PAT) initially, with structure for OAuth2
 */

class FigmaAuth {
    constructor(config = {}) {
        this.pat = config.figmaAccessToken || process.env.FIGMA_ACCESS_TOKEN;
        this.oauthClientId = config.oauthClientId || process.env.FIGMA_OAUTH_CLIENT_ID;
        this.oauthClientSecret = config.oauthClientSecret || process.env.FIGMA_OAUTH_CLIENT_SECRET;
        this.oauthTokens = new Map(); // Store OAuth tokens by user ID
    }

    /**
     * Get authentication header for API requests
     * @param {string} userId - Optional user ID for OAuth tokens
     * @returns {Object} Headers object with Authorization header
     */
    getAuthHeaders(userId = null) {
        // Phase 1: Use PAT if available
        if (this.pat) {
            return {
                'X-Figma-Token': this.pat,
            };
        }

        // Phase 2: Use OAuth token if available (for future implementation)
        if (userId && this.oauthTokens.has(userId)) {
            const token = this.oauthTokens.get(userId);
            return {
                'Authorization': `Bearer ${token.accessToken}`,
            };
        }

        throw new Error('No authentication token available. Please provide a Figma Personal Access Token.');
    }

    /**
     * Check if authentication is configured
     * @returns {boolean}
     */
    isAuthenticated() {
        return !!this.pat || this.oauthTokens.size > 0;
    }

    /**
     * Store OAuth token for a user (Phase 2 - OAuth2 implementation)
     * @param {string} userId - User identifier
     * @param {Object} tokenData - Token data from OAuth flow
     */
    setOAuthToken(userId, tokenData) {
        this.oauthTokens.set(userId, {
            accessToken: tokenData.access_token,
            refreshToken: tokenData.refresh_token,
            expiresAt: Date.now() + (tokenData.expires_in * 1000),
        });
    }

    /**
     * Get OAuth authorization URL (Phase 2 - OAuth2 implementation)
     * @param {string} redirectUri - OAuth redirect URI
     * @param {string} state - State parameter for CSRF protection
     * @returns {string} Authorization URL
     */
    getOAuthAuthorizationUrl(redirectUri, state) {
        if (!this.oauthClientId) {
            throw new Error('OAuth client ID not configured');
        }

        const params = new URLSearchParams({
            client_id: this.oauthClientId,
            redirect_uri: redirectUri,
            response_type: 'code',
            scope: 'file_read file_write',
            state: state,
        });

        return `https://www.figma.com/oauth?${params.toString()}`;
    }

    /**
     * Exchange authorization code for access token (Phase 2 - OAuth2 implementation)
     * @param {string} code - Authorization code from OAuth callback
     * @param {string} redirectUri - OAuth redirect URI
     * @returns {Promise<Object>} Token data
     */
    async exchangeCodeForToken(code, redirectUri) {
        if (!this.oauthClientId || !this.oauthClientSecret) {
            throw new Error('OAuth credentials not configured');
        }

        // This would make a POST request to Figma's token endpoint
        // Implementation pending OAuth2 flow completion
        throw new Error('OAuth2 token exchange not yet implemented');
    }
}

export default FigmaAuth;


