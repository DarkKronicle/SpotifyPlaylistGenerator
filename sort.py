import pathlib
import tekore as tk
import generator

import argparse
import logging
import generator.spotify as spotify


def get_args():
    parser = argparse.ArgumentParser(description='Generates playlists for a user')
    parser.add_argument('playlist', help='The playlist to sort')
    parser.add_argument('-v', '--verbose', required=False, action='store_true',
                        help='Log more information on what everything does')
    return parser.parse_args()


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

    sp = tk.Spotify(generator.get_default_token(manager), chunked_on=True)
    sp.token = tk.refresh_user_token(tk.client_id_var, tk.client_secret_var, tk.user_refresh_var)

    # We want to cache user stuff first
    generator.setup(sp)

    playlists = spotify.get_user_playlists(sp)
    play = None
    for p in playlists:
        if p.name.lower() == args.playlist.lower():
            play = p
            break
    if play is None:
        generator.logger.info('No playlist found with name ' + args.playlist)
        return
    generator.sort_playlist(sp, play)


if __name__ == '__main__':
    main()
