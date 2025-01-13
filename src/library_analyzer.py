from api_handler import SpotifyApiClient
import json

class LibraryAnalyzer:
    def __init__(self):
        self.spotify_api_handler = SpotifyApiClient()
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
    def get_library_artists(self) -> list[str]:
        pass

    def get_library_albums(self) -> list[str]:
        pass

    def get_library_genres(self) -> list[str]:
        pass

    def get_top_library_genres(self) -> list[str]:
        pass

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
        pass
    

if __name__ == '__main__':
    analyzer = LibraryAnalyzer()
    
    while True:
        print("\n=== Spotify Library Analysis ===")
        print("1. Count tracks in library")
        print("2. Fetch all library tracks")
        print("3. Find duplicate tracks")
        print("4. Remove duplicate tracks")
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
            print("\nAnalyzing library for duplicate tracks...")
            analyzer.find_duplicate_library_tracks()
            print("Duplicate tracks have been saved to 'data/processed/duplicate_library_tracks.json'")
            
        elif choice == '4':
            try:
                with open('data/processed/duplicate_library_tracks.json', 'r') as f:
                    duplicate_tracks = json.load(f)
                print(f"\nFound {len(duplicate_tracks)} duplicate tracks to remove")
                confirm = input("Do you want to proceed with removal? (y/n): ")
                if confirm.lower() == 'y':
                    analyzer.remove_duplicate_library_tracks(duplicate_tracks)
                    print("Successfully removed duplicate tracks")
            except FileNotFoundError:
                print("\nNo duplicate tracks file found. Please run option 3 first.")
            
        elif choice == '99':
            print("\nGoodbye!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")