import logging
import traceback
from typing import Iterable

from sklearn_extra.cluster import KMedoids

import generator
import tekore as tk
import pathlib
import numpy as np


def normalize_np_array(arr: np.array):
    for i in range(arr.shape[1]):
        minimum = arr[:, i].min()
        arr[:, i] = (arr[:, i] - minimum) / (arr[:, i].max() - minimum)


def get_normalize(arr: Iterable) -> Iterable:
    """
    Normalize values from 0-1
    """
    max_element = max(arr)
    min_element = min(arr)
    return ((el - min_element) / (max_element - min_element) for el in arr)


def get_features(audio_data, attributes):
    return [tuple(getattr(a, attr) for attr in attributes) for a in audio_data]


def get_normalized_features(audio_data, attributes) -> np.array:
    features = np.array(get_features(audio_data, attributes))
    normalize_np_array(features)
    return features


def get_best_clusters(data: np.array, *, min_k=2, max_k=10, average=5, max_iter=300) -> np.array:
    average_elbows = np.zeros((max_k - min_k + 1,), dtype=float)
    for a in range(0, average):
        elbows = []
        for i in range(0, max_k - min_k + 1):
            k = i + min_k
            model = KMedoids(n_clusters=k, max_iter=max_iter)
            model.fit(data)
            elbows.append(model.inertia_)

        averaged = list(get_normalize(elbows))
        for i, num in enumerate(averaged):
            average_elbows[i] += num

    average_elbows = average_elbows / average
    prev = average_elbows[1]
    prev_dif = average_elbows[1] - average_elbows[0]
    best_k = 0
    for i in range(1, len(average_elbows)):
        s = average_elbows[i]
        dif = s - prev
        if abs(prev_dif - dif) < 0.05:
            best_k = i + min_k
            break
        prev_dif = dif
        prev = s
    # Get unique cluster values
    model = KMedoids(n_clusters=best_k, max_iter=max_iter)
    model.fit(data)
    predicted_clusters = model.predict(data)
    return predicted_clusters, np.unique(predicted_clusters)


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
