import generator
from scipy.spatial.distance import pdist, squareform
import time
from itertools import zip_longest
import random
import numpy as np
from sklearn.decomposition import PCA
import math


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


def _traveling_two(pairs, attributes, **kwargs):
    now = math.ceil(time.time() * 1000)
    if generator.verbose:
        generator.logger.info('Starting traveling salesman... this may take a minute')
    songs, analysis = list(zip(*pairs))
    features = [tuple(getattr(a, attr) for attr in attributes) for a in analysis]
    data = np.array(features)

    for i, col in enumerate(attributes):
        minimum = data[:, i].min()
        if data[:, i].max() == minimum:
            data[:, i] = 0
            continue
        data[:, i] = (data[:, i] - minimum) / (data[:, i].max() - minimum)
    data[np.isnan(data)] = 0

    pca = PCA(n_components=2)
    data = pca.fit_transform(data)

    distances = squareform(pdist(data))
    route = two_opt(distances, tolerance=kwargs.get('tolerance', 0))

    route_dist = distances[route[1:], route[:-1]]
    worst = np.argmax(route_dist)
    new_route = np.concatenate((route[worst + 1:], route[1:worst + 1]))

    if generator.verbose:
        generator.logger.info('Done in {0} seconds'.format((math.ceil(time.time() * 1000) - now) / 1000))

    # Reorder tracks
    return [(songs[i], analysis[i]) for i in new_route]


def _traveling_one(pairs, attribute, **kwargs):
    # Create a loop since it's only 1d
    pairs = sorted(pairs, key=lambda t: getattr(t[1], attribute))
    return pairs[::2] + list(reversed(pairs[1::2]))


def _traveling_impl(pairs, attributes, **kwargs):
    if len(attributes) == 1:
        return _traveling_one(pairs, attributes[0], **kwargs)
    return _traveling_two(pairs, attributes, **kwargs)


def traveling(pairs, return_tuple=False, **kwargs):
    if len(pairs) < 3:
        if return_tuple:
            return pairs
        return [p[0] for p in pairs]
    # Code by https://dev.to/felixhilden/smart-playlist-shuffle-using-travelling-salesman-58i1 (author of Tekore)
    attributes = kwargs.pop('attributes', ['acousticness', 'energy', 'instrumentalness', 'loudness', 'speechiness', 'valence'])
    new_pairs = _traveling_impl(pairs, attributes, **kwargs)
    chunk_size = kwargs.get('chunks', -1)
    if chunk_size > 0:
        pairs_chunked = []
        groups = list(zip_longest(*[iter(new_pairs)] * chunk_size))
        for group_songs in groups:
            group_songs = list(filter(lambda p: p is not None, group_songs))
            if len(group_songs) < 3:
                pairs_chunked.extend(group_songs)
                continue
            pairs_chunked.extend(_traveling_impl(group_songs, attributes, **kwargs))
        new_pairs = pairs_chunked

    if kwargs.get('random_offset', True):
        new_pairs = list(np.roll(np.array(new_pairs), random.randint(0, len(new_pairs))))

    if return_tuple:
        return new_pairs
    return [p[0] for p in new_pairs]
