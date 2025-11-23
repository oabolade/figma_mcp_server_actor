/** Utility functions for parsing and filtering content */
const cheerio = require('cheerio');

/**
 * Extract summary from HTML content
 * @param {string} html - HTML content
 * @param {number} maxLength - Maximum length of summary
 * @returns {string} Extracted summary
 */
function extractSummary(html, maxLength = 200) {
  if (!html) return '';
  
  const $ = cheerio.load(html);
  const text = $.text();
  return text.trim().substring(0, maxLength) + (text.length > maxLength ? '...' : '');
}

/**
 * Check if content is startup/funding related
 * @param {string} text - Text to check
 * @returns {boolean} True if startup-related
 */
function isStartupRelated(text) {
  if (!text) return false;
  
  const lowerText = text.toLowerCase();
  const keywords = [
    'startup', 'funding', 'venture', 'capital', 'series a', 'series b',
    'seed', 'round', 'raised', 'investment', 'investor', 'crunchbase',
    'y combinator', 'techstars', 'accelerator', 'unicorn', 'ipo',
    'acquisition', 'merge', 'exit'
  ];
  
  return keywords.some(keyword => lowerText.includes(keyword));
}

/**
 * Parse funding amount from text
 * @param {string} text - Text containing funding amount
 * @returns {Object|null} Parsed amount object {amount: number, currency: string} or null
 */
function parseFundingAmount(text) {
  if (!text) return null;
  
  const match = text.match(/(\$|€|£)?\s*(\d+(?:\.\d+)?)\s*([MBK]|million|billion|thousand)?/i);
  if (!match) return null;
  
  const currency = match[1] || '$';
  const number = parseFloat(match[2]);
  const unit = match[3]?.toLowerCase() || '';
  
  let multiplier = 1;
  if (unit === 'b' || unit === 'billion') multiplier = 1000000000;
  else if (unit === 'm' || unit === 'million') multiplier = 1000000;
  else if (unit === 'k' || unit === 'thousand') multiplier = 1000;
  
  return {
    amount: number * multiplier,
    currency: currency.replace(/[€£]/, '$')
  };
}

/**
 * Format timestamp to ISO string
 * @param {Date|string} date - Date to format
 * @returns {string} ISO formatted date string
 */
function formatTimestamp(date) {
  if (!date) return new Date().toISOString();
  if (typeof date === 'string') {
    const parsed = new Date(date);
    return isNaN(parsed.getTime()) ? new Date().toISOString() : parsed.toISOString();
  }
  return date.toISOString();
}

/**
 * Filter articles by time window
 * @param {Array} articles - Articles array
 * @param {number} hours - Number of hours to look back
 * @returns {Array} Filtered articles
 */
function filterByTimeWindow(articles, hours = 24) {
  const cutoffTime = Date.now() - (hours * 60 * 60 * 1000);
  
  return articles.filter(article => {
    const articleTime = new Date(article.timestamp).getTime();
    return articleTime >= cutoffTime;
  });
}

module.exports = {
  extractSummary,
  isStartupRelated,
  parseFundingAmount,
  formatTimestamp,
  filterByTimeWindow
};

