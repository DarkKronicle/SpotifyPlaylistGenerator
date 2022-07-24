import math

from . import *
import random
import generator
from generator import sort


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
    recs = sp.recommendations(
        artist_ids=[a.id for a in artists],
        genres=genres,
        track_ids=[t.id for t in tracks],
        **attributes
    ).tracks
    if generator.verbose:
        generator.logger.info('Fetched {0} recommendations with extra settings {1}'.format(len(recs), attributes))
    return recs


@instruction('generate')
def playlist_generate(sp: tk.Spotify, tracks: list[tk.model.Track], amount: int = 50, random_sample: bool = True, **attributes) -> list[tk.model.Track]:
    """
    Generates many tracks from specified tracks. Can be used to generate a playlist from a playlist

    tracks (list of tracks) - Tracks to generate from
    amount (int) - Amount of tracks to return
    random_sample (bool) - If it should randomly select the tracks that it's seed is
    """
    songs = []
    total = len(tracks)
    iters = math.ceil(len(tracks) / 5)
    analysis = sp.tracks_audio_features([t.id for t in tracks])
    pair = [(tracks[i], analysis[i]) for i in range(len(tracks))]
    tracks = sort.traveling(pair)
    if random_sample:
        random.shuffle(tracks)
    for i in range(iters):
        cut = min(5, len(tracks))
        lim = math.floor(amount / iters) if iters == i + 1 else math.ceil(amount / iters)
        songs.extend(sp.recommendations(limit=lim, track_ids=[t.id for t in tracks[:cut]], **attributes).tracks)
        tracks = tracks[cut:]
    if generator.verbose:
        generator.logger.info('Generated {0} tracks from {1} tracks with {2} requests'.format(len(songs), total, iters))
    return songs

