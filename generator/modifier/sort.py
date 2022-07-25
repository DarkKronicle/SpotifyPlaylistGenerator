from . import *

from generator import sort


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

