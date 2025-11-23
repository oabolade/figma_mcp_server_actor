/** ProductHunt scraper using Playwright */
const { chromium } = require('playwright');
const { extractSummary, formatTimestamp } = require('../utils/parser');
const config = require('../config');

/**
 * Scrape ProductHunt using Playwright
 * @param {number} limit - Maximum number of products to return
 * @returns {Promise<Object>} Products response
 */
async function scrapeProductHunt(limit = 20) {
  let browser;
  
  try {
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewportSize({ width: 1920, height: 1080 });
    
    // Navigate to ProductHunt today's page
    const url = `${config.sources.producthunt.baseUrl}?date=${new Date().toISOString().split('T')[0]}`;
    await page.goto(url, { waitUntil: 'networkidle', timeout: config.timeout });
    
    // Wait for products to load
    await page.waitForSelector('[data-test="post-item"]', { timeout: 10000 }).catch(() => {});
    
    // Extract product information
    const products = await page.evaluate((limit) => {
      const items = Array.from(document.querySelectorAll('[data-test="post-item"]')).slice(0, limit);
      
      return items.map(item => {
        const titleEl = item.querySelector('[data-test="post-name"]');
        const taglineEl = item.querySelector('[data-test="post-tagline"]');
        const votesEl = item.querySelector('[data-test="vote-button"]');
        const makerEl = item.querySelector('[data-test="post-maker"]');
        const linkEl = item.querySelector('a[href^="/posts/"]');
        
        return {
          title: titleEl?.textContent?.trim() || '',
          tagline: taglineEl?.textContent?.trim() || '',
          votes: parseInt(votesEl?.textContent?.trim()?.replace(/\D/g, '') || '0'),
          maker: makerEl?.textContent?.trim() || '',
          url: linkEl ? `https://www.producthunt.com${linkEl.getAttribute('href')}` : '',
          description: taglineEl?.textContent?.trim() || ''
        };
      }).filter(product => product.title && product.url);
    }, limit);
    
    // Format as articles
    const articles = products.map(product => ({
      title: product.title,
      url: product.url,
      timestamp: formatTimestamp(new Date()),
      summary: extractSummary(product.description || product.tagline),
      maker: product.maker,
      votes: product.votes,
      tagline: product.tagline
    }));
    
    return {
      source: 'producthunt',
      count: articles.length,
      articles
    };
  } catch (error) {
    console.error('Error scraping ProductHunt:', error);
    return {
      source: 'producthunt',
      count: 0,
      articles: [],
      error: error.message
    };
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

module.exports = { scrapeProductHunt };

