import pathlib
import tekore as tk
import generator

import argparse
import sys
import logging
import asyncio
import platform


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
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help='Log more information on what everything does')
    parser.add_argument('--prompt', required=False, action='store_true',
                        help='Prompt for new token')
    if len(sys.argv) <= 1:
        parser.error('No arguments provided.')
    args = parser.parse_args()
    if not args.playlist and not args.all and not args.show_docs:
        parser.error('You have to either specify a playlist or all.')
    return args


async def async_main(sp, args):
    # We want to cache user stuff first
    await generator.setup(sp)

    if args.all:
        collected = []
        for playlist in pathlib.Path('./playlists').glob('**/*.toml'):
            await generator.run_playlist_file(sp, str(playlist))

    if args.playlist:
        file = str(args.playlist)
        if not file.startswith('playlists/'):
            file = 'playlists/' + file
        await generator.run_playlist_file(sp, file)


def main():
    args = get_args()

    if args.show_docs:
        generator.show_all_help()
        return

    if args.verbose:
        generator.verbose = True

    logging.basicConfig(
        level='INFO',
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M:%S'
    )

    if args.no_upload:
        generator.prevent_uploading = True

    manager = generator.config.ConfigManager()

    sp = tk.Spotify(generator.get_default_token(manager), chunked_on=True, asynchronous=True)
    if args.prompt:
        sp.token = tk.prompt_for_user_token(
            tk.client_id_var, tk.client_secret_var, tk.redirect_uri_var, scope=generator.scopes,
        )
    else:
        sp.token = tk.refresh_user_token(tk.client_id_var, tk.client_secret_var, tk.user_refresh_var)

    if platform.system() == 'Windows':
        # Windows be like
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(async_main(sp, args))


if __name__ == '__main__':
    main()
