import logging
import math
import statistics

from . import instruction
import random
import generator
from generator import sort
import tekore as tk

from ..context import Context
from ..parser.instruction_holder import Instructions
import numpy as np


@instruction('recommendations', aliases=['recs'])
async def recommendations(ctx: Context, tracks: list[tk.model.Track] = None, artists: list[tk.model.Artist] = None, limit: int = 20, pool_size: int = 20, genres: list[str] = None, **attributes) -> list[tk.model.Track]:
    """
    Get recommendations based on some seeds (maximum 5 of all combined, with at least one)

    You can specify tracks/artists as an instruction that returns the required argument

    tracks (list[str], or instruction) - Tracks for seed
    artists (list[str], or instruction) - Artists for seed
    genres (list[str], or instruction) - Genres for seed
    limit (int) - Amount of songs to get
    pool_size (int) - The amount of recommendations to get for a group, and then randomly select for the limit
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
            recs = (await ctx.sp.recommendations(
                artist_ids=[a.id for a in artists],
                genres=genres,
                limit=pool_size if pool_size > limit else limit,
                track_ids=[t.id for t in tracks],
                **attributes
            )).tracks
            if len(recs) > limit:
                recs = random.sample(recs, limit)
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


def get_prob_list(analysis: list):
    return [np.percentile(analysis, 25), np.percentile(analysis, 50), np.percentile(analysis, 50), np.percentile(analysis, 75)]


@instruction('generate', aliases=['gen'])
async def playlist_generate(ctx: Context, tracks: list[tk.model.Track], amount: int = 50, random_sample: bool = True, mix_same=False, pool_size: int = 15, **attributes) -> list[tk.model.Track]:
    """
    Generates many tracks from specified tracks. Can be used to generate a playlist from a playlist

    tracks (list of tracks) - Tracks to generate from
    amount (int) - Amount of tracks to return
    random_sample (bool) - If it should randomly select the tracks that it's seed is
    pool_size (int) - The amount of recommendations to get for a group, and then randomly select for the limit
    """
    songs = []
    if isinstance(tracks, Instructions):
        tracks = await tracks.run(ctx)
    total = len(tracks)
    iters = math.ceil(len(tracks) / 5)
    analysis: list[tk.model.AudioFeatures] = await ctx.sp.tracks_audio_features([t.id for t in tracks])
    pair = [(tracks[i], analysis[i]) for i in range(len(tracks))]
    if not random_sample:
        if len(tracks) < 50:
            tracks = sort.traveling(pair)
        else:
            tracks = sort.traveling(pair, attributes=['valence'])

    targets = {
        'target_valence': get_prob_list([a.valence for a in analysis]),
        'target_energy': get_prob_list([a.energy for a in analysis]),
        'target_instrumentalness': get_prob_list([a.instrumentalness for a in analysis]),
    }
    #
    # for k in list(attributes.keys()):
    #     if 'valence' in k:
    #         del targets['target_valence']
    #     if 'energy' in k:
    #         del targets['target_energy']
    #     if 'instrumentalness' in k:
    #         del targets['target_instrumentalness']

    save_tracks = []
    if mix_same:
        save_tracks = tracks
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
                if "limit" in attributes:
                    attributes.pop("limit")
                limit = pool_size if pool_size > lim else lim
                temp_targets = {k: random.choice(v) for k, v in targets.items()}
                tracks = (await ctx.sp.recommendations(track_ids=cur_track, limit=limit, **attributes, **temp_targets)).tracks
                if len(tracks) <= lim:
                    songs.extend(tracks)
                else:
                    songs.extend(random.sample(tracks, lim))
                break
            except Exception as e:
                print("AAAA")
                print(e)
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

