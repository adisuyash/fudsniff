import requests
import os
from dotenv import load_dotenv

load_dotenv()

class NewsFetcher:
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2"
    
    def get_crypto_news(self, limit=10):
        """Fetch latest crypto news"""
        try:
            if not self.news_api_key:
                return self._get_sample_news()
            
            response = requests.get(
                f"{self.base_url}/everything",
                params={
                    'q': 'cryptocurrency OR bitcoin OR ethereum',
                    'sortBy': 'publishedAt',
                    'pageSize': limit,
                    'apiKey': self.news_api_key
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        'title': article['title'],
                        'description': article['description'],
                        'url': article['url'],
                        'publishedAt': article['publishedAt']
                    }
                    for article in data['articles']
                    if article['title'] and article['description']
                ]
            
            return self._get_sample_news()
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return self._get_sample_news()
    
    def _get_sample_news(self):
        """Sample news for testing when API key not available"""
        return [
            {
                'title': 'Bitcoin Reaches New All-Time High',
                'description': 'Bitcoin surges past $70,000 as institutional adoption continues',
                'url': 'https://example.com/news1',
                'publishedAt': '2024-01-15T10:00:00Z'
            },
            {
                'title': 'Ethereum Upgrade Shows Promise',
                'description': 'Latest Ethereum network upgrade improves transaction speeds',
                'url': 'https://example.com/news2',
                'publishedAt': '2024-01-15T09:00:00Z'
            }
        ]