import math

from . import *
import numpy as np
from sklearn.decomposition import PCA

from generator import instruction
from generator import sort


@modifier('audio_sort', sort=3)
def audio_sort_playlist(sp, songs, method: str, reverse: bool = False, **kwargs):
    """
    Sorts a playlist, but using audio analysis (which is slower)

    method (str) - Method of sorting
    reverse (bool) - Reverse the output
    """
    analysis = sp.tracks_audio_features([t.id for t in songs])
    pair = [(songs[i], analysis[i]) for i in range(len(songs))]
    if method == 'bpm':
        return [song[0] for song in sorted(pair, key=lambda s: s[1].tempo, reverse=reverse)]
    if method == 'energy':
        return [song[0] for song in sorted(pair, key=lambda s: s[1].energy, reverse=reverse)]
    if method == 'loudness':
        return [song[0] for song in sorted(pair, key=lambda s: s[1].energy, reverse=reverse)]
    if method == 'danceability':
        return [song[0] for song in sorted(pair, key=lambda s: s[1].danceability, reverse=reverse)]
    if method == 'valence':
        return [song[0] for song in sorted(pair, key=lambda s: s[1].valence, reverse=reverse)]
    if method == 'speechiness':
        return [song[0] for song in sorted(pair, key=lambda s: s[1].speechiness, reverse=reverse)]
    if method == 'acousticness':
        return [song[0] for song in sorted(pair, key=lambda s: s[1].acousticness, reverse=reverse)]
    if method == 'traveling' or method == 'travelling':
        return sort.traveling(pair, **kwargs)
    return songs


def get_closest(song_pos, input_songs_pca):
    closest_index = 0
    closest_margin = -1
    for i in range(len(input_songs_pca)):
        s_pos = input_songs_pca[i]
        dist = math.sqrt(math.pow(song_pos[0] - s_pos[0], 2) + math.pow(song_pos[1] - s_pos[1], 2))
        if dist < closest_margin or closest_margin < 0:
            closest_index = i
            closest_margin = dist
    return closest_index


@modifier('sort_together')
def advanced_sort(sp, songs, tracks, **kwargs):
    attributes = kwargs.get('attributes',
                            ['energy', 'valence'])

    tracks = instruction.run(sp, tracks)
    top_analysis = sp.tracks_audio_features([t.id for t in tracks])
    analysis = list(sp.tracks_audio_features([t.id for t in songs]))
    pairs = sort.traveling([(tracks[i], top_analysis[i]) for i in range(len(top_analysis))], return_tuple=True)
    tracks, top_analysis = list(zip(*pairs))

    features = [tuple(getattr(a, attr) for attr in attributes) for a in list(top_analysis) + analysis]
    data = np.array(features)

    pca = PCA(n_components=2)
    data = pca.fit_transform(data)
    top_pca = data[:len(tracks)]
    song_pca = data[len(tracks):]

    final = {}

    for i in range(len(songs)):
        closest = get_closest(song_pca[i], top_pca)
        l = final.get(closest, None)
        if l is None:
            final[closest] = []
            l = final.get(closest)
        l.append(songs[i])

    new_songs = []
    for t_index, song_list in final.items():
        new_songs.extend([tracks[t_index], *song_list])
    return new_songs


@modifier('sort', sort=3)
def sort_playlist(sp, songs, method: str, reverse: bool = False, **kwargs):
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

