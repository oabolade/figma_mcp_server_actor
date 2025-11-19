/**
 * Figma API Client
 * Wrapper for Figma REST API endpoints
 */

import fetch from "node-fetch";

import { FigmaAuth } from "./auth.js";

const FIGMA_API_BASE = "https://api.figma.com/v1";

class FigmaClient {
  constructor(auth) {
    this.auth = auth instanceof FigmaAuth ? auth : new FigmaAuth(auth);
    this.cache = new Map();
    this.cacheEnabled = true;
    this.cacheTTL = 5 * 60 * 1000; // 5 minutes default
  }

  /**
   * Make a request to the Figma API
   * @private
   */
  async _request(endpoint, options = {}) {
    const url = `${FIGMA_API_BASE}${endpoint}`;
    const cacheKey = `${url}:${JSON.stringify(options)}`;

    // Check cache if enabled
    if (
      this.cacheEnabled &&
      options.method === "GET" &&
      this.cache.has(cacheKey)
    ) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() < cached.expiresAt) {
        return cached.data;
      }
      this.cache.delete(cacheKey);
    }

    const headers = {
      ...this.auth.getAuthHeaders(),
      "Content-Type": "application/json",
      ...options.headers,
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Figma API error: ${response.status} ${response.statusText} - ${errorText}`,
        );
      }

      const data = await response.json();

      // Cache GET requests
      if ((this.cacheEnabled && options.method === "GET") || !options.method) {
        this.cache.set(cacheKey, {
          data,
          expiresAt: Date.now() + this.cacheTTL,
        });
      }

      return data;
    } catch (error) {
      if (error.message.includes("Figma API error")) {
        throw error;
      }
      throw new Error(`Network error: ${error.message}`);
    }
  }

  /**
   * Get file data
   * @param {string} fileKey - Figma file key
   * @param {Object} options - Optional parameters (version, ids, depth, geometry, plugin_data)
   * @returns {Promise<Object>} File data
   */
  async getFile(fileKey, options = {}) {
    const params = new URLSearchParams();
    if (options.version) params.append("version", options.version);
    if (options.ids) params.append("ids", options.ids.join(","));
    if (options.depth) params.append("depth", options.depth);
    if (options.geometry !== undefined)
      params.append("geometry", options.geometry);
    if (options.plugin_data) params.append("plugin_data", options.plugin_data);

    const query = params.toString();
    return this._request(`/files/${fileKey}${query ? `?${query}` : ""}`);
  }

  /**
   * Get specific nodes from a file
   * @param {string} fileKey - Figma file key
   * @param {string[]} nodeIds - Array of node IDs
   * @param {Object} options - Optional parameters
   * @returns {Promise<Object>} Node data
   */
  async getFileNodes(fileKey, nodeIds, options = {}) {
    const params = new URLSearchParams();
    params.append("ids", nodeIds.join(","));
    if (options.version) params.append("version", options.version);
    if (options.depth) params.append("depth", options.depth);
    if (options.geometry !== undefined)
      params.append("geometry", options.geometry);
    if (options.plugin_data) params.append("plugin_data", options.plugin_data);

    return this._request(`/files/${fileKey}/nodes?${params.toString()}`);
  }

  /**
   * Get images from a file
   * @param {string} fileKey - Figma file key
   * @param {Object} options - Options: ids (array), format (PNG, SVG, PDF), scale (number)
   * @returns {Promise<Object>} Image URLs
   */
  async getImages(fileKey, options = {}) {
    const params = new URLSearchParams();
    if (options.ids && options.ids.length > 0) {
      params.append("ids", options.ids.join(","));
    }
    if (options.format) {
      params.append("format", options.format); // PNG, SVG, PDF, JPG
    }
    if (options.scale) {
      params.append("scale", options.scale);
    }
    if (options.svg_include_id !== undefined) {
      params.append("svg_include_id", options.svg_include_id);
    }
    if (options.svg_simplify_stroke !== undefined) {
      params.append("svg_simplify_stroke", options.svg_simplify_stroke);
    }
    if (options.use_absolute_bounds !== undefined) {
      params.append("use_absolute_bounds", options.use_absolute_bounds);
    }

    return this._request(`/images/${fileKey}?${params.toString()}`);
  }

  /**
   * Get comments from a file
   * @param {string} fileKey - Figma file key
   * @returns {Promise<Object>} Comments data
   */
  async getComments(fileKey) {
    return this._request(`/files/${fileKey}/comments`);
  }

  /**
   * Post a comment to a file
   * @param {string} fileKey - Figma file key
   * @param {Object} commentData - Comment data: message, client_meta (x, y, node_id)
   * @returns {Promise<Object>} Created comment
   */
  async postComment(fileKey, commentData) {
    return this._request(`/files/${fileKey}/comments`, {
      method: "POST",
      body: JSON.stringify(commentData),
    });
  }

  /**
   * Get projects for a team
   * @param {string} teamId - Team ID
   * @returns {Promise<Object>} Projects data
   */
  async getProjects(teamId) {
    return this._request(`/teams/${teamId}/projects`);
  }

  /**
   * Get files in a project
   * @param {string} projectId - Project ID
   * @param {Object} options - Optional parameters (branch_data, etc.)
   * @returns {Promise<Object>} Files data
   */
  async getProjectFiles(projectId, options = {}) {
    const params = new URLSearchParams();
    if (options.branch_data !== undefined) {
      params.append("branch_data", options.branch_data);
    }

    const query = params.toString();
    return this._request(
      `/projects/${projectId}/files${query ? `?${query}` : ""}`,
    );
  }

  /**
   * Get team projects
   * @param {string} teamId - Team ID
   * @returns {Promise<Object>} Teams data
   */
  async getTeamProjects(teamId) {
    return this.getProjects(teamId);
  }

  /**
   * Get file versions
   * @param {string} fileKey - Figma file key
   * @returns {Promise<Object>} Versions data
   */
  async getFileVersions(fileKey) {
    return this._request(`/files/${fileKey}/versions`);
  }

  /**
   * Clear the cache
   */
  clearCache() {
    this.cache.clear();
  }

  /**
   * Enable or disable caching
   * @param {boolean} enabled
   */
  setCacheEnabled(enabled) {
    this.cacheEnabled = enabled;
    if (!enabled) {
      this.clearCache();
    }
  }
}

export { FigmaClient };
