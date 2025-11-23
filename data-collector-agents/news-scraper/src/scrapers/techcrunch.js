/** TechCrunch scraper using RSS feed */
const RSSParser = require('rss-parser');
const fetch = require('node-fetch');
const { extractSummary, isStartupRelated, formatTimestamp } = require('../utils/parser');
const config = require('../config');

const parser = new RSSParser({
  timeout: config.timeout,
  customFields: {
    item: ['author', 'category']
  }
});

/**
 * Scrape TechCrunch articles from RSS feed
 * @param {number} limit - Maximum number of articles to return
 * @returns {Promise<Object>} Articles response
 */
async function scrapeTechCrunch(limit = 20) {
  try {
    const feed = await parser.parseURL(config.sources.techcrunch.rssUrl);
    
    let articles = feed.items
      .map(item => ({
        title: item.title || '',
        url: item.link || '',
        timestamp: formatTimestamp(item.pubDate),
        summary: extractSummary(item.contentSnippet || item.content || ''),
        author: item.author || item.creator || 'TechCrunch',
        categories: item.categories || []
      }))
      .filter(article => {
        // Filter for startup-related content
        return isStartupRelated(article.title) || 
               isStartupRelated(article.summary);
      })
      .slice(0, limit);

    return {
      source: 'techcrunch',
      count: articles.length,
      articles
    };
  } catch (error) {
    console.error('Error scraping TechCrunch:', error);
    return {
      source: 'techcrunch',
      count: 0,
      articles: [],
      error: error.message
    };
  }
}

module.exports = { scrapeTechCrunch };

