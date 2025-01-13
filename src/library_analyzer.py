from api_handler import SpotifyApiClient
from metadata_enricher import MetadataEnricher
import json

class LibraryAnalyzer:
    def __init__(self):
        self.spotify_api_handler = SpotifyApiClient()
        self.metadata_enricher = MetadataEnricher()
        self.library_track_data = []  
        self.MAX_REQUESTS = 50

    def get_library_track_count(self) -> int:
        # Get the total number of tracks in the library
        response = self.spotify_api_handler.make_request(
            endpoint='me/tracks',
            limit=1
        )
        return response['total']
    
    def get_followed_artist_count(self) -> int:
        # Get the total number of artists in the library
        response = self.spotify_api_handler.make_request(
            endpoint='me/following?type=artist',
            limit=1
        )
        return response['artists']['total']

    def get_library_tracks(self) -> list[str]:
        # Initialize variables for pagination
        library_tracks = []
        offset = 0

        # Determine the total number of tracks in the library
        total_tracks_in_library = self.get_library_track_count()

        while offset < total_tracks_in_library:
            # Get batch of tracks
            response = self.spotify_api_handler.make_request(
                endpoint='me/tracks',
                limit=self.MAX_REQUESTS,
                offset=offset
            )
            
            # Add tracks from this batch
            library_tracks.extend(response['items'])

            # Increment offset for next batch
            offset += self.MAX_REQUESTS

        # Print the raw library track data to JSON 
        with open('data/raw/library_tracks_raw.json', 'w') as f:
            json.dump(library_tracks, f, indent=4)
        
        # Extract just the basic track info we need
        simplified_tracks = []
        for track in library_tracks:
            track_info = {
                'name': track['track']['name'],
                'artist': track['track']['artists'][0]['name'],
                'album': track['track']['album']['name'],
                'id': track['track']['id'],
                'added_at': track['added_at']
            }
            simplified_tracks.append(track_info)

        # Save simplified library tracks to processed folder
        with open('data/processed/library_tracks_simplified.json', 'w') as f:
            json.dump(simplified_tracks, f, indent=4)
        
        return simplified_tracks
    
    def get_followed_artists(self) -> list[str]:
        # Initialize variables for pagination
        followed_artists = []
        offset = 0

        # Determine the total number of artists in the library
        total_artists_in_library = self.get_followed_artist_count()

        while offset < total_artists_in_library:
            # Get batch of artists
            response = self.spotify_api_handler.make_request(
                endpoint='me/following?type=artist',
                limit=self.MAX_REQUESTS,
                offset=offset
            )

            # Add artists from this batch
            followed_artists.extend(response['artists']['items'])

            # Increment offset for next batch
            offset += self.MAX_REQUESTS
        
        # Simplify the followed artists 
        simplified_followed_artists = []
        for artist in followed_artists:
            artist_info = {
                'name': artist['name'],
                'id': artist['id']
            }
            simplified_followed_artists.append(artist_info)

        # Return the followed artists
        return simplified_followed_artists

    def find_unfollowed_library_artists(self) -> list[str]:
        # Get the followed artists
        followed_artists = self.get_followed_artists()

        # Get the library artists
        library_artists = self.load_library_artists()
        
        # Create a set of followed artist IDs for efficient lookup
        followed_artist_ids = {artist['id'] for artist in followed_artists}
        
        # Find artists in library that aren't in followed_artist_ids
        unfollowed_artists = [
            artist for artist in library_artists 
            if artist['id'] not in followed_artist_ids
        ]

        # Remove duplicates while preserving artist name and id
        unique_unfollowed_artists = []
        seen = set()
        for artist in unfollowed_artists:
            artist_tuple = (artist['name'], artist['id'])
            if artist_tuple not in seen:
                seen.add(artist_tuple)
                unique_unfollowed_artists.append(artist)
        unfollowed_artists = unique_unfollowed_artists
        
        return unfollowed_artists

    def load_library_artists(self) -> list[str]:
        # Open the library tracks file
        with open('data/processed/library_tracks_simplified.json', 'r') as f:
            library_tracks = json.load(f)

        # Get all of the track IDs in a list
        track_ids = [track['id'] for track in library_tracks]

        # In batches, make a request to get the track information
        track_info = self.spotify_api_handler.make_batch_request(
            items=track_ids,
            max_batch_size=self.MAX_REQUESTS,
            endpoint_template='tracks?ids={}',
            key='tracks'
        )

        # Get the artist name and ID from the track information
        artists = [{'name': track['artists'][0]['name'], 'id': track['artists'][0]['id']} for track in track_info]

        # Remove the track ID from the track information
        artists = [{'name': artist['name'], 'id': artist['id']} for artist in artists]

        # Remove duplicates while preserving artist name and id
        unique_artists = []
        seen = set()
        for artist in artists:
            artist_tuple = (artist['name'], artist['id'])
            if artist_tuple not in seen:
                seen.add(artist_tuple)
                unique_artists.append(artist)
        artists = unique_artists

        # Return the artists
        return artists

    def load_library_albums(self) -> list[str]:
        # Open the library tracks file
        with open('data/processed/library_tracks_simplified.json', 'r') as f:
            library_tracks = json.load(f)

        # Get all of the track IDs in a list    
        track_ids = [track['id'] for track in library_tracks]

        # In batches, make a request to get the track information
        track_info = self.spotify_api_handler.make_batch_request(
            items=track_ids,
            max_batch_size=self.MAX_REQUESTS,
            endpoint_template='tracks?ids={}',
            key='tracks'
        )

        # Get the albums and their IDs from the track information
        albums = [{'name': track['album']['name'], 'id': track['album']['id']} for track in track_info]
        
        # Remove the track ID from the track information
        albums = [{'name': album['name'], 'id': album['id']} for album in albums]

        # Remove duplicates while preserving album name and id
        unique_albums = []
        seen = set()
        for album in albums:
            album_tuple = (album['name'], album['id'])
            if album_tuple not in seen:
                seen.add(album_tuple)
                unique_albums.append(album)
        albums = unique_albums

        # Return the albums
        return albums

    def get_library_genres(self, top_n: int = None) -> list[str]:
        # Get the library track IDs from the library tracks file
        with open('data/processed/library_tracks_simplified.json', 'r') as f:
            library_tracks = json.load(f)

        # Pull all of the track IDs from the library tracks
        track_ids = [track['id'] for track in library_tracks]

        # Swap the track IDs for the artist IDs
        artist_ids = self.metadata_enricher.get_ids(track_ids, 'artist')

        # Get the genres from the library tracks
        genres = self.metadata_enricher.get_artist_genres(artist_ids)

        # Provide the genres in a list with the count of each genre
        genre_counts = {}
        for genre_list in genres:
            for genre in genre_list:
                if genre in genre_counts:
                    genre_counts[genre] += 1
                else:
                    genre_counts[genre] = 1

        # Sort the genres by count
        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)

        # If top_n is provided, return the top N genres 
        if top_n:
            return sorted_genres[:top_n]
        # Otherwise, return all genres
        else:
            return sorted_genres

    def find_duplicate_library_tracks(self) -> list[str]:
        # Pull in the library track data from file
        with open('data/processed/library_tracks_simplified.json', 'r') as f:
            library_track_data = json.load(f)

        # Create a dictionary to track unique songs and their duplicates
        seen_tracks = []
        duplicate_tracks = []

        # Find all songs that have the same name and artist
        # Initialize dictionary to track seen tracks
        seen_tracks = {}

        # Iterate through all tracks in library
        for track in library_track_data:
            track_key = f"{track['name']}-{track['artist']}"
            
            # If we've seen this track before, add the ID to the list
            if track_key in seen_tracks:
                seen_tracks[track_key]['ids'].append(track['id'])
            # Otherwise create a new entry
            else:
                seen_tracks[track_key] = {
                    'artist': track['artist'],
                    'ids': [track['id']]
                }

        # Convert seen_tracks to list format
        for track_name, track_data in seen_tracks.items():
            if len(track_data['ids']) > 1:
                duplicate_tracks.append({
                    track_name: {
                        'artist': track_data['artist'],
                        'ids': track_data['ids']
                    }
                })
        # Determine count of duplicate tracks
        print(f"Total duplicate tracks: {len(duplicate_tracks)}")

        # Add duplicate tracks to a new file
        with open('data/processed/duplicate_library_tracks.json', 'w') as f:
            json.dump(duplicate_tracks, f, indent=4)
    
    def remove_duplicate_library_tracks(self, duplicate_tracks: list[str]) -> None:
        # Initialize list to track track IDs to remove
        track_ids_to_remove = []
        
        # Get the track IDs to remove from the duplicate tracks
        for track in duplicate_tracks:
            # Pull the additional track IDs to remove (leaving the first one)
            individual_track_ids_to_remove = list(track.values())[0]['ids'][1:]

            # Remove this track from the duplicate tracks
            duplicate_tracks.remove(track)

            # Add each track ID to a list
            for track_id in individual_track_ids_to_remove:
                track_ids_to_remove.append(track_id)
        
        # Overwrite duplicate tracks file with updated data
        with open('data/processed/duplicate_library_tracks.json', 'w') as f:
            json.dump(duplicate_tracks, f, indent=4)
        
        # Remove duplicate tracks in batches
        while track_ids_to_remove:
            # Get batch of track IDs to remove
            batch_size = min(self.MAX_REQUESTS, len(track_ids_to_remove))
            batch_of_track_ids_to_remove = track_ids_to_remove[:batch_size]
            
            # Format the data correctly for the API
            formatted_data = {"ids": batch_of_track_ids_to_remove}
            
            # Remove the batch of track IDs
            self.spotify_api_handler.make_request(
                endpoint='me/tracks',
                method='DELETE',
                data=formatted_data,  # Send formatted data
            )
            
            # Remove the processed batch
            track_ids_to_remove = track_ids_to_remove[batch_size:]

    def follow_library_artists(self) -> None:
        # Get the unfollowed artists from my library
        # unfollowed_artists = self.find_unfollowed_library_artists()
        unfollowed_artists = ['4j7DrazfBZLLD0OrVoAtEe']
        # Follow the unfollowed artists
        for artist in unfollowed_artists:
            self.spotify_api_handler.make_request(
                endpoint=f'me/following?type=artist&ids={artist["id"]}',
                method='PUT'
            )
    

if __name__ == '__main__':
    analyzer = LibraryAnalyzer()
    
    while True:
        print("\n=== Spotify Library Analysis ===")
        print("1. Fetch library track count")
        print("2. Fetch all library tracks")
        print("3. Fetch all library artists")
        print("4. Fetch all library albums")
        print("5. Find duplicate library tracks")
        print("6. Remove duplicate library tracks")
        print("7. Get followed artists")
        print("8. Find unfollowed library artists")
        print("9. Get library genres")
        print("99. Exit")
        
        choice = input("\nEnter your choice (1-99): ")
        
        if choice == '1':
            print("\nCounting tracks in your library...")
            total_tracks = analyzer.get_library_track_count()
            print(f"Found {total_tracks} total tracks")
            
        elif choice == '2':
            print("\nFetching all tracks from your library...")
            analyzer.get_library_tracks()
            print("Successfully retrieved all library tracks")
            
        elif choice == '3':
            print("\nFetching all artists from your library...")
            library_artists = analyzer.load_library_artists()
            print(f"Successfully retrieved {len(library_artists)} library artists")
            print(library_artists)
            
        elif choice == '4':
            print("\nFetching all albums from your library...")
            library_albums = analyzer.load_library_albums()
            print(f"Successfully retrieved {len(library_albums)} library albums")
            print(library_albums)
            
        elif choice == '5':
            print("\nAnalyzing library for duplicate tracks...")
            analyzer.find_duplicate_library_tracks()
            print("Duplicate tracks have been saved to 'data/processed/duplicate_library_tracks.json'")
            
        elif choice == '6':
            try:
                with open('data/processed/duplicate_library_tracks.json', 'r') as f:
                    duplicate_tracks = json.load(f)
                print(f"\nFound {len(duplicate_tracks)} duplicate tracks to remove")
                confirm = input("Do you want to proceed with removal? (y/n): ")
                if confirm.lower() == 'y':
                    analyzer.remove_duplicate_library_tracks(duplicate_tracks)
                    print("Successfully removed duplicate tracks")
            except FileNotFoundError:
                print("\nNo duplicate tracks file found. Please run option 5 first.")
                
        elif choice == '7':
            print("\nFetching followed artists...")
            followed_artists = analyzer.get_followed_artists()
            print(f"Successfully retrieved {len(followed_artists)} followed artists")
            print(followed_artists)
            
        elif choice == '8':
            print("\nFinding unfollowed library artists...")
            unfollowed_artists = analyzer.find_unfollowed_library_artists()
            print(f"Successfully identified {len(unfollowed_artists)} unfollowed library artists")
            print(unfollowed_artists)
            
        elif choice == '9':
            print("\nFetching library genres...")
            top_n = input("Enter number of top genres to display (press Enter for all): ")
            top_n = int(top_n) if top_n.strip() else None
            library_genres = analyzer.get_library_genres(top_n)
            print(f"Successfully retrieved library genres")
            print(library_genres)
            
        elif choice == '99':
            print("\nGoodbye!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")