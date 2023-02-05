import logging
import traceback

import generator
import tekore as tk
import pathlib


async def sort_playlist(sp, playlist):
    tracks = await generator.spotify.get_playlist_tracks(sp, playlist)

    analysis = await sp.tracks_audio_features([t.id for t in tracks])
    pair = [(tracks[i], analysis[i]) for i in range(len(tracks))]
    tracks = generator.sort.traveling(pair)
    await generator.spotify.replace_all_playlist(sp, playlist, tracks)


def load_playlist(file):
    data = generator.config.load_file(file)
    name = data.get('name', None)
    if not name:
        name = pathlib.Path(file).name
    return generator.config.Playlist(data, name)


async def run_playlist_file(sp: tk.Spotify, file):
    try:
        playlist = load_playlist(file)
    except:
        logging.warning('Could not load file: {0}'.format(file))
        traceback.print_exc()
        return
    await run_playlist(sp, playlist)


async def run_playlist(sp: tk.Spotify, playlist):
    try:
        songs = await playlist.get_songs(sp)
        if not generator.silent:
            generator.logger.info('Done with ' + str(len(songs)) + ' songs')
    except:
        logging.warning('Error handling playlist file: {0}'.format(playlist))
        traceback.print_exc()
        return


def show_all_help():
    generator.instruction.show_all_help()
    print('-------------')
    generator.modifier.show_all_help()


class _ModifierDefault:

    def __init__(self):
        pass

    def __eq__(self, o: object) -> bool:
        return isinstance(o, _ModifierDefault)

    def __str__(self):
        return "MODIFIER DEFAULT"

    def __repr__(self):
        return "MODIFIER DEFAULT"


DEFAULT_VALUE = _ModifierDefault()

