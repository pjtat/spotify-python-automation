from api_handler import SpotifyApiClient

# Initialize the client with authentication
spotify_api_handler = SpotifyApiClient()

# API Parameters
REQUEST_TYPE = 'artist'
REQUEST_LIMIT = '50'
SCOPE = "user-follow-modify user-follow-read"

# Script Constants 
# How many top artists to follow
TOP_ARTIST_AMOUNT = 150

def test(): 
    # How many artists to grab
    test_artists = 5

    url = f'me/following?type={REQUEST_TYPE}&limit={test_artists}'
    response = spotify_api_handler.make_get_request(url)
    
    # Pretty print the response
    import json
    print(json.dumps(response, indent=2))

def main():
    # Determine top artists

    # Determine list of all followed artists
    url = f'me/top/{REQUEST_TYPE}?time_range=short_term&limit={REQUEST_LIMIT}'
    # response = spotify_api_handler.make_get_request(url)

    # Determine list of all artists that are not followed

    # Follow all artists that are not followed

    user_followed_artists = spotify_api_handler.make_request('me/following?type=artist&limit=5')
    
if __name__ == "__main__":
    #main()
    test()