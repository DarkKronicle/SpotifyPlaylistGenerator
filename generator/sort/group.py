import math

from sklearn.metrics import silhouette_score

from . import get_features, pca
import numpy as np
from sklearn.cluster import Birch
from sklearn_extra.cluster import KMedoids


def get_groups(tracks, analysis, n=-1):
    attributes = ['energy', 'instrumentalness', 'loudness', 'valence']
    data = np.array(get_features(analysis, attributes))
    for i, col in enumerate(attributes):
        minimum = data[:, i].min()
        data[:, i] = (data[:, i] - minimum) / (data[:, i].max() - minimum)
    data = pca(data)
    data = data.copy(order='C')

    tracks = np.array(tracks)
    analysis = np.array(analysis)

    # model = Birch(threshold=.27, n_clusters=n if n > 0 else None)
    # model.fit(data)
    silhouettes = []
    unique_clusters = []
    for k in range(2, 10 + 1):
        model = KMedoids(n_clusters=k)
        model.fit(data)
        predicted_clusters = model.predict(data)
        silhouettes.append(model.inertia_)
        unique_clusters.append(predicted_clusters)

    min_s = min(silhouettes)
    max_s = max(silhouettes)
    silhouettes = [(s - min_s) / (max_s - min_s) for s in silhouettes]
    prev = silhouettes[1]
    prev_dif = silhouettes[1] - silhouettes[0]
    best_k = 0
    for i in range(1, len(silhouettes)):
        s = silhouettes[i]
        dif = s - prev
        if abs(prev_dif - dif) < 0.08:
            best_k = i - 1
            break
        prev_dif = dif
        prev = s
    predicted_clusters = unique_clusters[best_k]
    # Get unique cluster values
    clusters = np.unique(predicted_clusters)

    # Sort by distance so that if ran again we get similar results
    clustered_data = []
    dists = []
    bottom = np.array([-1, -1])
    for cluster in clusters:
        row_ix = np.where(predicted_clusters == cluster)
        mean = data[row_ix].mean(axis=0)
        dists.append(np.linalg.norm(mean - bottom))
        clustered_data.append((tracks[row_ix], analysis[row_ix]))
    new_clustered = []
    dists = np.array(dists)
    for index in np.argsort(dists):
        new_clustered.append(clustered_data[index])

    return new_clustered
