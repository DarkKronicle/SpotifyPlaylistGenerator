import generator.config.config_manager as config
import pathlib
import tekore as tk
import generator.spotify as spotify
import generator.instruction as instruction
import generator.modifier as modifier


def set_playlist(sp: tk.Spotify, file, manager):
    playlist = manager.load_playlist(file)
    if not playlist.get('daily', True):
        return

    songs = playlist.get_songs(sp)
    playlist_id = spotify.get_or_create_playlist(sp, playlist['name'])
    spotify.replace_all_playlist(sp, playlist_id, songs)
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

    tk.client_id_var = manager['client_id']
    tk.client_secret_var = manager['client_secret']
    tk.redirect_uri_var = manager['redirect_uri']
    tk.user_refresh_var = manager['saved_token']

    app_token = tk.request_client_token(tk.client_id_var, tk.client_secret_var)

    sp = tk.Spotify(app_token, chunked_on=True)
    sp.token = tk.refresh_user_token(tk.client_id_var, tk.client_secret_var, tk.user_refresh_var)

    # We want to cache user stuff first
    instruction.setup()
    modifier.setup()
    spotify.get_user_playlists(sp)

    for playlist in pathlib.Path('./playlists').glob('**/*.toml'):
        print('Loading playlist ' + str(playlist))
        set_playlist(sp, str(playlist), manager)


if __name__ == '__main__':
    main()
