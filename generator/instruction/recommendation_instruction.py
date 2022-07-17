from . import *


@instruction('recommendations')
def recommendations(sp: tk.Spotify, tracks: list[tk.model.Track] = None, artists: list[tk.model.Artist] = None, genres: list[str] = None, **attributes) -> list[tk.model.Track]:
    if artists is None:
        artists = []
    if tracks is None:
        tracks = []
    return sp.recommendations(
        artist_ids=[a.id for a in artists],
        genres=genres,
        track_ids=[t.id for t in tracks],
        **attributes
    ).tracks
