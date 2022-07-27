from . import *

import generator
from generator import sort
from generator.sort import group
from generator import spotify
from generator import instruction as inst


@modifier('audio_sort', sort=3)
async def audio_sort_playlist(sp, songs, method: str, reverse: bool = False, **kwargs):
    """
    Sorts a playlist, but using audio analysis (which is slower)

    method (str) - Method of sorting
    reverse (bool) - Reverse the output
    """
    analysis = await sp.tracks_audio_features([t.id for t in songs])
    pair = [(songs[i], analysis[i]) for i in range(len(songs))]
    if method in ('tempo', 'energy', 'loudness', 'danceability', 'valence', 'speechiness', 'acousticness'):
        return [song[0] for song in sorted(pair, key=lambda s: getattr(s[1], method), reverse=reverse)]
    if method == 'traveling' or method == 'travelling':
        return sort.traveling(pair, **kwargs)
    return songs


@modifier('sort', sort=3)
async def sort_playlist(sp, songs, method: str, reverse: bool = False, **kwargs):
    """
    Sorts a playlist

    method (str) - Method of sorting
    reverse (bool) - Reverse the output
    """
    if method == 'alphabetical':
        return sorted(songs, key=lambda s: s.name, reverse=reverse)
    if method == 'duration':
        return sorted(songs, key=lambda s: s.duration_ms, reverse=reverse)
    if method == 'album':
        return sorted(songs, key=lambda s: (s.album.name, s.name), reverse=reverse)
    if method == 'artist':
        return sorted(songs, key=lambda s: (s.album.artists[0].name, s.album.name, s.name), reverse=reverse)
    return songs


@modifier('separate')
async def groups(sp, songs, instruction: dict, title: str = 'Mix {0}', n=-1, **modifiers):
    analysis = await sp.tracks_audio_features([t.id for t in songs])
    if n > 10:
        n = 10
    clusters = group.get_groups(songs, analysis, n=n)

    for i, cluster in enumerate(clusters):
        if i > 10:
            generator.logger.info('Woah, way more than 10!')
            return songs
        cluster_songs = await inst.run(sp, dict(instruction), tracks=list(cluster[0]))
        if sort is not None:
            cluster_songs = await run_modifiers(sp, cluster_songs, modifiers)
        if generator.prevent_uploading:
            if not generator.silent:
                generator.logger.info(
                    'Uploading songs for ' + title.format(i) + ' was skipped because prevent_uploading is on')
            continue
        playlist = await spotify.get_or_create_playlist(sp, title.format(i + 1))
        await spotify.replace_all_playlist(sp, playlist, cluster_songs)
        if generator.verbose:
            generator.logger.info('Uploaded {0} songs to {1} (id {2})'.format(len(songs), playlist.name, playlist.id))
    return songs


