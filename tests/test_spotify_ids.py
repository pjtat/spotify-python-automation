import unittest
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api_handler import SpotifyApiClient

class TestSpotifyIds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the SpotifyApiClient once for all tests"""
        cls.client = SpotifyApiClient()
    
    def test_track_id(self):
        """Test that we can get track info from an ID"""
        track_id = "3z8h0TU7ReDPLIbEnYhWZb" # Bohemian Rhapsody
        track_info = self.client.make_request(
            endpoint=f'tracks/{track_id}',
            method='GET'
        )
        self.assertIsNotNone(track_info)
        print(track_info['name'])
    
    def test_artist_id(self):
        """Test that we can get artist info from an ID"""
        artist_id = "0YsLR3SQd5QTXAhGIGX7cl"  # Del the Funky Homosapien
        artist_info = self.client.make_request(
            endpoint=f'artists/{artist_id}',
            method='GET'
        )
        self.assertIsNotNone(artist_info)
        print(artist_info['name'])
    
    def test_album_id(self):
        """Test that we can get album info from an ID"""
        album_id = "1u5BsuBK45mLwrbqdASN3g"  # Led Zeppelin III
        album_info = self.client.make_request(
            endpoint=f'albums/{album_id}',
            method='GET'
        )
        self.assertIsNotNone(album_info)
        print(album_info['name'])

if __name__ == '__main__':
    unittest.main()
