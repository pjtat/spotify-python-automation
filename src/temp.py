from api_handler import SpotifyApiClient

SCOPE = "user-follow-modify user-follow-read"

def main():
    spotify_api_handler = SpotifyApiClient()
    spotify_api_handler.authenticate_user(SCOPE)
    following = spotify_api_handler.make_request('me/following?type=artist&limit=5')
    print(following)

if __name__ == "__main__":
    main()