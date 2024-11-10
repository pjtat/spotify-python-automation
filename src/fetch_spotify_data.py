import requests
import logging
import time

from config import Config
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/spotify_api.log')
    ]
)

class RateLimiter:
    def __init__(self, requests_per_day):
        self.requests_per_day = requests_per_day
        self.tokens = requests_per_day
        self.last_updated = datetime.now()
    
    def acquire(self):
        now = datetime.now()
        time_passed = now - self.last_updated
        
        # Replenish tokens based on time passed
        self.tokens = min(
            self.requests_per_day,
            self.tokens + (time_passed.total_seconds() * self.requests_per_day / (24 * 3600))
        )
        
        if self.tokens < 1:
            sleep_time = (1 - self.tokens) * (24 * 3600) / self.requests_per_day
            logging.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
            self.tokens = 1
            
        self.tokens -= 1
        self.last_updated = now

class SpotifyApiClient: 
    def __init__(self):
        self.access_token = self._get_access_token()
        # Initialize rate limiter with 10,000 requests per day (adjust as needed)
        self.rate_limiter = RateLimiter(10000)

    def _get_access_token(self):
        # Define the endpoint and your credentials
        url = "https://accounts.spotify.com/api/token"
        client_id = Config.get('client_id')
        client_secret = Config.get('client_secret')

        # Get access token
        auth_response = requests.post(url, {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        })

        # Convert response to JSON
        auth_response_data = auth_response.json()

        return auth_response_data['access_token']
    
    def _make_request(self, url, retry_count=0):
        """Makes a GET request to the Spotify API with proper authorization headers"""
        # Check rate limit before making request
        self.rate_limiter.acquire()
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 401 and retry_count < 1:
                self.access_token = self._get_access_token()
                return self._make_request(url, retry_count + 1)
                
            response.raise_for_status()
            logging.info(f"Successfully made request to {url} with status code {response.status_code}")
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 'unknown')
                remaining = response.headers.get('X-RateLimit-Remaining', 'unknown')
                limit = response.headers.get('X-RateLimit-Limit', 'unknown')
                logging.error(
                    f"Rate limit exceeded (429). Too many requests.\n"
                    f"Retry after: {int(retry_after) // 3600}h {(int(retry_after) % 3600) // 60}m\n"
                    f"Current token count: {self.rate_limiter.tokens:.2f}"
                )
            else:
                logging.error(f"HTTP error occurred: {response.status_code}")
            raise Exception(f"HTTP error {response.status_code}")
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {str(e)}")
            raise Exception(f"Request failed: {str(e)}")

        return response
    def get_item_info(self, item_id: str, item_type: str) -> dict:
        """
        Get information about a Spotify item (artist, album, or track)
        
        Args:
            item_id (str): Spotify ID for the item
            item_type (str): Type of item ('artists', 'albums', or 'tracks')
            
        Returns:
            dict: JSON response from Spotify API
        """
        # Create request URL
        url = f"https://api.spotify.com/v1/{item_type}/{item_id}"
        
        # Make request
        response = self._make_request(url)
        return response.json()









    # TEMP - DELETE LATER
    # def get_album_chart_info(self, album_id: str) -> dict:
    #     return self.get_item_info(album_id, "albums")