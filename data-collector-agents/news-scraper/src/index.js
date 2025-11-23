/** News Scraper Agent - Main entry point */
const express = require('express');
const { scrapeTechCrunch } = require('./scrapers/techcrunch');
const { scrapeHackerNews } = require('./scrapers/hackernews');
const { scrapeProductHunt } = require('./scrapers/producthunt');
const Cache = require('./utils/cache');
const { filterByTimeWindow } = require('./utils/parser');
const config = require('./config');

const app = express();
const cache = new Cache(config.cacheTTL);

// Middleware
app.use(express.json());
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type');
  next();
});

/**
 * Health check endpoint
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'news-scraper',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

/**
 * TechCrunch endpoint
 */
app.get('/techcrunch', async (req, res) => {
  try {
    const cacheKey = Cache.key('techcrunch');
    let result = cache.get(cacheKey);
    
    if (!result) {
      result = await scrapeTechCrunch(20);
      cache.set(cacheKey, result);
    }
    
    res.json(result);
  } catch (error) {
    res.status(500).json({
      source: 'techcrunch',
      count: 0,
      articles: [],
      error: error.message
    });
  }
});

/**
 * HackerNews endpoint
 */
app.get('/hackernews', async (req, res) => {
  try {
    const cacheKey = Cache.key('hackernews');
    let result = cache.get(cacheKey);
    
    if (!result) {
      result = await scrapeHackerNews(30);
      cache.set(cacheKey, result);
    }
    
    res.json(result);
  } catch (error) {
    res.status(500).json({
      source: 'hackernews',
      count: 0,
      articles: [],
      error: error.message
    });
  }
});

/**
 * ProductHunt endpoint
 */
app.get('/producthunt', async (req, res) => {
  try {
    const cacheKey = Cache.key('producthunt');
    let result = cache.get(cacheKey);
    
    if (!result) {
      result = await scrapeProductHunt(20);
      cache.set(cacheKey, result);
    }
    
    res.json(result);
  } catch (error) {
    res.status(500).json({
      source: 'producthunt',
      count: 0,
      articles: [],
      error: error.message
    });
  }
});

/**
 * Aggregate all sources
 */
app.get('/all', async (req, res) => {
  try {
    const limit = parseInt(req.query.limit) || 20;
    const hours = parseInt(req.query.hours) || 24;
    
    // Generate cache key with date and parameters
    // Format: all-YYYY-MM-DD-limit-hours
    const dateStr = new Date().toISOString().split('T')[0];
    const cacheKey = `all-${dateStr}-${limit}-${hours}`;
    let result = cache.get(cacheKey);
    
    if (!result) {
      // Fetch from all sources in parallel
      const [techcrunch, hackernews, producthunt] = await Promise.allSettled([
        scrapeTechCrunch(limit),
        scrapeHackerNews(limit),
        scrapeProductHunt(limit)
      ]);
      
      // Process results
      const sources = {
        techcrunch: techcrunch.status === 'fulfilled' ? techcrunch.value : { count: 0, articles: [], error: techcrunch.reason?.message },
        hackernews: hackernews.status === 'fulfilled' ? hackernews.value : { count: 0, articles: [], error: hackernews.reason?.message },
        producthunt: producthunt.status === 'fulfilled' ? producthunt.value : { count: 0, articles: [], error: producthunt.reason?.message }
      };
      
      // Filter by time window
      if (hours < 24) {
        Object.keys(sources).forEach(source => {
          if (sources[source].articles) {
            sources[source].articles = filterByTimeWindow(sources[source].articles, hours);
            sources[source].count = sources[source].articles.length;
          }
        });
      }
      
      const total = Object.values(sources).reduce((sum, source) => sum + (source.count || 0), 0);
      
      result = {
        timestamp: new Date().toISOString(),
        sources,
        total
      };
      
      cache.set(cacheKey, result);
    }
    
    res.json(result);
  } catch (error) {
    res.status(500).json({
      timestamp: new Date().toISOString(),
      sources: {},
      total: 0,
      error: error.message
    });
  }
});

// Start server
const PORT = config.port;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`News Scraper Agent running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`TechCrunch: http://localhost:${PORT}/techcrunch`);
  console.log(`HackerNews: http://localhost:${PORT}/hackernews`);
  console.log(`ProductHunt: http://localhost:${PORT}/producthunt`);
  console.log(`All sources: http://localhost:${PORT}/all`);
});

module.exports = app;

