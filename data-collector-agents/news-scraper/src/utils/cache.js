/** Simple in-memory cache implementation */
class Cache {
  constructor(ttlSeconds = 900) {
    this.cache = new Map();
    this.ttl = ttlSeconds * 1000; // Convert to milliseconds
  }

  /**
   * Get cached value
   * @param {string} key - Cache key
   * @returns {any|null} Cached value or null if expired/not found
   */
  get(key) {
    const item = this.cache.get(key);
    if (!item) return null;
    
    if (Date.now() > item.expiresAt) {
      this.cache.delete(key);
      return null;
    }
    
    return item.value;
  }

  /**
   * Set cached value
   * @param {string} key - Cache key
   * @param {any} value - Value to cache
   */
  set(key, value) {
    this.cache.set(key, {
      value,
      expiresAt: Date.now() + this.ttl
    });
  }

  /**
   * Clear cache
   */
  clear() {
    this.cache.clear();
  }

  /**
   * Generate cache key
   * @param {string} source - Source name
   * @param {string} date - Date string (YYYY-MM-DD)
   * @returns {string} Cache key
   */
  static key(source, date = null) {
    const dateStr = date || new Date().toISOString().split('T')[0];
    return `${source}-${dateStr}`;
  }
}

module.exports = Cache;

