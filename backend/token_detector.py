import requests
import time
import logging
from functools import lru_cache

class TokenDetector:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.cache_duration = 300  # seconds
        self._last_updated = 0
        self._token_map = {}

    def refresh_cache(self):
        try:
            logging.info("Refreshing CoinGecko token list cache...")
            response = requests.get(f"{self.base_url}/coins/list", timeout=10)
            response.raise_for_status()
            coins = response.json()
            self._token_map = {c['symbol'].upper(): c for c in coins}
            self._last_updated = time.time()
        except Exception as e:
            logging.error(f"Failed to fetch coin list: {e}")

    def find_possible_tokens(self, text):
        if time.time() - self._last_updated > self.cache_duration:
            self.refresh_cache()
        
        found = []
        text_upper = text.upper()
        words = set(word.strip("$") for word in text_upper.split())

        for w in words:
            if w in self._token_map:
                found.append({
                    "id": self._token_map[w]['id'],
                    "symbol": self._token_map[w]['symbol'],
                    "name": self._token_map[w]['name']
                })
        return found
