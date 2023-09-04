from . import *
import tekore as tk

from ..context import Context
from .. import DEFAULT_VALUE

from datetime import datetime


@modifier('energy')
async def energy(ctx: Context, songs, lower: float = 0, upper: float = 1):
    return await filter_by_var(ctx.sp, songs, 'energy', lower, upper)


@modifier('danceability')
async def danceability(ctx: Context, songs, lower: float = 0, upper: float = 1):
    return await filter_by_var(ctx.sp, songs, 'danceability', lower, upper)


@modifier('valence')
async def valence(ctx: Context, songs, lower: float = 0, upper: float = 1):
    return await filter_by_var(ctx.sp, songs, 'valence', lower, upper)


@modifier('instrumentalness')
async def instrumentalness(ctx: Context, songs, lower: float = 0, upper: float = 1):
    return await filter_by_var(ctx.sp, songs, 'instrumentalness', lower, upper)


@modifier('acousticness')
async def acaousticness(ctx: Context, songs, lower: float = 0, upper: float = 1):
    return await filter_by_var(ctx.sp, songs, 'acousticness', lower, upper)


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


@modifier('remove_ai')
async def remove_ai(ctx: Context, songs, active: bool):
    if active == DEFAULT_VALUE:
        active = True
    if not active:
        return songs

    analysis = await sp.tracks_audio_features([t.id for t in songs])
    full_info = await sp.tracks([t.id for t in songs])
    new_songs = []
    start = datetime(2022, 2, 1)
    end = datetime(2022, 4, 1)
    removed = 0
    for i in range(len(analysis)):
        a: tk.model.AudioFeatures = analysis[i]
        s: tk.model.Track = songs[i]
        i: tk.model.FullTrack = full_info[i]
        album = i.album
        date = None
        if album.release_date_precision == 'day':
            date = datetime.strptime(album.release_date, '%Y-%m-%d')
        elif album.release_date_precision == 'month':
            date = datetime.strptime(album.release_date, '%Y-%m')
        elif album.release_date_precision == 'day':
            date = datetime.strptime(album.release_date, '%Y-%m-%m')
            date = date.replace(tzinfo=pytz.timezone('UTC'))
        if a.instrumentalness > 0.6 and (date is not None and date > s and date < e) and (i.popularity is not None and i.popularity < 20):
            removed += 1
            continue
        new_songs.add(s)
    if removed > 0:
        print("Removed AI: " + str(removed))
    return new_songs
