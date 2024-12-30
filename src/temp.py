import json 

# Determine how many entries are in the file
with open('data/processed/combined_spotify_data_modified.json', 'r') as file:
    data = json.load(file)
    print(len(data))