# Prompt 11: Frontend UI

## Objective

Create a simple, modern frontend UI that fetches and displays the daily briefing from the API endpoint. The UI should be responsive, visually appealing, and show all key intelligence in an organized dashboard.

## Requirements

### Frontend Specifications

**Technology Stack:**
- HTML5 + Tailwind CSS (from CDN)
- Vanilla JavaScript (no frameworks)
- Single-page application
- Responsive design (mobile-friendly)

**Alternative Options:**
- Minimal Next.js page (if preferred)
- Chat-like interface using a single API route

### UI Components

1. **Header**
   - Title: "Startup Intelligence Dashboard"
   - Briefing date
   - Refresh button

2. **Today's Summary**
   - Executive summary paragraph
   - Highlighted insights

3. **Top Trends**
   - Cards showing trend clusters
   - Trend title, description, signals
   - Confidence indicators

4. **Funding Rounds**
   - Table or cards showing recent funding
   - Company name, amount, type, date
   - Links to original sources

5. **Product Launches**
   - Cards showing recent launches
   - Product name, description, category
   - Links to products

6. **Competitor Moves**
   - List of strategic moves
   - Company, move type, significance

7. **Opportunities for Founders**
   - Cards with opportunity details
   - Title, description, reasoning, urgency

8. **Opportunities for Investors**
   - Cards with investment opportunities
   - Title, description, reasoning, sector, risk/return

9. **Intelligence Threads**
   - Expandable threads for major trends
   - Related articles and evidence

### Implementation

**File:** `frontend/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Startup Intelligence Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#3b82f6',
                        secondary: '#8b5cf6'
                    }
                }
            }
        }
    </script>
    <style>
        .fade-in {
            animation: fadeIn 0.5s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900">Startup Intelligence Dashboard</h1>
                    <p class="text-sm text-gray-500 mt-1" id="briefing-date">Loading...</p>
                </div>
                <button 
                    id="refresh-btn"
                    onclick="loadBriefing()"
                    class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2"
                >
                    <span id="refresh-icon">⟳</span>
                    <span>Refresh</span>
                </button>
            </div>
        </div>
    </header>

    <!-- Loading State -->
    <div id="loading" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center">
        <div class="inline-block loading"></div>
        <p class="mt-4 text-gray-600">Loading briefing...</p>
    </div>

    <!-- Error State -->
    <div id="error" class="hidden max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="bg-red-50 border border-red-200 rounded-lg p-4">
            <p class="text-red-800" id="error-message">Failed to load briefing</p>
        </div>
    </div>

    <!-- Main Content -->
    <main id="content" class="hidden max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        <!-- Today's Summary -->
        <section class="mb-8 fade-in">
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-xl font-semibold text-gray-900 mb-4">Today's Summary</h2>
                <p class="text-gray-700 leading-relaxed" id="summary"></p>
            </div>
        </section>

        <!-- Statistics -->
        <section class="mb-8 fade-in">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="bg-white rounded-lg shadow p-4">
                    <div class="text-sm text-gray-500">News Articles</div>
                    <div class="text-2xl font-bold text-gray-900" id="stats-news">0</div>
                </div>
                <div class="bg-white rounded-lg shadow p-4">
                    <div class="text-sm text-gray-500">Funding Rounds</div>
                    <div class="text-2xl font-bold text-gray-900" id="stats-funding">0</div>
                </div>
                <div class="bg-white rounded-lg shadow p-4">
                    <div class="text-sm text-gray-500">Launches</div>
                    <div class="text-2xl font-bold text-gray-900" id="stats-launches">0</div>
                </div>
                <div class="bg-white rounded-lg shadow p-4">
                    <div class="text-sm text-gray-500">Trends Identified</div>
                    <div class="text-2xl font-bold text-gray-900" id="stats-trends">0</div>
                </div>
            </div>
        </section>

        <!-- Top Trends -->
        <section class="mb-8 fade-in">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Top Trends</h2>
            <div id="trends-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <!-- Trends will be populated here -->
            </div>
        </section>

        <!-- Funding Rounds -->
        <section class="mb-8 fade-in">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Recent Funding Rounds</h2>
            <div id="funding-container" class="space-y-4">
                <!-- Funding rounds will be populated here -->
            </div>
        </section>

        <!-- Product Launches -->
        <section class="mb-8 fade-in">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Recent Product Launches</h2>
            <div id="launches-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <!-- Launches will be populated here -->
            </div>
        </section>

        <!-- Opportunities for Founders -->
        <section class="mb-8 fade-in">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Opportunities for Founders</h2>
            <div id="founder-opportunities-container" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Founder opportunities will be populated here -->
            </div>
        </section>

        <!-- Opportunities for Investors -->
        <section class="mb-8 fade-in">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Opportunities for Investors</h2>
            <div id="investor-opportunities-container" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Investor opportunities will be populated here -->
            </div>
        </section>

        <!-- Intelligence Threads -->
        <section class="mb-8 fade-in">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Intelligence Threads</h2>
            <div id="threads-container" class="space-y-4">
                <!-- Intelligence threads will be populated here -->
            </div>
        </section>

    </main>

    <script>
        // API Configuration
        const API_BASE_URL = window.location.origin; // Or set to your API URL
        const API_BRIEFING_URL = `${API_BASE_URL}/briefing`;

        // Load briefing on page load
        document.addEventListener('DOMContentLoaded', () => {
            loadBriefing();
            // Auto-refresh every 30 minutes
            setInterval(loadBriefing, 30 * 60 * 1000);
        });

        async function loadBriefing() {
            const loadingEl = document.getElementById('loading');
            const errorEl = document.getElementById('error');
            const contentEl = document.getElementById('content');
            const refreshBtn = document.getElementById('refresh-btn');
            const refreshIcon = document.getElementById('refresh-icon');

            // Show loading state
            loadingEl.classList.remove('hidden');
            errorEl.classList.add('hidden');
            contentEl.classList.add('hidden');
            refreshBtn.disabled = true;
            refreshIcon.classList.add('animate-spin');

            try {
                const response = await fetch(API_BRIEFING_URL);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const briefing = await response.json();
                displayBriefing(briefing);

                // Hide loading, show content
                loadingEl.classList.add('hidden');
                contentEl.classList.remove('hidden');
                
            } catch (error) {
                console.error('Error loading briefing:', error);
                
                // Show error state
                loadingEl.classList.add('hidden');
                errorEl.classList.remove('hidden');
                document.getElementById('error-message').textContent = 
                    `Failed to load briefing: ${error.message}`;
                    
            } finally {
                refreshBtn.disabled = false;
                refreshIcon.classList.remove('animate-spin');
            }
        }

        function displayBriefing(briefing) {
            // Set briefing date
            document.getElementById('briefing-date').textContent = 
                `Briefing for ${briefing.briefing_date || 'Today'}`;

            // Display summary
            document.getElementById('summary').textContent = briefing.summary || 'No summary available';

            // Display statistics
            const stats = briefing.statistics || {};
            document.getElementById('stats-news').textContent = stats.news_articles_analyzed || 0;
            document.getElementById('stats-funding').textContent = stats.funding_rounds_analyzed || 0;
            document.getElementById('stats-launches').textContent = stats.launches_analyzed || 0;
            document.getElementById('stats-trends').textContent = stats.trends_identified || 0;

            // Display trends
            displayTrends(briefing.trends || []);

            // Display funding rounds
            displayFundingRounds(briefing.funding_rounds || []);

            // Display launches
            displayLaunches(briefing.product_launches || []);

            // Display founder opportunities
            displayFounderOpportunities(briefing.opportunities_for_founders || []);

            // Display investor opportunities
            displayInvestorOpportunities(briefing.opportunities_for_investors || []);

            // Display intelligence threads
            displayIntelligenceThreads(briefing.intelligence_threads || []);
        }

        function displayTrends(trends) {
            const container = document.getElementById('trends-container');
            container.innerHTML = trends.map(trend => `
                <div class="bg-white rounded-lg shadow p-4 border-l-4 border-primary">
                    <h3 class="font-semibold text-gray-900 mb-2">${escapeHtml(trend.title)}</h3>
                    <p class="text-sm text-gray-600 mb-3">${escapeHtml(trend.description)}</p>
                    <div class="flex items-center gap-2 mb-2">
                        <span class="px-2 py-1 text-xs rounded ${getConfidenceColor(trend.confidence)}">
                            ${trend.confidence || 'medium'}
                        </span>
                        <span class="text-xs text-gray-500">${trend.sector || 'General'}</span>
                    </div>
                    ${trend.signals && trend.signals.length > 0 ? `
                        <div class="mt-2">
                            <div class="text-xs font-medium text-gray-700 mb-1">Signals:</div>
                            <div class="flex flex-wrap gap-1">
                                ${trend.signals.slice(0, 3).map(signal => `
                                    <span class="px-2 py-1 bg-gray-100 text-xs rounded">${escapeHtml(signal)}</span>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }

        function displayFundingRounds(fundingRounds) {
            const container = document.getElementById('funding-container');
            container.innerHTML = fundingRounds.map(funding => `
                <div class="bg-white rounded-lg shadow p-4">
                    <div class="flex justify-between items-start mb-2">
                        <div>
                            <h3 class="font-semibold text-gray-900">${escapeHtml(funding.name)}</h3>
                            <p class="text-sm text-gray-600">${escapeHtml(funding.type || 'N/A')} • ${funding.date || 'N/A'}</p>
                        </div>
                        <span class="px-3 py-1 bg-green-100 text-green-800 rounded-lg font-semibold">
                            ${escapeHtml(funding.amount || 'N/A')}
                        </span>
                    </div>
                    ${funding.description ? `<p class="text-sm text-gray-700 mb-2">${escapeHtml(funding.description)}</p>` : ''}
                    ${funding.link ? `
                        <a href="${funding.link}" target="_blank" class="text-sm text-primary hover:underline">
                            View Source →
                        </a>
                    ` : ''}
                </div>
            `).join('');
        }

        function displayLaunches(launches) {
            const container = document.getElementById('launches-container');
            container.innerHTML = launches.map(launch => `
                <div class="bg-white rounded-lg shadow p-4">
                    <h3 class="font-semibold text-gray-900 mb-2">${escapeHtml(launch.name)}</h3>
                    ${launch.tagline ? `<p class="text-sm text-gray-600 mb-2 italic">${escapeHtml(launch.tagline)}</p>` : ''}
                    <p class="text-sm text-gray-700 mb-3">${escapeHtml(launch.description || '')}</p>
                    <div class="flex items-center gap-2 mb-2">
                        <span class="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                            ${escapeHtml(launch.category || launch.product_category || 'N/A')}
                        </span>
                        <span class="text-xs text-gray-500">${launch.date || ''}</span>
                    </div>
                    ${launch.link ? `
                        <a href="${launch.link}" target="_blank" class="text-sm text-primary hover:underline">
                            View Product →
                        </a>
                    ` : ''}
                </div>
            `).join('');
        }

        function displayFounderOpportunities(opportunities) {
            const container = document.getElementById('founder-opportunities-container');
            container.innerHTML = opportunities.map(opp => `
                <div class="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
                    <h3 class="font-semibold text-gray-900 mb-2">${escapeHtml(opp.title)}</h3>
                    <p class="text-sm text-gray-700 mb-3">${escapeHtml(opp.description)}</p>
                    <div class="mb-2">
                        <div class="text-xs font-medium text-gray-700 mb-1">Reasoning:</div>
                        <p class="text-xs text-gray-600">${escapeHtml(opp.reasoning)}</p>
                    </div>
                    <div class="flex gap-2 mt-3">
                        <span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                            ${opp.urgency || 'medium'} urgency
                        </span>
                        <span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                            ${opp.category || 'general'}
                        </span>
                    </div>
                </div>
            `).join('');
        }

        function displayInvestorOpportunities(opportunities) {
            const container = document.getElementById('investor-opportunities-container');
            container.innerHTML = opportunities.map(opp => `
                <div class="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
                    <h3 class="font-semibold text-gray-900 mb-2">${escapeHtml(opp.title)}</h3>
                    <p class="text-sm text-gray-700 mb-3">${escapeHtml(opp.description)}</p>
                    <div class="mb-2">
                        <div class="text-xs font-medium text-gray-700 mb-1">Investment Thesis:</div>
                        <p class="text-xs text-gray-600">${escapeHtml(opp.reasoning)}</p>
                    </div>
                    <div class="flex flex-wrap gap-2 mt-3">
                        <span class="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                            ${opp.sector || 'General'}
                        </span>
                        <span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                            ${opp.stage_preference || 'flexible'}
                        </span>
                        <span class="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">
                            Risk: ${opp.risk_level || 'medium'}
                        </span>
                        <span class="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                            Return: ${opp.potential_return || 'medium'}
                        </span>
                    </div>
                </div>
            `).join('');
        }

        function displayIntelligenceThreads(threads) {
            const container = document.getElementById('threads-container');
            container.innerHTML = threads.map(thread => `
                <div class="bg-white rounded-lg shadow">
                    <button 
                        onclick="toggleThread('${thread.thread_id}')"
                        class="w-full p-4 text-left flex justify-between items-center hover:bg-gray-50 transition-colors"
                    >
                        <div>
                            <h3 class="font-semibold text-gray-900">${escapeHtml(thread.title)}</h3>
                            <p class="text-sm text-gray-600 mt-1">${escapeHtml(thread.sector || 'General')}</p>
                        </div>
                        <span class="text-gray-400" id="icon-${thread.thread_id}">▼</span>
                    </button>
                    <div id="thread-${thread.thread_id}" class="hidden p-4 pt-0 border-t border-gray-200">
                        <p class="text-sm text-gray-700 mb-4">${escapeHtml(thread.description)}</p>
                        ${thread.related_articles && thread.related_articles.length > 0 ? `
                            <div class="mb-4">
                                <div class="text-sm font-medium text-gray-700 mb-2">Related Articles:</div>
                                <ul class="space-y-2">
                                    ${thread.related_articles.map(article => `
                                        <li class="text-sm">
                                            <a href="${article.url}" target="_blank" class="text-primary hover:underline">
                                                ${escapeHtml(article.title)}
                                            </a>
                                            <span class="text-gray-500 text-xs ml-2">${article.source}</span>
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `).join('');
        }

        function toggleThread(threadId) {
            const content = document.getElementById(`thread-${threadId}`);
            const icon = document.getElementById(`icon-${threadId}`);
            content.classList.toggle('hidden');
            icon.textContent = content.classList.contains('hidden') ? '▼' : '▲';
        }

        function getConfidenceColor(confidence) {
            const colors = {
                high: 'bg-green-100 text-green-800',
                medium: 'bg-yellow-100 text-yellow-800',
                low: 'bg-gray-100 text-gray-800'
            };
            return colors[confidence] || colors.medium;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
```

### API Configuration

Update the API_BASE_URL in the script if your frontend is served separately:
```javascript
const API_BASE_URL = 'https://your-e2b-sandbox-url.runs.apify.net';
```

### Alternative: Next.js Implementation

If you prefer Next.js, create a minimal page:

**File:** `frontend/pages/index.js`
```javascript
import { useEffect, useState } from 'react';

export default function Dashboard() {
  const [briefing, setBriefing] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/briefing')
      .then(res => res.json())
      .then(data => {
        setBriefing(data);
        setLoading(false);
      });
  }, []);

  // Render UI similar to HTML version
  // ...
}
```

### Deliverables

1. Complete HTML/CSS/JS frontend implementation
2. Responsive design with Tailwind CSS
3. All UI sections (summary, trends, funding, launches, opportunities)
4. Loading and error states
5. Auto-refresh functionality
6. Intelligence threads with expand/collapse
7. Mobile-friendly responsive layout
8. Clean, modern design

### Testing

1. Serve the HTML file:
   ```bash
   # Using Python
   cd frontend
   python -m http.server 3000

   # Using Node.js
   npx http-server -p 3000
   ```

2. Access at `http://localhost:3000`

3. Ensure API is running and accessible from the frontend

### Next Steps

After completing the frontend, proceed to:
- **12-integration-deployment.md** - Integration testing and deployment guide
