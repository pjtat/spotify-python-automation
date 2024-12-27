import json
import os
from os.path import dirname

class FileHandler:
    def __init__(self):
        self.export_path = os.path.join(dirname(dirname(__file__)), 'data')
        
    def combine_spotify_exports(self):
        # Determine the export path to the raw folder 
        raw_folder = os.path.join(self.export_path, 'raw')
        
        # Initialize an empty list to hold all JSON data
        combined_spotify_export = []

        # Loop through each file in the specified directory
        for filename in os.listdir(raw_folder):
            if filename.endswith('.json'):
                file_path = os.path.join(raw_folder, filename)
                with open(file_path, 'r') as f:
                    # Load the JSON data from the file
                    data = json.load(f)
                    # Ensure the data is a list and extend the combined_data list
                    if isinstance(data, list):
                        combined_spotify_export.extend(data)

        # Write the combined data to a new JSON file
        output_file_raw = os.path.join(raw_folder, 'combined_spotify_data_raw.json')
        with open(output_file_raw, 'w') as f:
            json.dump(combined_spotify_export, f, indent=2)
        
    def create_new_modified_data_file(self):
        # Pull in the raw data
        raw_file_path = os.path.join(self.export_path, 'raw', 'combined_spotify_data_raw.json')
        with open(raw_file_path, 'r') as f:
            combined_spotify_data = json.load(f)

        # Copy the raw data to the modified file 
        modified_file_path = os.path.join(self.export_path, 'processed', 'combined_spotify_data_modified.json')
        with open(modified_file_path, 'w') as f:
            json.dump(combined_spotify_data, f, indent=2)
    
    def pull_modified_data(self):
        modified_file_path = os.path.join(self.export_path, 'processed', 'combined_spotify_data_modified.json')
        with open(modified_file_path, 'r') as f:
            modified_data = json.load(f)
        return modified_data

    def export_to_folder(self, data, file_name, export_folder):
        # Create the directory if it doesn't exist
        os.makedirs(export_folder, exist_ok=True)
        
        # Now write the file
        with open(os.path.join(export_folder, file_name), 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_example_file(self, file, file_name, folder_name):
        # Grab the first 5 items from the data
        first_five_items = file[:5]

        # Add examples subfolder to the export path
        examples_folder = os.path.join(self.export_path, folder_name, 'examples')
        # Create the directory if it doesn't exist
        os.makedirs(examples_folder, exist_ok=True)

        # Export the first 5 items to the examples folder
        self.export_to_folder(first_five_items, file_name, examples_folder)
    
    def create_test_file(self, file, file_name):
        # Add test subfolder to the export path
        test_folder = os.path.join(self.export_path, 'test')
        # Create the directory if it doesn't exist
        os.makedirs(test_folder, exist_ok=True)

        # Export the last 5 items to the test folder
        self.export_to_folder(file, file_name, test_folder)