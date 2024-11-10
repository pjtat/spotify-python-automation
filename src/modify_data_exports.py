import os
import json

from os.path import dirname
from config import Config

# Load all ignore and field configs at once
IGNORE_CONFIG = {
    'artists': Config.get('ignore_artists'),
    'albums': Config.get('ignore_albums'),
    'tracks': Config.get('ignore_tracks')
}
FIELD_CONFIG = {
    'unneeded': Config.get('unneeded_fields'),
    'rename': Config.get('fields_to_rename')
}

# Initialize Spotify API client
from fetch_spotify_data import SpotifyApiClient
spotify_api_client = SpotifyApiClient()

class ModifyDataExports:
    def __init__(self):
        self.export_path = os.path.join(dirname(dirname(__file__)), 'exported_data')

    def combine_spotify_exports(self):
        # Initialize an empty list to hold all JSON data
        combined_spotify_export = []

        # Loop through each file in the specified directory
        for filename in os.listdir(self.export_path):
            if filename.endswith('.json'):
                file_path = os.path.join(self.export_path, filename)
                with open(file_path, 'r') as f:
                    # Load the JSON data from the file
                    data = json.load(f)
                    # Ensure the data is a list and extend the combined_data list
                    if isinstance(data, list):
                        combined_spotify_export.extend(data)

        # Write the combined data to a new JSON file
        output_file_raw = 'combined_spotify_data_raw.json'
        output_file_modified = 'combined_spotify_data_modified.json'

        with open(output_file_raw, 'w') as f:
            json.dump(combined_spotify_export, f, indent=2)
        
        with open(output_file_modified, 'w') as f:
            json.dump(combined_spotify_export, f, indent=2)

    def remove_null_items(self):
        # Pull in the existing combined export
        with open('combined_spotify_data_modified.json', 'r') as f:
            modified_data = json.load(f)

        # Filter out items with null values for track, artist, AND album
        modified_data_without_null_items = [
            item for item in modified_data
            if not (
                (item['master_metadata_track_name'] is None or item['master_metadata_track_name'] == 'null') and
                (item['master_metadata_album_artist_name'] is None or item['master_metadata_album_artist_name'] == 'null') and
                (item['master_metadata_album_album_name'] is None or item['master_metadata_album_album_name'] == 'null')
            )
        ]
        
        # Overwrite the existing file with the new data
        with open('combined_spotify_data_modified.json', 'w') as f:
            json.dump(modified_data_without_null_items, f, indent=2)

    def remove_ignored_items(self):
        # Pull in the existing combined export
        with open('combined_spotify_data_modified.json', 'r') as f:
            modified_data = json.load(f)

        # Filter out items will values in the ignore lists for track, artist, OR album
        modified_data_without_ignored_items = [
            item for item in modified_data
            if item['master_metadata_album_artist_name'] not in IGNORE_CONFIG['artists'] and
               item['master_metadata_album_album_name'] not in IGNORE_CONFIG['albums'] and
               item['master_metadata_track_name'] not in IGNORE_CONFIG['tracks']
        ]

        # Overwrite the existing file with the new data
        with open('combined_spotify_data_modified.json', 'w') as f:
            json.dump(modified_data_without_ignored_items, f, indent=2) 

    def remove_unneeded_data(self):
        # Pull in the existing combined export
        with open('combined_spotify_data_modified.json', 'r') as f:
            modified_data = json.load(f)
            
        # Remove unneeded fields 
        for item in modified_data:
            for field in FIELD_CONFIG['unneeded']:
                if field in item:
                    del item[field]
        
        # Overwrite the existing file with the new data
        with open('combined_spotify_data_modified.json', 'w') as f:
            json.dump(modified_data, f, indent=2)

    def rename_fields(self):
        # Pull in the existing combined export
        with open('combined_spotify_data_modified.json', 'r') as f:
            modified_data = json.load(f)

        #  Rename the fields
        for item in modified_data:
            for old_name, new_name in FIELD_CONFIG['rename'].items():
                if old_name in item:
                    item[new_name] = item.pop(old_name)

        # Overwrite the existing file with the new data
        with open('combined_spotify_data_modified.json', 'w') as f:
            json.dump(modified_data, f, indent=2)

    def clean_data(self):
        # Pull in the existing combined export
        with open('combined_spotify_data_modified.json', 'r') as f:
            modified_data = json.load(f)

        for item in modified_data:
            # Convert duration to seconds
            item['Play Duration (s)'] = round(item['Play Duration (s)'] / 1000, 2)
            # Remove the 'Z' and replace 'T' with a space
            item['Timestamp'] = item['Timestamp'].replace('Z', '').replace('T', ' ')
            # Convert Spotify URI to ID
            item['id'] = item['id'].replace('spotify:track:','')

        # Overwrite the existing file with the new data
        with open('combined_spotify_data_modified.json', 'w') as f:
            json.dump(modified_data, f, indent=2)