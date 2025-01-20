import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api_handler import SpotifyApiClient

if __name__ == "__main__":
    # Pull track info via request method
    client = SpotifyApiClient()
    track_id = "3BHFResGQiUvbYToUdaDQz" # Post Malone - Enough Is Enough
    track_info = client.make_request(
        endpoint=f'tracks/{track_id}',
        method='GET'
    )
    print(track_info['artists'][0]['id'])

    # Pull an artist's info via request method
    client = SpotifyApiClient()
    artist_id = "246dkjvS1zLTtiykXe5h60" # Post Malone
    artist_info = client.make_request(
        endpoint=f'artists/{artist_id}',
        method='GET'
    )
    print(artist_info['genres'])