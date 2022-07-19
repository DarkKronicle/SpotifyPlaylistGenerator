from . import *


@instruction('recommendations')
def recommendations(sp: tk.Spotify, tracks: list[tk.model.Track] = None, artists: list[tk.model.Artist] = None, genres: list[str] = None, **attributes) -> list[tk.model.Track]:
    """
    Get recommendations based on some seeds (maximum 5 of all combined, with at least one)

    You can specify tracks/artists as an instruction that returns the required argument

    tracks (list[str], or instruction) - Tracks for seed
    artists (list[str], or instruction) - Artists for seed
    genres (list[str], or instruction) - Genres for seed
    **attributes - Anything from https://developer.spotify.com/documentation/web-api/reference/#/operations/get-recommendations
                 - (Should be referenced in key/pair)
    """
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
