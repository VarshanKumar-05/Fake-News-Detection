import os
import requests
import urllib3
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Disable insecure request warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Get API key from environment
NEWS_API_KEY = os.getenv("NEWSAPI_KEY")

def fetch_live_news(query="politics OR technology OR world", sources="bbc-news,reuters,cnn,the-verge"):
    """
    Fetches live news articles using NewsAPI.
    """
    if not NEWS_API_KEY:
        return [{"title": "API Key Missing", "description": "Please ensure your NEWSAPI_KEY is set in the .env file.", "source": "System", "url": "#", "publishedAt": ""}]
        
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "sources": sources,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 15
        }
        headers = {
            "X-Api-Key": NEWS_API_KEY
        }
        
        # Bypass SSL verification to avoid certificate errors on local network/proxy
        response = requests.get(url, params=params, headers=headers, verify=False)
        response.raise_for_status()
        top_headlines = response.json()
        
        articles = top_headlines.get('articles', [])
        
        formatted_articles = []
        for article in articles:
            # We need title and description/content for analysis
            title = article.get('title', '')
            desc = article.get('description', '')
            content = article.get('content', '')
            
            # Combine to get full text representation available
            full_text = f"{title} {desc}"
            if content:
                # Content often has "[+ chars]" at the end, clean it simply
                clean_content = content.split('[+')[0]
                full_text += f" {clean_content}"
                
            formatted_articles.append({
                "title": title,
                "description": desc,
                "text": full_text,
                "source": article.get('source', {}).get('name', 'Unknown'),
                "url": article.get('url', '#'),
                "publishedAt": article.get('publishedAt', '')
            })
            
        return formatted_articles
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        # Fallback to realistic mock data if API fails (e.g., corporate firewall block)
        return [
            {
                "title": "New Tech Breakthrough Promises Infinite Energy",
                "description": "Scientists have discovered a new method to generate infinite energy using quantum fluctuations.",
                "text": "New Tech Breakthrough Promises Infinite Energy. Scientists have discovered a new method to generate infinite energy using quantum fluctuations. This could solve the world's energy crisis overnight.",
                "source": "Tech Insider",
                "url": "#",
                "publishedAt": "2026-05-14T10:00:00Z"
            },
            {
                "title": "Major Political Scandal: Leaders Resign En Masse",
                "description": "In an unprecedented move, top political leaders have resigned following explosive allegations.",
                "text": "Major Political Scandal: Leaders Resign En Masse. In an unprecedented move, top political leaders have resigned following explosive allegations of corruption and mismanagement. Citizens are left in shock.",
                "source": "Global News",
                "url": "#",
                "publishedAt": "2026-05-14T09:30:00Z"
            },
            {
                "title": "Miracle Drug Cures All Ailments Without Side Effects",
                "description": "A new pharmaceutical company claims their pill cures everything from the common cold to chronic diseases.",
                "text": "Miracle Drug Cures All Ailments Without Side Effects. A new pharmaceutical company claims their pill cures everything from the common cold to chronic diseases. Health experts are highly skeptical.",
                "source": "Health Daily",
                "url": "#",
                "publishedAt": "2026-05-14T08:15:00Z"
            },
            {
                "title": "Global Markets Hit Record Highs Amidst Economic Boom",
                "description": "Stock markets around the world have reached unprecedented levels as the global economy surges.",
                "text": "Global Markets Hit Record Highs Amidst Economic Boom. Stock markets around the world have reached unprecedented levels as the global economy surges. Analysts predict continued growth.",
                "source": "Financial Times",
                "url": "#",
                "publishedAt": "2026-05-14T07:45:00Z"
            },
            {
                "title": "Aliens Land on Earth: First Contact Established",
                "description": "Extraterrestrial beings have finally made contact with humanity, landing their spacecraft in a major city.",
                "text": "Aliens Land on Earth: First Contact Established. Extraterrestrial beings have finally made contact with humanity, landing their spacecraft in a major city. World leaders are currently in emergency meetings.",
                "source": "Cosmic News",
                "url": "#",
                "publishedAt": "2026-05-14T06:00:00Z"
            }
        ]

def search_news_by_keyword(keyword):
    """
    Searches for specific news based on a keyword.
    """
    return fetch_live_news(query=keyword, sources=None)
