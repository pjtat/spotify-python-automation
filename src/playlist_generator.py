""" After starting this, I realized that it's pretty limited since there are 
many artists that Spotify does not assign genres to. Tabling any future work on this."""

from api_handler import SpotifyApiClient
from library_analyzer import LibraryAnalyzer
import random
import datetime
import json

class PlaylistGenerator:
    def __init__(self):
        self.spotify_api_handler = SpotifyApiClient()
        self.library_analyzer = LibraryAnalyzer()
        # Set playlist constants
        self.public_playlist = False
        self.collaboration_playlist = False
        self.playlist_description = ""

    def generate_playlist(self, playlist_name: str, number_of_tracks: int, genres: list[str]):
        """ Generate a playlist with the given parameters
        Args:
            playlist_name (str): Name of the playlist
            number_of_tracks (int): Number of tracks to include
            genres (list[str]): List of genres to include
        """
        # Clean up genres by stripping whitespace
        genres = [genre.strip() for genre in genres]

        # Get the user's ID
        user_response = self.spotify_api_handler.make_request(endpoint='me', method='GET')
        user_id = user_response['id']

        # Create the playlist with required body parameters
        playlist_body = {
            "name": playlist_name,
            "description": self.playlist_description,
            "public": self.public_playlist
        }
        playlist_response = self.spotify_api_handler.make_request(
            endpoint=f"users/{user_id}/playlists",
            method="POST", 
            data=playlist_body
        )

        playlist_id = playlist_response['id']

        # Search through the library for the tracks that match the user's input
        # Create a new file with library tracks
        self.library_analyzer.get_library_tracks()

        # Open the file and read the tracks
        with open('data/processed/library_tracks_simplified.json', 'r') as file:
            tracks = json.load(file)

        # Search through the tracks for the ones that match the user's input
        playlist_tracks = []  # Initialize the list
        for track in tracks:
            # Check if any of the track's genres match the user's selected genres
            if any(genre in track['genres'] for genre in genres):
                playlist_tracks.append(track)

        # Error handling if the number of tracks found is less than the number of tracks requested
        if len(playlist_tracks) < number_of_tracks:
            print(f"Error: Only found {len(playlist_tracks)} tracks that match the user's input. Please try again with a different set of genres.")
            return

        # Pull a random selectionon the tracks to match the total number of tracks
        playlist_tracks = random.sample(playlist_tracks, number_of_tracks)

        # Add the tracks to the playlist
        track_uris = [f"spotify:track:{track['id']}" for track in playlist_tracks]
        playlist_body = {
            "uris": track_uris,
            "position": 0
        }
        self.spotify_api_handler.make_request(
            endpoint=f"playlists/{playlist_id}/tracks",
            method="POST",
            data=playlist_body
        )

        # Return confirmation message 
        print(f"Playlist {playlist_name} created successfully with {number_of_tracks} tracks.")

if __name__ == "__main__":
    # Ask user if they want to test or run in production
    mode = input("Would you like to run in test mode or production mode? (test/prod): ").lower()

    if mode == "test":
        # Use test parameters
        playlist_name = f"Test Playlist - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        number_of_tracks = 20
        genres = ["grunge"]
    elif mode == "prod":
        # Get user input for parameters
        playlist_name = input("Enter playlist name: ")
        while True:
            try:
                number_of_tracks = int(input("Enter number of tracks (1-100): "))
                if 1 <= number_of_tracks <= 100:
                    break
                print("Please enter a number between 1 and 100")
            except ValueError:
                print("Please enter a valid number")
        
        print("Enter genres (separated by commas):")
        genres = [genre.strip() for genre in input().split(",")]
    else:
        print("Invalid mode selected. Please run again and select 'test' or 'prod'")
        exit()

    playlist_generator = PlaylistGenerator()
    playlist_generator.generate_playlist(playlist_name, number_of_tracks, genres)