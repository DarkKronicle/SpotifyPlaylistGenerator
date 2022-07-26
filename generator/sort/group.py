from . import get_features, pca
import numpy as np
from sklearn.cluster import Birch


def get_groups(tracks, analysis, n=-1):
    attributes = ['energy', 'valence', 'acousticness']
    data = np.array(get_features(analysis, attributes))
    for i, col in enumerate(attributes):
        minimum = data[:, i].min()
        data[:, i] = (data[:, i] - minimum) / (data[:, i].max() - minimum)
    data = pca(data)
    data = data.copy(order='C')

    tracks = np.array(tracks)
    analysis = np.array(analysis)

    model = Birch(threshold=.27, n_clusters=n if n > 0 else None)
    model.fit(data)
    predicted_clusters = model.predict(data)
    # Get unique cluster values
    clusters = np.unique(predicted_clusters)

    clustered_data = []
    for cluster in clusters:
        row_ix = np.where(predicted_clusters == cluster)
        clustered_data.append((tracks[row_ix], analysis[row_ix]))

    return clustered_data
