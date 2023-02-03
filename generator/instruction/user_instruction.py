from . import instruction, Instruction
import random
import generator.spotify as spotify
import generator
import tekore as tk

from ..context import Context


@instruction('saved_tracks', aliases=['liked_tracks', 'liked'])
async def saved_tracks(ctx: Context, sample: int = -1, amount: int = -1, artist: tk.model.Artist = None) -> list[tk.model.Track]:
    """
    Saved tracks

    amount (int) - Amount to get. If -1 it does all
    sample (int) - Random sample to get. If -1 it does all
    artist (string) - Filter artist. This is not required.
    """
    tracks = await spotify.get_saved_tracks(ctx.sp)
    if artist:
        tracks = list(filter(lambda t: artist.name.lower() in [a.name.lower() for a in t.artists], tracks))
    if 0 < amount < len(tracks):
        tracks = tracks[:amount]
    if 0 < sample < amount:
        tracks = random.sample(tracks, sample)
    if generator.verbose:
        generator.logger.info('Fetched {0} songs saved songs'.format(len(tracks)))
    return tracks


@instruction('top_tracks', aliases=['top_tr'])
async def top_tracks(ctx: Context, amount: int = 20, term: str = 'short') -> list[tk.model.Track]:
    """
    Gets users top tracks

    amount (int) - Amount of tracks to get
    term [short/medium/long] - Time frame
    """
    top = (await ctx.sp.current_user_top_tracks(limit=amount, time_range='{0}_term'.format(term))).items
    if generator.verbose:
        generator.logger.info('Fetched {0} top tracks in {1} term'.format(len(top), term))
    return top


@instruction('top_artists', aliases=['top_art'])
async def top_artists(ctx: Context, instruction: Instruction = None, term: str = 'short', amount: int = 10) -> list[tk.model.Track]:
    """
    Gets a users top artists

    instruction (dict) - Instruction to run for each artist
    limit - Amount of artists to get
    term [short/medium/long] - Time frame
    """
    results = await ctx.sp.current_user_top_artists(time_range='{0}_term'.format(term), limit=amount).items
    songs = []
    for artist in results:
        kwargs = instruction[1]
        kwargs['artist'] = artist
        songs.extend(await instruction[0].run(ctx, **kwargs))
    if generator.verbose:
        generator.logger.info('Fetched {0} top artists and then {1} songs'.format(len(results), len(songs)))
    return songs
