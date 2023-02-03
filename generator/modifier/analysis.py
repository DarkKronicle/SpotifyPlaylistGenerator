from . import *
import tekore as tk

from ..context import Context


@modifier('energy')
async def energy(ctx: Context, songs, lower=0, upper=1):
    return await filter_by_var(ctx.sp, songs, 'energy', lower, upper)


@modifier('danceability')
async def danceability(ctx: Context, songs, lower=0, upper=1):
    return await filter_by_var(ctx.sp, songs, 'danceability', lower, upper)


@modifier('instrumentalness')
async def instrumentalness(ctx: Context, songs, lower=0, upper=1):
    return await filter_by_var(ctx.sp, songs, 'instrumentalness', lower, upper)


async def filter_by_var(sp: tk.Spotify, songs, attribute, lower=0, upper=1):
    analysis = await sp.tracks_audio_features([t.id for t in songs])
    new_songs = []
    for i in range(len(analysis)):
        a: tk.model.AudioFeatures = analysis[i]
        s: tk.model.Track = songs[i]
        val = getattr(a, attribute)
        if lower <= val <= upper:
            new_songs.append(s)
    return new_songs
