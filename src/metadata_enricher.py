import json

from api_handler import SpotifyApiClient

class MetadataEnricher:
    def __init__(self) -> None:
        self.spotify_api_handler = SpotifyApiClient()

        self.MAX_REQUESTS = 50

    def get_ids(self, track_ids: 'str | list[str]', return_type: 'str') -> 'str':
        """
        Takes a list of track IDs and returns either the corresponding artist IDs or album IDs.

        Args:
            track_ids: Single track ID string or list of track ID strings
            return_type: Type of IDs to return - either 'artist' or 'album'

        Returns:
            list: Array of artist IDs or album IDs depending on return_type

        Raises:
            ValueError: If return_type is not 'artist' or 'album'
        """
        
        # Convert single string to list if necessary
        track_ids = [track_ids] if isinstance(track_ids, str) else track_ids

        # Initialize the dictionary to store artist ids or album ids
        return_ids = []
        
        # Use batch request to get artist/album ids
        track_data = self.spotify_api_handler.make_batch_request(
            items=track_ids,
            max_batch_size=self.MAX_REQUESTS,
            endpoint_template='tracks?ids={}'
        )

        # Get the artist or album ids
        if return_type == 'artist':
            for track in track_data:
                return_ids.append(track['artists'][0]['id'])
        elif return_type == 'album':
            for track in track_data:
                return_ids.append(track['album']['id'])
        else:
            raise ValueError(f'Invalid return_id_type: {return_type}')

        return return_ids

    def get_artist_genres(self, artist_ids: 'str | list[str]') -> 'dict[str, list[str]]':      
        # Convert single string to list if necessary
        artist_ids = [artist_ids] if isinstance(artist_ids, str) else artist_ids

        # Initialize the list to store artist genres
        artist_genres = []

        # Get genres for all artists
        artists_data = self.spotify_api_handler.make_batch_request(
            items=artist_ids,
            max_batch_size=self.MAX_REQUESTS,
            endpoint_template='artists?ids={}'
        )
        
        for artist in artists_data:
            artist_genres.append(artist['genres'])
            
        return artist_genres
    
    def get_artist_artwork(self, artist_ids: 'str | list[str]') -> 'dict[str, str]':
        # Convert single string to list if necessary
        artist_ids = [artist_ids] if isinstance(artist_ids, str) else artist_ids

        # Initialize the list to store artist artwork
        artist_artwork = []

        # Get artwork for all artists
        artists_data = self.spotify_api_handler.make_batch_request(
            items=artist_ids,
            max_batch_size=self.MAX_REQUESTS,
            endpoint_template='artists?ids={}'
        )

        for artist in artists_data:
            artist_artwork.append(artist['images'][0]['url'])

        return artist_artwork
    
    def get_album_artwork(self, album_ids: 'str | list[str]') -> 'dict[str, str]':
        # Convert single string to list if necessary
        album_ids = [album_ids] if isinstance(album_ids, str) else album_ids

        # Initialize the list to store album artwork
        album_artwork = []

        # Get artwork for all albums
        albums_data = self.spotify_api_handler.make_batch_request(
            items=album_ids,
            max_batch_size=self.MAX_REQUESTS,
            endpoint_template='albums?ids={}'
        )

        for album in albums_data:
            album_artwork.append(album['images'][0]['url'])

        return album_artwork

def test():
    metadata_enricher = MetadataEnricher()

    # Get test data from example file
    with open('data/processed/examples/combined_spotify_data_modified_example.json', 'r') as file:
        test_data = json.load(file)

    # Authenticate user with read-only scope
    metadata_enricher.spotify_api_handler.authenticate_user('user-read-private')

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