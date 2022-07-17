import generator.config.config_manager as config
import pathlib
import tekore as tk
import generator.spotify as spotify
import generator.instruction as instruction
import importlib


def set_playlist(sp: tk.Spotify, file, manager):
    playlist = manager.load_playlist(file)
    if not playlist.get('daily', True):
        return

    songs = []
    for data in playlist['instructions']:
        songs.extend(instruction.run(sp, data))

    playlists = spotify.get_user_playlists(sp)
    name = playlist['name']
    playlist_id = None
    for p in playlists:
        if p.name.lower() == name.lower():
            playlist_id = p.id
            break

    if playlist_id is None:
        playlist_id = sp.playlist_create(sp.current_user.id).id

    sp.playlist_replace(playlist_id, [t.uri for t in songs[:min(100, len(songs))]])

    if len(songs) > 100:
        for i in range(len(songs) // 100 - 1):
            max_num = min((i + 1) * 100, len(songs))
            sp.playlist_add(playlist_id, [t.uri for t in songs[i * 100:max_num]])

    print('Done with ' + str(len(songs)) + ' songs')


def main():
    manager = config.ConfigManager()

    scopes = {
        tk.scope.user_library_read,
        tk.scope.user_top_read,
        tk.scope.playlist_read_collaborative,
        tk.scope.playlist_read_private,
        tk.scope.playlist_modify_private,
        tk.scope.playlist_modify_public,
    }

    for file in list(pathlib.Path('generator/instruction').glob('**/*.py')):
        importlib.import_module('' + str(file).replace('\\', '.').replace('/', '.')[:-3], package=__package__)

    tk.client_id_var = manager['client_id']
    tk.client_secret_var = manager['client_secret']
    tk.redirect_uri_var = manager['redirect_uri']
    tk.user_refresh_var = manager['saved_token']

    app_token = tk.request_client_token(tk.client_id_var, tk.client_secret_var)

    sp = tk.Spotify(app_token, chunked_on=True)
    sp.token = tk.refresh_user_token(tk.client_id_var, tk.client_secret_var, tk.user_refresh_var)

    for playlist in pathlib.Path('./playlists').glob('**/*.toml'):
        print('Loading playlist ' + str(playlist))
        set_playlist(sp, str(playlist), manager)


if __name__ == '__main__':
    main()
