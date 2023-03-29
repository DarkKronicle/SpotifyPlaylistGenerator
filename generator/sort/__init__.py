from .salesman import traveling
from . import similar
from sklearn.decomposition import PCA


def pca(data):
    pca_obj = PCA(n_components=2)
    return pca_obj.fit_transform(data)
