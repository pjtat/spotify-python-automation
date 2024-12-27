from config import Config
from file_handler import FileHandler

class ModifyDataExports:
    def __init__(self):
        self.config = Config()
        self.file_handler = FileHandler()

    def remove_null_items(self):
        # Pull in the existing combined export
        modified_data = self.file_handler.pull_modified_data()

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
        self.file_handler.export_to_folder(modified_data_without_null_items, 'combined_spotify_data_modified.json', 'processed')

    def remove_ignored_items(self):
        # Pull in the existing combined export
        modified_data = self.file_handler.pull_modified_data()

        # Filter out items will values in the ignore lists for track, artist, OR album
        modified_data_without_ignored_items = [
            item for item in modified_data
            if item['master_metadata_album_artist_name'] not in self.config.get('ignore_artists') and
               item['master_metadata_album_album_name'] not in self.config.get('ignore_albums') and
               item['master_metadata_track_name'] not in self.config.get('ignore_tracks')
        ]

        # Overwrite the existing file with the new data
        self.file_handler.export_to_folder(modified_data_without_ignored_items, 'combined_spotify_data_modified.json', 'processed')

    def remove_unneeded_data(self):
        # Pull in the existing combined export
        modified_data = self.file_handler.pull_modified_data()
            
        # Remove unneeded fields 
        for item in modified_data:
            for field in self.config.get('unneeded_fields'):
                if field in item:
                    del item[field]
        
        # Overwrite the existing file with the new data
        self.file_handler.export_to_folder(modified_data, 'combined_spotify_data_modified.json', 'processed')

    def rename_fields(self):
        # Pull in the existing combined export
        modified_data = self.file_handler.pull_modified_data()

        #  Rename the fields
        for item in modified_data:
            for old_name, new_name in self.config.get('fields_to_rename').items():
                if old_name in item:
                    item[new_name] = item.pop(old_name)

        # Overwrite the existing file with the new data
        self.file_handler.export_to_folder(modified_data, 'combined_spotify_data_modified.json', 'processed')

    def clean_data(self):
        # Pull in the existing combined export
        modified_data = self.file_handler.pull_modified_data()

        for item in modified_data:
            # Convert duration to seconds
            item['Play Duration (s)'] = round(item['Play Duration (s)'] / 1000, 2)
            # Remove the 'Z' and replace 'T' with a space
            item['Timestamp'] = item['Timestamp'].replace('Z', '').replace('T', ' ')
            # Convert Spotify URI to ID
            item['id'] = item['id'].replace('spotify:track:','')

        # Overwrite the existing file with the new data
        self.file_handler.export_to_folder(modified_data, 'combined_spotify_data_modified.json', 'processed')
