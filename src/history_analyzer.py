import os
import json

from datetime import datetime

class HistoryAnalyzer:
    def __init__(self) -> None:
        pass

    def get_user_listening_start_end_dates(self) -> tuple[str, str]:
        # Search for the first and last timestamp in the data
        modified_file_path = os.path.join('data', 'processed', 'combined_spotify_data_modified.json')
        with open(modified_file_path, 'r') as f:
            listening_history = json.load(f)

        # Convert timestamps to datetime objects for comparison
        timestamps = [datetime.strptime(item['Timestamp'], '%Y-%m-%d %H:%M:%S') for item in listening_history]
        
        first_timestamp = min(timestamps).strftime('%Y-%m-%d %H:%M:%S')
        last_timestamp = max(timestamps).strftime('%Y-%m-%d %H:%M:%S')

        return first_timestamp, last_timestamp

    def get_top_tracks(self, quantity: int, query_start_date: datetime, query_end_date: datetime) -> list[str]:
        # Pull in the modified data
        modified_file_path = os.path.join('data', 'processed', 'combined_spotify_data_modified.json')
        with open(modified_file_path, 'r') as f:
            listening_history = json.load(f)

        # Filter the data to only include the dates we want
        filtered_data = [item for item in listening_history if query_start_date <= datetime.strptime(item['Timestamp'], '%Y-%m-%d %H:%M:%S') <= query_end_date]

        # Scan through the data and get the top tracks
        top_tracks = {}
        for item in filtered_data:
            track_with_artist = f"{item['Track']} - {item['Arist']}"
            if track_with_artist in top_tracks:
                top_tracks[track_with_artist] += 1
            else:
                top_tracks[track_with_artist] = 1

        # Sort the tracks by number of plays
        sorted_tracks = sorted(top_tracks.items(), key=lambda x: x[1], reverse=True)

        # Return the top tracks with play counts
        return [f"{i+1}. {track[0]} - {track[1]} plays" for i, track in enumerate(sorted_tracks[:quantity])]

    def get_top_artists(self, quantity: int, query_start_date: datetime, query_end_date: datetime) -> list[str]:
        # Pull in the modified data
        modified_file_path = os.path.join('data', 'processed', 'combined_spotify_data_modified.json')
        with open(modified_file_path, 'r') as f:
            listening_history = json.load(f)

        # Filter the data to only include the dates we want
        filtered_data = [item for item in listening_history if query_start_date <= datetime.strptime(item['Timestamp'], '%Y-%m-%d %H:%M:%S') <= query_end_date]

       # Scan through the data and get the top artists
        top_artists = {}
        for item in filtered_data:
            if item['Arist'] in top_artists:
                top_artists[item['Arist']] += 1
            else:
                top_artists[item['Arist']] = 1

        # Sort the artists by number of plays
        sorted_artists = sorted(top_artists.items(), key=lambda x: x[1], reverse=True)

        # Return the top artists with play counts
        return [f"{i+1}. {artist[0]} - {artist[1]} plays" for i, artist in enumerate(sorted_artists[:quantity])]

    def get_top_albums(self, quantity: int, query_start_date: datetime, query_end_date: datetime) -> list[str]:
        # Pull in the modified data
        modified_file_path = os.path.join('data', 'processed', 'combined_spotify_data_modified.json')
        with open(modified_file_path, 'r') as f:
            listening_history = json.load(f)

        # Filter the data to only include the dates we want
        filtered_data = [item for item in listening_history if query_start_date <= datetime.strptime(item['Timestamp'], '%Y-%m-%d %H:%M:%S') <= query_end_date]

       # Scan through the data and get the top albums
        top_albums = {}
        for item in filtered_data:
            album_with_artist = f"{item['Album']} - {item['Arist']}"
            if album_with_artist in top_albums:
                top_albums[album_with_artist] += 1
            else:
                top_albums[album_with_artist] = 1

        # Sort the albums by number of plays
        sorted_albums = sorted(top_albums.items(), key=lambda x: x[1], reverse=True)

        # Return the top albums with play counts
        return [f"{i+1}. {album[0]} - {album[1]} plays" for i, album in enumerate(sorted_albums[:quantity])]

    def get_top_new_tracks_of_the_year(self, quantity: int, year: int) -> list[str]:
        # Pull in the modified data
        modified_file_path = os.path.join('data', 'processed', 'combined_spotify_data_modified.json')
        with open(modified_file_path, 'r') as f:
            listening_history = json.load(f)

        # Determine the first listening date of each track
        first_listening_dates = {}
        for item in listening_history:
            track_key = item['Track']  # Use track name as key
            if track_key not in first_listening_dates:
                first_listening_dates[track_key] = datetime.strptime(item['Timestamp'], '%Y-%m-%d %H:%M:%S')
            else:
                first_listening_dates[track_key] = min(first_listening_dates[track_key], datetime.strptime(item['Timestamp'], '%Y-%m-%d %H:%M:%S'))

        # Filter out all of the tracks that have a first listening date before the year started
        filtered_tracks = [item for item in listening_history if first_listening_dates[item['Track']] >= datetime(year, 1, 1)]

        # Scan through the data and get the top new tracks
        top_tracks = {}
        for item in filtered_tracks:
            track_with_artist = f"{item['Track']} - {item['Arist']}"
            if track_with_artist in top_tracks:
                top_tracks[track_with_artist] += 1
            else:
                top_tracks[track_with_artist] = 1

        # Sort the tracks by number of plays
        sorted_tracks = sorted(top_tracks.items(), key=lambda x: x[1], reverse=True)

        # Return the top tracks with play counts
        return [f"{i+1}. {track[0]} - {track[1]} plays" for i, track in enumerate(sorted_tracks[:quantity])]
    
    def get_top_new_albums_of_the_year(self, quantity: int, year: int) -> list[str]:
        # Pull in the modified data
        modified_file_path = os.path.join('data', 'processed', 'combined_spotify_data_modified.json')
        with open(modified_file_path, 'r') as f:
            listening_history = json.load(f)

        # Determine the first listening date of each album
        first_listening_dates = {}
        for item in listening_history:
            album_key = item['Album']  # Use album name as key
            if album_key not in first_listening_dates:
                first_listening_dates[album_key] = datetime.strptime(item['Timestamp'], '%Y-%m-%d %H:%M:%S')
            else:
                first_listening_dates[album_key] = min(first_listening_dates[album_key], datetime.strptime(item['Timestamp'], '%Y-%m-%d %H:%M:%S'))

        # Filter out all of the albums that have a first listening date before the year started
        filtered_albums = [item for item in listening_history if first_listening_dates[item['Album']] >= datetime(year, 1, 1)]

        # Scan through the data and get the top new albums
        top_albums = {}
        for item in filtered_albums:
            album_with_artist = f"{item['Album']} - {item['Arist']}"
            if album_with_artist in top_albums:
                top_albums[album_with_artist] += 1
            else:
                top_albums[album_with_artist] = 1

        # Sort the albums by number of plays
        sorted_albums = sorted(top_albums.items(), key=lambda x: x[1], reverse=True)

        # Return the top albums with play counts
        return [f"{i+1}. {album[0]} - {album[1]} plays" for i, album in enumerate(sorted_albums[:quantity])]
    
    def get_top_new_artists_of_the_year(self, quantity: int, year: int) -> list[str]:
        # Pull in the modified data
        modified_file_path = os.path.join('data', 'processed', 'combined_spotify_data_modified.json')
        with open(modified_file_path, 'r') as f:
            listening_history = json.load(f)

        # Determine the first listening date of each artist
        first_listening_dates = {}
        for item in listening_history:
            artist_key = item['Arist']  # Use artist name as key
            if artist_key not in first_listening_dates:
                first_listening_dates[artist_key] = datetime.strptime(item['Timestamp'], '%Y-%m-%d %H:%M:%S')
            else:
                first_listening_dates[artist_key] = min(first_listening_dates[artist_key], datetime.strptime(item['Timestamp'], '%Y-%m-%d %H:%M:%S'))

        # Filter out all of the artists that have a first listening date before the year started
        filtered_artists = [item for item in listening_history if first_listening_dates[item['Arist']] >= datetime(year, 1, 1)]

        # Scan through the data and get the top new artists
        top_artists = {}
        for item in filtered_artists:
            if item['Arist'] in top_artists:
                top_artists[item['Arist']] += 1
            else:
                top_artists[item['Arist']] = 1

        # Sort the artists by number of plays
        sorted_artists = sorted(top_artists.items(), key=lambda x: x[1], reverse=True)

        # Return the top artists with play counts
        return [f"{i+1}. {artist[0]} - {artist[1]} plays" for i, artist in enumerate(sorted_artists[:quantity])]

if __name__ == "__main__":
    history_analyzer = HistoryAnalyzer()
    
    while True:
        print("\nSpotify History Analyzer Menu:")
        print("1. Get top albums for time period")
        print("2. Get top artists for time period") 
        print("3. Get top tracks for time period")
        print("4. Get top new tracks of year")
        print("5. Get top new albums of year")
        print("6. Get top new artists of year")
        print("7. Exit")

        choice = input("\nEnter your choice (1-7): ")

        if choice == "7":
            break

        if choice in ["1", "2", "3"]:
            start_date = datetime.strptime(input("Enter start date (YYYY-MM-DD): "), "%Y-%m-%d")
            end_date = datetime.strptime(input("Enter end date (YYYY-MM-DD): "), "%Y-%m-%d")
            quantity = int(input("Enter number of results to show: "))

            if choice == "1":
                print("\nTop Albums:")
                print("\n".join(history_analyzer.get_top_albums(quantity, start_date, end_date)))
            elif choice == "2":
                print("\nTop Artists:")
                print("\n".join(history_analyzer.get_top_artists(quantity, start_date, end_date)))
            elif choice == "3":
                print("\nTop Tracks:")
                print("\n".join(history_analyzer.get_top_tracks(quantity, start_date, end_date)))

        elif choice in ["4", "5", "6"]:
            start_date = datetime.strptime(input("Enter start date (YYYY-MM-DD): "), "%Y-%m-%d")
            end_date = datetime.strptime(input("Enter end date (YYYY-MM-DD): "), "%Y-%m-%d")
            quantity = int(input("Enter number of results to show: "))

            if choice == "4":
                print("\nTop New Tracks:")
                print("\n".join(history_analyzer.get_top_new_tracks_of_the_year(quantity, start_date, end_date)))
            elif choice == "5":
                print("\nTop New Albums:")
                print("\n".join(history_analyzer.get_top_new_albums_of_the_year(quantity, start_date, end_date)))
            elif choice == "6":
                print("\nTop New Artists:")
                print("\n".join(history_analyzer.get_top_new_artists_of_the_year(quantity, start_date, end_date)))
        
        else:
            print("\nInvalid choice. Please try again.")