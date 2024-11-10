# Spotify Automation with Python

Various scripts that allow you to automate common Spotify actions using your listening history. 

## Prerequisites
- Spotify Account (Free or Premium)
- Python 

## Features 
- Python script to preprocess Spotify data
- Pre-configured Tableau dashboard with various visualizations such as:
  - Most played songs/artists/albums by year/all time
  - Top new songs/artists/albums of the year
  - Most listened to genres 
  - ...

## Installation & Setup

1. **Request Your Spotify Data**
   - Go to [Spotify Account Privacy Settings](https://www.spotify.com/us/account/privacy/)
   - Check 'Extended streaming history'
   - Click 'Request Data'
   
   *Note: Full data delivery takes approximately 30 days*

2. **Get the Project**
   ```bash
   git clone https://github.com/pjtat/spotify-tableau-data-visualization.git
   cd spotify-python-automation
   ```

3. **Update Config File**
   - Add client id and client secret for your profile to config.yaml 
   
   Instructions on how to gather your client information here: https://developer.spotify.com/documentation/web-api/tutorials/getting-started

4. **Data Preparation**
   - Once you receive your Spotify data, extract the files
   - Place your `StreamingHistory*.json` files in the `data/raw` directory
   - Run the preprocessing script:
     ```bash
     python src/preprocess_data.py
     ```

5. **Execute Scripts for Desired Features**
   - TBD

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.