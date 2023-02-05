import pathlib
from pprint import pprint

import httpx
import tekore as tk
import generator

import argparse
import sys
import logging
import asyncio
import platform

from generator.parser.script_parser import ScriptParser
from generator.spotify import spotify_instruction


def get_args():
    parser = argparse.ArgumentParser(description='Generates playlists for a user')
    parser.add_argument('-s', '--spotify', required=False, action='store_true',
                        help='Generate Spotify playlists')
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
    if not args.playlist and not args.all and not args.show_docs and not args.spotify:
        parser.error('You have to either specify a playlist, all, or spotify.')
    return args


async def async_main(sp, args):
    # We want to cache user stuff first
    await generator.setup(sp)

    if args.spotify:
        playlists = await spotify_instruction.get_user_instruction_playlists(sp)
        for p in playlists:
            await spotify_instruction.generate_user_playlist(sp, p)

    if args.all:
        for playlist in pathlib.Path('./playlists').glob('**/*.toml'):
            await generator.run_playlist_file(sp, str(playlist))

    if args.playlist:
        file = str(args.playlist)
        if not file.startswith('playlists/'):
            file = 'playlists/' + file
        if not file.endswith('.toml'):
            file = file + '.toml'
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

    trans = httpx.AsyncHTTPTransport(retries=3)
    client = httpx.AsyncClient(timeout=120, transport=trans)
    sender = tk.CachingSender(256, tk.AsyncSender(client=client))

    sp = tk.Spotify(generator.get_default_token(manager), sender=sender, chunked_on=True)
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


def script_parser():
    parser = ScriptParser('''
    Top{top_tracks|term=short|amount=50|,|top_tracks|term=medium|amount=20}
    ''')
    print(str(parser.parse()))


if __name__ == '__main__':
    main()
