import requests
import os
from dotenv import load_dotenv

load_dotenv()

class MarketData:
    def __init__(self):
        self.coingecko_key = os.getenv('COINGECKO_API_KEY')
        self.base_url = "https://api.coingecko.com/api/v3"
    
    def get_trending_coins(self, limit=10):
        """Get trending coins for context"""
        try:
            headers = {}
            if self.coingecko_key:
                headers['X-CG-API-KEY'] = self.coingecko_key
            
            response = requests.get(
                f"{self.base_url}/search/trending",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return [coin['item'] for coin in data['coins'][:limit]]
            
            return []
            
        except Exception as e:
            print(f"Error fetching trending coins: {e}")
            return []
    
    def get_coin_price(self, coin_id):
        """Get current price for a specific coin"""
        try:
            headers = {}
            if self.coingecko_key:
                headers['X-CG-API-KEY'] = self.coingecko_key
            
            response = requests.get(
                f"{self.base_url}/simple/price",
                params={'ids': coin_id, 'vs_currencies': 'usd'},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get(coin_id, {}).get('usd', 0)
            
            return 0
            
        except Exception as e:
            print(f"Error fetching price for {coin_id}: {e}")
            return 0