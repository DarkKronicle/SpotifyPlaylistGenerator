import generator
import tekore as tk
import pathlib


def setup(sp):
    # We want user playlists to have priority in search
    generator.spotify.get_user_playlists(sp)


def get_default_token(manager):
    tk.client_id_var = manager['client_id']
    tk.client_secret_var = manager['client_secret']
    tk.redirect_uri_var = manager['redirect_uri']
    tk.user_refresh_var = manager['saved_token']

    return tk.request_client_token(tk.client_id_var, tk.client_secret_var)


def sort_playlist(sp, playlist):
    tracks = generator.spotify.get_playlist_tracks(sp, playlist)

    analysis = sp.tracks_audio_features([t.id for t in tracks])
    pair = [(tracks[i], analysis[i]) for i in range(len(tracks))]
    tracks = generator.sort.traveling(pair)
    generator.spotify.replace_all_playlist(sp, playlist, tracks)


def load_playlist(file):
    data = generator.config.load_file(file)
    name = data.get('name', None)
    if not name:
        name = pathlib.Path(file).name
    return generator.config.Playlist(data, name)


def run_playlist_file(sp: tk.Spotify, file):
    playlist = load_playlist(file)
    run_playlist(sp, playlist)


def run_playlist(sp: tk.Spotify, playlist):
    songs = playlist.get_songs(sp)
    generator.logger.info('Done with ' + str(len(songs)) + ' songs')


def show_all_help():
    generator.instruction.show_all_help()
    print('-------------')
    generator.modifier.show_all_help()
