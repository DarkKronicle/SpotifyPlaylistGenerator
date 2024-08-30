import traceback

import httpx
import tekore as tk
from tqdm import tqdm

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
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help='Log more information on what everything does')
    parser.add_argument('--prompt', required=False, action='store_true',
                        help='Prompt for new token')
    args = parser.parse_args()
    return args


async def async_main(sp: tk.Spotify, args):
    # We want to cache user stuff first
    playlists: list[tk.model.Playlist] = await generator.spotify.get_user_playlists(sp)
    user: tk.model.PrivateUser = await sp.current_user()
    to_cover = []
    for playlist in playlists:
        if playlist.owner.id != user.id:
            # Don't own this one
            continue
        # if any(c.isdigit() for c in playlist.name):
            # continue
        if playlist.name.startswith("Mix"):
            to_cover.append(playlist)
            continue
        if playlist.name[0] == '%':
            continue
        if playlist.name in ('Electro', 'Peace', 'Math', 'Ambience'):
            continue
        if playlist.name != 'The Dark Playlist of Doom':
            continue
    for playlist in tqdm(to_cover):
        print(playlist.name)
        try:
            tracks = await generator.spotify.get_playlist_tracks(sp, playlist)
            if len(tracks) < 5:
                continue
            await generator.spotify.generate_cover(sp, playlist, tracks)
        except Exception as e:
            traceback.print_exc()
            print(e)


def main():
    args = get_args()

    if args.verbose:
        generator.verbose = True

    logging.basicConfig(
        level='INFO' if args.verbose else 'WARNING',
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M:%S'
    )

    manager = generator.config.ConfigManager()

    trans = httpx.AsyncHTTPTransport(retries=3)
    client = httpx.AsyncClient(timeout=120, transport=trans)
    sender = tk.CachingSender(256, tk.AsyncSender(client=client))

    sp = tk.Spotify(generator.get_default_token(manager), sender=sender, chunked_on=True)
    if args.prompt:
        sp.token = tk.prompt_for_user_token(
            tk.client_id_var, tk.client_secret_var, tk.redirect_uri_var, scope=generator.scopes,
        )
        print(sp.token.refresh_token)
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
