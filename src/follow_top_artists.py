import json

from fetch_spotify_data import SpotifyApiClient

spotify_api_client = SpotifyApiClient()

# Pull in top artists
with open('data/processed/top_artists.json', 'r') as f:
    top_artists = json.load(f)

# Separate top artsists into two lists (1-50 and 51-100)
# This is done because you can request following verification of 50 artists at a time
top_artists_1_50 = top_artists[:50]
top_artists_51_100 = top_artists[50:]

# Make (2) API calls to confirm following of top artists
url_1_50 = f"https://api.spotify.com/v1/me/following/contains?type=artist&ids={%2C}".join([artist[0] for artist in top_artists_1_50])
url_51_100 = f"https://api.spotify.com/v1/me/following/contains?type=artist&ids={%2C}".join([artist[0] for artist in top_artists_51_100])

response_1_50 = spotify_api_client.make_request(url_1_50)
response_51_100 = spotify_api_client.make_request(url_51_100)

# Initialize list of artists that need to be followed
artists_to_follow = []

# Update list of artists that need to be followed
first_half_index = 0
for artist in top_artists_1_50:
    if not response_1_50[first_half_index]:
        artists_to_follow.append(artist)
    first_half_index += 1

second_half_index = 0
for artist in top_artists_51_100:
    if not response_51_100[second_half_index]:
        artists_to_follow.append(artist)
    second_half_index += 1

# Determine how many requests are needed to follow all artists
# Then make the requests to follow the artists 
if len(artists_to_follow) < 50:
    url_1_50 = f"https://api.spotify.com/v1/me/following?type=artist&ids={%2C}".join([artist[0] for artist in artists_to_follow])
    spotify_api_client.make_request(url_1_50)
else:
    url_1_50 = f"https://api.spotify.com/v1/me/following?type=artist&ids={%2C}".join([artist[0] for artist in artists_to_follow])
    spotify_api_client.make_request(url_1_50)
    url_51_100 = f"https://api.spotify.com/v1/me/following?type=artist&ids={%2C}".join([artist[0] for artist in artists_to_follow])
    spotify_api_client.make_request(url_51_100)