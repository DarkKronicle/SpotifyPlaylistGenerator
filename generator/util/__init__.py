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
    playlist = load_playlist(file)
    await run_playlist(sp, playlist)


async def run_playlist(sp: tk.Spotify, playlist):
    songs = await playlist.get_songs(sp)
    if not generator.silent:
        generator.logger.info('Done with ' + str(len(songs)) + ' songs')


def show_all_help():
    generator.instruction.show_all_help()
    print('-------------')
    generator.modifier.show_all_help()
