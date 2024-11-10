import json

# Number of top artists to follow 
# Update this number if you'd like to follow more or fewer artists
NUM_TOP_ARTISTS = 100

# Pull in preprocessed data
with open('data/processed/combined_spotify_data_modified.json', 'r') as f:
    listening_history = json.load(f)

# Initialize a dictionary to hold the count of each artist
artist_counts = {}

# Count the number of times each artist appears in the listening history
for listening_event in listening_history:
    artist = listening_event['Arist']
    if artist in artist_counts:
        artist_counts[artist] += 1
    else:
        artist_counts[artist] = 1

# Sort the artists by their counts in descending order
sorted_artists = sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)

# Get the top NUM_TOP_ARTISTS artists
top_artists = sorted_artists[:NUM_TOP_ARTISTS]

# Export top artists to a JSON file
with open('data/processed/top_artists.json', 'w') as f:
    json.dump(top_artists, f)