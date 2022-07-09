import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import generator.config.config_manager as config


def main():
    manager = config.ConfigManager()

    os.environ["SPOTIPY_CLIENT_ID"] = manager['client_id']
    os.environ["SPOTIPY_CLIENT_SECRET"] = manager['client_secret']
    os.environ["SPOTIPY_REDIRECT_URI"] = manager['redirect_uri']

    scope = "user-library-read,user-top-read"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    instance = manager.load_playlist(manager['playlist_generate'])
    songs = instance.run(sp)
    for track in songs:
        print(track.url)


if __name__ == '__main__':
    main()
