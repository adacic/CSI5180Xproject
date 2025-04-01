import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from spotipy import SpotifyException
import json
import os
import time

class Connect2Spotify:
    def __init__(self, file_name):
        try:
            with open(file_name, "r") as file:
                basicInfoJson = json.load(file)
        except FileNotFoundError:
            print("basic info file not found")
            return ""
        
        # Check if Spotify app is already running
        if not self.__is_spotify_running():
            self.__open_spotify_app()

        try:
            self.__sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=basicInfoJson.get("cid"),
                    client_secret=basicInfoJson.get("secret"),
                    redirect_uri=basicInfoJson.get("redirectURI"),
                    scope=basicInfoJson.get("scope"),
                )
            )
            self.mode = "title"  # can be title or lyric
        except SpotifyException as e:
            print(e)
            raise Exception("Unable to initialize connection to Spotify API")
    
    def __is_spotify_running(self):
        """Check if Spotify app is already running."""
        try:
            if os.name == "nt":  # Windows
                tasks = os.popen('tasklist /FI "IMAGENAME eq spotify.exe" /FO LIST').read().lower()
                return "spotify.exe" in tasks
            elif os.name == "posix":  # macOS/Linux
                processes = os.popen('ps -e | grep spotify').read().strip()
                return bool(processes)
        except Exception as e:
            print(f"Error checking Spotify status: {e}")
        return False
    
    def __open_spotify_app(self):
        """Open the Spotify app automatically."""
        try:
            if os.name == "nt":  # Windows
                os.startfile("spotify")
            elif os.name == "posix":  # macOS/Linux
                os.system("open -a Spotify" if "darwin" in os.uname().sysname.lower() else "spotify &")
            print("Spotify app opened successfully.")
            time.sleep(5)
        except Exception as e:
            print(f"Failed to open Spotify app: {e}")

    def play(self, song_name, artist_name):
        user_info = self.__sp.current_user()
        print(f"User Info: {user_info}")  # Debug: Print user info
        if user_info.get("product") != "premium":
            return "Spotify Premium is required to play songs."

        query = f'track:"{song_name}" artist:"{artist_name}"'  # Ensure proper formatting
        results = self.__sp.search(q=query, type='track', limit=1)
        print(f"Search Results: {results}")  # Debug: Print search results
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            track_uri = track['uri']
            devices = self.__sp.devices()
            print(f"Devices: {devices}")  # Debug: Print available devices
            if devices['devices']:
                device_id = devices['devices'][0]['id']
                # Add the track to the playback queue
                self.__sp.add_to_queue(uri=track_uri, device_id=device_id)
                # Start playback
                self.__sp.start_playback(device_id=device_id, uris=[track_uri])
                return f"Playing: {track['name']} by {track['artists'][0]['name']}"
            else:
                return "No active devices found."
        else:
            return "No song found with that name and artist."
    
    def play_by_lyric(self, lyric):
        # Use a general search query without the 'lyrics:' prefix
        results = self.__sp.search(q=lyric, type='track', limit=10)
        print(f"Search Results: {results}")  # Debug: Print search results

        if results['tracks']['items']:
            # Iterate through the results to find the most relevant match
            for track in results['tracks']['items']:
                # Check if the lyric matches part of the track name or artist name
                if lyric.lower() in track['name'].lower() or any(lyric.lower() in artist['name'].lower() for artist in track['artists']):
                    track_uri = track['uri']
                    devices = self.__sp.devices()
                    print(f"Devices: {devices}")  # Debug: Print available devices
                    if devices['devices']:
                        device_id = devices['devices'][0]['id']
                        # Add the track to the playback queue
                        self.__sp.add_to_queue(uri=track_uri, device_id=device_id)
                        # Start playback
                        self.__sp.start_playback(device_id=device_id, uris=[track_uri])
                        return f"Playing: {track['name']} by {track['artists'][0]['name']}"
            # If no exact match is found, return the first result
            track = results['tracks']['items'][0]
            track_uri = track['uri']
            devices = self.__sp.devices()
            if devices['devices']:
                device_id = devices['devices'][0]['id']
                self.__sp.add_to_queue(uri=track_uri, device_id=device_id)
                self.__sp.start_playback(device_id=device_id, uris=[track_uri])
                return f"Playing: {track['name']} by {track['artists'][0]['name']}"
            return "No active devices found to play the song."
        else:
            return "No song found with those lyrics."
    
    def pause(self):
        devices = self.__sp.devices()
        if devices['devices']:
            device_id = devices['devices'][0]['id']
            try:
                self.__sp.pause_playback(device_id=device_id)
                return "Playback paused."
            except SpotifyException as e:
                if e.http_status == 403:
                    return "Unable to pause playback: Restriction violated. Ensure the device supports this action."
                else:
                    return f"An error occurred: {e}"
        else:
            return "No active devices found."
        
    def skip_to_next(self):
        devices = self.__sp.devices()
        if devices['devices']:
            device_id = devices['devices'][0]['id']
            self.__sp.next_track(device_id=device_id)
            return "Skipped to the next song."
        else:
            return "No active devices found."
        
    def change_mode_to_title(self):
        self.mode = "title"
        return "Mode changed to title."
    
    def change_mode_to_lyric(self):
        self.mode = "lyric"
        return "Mode changed to lyric."
    
if __name__ == "__main__":
    c2s = Connect2Spotify("app_config.json")
    # Wait for 5 seconds before continuing
    #print(c2s.mode)
    #print(c2s.pause())
    print(c2s.play("enemy","imagine dragons"))
    #lyric = "Just a young gun with a quick fuse"
    #print(c2s.play_by_lyric(lyric))
    #print(c2s.change_mode_to_title())
    #print(c2s.mode)