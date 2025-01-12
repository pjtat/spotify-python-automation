import requests
import logging
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta

from config import Config

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

    def get_status(self) -> dict:
        """
        Get the current rate limiting status.
        
        Returns:
            dict: Current rate limit status including requests made, remaining tokens,
                 and time until reset
        """
        now = datetime.now()
        time_until_reset = (self.day_start + timedelta(days=1)) - now
        
        return {
            "requests_made_today": self.requests_made_today,
            "remaining_tokens": self.tokens,
            "total_daily_limit": self.requests_per_day,
            "time_until_daily_reset": str(time_until_reset),
            "last_request_time": self.last_updated.strftime("%Y-%m-%d %H:%M:%S")
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
    # Class-level constants
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    AUTH_URL = "https://accounts.spotify.com/authorize"
    REDIRECT_URI = "http://localhost:8888/callback"
    MAX_RETRIES = 3
    DAILY_REQUEST_LIMIT = 1000
    SCOPES = [
        "user-follow-modify",
        "user-follow-read",
        "user-top-read",
        "user-library-read",
        "playlist-read-private"
    ]
    
    def __init__(self, max_retries: int = MAX_RETRIES) -> None:
        self.base_url = "https://api.spotify.com/v1/"
        self.rate_limiter = RateLimiter(self.DAILY_REQUEST_LIMIT)
        self.max_retries = max_retries
        self.error_handler = SpotifyErrorHandler()
        
        # Create SpotifyOAuth manager during initialization
        self.auth_manager = SpotifyOAuth(
            client_id=Config.get('client_id'),
            client_secret=Config.get('client_secret'),
            redirect_uri=self.REDIRECT_URI,
            scope=' '.join(self.SCOPES),
            cache_path='.spotify_cache'
        )
        
        # Set initial tokens
        self._refresh_token()

    def _refresh_token(self):
        """Refresh the access token using the auth manager"""
        token_info = self.auth_manager.get_cached_token()
        if not token_info:
            token_info = self.auth_manager.get_access_token()
        
        self.access_token = token_info['access_token']
        self.refresh_token = token_info.get('refresh_token')
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

    def authenticate_user(self):
        """
        Authenticate with Spotify, set up tokens, and return an authenticated client.
            
        Returns:
            spotipy.Spotify: An authenticated Spotify client instance
        """
        # Create SpotifyOAuth manager 
        self.auth_manager = SpotifyOAuth(
            client_id=Config.get('client_id'),
            client_secret=Config.get('client_secret'),
            redirect_uri=self.REDIRECT_URI,
            scope=' '.join(self.SCOPES),
            cache_path='.spotify_cache'
        )
        
        # Create Spotify client with auth manager
        spotify_client = spotipy.Spotify(auth_manager=self.auth_manager)

        # Get current user profile to verify authentication
        try:
            user_profile = spotify_client.current_user()
            logging.info(f"Successfully authenticated as user: {user_profile['id']}")
        except Exception as e:
            logging.error(f"Authentication failed: {str(e)}")
            raise
        
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
            
            self.error_handler.handle_response(response, self.rate_limiter)
            
            # Handle empty responses
            if not response.content:
                return {}
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if "401" in str(e) and auth_required and retry_count < self.max_retries:
                logging.info(f"Access token expired, attempting refresh {retry_count + 1}/{self.max_retries}")
                self._refresh_token()  # New method to handle token refresh
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

    def make_batch_request(self, items: list, max_batch_size: int, endpoint_template: str, response_key: str = None, method: str = 'GET', headers: dict = None, data: dict = None, auth_required: bool = True) -> tuple[list, list]:
        """
        Make batch requests to the Spotify API, splitting items into chunks.
        
        Args:
            items: List of items to process in batches (e.g. track IDs, artist IDs)
            max_batch_size: Maximum number of items per request
            endpoint_template: API endpoint template with placeholder for items
            response_key: The specific key in the response dict containing the results
            method: HTTP method (GET, POST, PUT, DELETE)
            headers: Additional headers to include
            data: Request body for POST/PUT requests
            auth_required: Whether this endpoint requires authentication
            
        Returns:
            tuple[list, list]: (successful_results, failed_batches)
        """
        results = []
        failed_batches = []
        
        for i in range(0, len(items), max_batch_size):
            batch = items[i:i + max_batch_size]
            try:
                batch_result = self.make_request(
                    endpoint=endpoint_template.format(','.join(batch)),
                    method=method,
                    headers=headers,
                    data=data,
                    auth_required=auth_required
                )
                
                # Process results based on response structure
                if isinstance(batch_result, list):
                    results.extend(batch_result)
                elif isinstance(batch_result, dict) and response_key:
                    if response_key in batch_result:
                        results.extend(batch_result[response_key])
                    else:
                        logging.warning(f"Response key '{response_key}' not found in batch result")
                        failed_batches.append(batch)
                
            except Exception as e:
                logging.error(f"Batch request failed: {str(e)}")
                failed_batches.append(batch)
                
        return results, failed_batches