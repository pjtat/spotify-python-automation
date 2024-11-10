import json

from fetch_spotify_data import SpotifyApiClient

spotify_api_client = SpotifyApiClient()

# Pull in top artists
with open('data/processed/top_artists.json', 'r') as f:
    top_artists = json.load(f)

