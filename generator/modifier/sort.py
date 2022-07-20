import math

from . import *
import numpy as np
from sklearn.decomposition import PCA
import generator
from scipy.spatial.distance import pdist, squareform
import time


def two_opt(distances: np.ndarray, tolerance: float = 0) -> np.ndarray:
    # Code by https://dev.to/felixhilden/smart-playlist-shuffle-using-travelling-salesman-58i1 (author of Tekore)
    n_nodes = distances.shape[0]
    current_route = np.concatenate((np.arange(n_nodes, dtype=int), [0]))
    candidate = np.zeros(n_nodes + 1, dtype=int)
    best_cost = np.sum(distances[current_route[:-1], current_route[1:]])
    cost = np.inf

    while True:
        for i in range(1, n_nodes):
            for k in range(i + 1, n_nodes + 1):
                candidate[:i] = current_route[:i]
                candidate[i:k] = current_route[k-1:i-1:-1]
                candidate[k:] = current_route[k:]
                cost = np.sum(distances[candidate[:-1], candidate[1:]])
                if cost + tolerance < best_cost:
                    break
            if cost + tolerance < best_cost:
                current_route[:] = candidate
                best_cost = cost
                if generator.verbose:
                    generator.logger.info(f'2-opt: node={i}/{n_nodes}, cost={best_cost}')
                break
        else:
            break
    return current_route


def traveling(pairs, **kwargs):
    generator.logger.info('Starting traveling salesman... this may take a minute')
    now = math.ceil(time.time() * 1000)
    # Code by https://dev.to/felixhilden/smart-playlist-shuffle-using-travelling-salesman-58i1 (author of Tekore)
    attributes = kwargs.get('attributes', ['acousticness', 'danceability', 'energy', 'instrumentalness', 'loudness', 'speechiness', 'tempo', 'valence'])
    if len(attributes) == 1:
        # Create a loop since it's only 1d
        pairs = sorted(pairs, key=lambda t: getattr(t[1], attributes[0]))
        songs = list(list(zip(*pairs))[0])
        new_songs = []
        temp = list(songs[::2])
        for s in temp:
            songs.remove(s)
            new_songs.append(s)
        songs.reverse()
        for s in songs:
            new_songs.append(s)
        return new_songs

    songs, analysis = list(zip(*pairs))
    features = [tuple(getattr(a, attr) for attr in attributes) for a in analysis]
    data = np.array(features)

    for i, col in enumerate(attributes):
        minimum = data[:, i].min()
        data[:, i] = (data[:, i] - minimum) / (data[:, i].max() - minimum)

    pca = PCA(n_components=2)
    data = pca.fit_transform(data)

    distances = squareform(pdist(data))
    route = two_opt(distances, tolerance=kwargs.get('tolerance', 0))

    route_dist = distances[route[1:], route[:-1]]
    worst = np.argmax(route_dist)
    new_route = np.concatenate((route[worst + 1:], route[1:worst + 1]))

    generator.logger.info('Done in {0} seconds'.format((math.ceil(time.time() * 1000) - now) / 1000))

    # Reorder tracks
    return [songs[i] for i in new_route]


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
        return traveling(pair, **kwargs)
    return songs


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

