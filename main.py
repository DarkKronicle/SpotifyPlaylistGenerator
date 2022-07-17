import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import generator.config.config_manager as config
from generator.util.EnvironmentCacheHandler import EnvironmentCacheHandler
import pathlib
import generator.types.playlist as playlist_mod


def set_playlist(sp, playlists, file, manager):
    playlist, instruction = manager.load_playlist(file)
    if playlist['daily'] == False:
        return
    name = playlist['name']
    playlist_id = None
    for p in playlists:
        if p.name.lower() == name.lower():
            playlist_id = p.playlist_id
            break
    if playlist_id is None:
        playlist_id = playlist_mod.Playlist.from_json(sp.user_playlist_create(sp.me()['id'], name)).playlist_id
    songs = instruction.run(sp)
    if len(songs) <= 100:
        sp.playlist_replace_items(playlist_id, [song.track_id for song in songs])
        return
    sp.playlist_replace_items(playlist_id, [song.track_id for song in songs[:100]])
    for i in range(len(songs) // 100 - 1):
        max_num = min((i + 1) * 100, len(songs))
        sp.playlist_add_items(songs[i * 100:max_num])


def main():
    manager = config.ConfigManager()

    os.environ["SAVED_TOKEN"] = manager['saved_token']
    os.environ["SPOTIPY_CLIENT_ID"] = manager['client_id']
    os.environ["SPOTIPY_CLIENT_SECRET"] = manager['client_secret']
    os.environ["SPOTIPY_REDIRECT_URI"] = manager['redirect_uri']

    scope = "user-library-read,user-top-read,playlist-read-collaborative,playlist-read-private,user-read-private,playlist-modify-private,playlist-modify-public"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, cache_handler=EnvironmentCacheHandler(os.environ["SAVED_TOKEN"])))
    playlists = playlist_mod.parse_playlist_list(sp.current_user_playlists(limit=50)['items'])
    for playlist in playlists:
        playlist_mod.get_playlist.set(playlist, sp, playlist.name)

    for playlist in pathlib.Path('./playlists').glob('**/*.toml'):
        set_playlist(sp, playlists, str(playlist), manager)


if __name__ == '__main__':
    main()
