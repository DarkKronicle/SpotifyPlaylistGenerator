import generator.instruction as instruction
import generator.modifier as modifier
import generator.spotify as spotify
import generator.config as config
import generator.modifier.sort as sort
import tekore as tk
import logging
import pathlib


scopes = tk.scope.read + tk.scope.write


logger = logging.getLogger('generator')


prevent_uploading = False
list_songs = False
verbose = False


def setup(sp):
    instruction.setup()
    modifier.setup()
    # We want user playlists to have priority in search
    spotify.get_user_playlists(sp)


def get_default_token(manager: config.ConfigManager):
    tk.client_id_var = manager['client_id']
    tk.client_secret_var = manager['client_secret']
    tk.redirect_uri_var = manager['redirect_uri']
    tk.user_refresh_var = manager['saved_token']

    return tk.request_client_token(tk.client_id_var, tk.client_secret_var)


def sort_playlist(sp, playlist):
    tracks = spotify.get_playlist_tracks(sp, playlist)

    analysis = sp.tracks_audio_features([t.id for t in tracks])
    pair = [(tracks[i], analysis[i]) for i in range(len(tracks))]
    tracks = sort.traveling(pair)
    spotify.replace_all_playlist(sp, playlist, tracks)


def load_playlist(file):
    data = config.config_manager.load_file(file)
    name = data.get('name', None)
    if not name:
        name = pathlib.Path(file).name
    return config.Playlist(data, name)


def run_playlist_file(sp: tk.Spotify, file):
    playlist = load_playlist(file)
    run_playlist(sp, playlist)


def run_playlist(sp: tk.Spotify, playlist):
    songs = playlist.get_songs(sp)
    logger.info('Done with ' + str(len(songs)) + ' songs')


def show_all_help():
    instruction.setup()
    modifier.setup()
    instruction.show_all_help()
    print('-------------')
    modifier.show_all_help()
