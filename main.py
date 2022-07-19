import pathlib
import tekore as tk
import generator

import argparse
import sys
import logging


def get_args():
    parser = argparse.ArgumentParser(description='Generates playlists for a user')
    parser.add_argument('-a', '--all', required=False, action='store_true',
                        help='Generate all playlists')
    parser.add_argument('--no-upload', required=False, action='store_true',
                        help='Prevents playlists from being modified')
    parser.add_argument('-p', '--playlist', required=False,
                        help='Generate a specific playlist')
    parser.add_argument('--show-docs', required=False, action='store_true',
                        help='Prints out all instructions and modifiers')
    if len(sys.argv) <= 1:
        parser.error('No arguments provided.')
    args = parser.parse_args()
    if not args.playlist and not args.all and not args.show_docs:
        parser.error('You have to either specify a playlist or all.')
    return args


def main():
    args = get_args()

    if args.show_docs:
        generator.show_all_help()
        return

    logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M:%S'
    )

    if args.no_upload:
        generator.prevent_uploading = True

    manager = generator.config.ConfigManager()

    sp = tk.Spotify(generator.get_default_token(manager), chunked_on=True)
    sp.token = tk.refresh_user_token(tk.client_id_var, tk.client_secret_var, tk.user_refresh_var)

    # We want to cache user stuff first
    generator.setup(sp)

    if args.all:
        for playlist in pathlib.Path('./playlists').glob('**/*.toml'):
            generator.run_playlist_file(sp, str(playlist))

    if args.playlist:
        file = str(args.playlist)
        if not file.startswith('playlists/'):
            file = 'playlists/' + file
        generator.run_playlist_file(sp, file)


if __name__ == '__main__':
    main()
