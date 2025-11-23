/** Configuration for news-scraper agent */
module.exports = {
  port: process.env.PORT || 3001,
  nodeEnv: process.env.NODE_ENV || 'production',
  cacheTTL: parseInt(process.env.CACHE_TTL) || 900, // 15 minutes in seconds
  timeout: parseInt(process.env.TIMEOUT) || 30000, // 30 seconds in milliseconds
  
  // Sources configuration
  sources: {
    techcrunch: {
      rssUrl: 'https://techcrunch.com/feed/',
      enabled: true
    },
    hackernews: {
      apiUrl: 'https://hacker-news.firebaseio.com/v0/',
      enabled: true
    },
    producthunt: {
      baseUrl: 'https://www.producthunt.com/',
      enabled: true
    }
  },
  
  // Rate limiting
  rateLimit: {
    maxRequests: 10,
    windowMs: 60000 // 1 minute
  }
};

