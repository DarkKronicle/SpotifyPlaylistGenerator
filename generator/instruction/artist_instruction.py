import random
from . import instruction, Instruction
import generator
import tekore as tk

from ..context import Context


@instruction('artist_tracks', aliases=['art'])
async def artist_tracks(ctx: Context, artist: tk.model.Artist = None, fetch: int = 50, select: int = 50) -> list[tk.model.Track]:
    """
    Gets a specific artists tracks

    artist (string) - Arist
    fetch (int) - Amount of songs to get
    select (int) - Random selection of the fetched songs
    """
    tracks = await generator.spotify.get_artist_songs(ctx.sp, artist)
    if len(tracks) > fetch:
        tracks = tracks[:fetch]
    if fetch == select:
        if generator.verbose:
            generator.logger.info('Fetched {0} songs from artist {1}'.format(len(tracks), artist.name))
        return tracks
    tracks = random.sample(tracks, select)
    if generator.verbose:
        generator.logger.info('Fetched {0} songs from artist {1}'.format(len(tracks), artist.name))
    return tracks


@instruction('artist_top', aliases=['art_t'])
async def artist_top(ctx: Context, artist: tk.model.Artist = None, amount: int = 10) -> list[tk.model.Track]:
    """
    Top artist tracks

    artist (string) - Arist
    amount (int) - Amount of songs to get. Maximum is 10
    """
    if generator.verbose:
        generator.logger.info('Fetched {0} top songs from artist {1}'.format(amount, artist.name))
    return (await ctx.sp.artist_top_tracks(market='US', artist_id=artist.id))[:amount]


# @instruction('related_artists', aliases=['rltd_art'])
async def related_artists(ctx: Context, artist: tk.model.Artist = None, instruction: Instruction = None, amount: int = 20) -> list[tk.model.Track]:
    """
    Get related artists and execute an instruction on them

    artist (string) - Arist
    amount (int) - Amount of artists to get
    instruction (int) - An instruction that has an `artist` argument in it
    """
    related = await ctx.sp.artist_related_artists(artist.id)
    if len(related) > amount:
        related = related[:amount]
    songs = []
    for artist in related:
        kwargs = instruction[1]
        kwargs['artist'] = artist
        songs.extend(await instruction[0].run(ctx.sp, **kwargs))
    if generator.verbose:
        generator.logger.info('Fetched {0} similar from artist {1} and collected {2} songs'.format(len(related), artist.name, len(songs)))
    return songs


@instruction('album_tracks', aliases=['album', 'alb'])
async def album_tracks(ctx: Context, album: tk.model.Album = None) -> list[tk.model.Track]:
    songs = []
    async for track in ctx.sp.all_items(await ctx.sp.album_tracks(album.id, limit=50)):
        songs.append(track)
    return songs