import unittest
import logging
import sys
import os

from api_handler import SpotifyApiClient

class TestSpotifyAuth(unittest.TestCase):
    def setUp(self):
        self.client = SpotifyApiClient()

    def test_authentication(self):
        """Test that we can authenticate and access basic user data"""
        try:
            # Attempt authentication
            spotify = self.client.authenticate_user()
            
            # Test basic API calls that require authentication
            user = spotify.current_user()
            self.assertIsNotNone(user['id'])
            print(f"Successfully authenticated as user: {user['id']}")
            
            # Test getting user's playlists (requires playlist-read-private scope)
            playlists = spotify.current_user_playlists(limit=1)
            self.assertIsNotNone(playlists)
            
            # Test getting user's followed artists (requires user-follow-read scope)
            following = spotify.current_user_followed_artists(limit=1)
            self.assertIsNotNone(following)

        except Exception as e:
            self.fail(f"Authentication test failed: {str(e)}")

if __name__ == '__main__':
    unittest.main() 