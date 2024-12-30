import json

from api_handler import SpotifyApiClient

# Initialize the client with authentication
spotify_api_handler = SpotifyApiClient()

class MetadataEnricher:
    def __init__(self) -> None:
        pass

    def get_ids(self, ids: 'str | list[str]', return_id_type: 'str') -> 'str':
        if return_id_type == 'artist':
            ids = f'artists?ids={",".join(ids)}'
        elif return_id_type == 'album':
            ids = f'albums?ids={",".join(ids)}'
        else:
            raise ValueError(f'Invalid return_id_type: {return_id_type}')
    
        return ids

    def get_artist_genres(self, artist_ids: 'str | list[str]') -> 'dict[str, list[str]]':
        # Define the URL for the artist artwork request
        request_url = f'artists?'
       
        # Define the maximum number of tracks to request at a time
        MAX_REQUESTS = 50

        artist_genres = {}  

        # Convert single string to list if necessary
        artist_ids = [artist_ids] if isinstance(artist_ids, str) else artist_ids

        # Get genres for all artists
        for i in range(0, len(artist_ids), MAX_REQUESTS):
            batch_artist_ids = artist_ids[i:i + MAX_REQUESTS]
            request_url = f'artists?{batch_artist_ids}'
            artists_response = spotify_api_handler.make_request(request_url)
            for artist in artists_response['artists']:
                artist_genres[artist['id']] = artist['genres']
            
        return artist_genres
    
    def get_artist_artwork(self, artist_ids: 'str | list[str]') -> 'dict[str, str]':
        # Define the URL for the artist artwork request
        request_url = f'artists?'

        # Define the maximum number of tracks to request at a time
        MAX_REQUESTS = 50

        artist_artwork = {}

        # Make batch requests for all artist artwork
        for i in range(0, len(artist_ids), MAX_REQUESTS):    
            batch_artist_ids = artist_ids[i:i + MAX_REQUESTS]
            request_url = f'artists?{batch_artist_ids}'
            response = spotify_api_handler.make_request(request_url)
            for artist in response['artists']:
                artist_artwork[artist['id']] = artist['images'][0]['url']
        
        return artist_artwork
    
    def get_album_artwork(self, album_ids: 'str | list[str]') -> 'dict[str, str]':
        # Define the URL for the album artwork request
        request_url = f'albums?'

        # Define the maximum number of tracks to request at a time
        MAX_REQUESTS = 50

        album_artwork = {}

        # Make batch requests for all album artwork
        for i in range(0, len(album_ids), MAX_REQUESTS):    
            batch_album_ids = album_ids[i:i + MAX_REQUESTS]
            request_url = f'albums?{batch_album_ids}'
            response = spotify_api_handler.make_request(request_url)
            for album in response['albums']:
                album_artwork[album['id']] = album['images'][0]['url']
        
        return album_artwork

def test():
    metadata_enricher = MetadataEnricher()

    # Get test data from example file
    with open('data/processed/examples/combined_spotify_data_modified_example.json', 'r') as file:
        test_data = json.load(file)

    # Authenticate user with read-only scope
    spotify_api_handler.authenticate_user('user-read-private')

    # Extract track IDs from test_data first
    test_track_ids = [track['id'] for track in test_data]

    # Now pass the list of IDs
    test_artist_ids = metadata_enricher.get_ids(test_track_ids, 'artist')
    test_album_ids = metadata_enricher.get_ids(test_track_ids, 'album')

    # Test get_artist_genres
    print(metadata_enricher.get_artist_genres(test_artist_ids))

    # Test get_artist_artwork
    print(metadata_enricher.get_artist_artwork(test_artist_ids))

    # Test get_album_artwork
    print(metadata_enricher.get_album_artwork(test_album_ids))

if __name__ == "__main__":
    test()