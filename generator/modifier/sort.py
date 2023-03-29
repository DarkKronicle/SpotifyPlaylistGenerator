import random

from . import *

import generator
from generator import sort, DEFAULT_VALUE
from generator.sort import group
from generator import spotify
from generator import instruction as inst
from .basic import clear_duplicates
from ..context import Context


@modifier('audio_sort', sort=3)
async def audio_sort_playlist(ctx: Context, songs, method: str, reverse: bool = False, **kwargs):
    """
    Sorts a playlist, but using audio analysis (which is slower)

    method (str) - Method of sorting
    reverse (bool) - Reverse the output
    """
    analysis = await ctx.sp.tracks_audio_features([t.id for t in songs])
    pair = [(songs[i], analysis[i]) for i in range(len(songs))]
    if method in ('tempo', 'energy', 'loudness', 'danceability', 'valence', 'speechiness', 'acousticness'):
        return [song[0] for song in sorted(pair, key=lambda s: getattr(s[1], method), reverse=reverse)]
    if method == 'traveling' or method == 'travelling':
        return sort.traveling(pair, **kwargs)
    return songs


@modifier('random')
async def random_sort(ctx: Context, songs, active: bool):
    if active == DEFAULT_VALUE:
        active = True

    if not active:
        return songs

    random.shuffle(songs)
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
async def groups(ctx: Context, songs, instruction: dict, title: str = 'Mix {0}', n: int = -1, keep_seed=False, **modifiers):
    songs = await clear_duplicates(ctx, songs, True)
    analysis = await ctx.sp.tracks_audio_features([t.id for t in songs])
    if n > 10:
        n = 10
    clusters = group.get_groups(songs, analysis)

    for i, cluster in enumerate(clusters):
        if i > 10:
            generator.logger.info('Woah, way more than 10!')
            return songs
        inner_context = ctx.with_tracks(list(cluster[0]))
        cluster_songs = list(cluster[0])
        cluster_songs: list = await instruction.run(inner_context, tracks=list(cluster_songs))
        if keep_seed:
            cluster_songs.extend(list(cluster[0]))
        if sort is not None:
            cluster_songs = await run_modifiers(ctx, cluster_songs, modifiers)
        if generator.prevent_uploading:
            if not generator.silent:
                generator.logger.info(
                    'Uploading songs for ' + title.format(i + 1) + ' was skipped because prevent_uploading is on')
            continue
        playlist = await spotify.get_or_create_playlist(ctx.sp, title.format(i + 1))
        await spotify.replace_all_playlist(ctx.sp, playlist, cluster_songs)
        try:
            await spotify.generate_cover(ctx.sp, playlist, cluster_songs)
        except Exception as e:
            print(e)

        if generator.verbose:
            generator.logger.info('Uploaded {0} songs to {1} (id {2})'.format(len(songs), playlist.name, playlist.id))
    return songs


