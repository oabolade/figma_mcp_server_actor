/** HackerNews scraper using official API */
const fetch = require('node-fetch');
const { isStartupRelated, formatTimestamp } = require('../utils/parser');
const config = require('../config');

const API_BASE = config.sources.hackernews.apiUrl;

/**
 * Fetch top stories from HackerNews
 * @param {number} limit - Maximum number of stories to return
 * @returns {Promise<Object>} Stories response
 */
async function scrapeHackerNews(limit = 30) {
  try {
    // Fetch top stories IDs
    const topStoriesResponse = await fetch(`${API_BASE}topstories.json`);
    if (!topStoriesResponse.ok) {
      throw new Error(`HTTP error! status: ${topStoriesResponse.status}`);
    }
    
    const storyIds = await topStoriesResponse.json();
    const topStoryIds = storyIds.slice(0, Math.min(limit * 2, storyIds.length)); // Fetch more to filter
    
    // Fetch story details
    const storyPromises = topStoryIds.map(id => 
      fetch(`${API_BASE}item/${id}.json`)
        .then(res => res.ok ? res.json() : null)
        .catch(() => null)
    );
    
    const stories = await Promise.all(storyPromises);
    
    // Filter and format startup-related stories
    let articles = stories
      .filter(story => story && story.type === 'story' && story.url && !story.deleted)
      .map(story => ({
        title: story.title || '',
        url: story.url || `https://news.ycombinator.com/item?id=${story.id}`,
        timestamp: formatTimestamp(new Date(story.time * 1000)),
        summary: story.text ? story.text.substring(0, 200) : '',
        author: story.by || 'unknown',
        score: story.score || 0,
        comments: story.descendants || 0
      }))
      .filter(article => {
        // Filter for startup-related content
        return isStartupRelated(article.title) || 
               isStartupRelated(article.summary);
      })
      .slice(0, limit);

    return {
      source: 'hackernews',
      count: articles.length,
      articles
    };
  } catch (error) {
    console.error('Error scraping HackerNews:', error);
    return {
      source: 'hackernews',
      count: 0,
      articles: [],
      error: error.message
    };
  }
}

module.exports = { scrapeHackerNews };

