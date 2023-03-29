from . import pca
import numpy as np

from .. import get_normalized_features, get_best_clusters


def get_groups(tracks, analysis):
    attributes = ['energy', 'instrumentalness', 'loudness', 'valence']
    data = get_normalized_features(analysis, attributes)
    data = pca(data)
    data = data.copy(order='C')

    tracks = np.array(tracks)
    analysis = np.array(analysis)

    predicted_clusters, unique_clusters = get_best_clusters(data)

    # Sort by distance so that if ran again we get similar results
    clustered_data = []
    dists = []
    bottom = np.array([-1, -1])
    for cluster in unique_clusters:
        row_ix = np.where(predicted_clusters == cluster)
        mean = data[row_ix].mean(axis=0)
        dists.append(np.linalg.norm(mean - bottom))
        clustered_data.append((tracks[row_ix], analysis[row_ix]))
    new_clustered = []
    dists = np.array(dists)
    for index in np.argsort(dists):
        new_clustered.append(clustered_data[index])

    return new_clustered
