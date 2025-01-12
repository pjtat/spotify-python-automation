import requests
import logging
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from config import Config
from datetime import datetime, timedelta

# Define request information 
TOKEN_URL = "https://accounts.spotify.com/api/token"
AUTH_URL = "https://accounts.spotify.com/authorize"
REDIRECT_URI = "http://localhost:8888/callback" 

# Constants
MAX_RETRIES = 3
DAILY_REQUEST_LIMIT = 1000

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/spotify_api.log')
    ]
)

class RateLimiter:
    def __init__(self, requests_per_day: int) -> None:
        """
        Initialize rate limiter.
        
        Args:
            requests_per_day: Maximum number of requests allowed per day
        """
        self.requests_per_day = requests_per_day
        self.tokens = requests_per_day
        self.last_updated = datetime.now()
        self.requests_made_today = 0
        self.day_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    def acquire(self):
        now = datetime.now()
        time_passed = now - self.last_updated
        
        # Reset daily counter if it's a new day
        if now.date() > self.day_start.date():
            self.requests_made_today = 0
            self.day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
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
        self.requests_made_today += 1
        self.last_updated = now

class RateLimitStatus:
    @staticmethod
    def get_status(rate_limiter):
        now = datetime.now()
        time_until_reset = (rate_limiter.day_start + timedelta(days=1)) - now
        
        return {
            "requests_made_today": rate_limiter.requests_made_today,
            "remaining_tokens": rate_limiter.tokens,
            "total_daily_limit": rate_limiter.requests_per_day,
            "time_until_daily_reset": str(time_until_reset),
            "last_request_time": rate_limiter.last_updated.strftime("%Y-%m-%d %H:%M:%S")
        }

class SpotifyErrorHandler:
    @staticmethod
    def handle_response(response, rate_limiter=None):
        """Handle different response status codes from Spotify API"""
        if response.status_code == 200:
            logging.info(f"Successfully made request with status code {response.status_code}")
            return True

        elif response.status_code == 429:
            retry_after = response.headers.get('Retry-After', 'unknown')
            remaining = response.headers.get('X-RateLimit-Remaining', 'unknown')
            limit = response.headers.get('X-RateLimit-Limit', 'unknown')
            
            error_msg = (
                f"Rate limit exceeded (429). Too many requests.\n"
                f"Retry after: {int(retry_after) // 3600}h {(int(retry_after) % 3600) // 60}m"
            )
            if rate_limiter:
                error_msg += f"\nCurrent token count: {rate_limiter.tokens:.2f}"
            
            logging.error(error_msg)
            raise requests.exceptions.HTTPError(error_msg)

        elif response.status_code == 403:
            error_msg = "Forbidden - Bad OAuth request (403)"
            logging.error(error_msg)
            raise requests.exceptions.HTTPError(error_msg)

        elif response.status_code == 401:
            error_msg = "Unauthorized - The access token has expired (401)"
            logging.error(error_msg)
            raise requests.exceptions.HTTPError(error_msg)

        else:
            error_msg = f"HTTP error occurred: {response.status_code}"
            logging.error(error_msg)
            raise requests.exceptions.HTTPError(error_msg)

class SpotifyApiClient:
    def __init__(self, max_retries: int = MAX_RETRIES) -> None:
        self.base_url = "https://api.spotify.com/v1/"
        self.rate_limiter = RateLimiter(DAILY_REQUEST_LIMIT)
        self.max_retries = max_retries
        self.error_handler = SpotifyErrorHandler()
        # Initialize without token - will be set during OAuth flow
        self.access_token = None
        self.refresh_token = None
        self.headers = {}

    def authenticate_user(self, scope: str):
        """
        Authenticate with Spotify, set up tokens, and return an authenticated client.
        
        Args:
            scope: The Spotify API scope(s) to request access for
            
        Returns:
            spotipy.Spotify: An authenticated Spotify client instance
        """
        # Create SpotifyOAuth manager 
        auth_manager = SpotifyOAuth(
            client_id=Config.get('client_id'),
            client_secret=Config.get('client_secret'),
            redirect_uri=REDIRECT_URI,
            scope=scope
        )
        
        # Create Spotify client with auth manager
        spotify_client = spotipy.Spotify(auth_manager=auth_manager)

        # Store tokens for future requests
        self.access_token = auth_manager.get_access_token()['access_token']
        self.refresh_token = auth_manager.get_cached_token()['refresh_token']
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

        # Get current user profile
        user_profile = spotify_client.current_user()
        print("User ID:", user_profile['id'])
        print("Display Name:", user_profile['display_name'])
        
        return spotify_client
    
    def make_request(self, endpoint: str, method: str = 'GET', headers: dict = None, data: dict = None, auth_required: bool = True, retry_count: int = 0) -> dict:
        """
        Make a request to the Spotify API.
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method (GET, POST, PUT, DELETE)
            headers: Additional headers to include
            data: Request body for POST/PUT requests
            auth_required: Whether this endpoint requires authentication
            retry_count: Current retry attempt number
            
        Returns:
            dict: Parsed JSON response data
        """
        # Construct full URL if endpoint is relative
        url = endpoint if endpoint.startswith('http') else self.base_url + endpoint
        
        # Prepare headers
        request_headers = {}
        if auth_required:
            if not self.access_token:
                raise Exception("No access token available. User must authenticate first.")
            request_headers.update(self.headers)
        if headers:
            request_headers.update(headers)
            
        logging.info(f"Making {method} request to: {url}")
        self.rate_limiter.acquire()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=request_headers,
                json=data if method in ['POST', 'PUT'] else None
            )
            
            # Let the error handler handle all response status codes
            self.error_handler.handle_response(response, self.rate_limiter)
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if "401" in str(e) and auth_required and retry_count < self.max_retries:
                logging.info(f"Access token expired, attempting refresh {retry_count + 1}/{self.max_retries}")
                self.authenticate_user()  # Re-authenticate
                return self.make_request(endpoint, method, headers, data, auth_required, retry_count + 1)
            raise e
            
        except requests.exceptions.RequestException as e:
            if retry_count < self.max_retries:
                logging.warning(f"Request failed, attempting retry {retry_count + 1}/{self.max_retries}")
                time.sleep(2 ** retry_count)  # Exponential backoff
                return self.make_request(endpoint, method, headers, data, auth_required, retry_count + 1)
            
            # Let the error handler handle the final failure
            error_msg = f"Request failed after {self.max_retries} retries: {str(e)}"
            logging.error(error_msg)
            raise requests.exceptions.HTTPError(error_msg)

    def make_batch_request(self, items: list, max_batch_size: int, endpoint_template: str, method: str = 'GET', headers: dict = None, data: dict = None, auth_required: bool = True) -> list:
        """
        Make batch requests to the Spotify API, splitting items into chunks.
        
        Args:
            items: List of items to process in batches (e.g. track IDs, artist IDs)
            max_batch_size: Maximum number of items per request
            endpoint_template: API endpoint template with placeholder for items
            method: HTTP method (GET, POST, PUT, DELETE)
            headers: Additional headers to include
            data: Request body for POST/PUT requests
            auth_required: Whether this endpoint requires authentication
            
        Returns:
            list: Combined results from all batch requests
        """
        results = []
        
        # Process items in batches
        for i in range(0, len(items), max_batch_size):
            batch = items[i:i + max_batch_size]
            
            # Format the endpoint with the current batch
            batch_endpoint = endpoint_template.format(','.join(batch))
            
            # Make the request for this batch
            batch_result = self.make_request(
                endpoint=batch_endpoint,
                method=method,
                headers=headers,
                data=data,
                auth_required=auth_required
            )
            
            # Add batch results to overall results
            if isinstance(batch_result, dict):
                # Handle case where response is a dict with a key containing the results
                for key in batch_result:
                    if isinstance(batch_result[key], list):
                        results.extend(batch_result[key])
            elif isinstance(batch_result, list):
                # Handle case where response is directly a list
                results.extend(batch_result)
                
        return results