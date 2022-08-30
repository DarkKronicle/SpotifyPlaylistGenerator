import logging
import math

from . import instruction
import random
import generator
from generator import sort
import tekore as tk


@instruction('recommendations')
async def recommendations(sp: tk.Spotify, tracks: list[tk.model.Track] = None, artists: list[tk.model.Artist] = None, genres: list[str] = None, **attributes) -> list[tk.model.Track]:
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
    i = 0
    while True:
        i += 1
        try:
            recs = (await sp.recommendations(
                artist_ids=[a.id for a in artists],
                genres=genres,
                track_ids=[t.id for t in tracks],
                **attributes
            )).tracks
        except Exception as e:
            if i < 5:
                logging.info('Recommendations failed, trying again.')
                continue
            else:
                raise e
        break

    if generator.verbose:
        generator.logger.info('Fetched {0} recommendations with extra settings {1}'.format(len(recs), attributes))
    return recs


@instruction('generate')
async def playlist_generate(sp: tk.Spotify, tracks: list[tk.model.Track], amount: int = 50, random_sample: bool = True, mix_same=False, **attributes) -> list[tk.model.Track]:
    """
    Generates many tracks from specified tracks. Can be used to generate a playlist from a playlist

    tracks (list of tracks) - Tracks to generate from
    amount (int) - Amount of tracks to return
    random_sample (bool) - If it should randomly select the tracks that it's seed is
    """
    songs = []
    total = len(tracks)
    iters = math.ceil(len(tracks) / 5)
    analysis = await sp.tracks_audio_features([t.id for t in tracks])
    pair = [(tracks[i], analysis[i]) for i in range(len(tracks))]
    if len(tracks) < 50:
        tracks = sort.traveling(pair)
    else:
        tracks = sort.traveling(pair, attributes=['valence'])

    save_tracks = []
    if mix_same:
        target = math.ceil(math.sqrt(4 * len(tracks)) - 5)
        if target >= 1:
            save_tracks = random.sample(tracks, target)
            amount = amount - len(save_tracks)
    if random_sample:
        random.shuffle(tracks)
    for i in range(iters):
        cut = min(5, len(tracks))
        lim = math.floor(amount / iters) if iters == i + 1 else math.ceil(amount / iters)
        num = 0
        while True:
            num += 1
            cur_track = [t.id for t in tracks[:cut]]
            try:
                songs.extend((await sp.recommendations(limit=lim, track_ids=cur_track, **attributes)).tracks)
                break
            except Exception as e:
                if num < 5:
                    # Some reason it just sometimes hates it more than it needs to
                    logging.info('Generation instruction failed, trying again')
                    random.shuffle(cur_track)
                    continue
                else:
                    logging.warning("Couldn't get generation to work, skipping")
                    break
        tracks = tracks[cut:]
    if generator.verbose:
        generator.logger.info('Generated {0} tracks from {1} tracks with {2} requests'.format(len(songs), total, iters))
    return songs + save_tracks

