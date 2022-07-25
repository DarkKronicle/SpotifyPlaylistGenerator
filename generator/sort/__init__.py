from .salesman import traveling
from . import similar
from sklearn.decomposition import PCA


def get_features(audio_data, attributes):
    return [tuple(getattr(a, attr) for attr in attributes) for a in audio_data]


def pca(data):
    pca_obj = PCA(n_components=2)
    return pca_obj.fit_transform(data)
