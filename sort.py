import asyncio

import httpx
import tekore as tk
import generator

import argparse
import logging
import generator.spotify as spotify


def get_args():
    parser = argparse.ArgumentParser(description='Generates playlists for a user')
    parser.add_argument('playlist', help='The playlist to sort')
    parser.add_argument('-s', '--save', required=False,
                        help='Save to a specific playlist')
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help='Log more information on what everything does')
    parser.add_argument('-p', '--prompt', required=False, action='store_true',
                        help='Prompt for new token')
    parser.add_argument('-e', '--export', required=False, type=str,
                        help='Sort and export to another playlist')
    parser.add_argument('-c', '--chunk', required=False, type=int,
                        help='Chunk size for sorting')
    parser.add_argument('-r', '--random', required=False, action='store_true',
                        help='Random offset for sorting')
    return parser.parse_args()


async def async_main(sp, args):
    # We want to cache user stuff first
    await generator.setup(sp)

    playlists = await spotify.get_user_playlists(sp)
    play = await spotify.get_playlist(sp, args.playlist)
    if play is None:
        generator.logger.warn('No playlist found with name ' + args.playlist)
        return
    if not args.export and play.owner.id != (await sp.current_user()).id:
        generator.logger.warn("To sort a playlist that isn't yours you have to provide the --export argument!")
        return
    kwargs = {}
    if args.chunk:
        kwargs['chunks'] = args.chunk
    if args.random:
        kwargs['random_offset'] = args.random
    await generator.sort_playlist(sp, play)


def main():
    args = get_args()

    if args.verbose:
        generator.verbose = True

    logging.basicConfig(
        level='INFO',
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
    else:
        sp.token = tk.refresh_user_token(tk.client_id_var, tk.client_secret_var, tk.user_refresh_var)

    asyncio.run(async_main(sp, args))


if __name__ == '__main__':
    main()
