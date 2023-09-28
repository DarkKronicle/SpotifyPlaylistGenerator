from . import instruction, Instruction
import generator
import tekore as tk
from datetime import datetime
import pytz

from ..context import Context
from generator import spotify


@instruction('new_releases')
async def new_releases(ctx: Context, days: int = 30):
    artists = await spotify.get_following_artists(ctx.sp)
    recent_albums = []
    now = datetime.now().replace(tzinfo=pytz.timezone('UTC'))
    for art in artists:
        albums = await spotify.get_artist_albums(ctx.sp, art, limit=5)
        for album in albums:
            album: tk.Album
            if album.release_date_precision == 'day':
                date = datetime.strptime(album.release_date, '%Y-%m-%d')
            elif album.release_date_precision == 'month':
                date = datetime.strptime(album.release_date, '%Y-%m')
            elif album.release_date_precision == 'day':
                date = datetime.strptime(album.release_date, '%Y-%m-%m')
            date = date.replace(tzinfo=pytz.timezone('UTC'))
            days_dif = (now - date).days
            if days_dif < days:
                recent_albums.append(album)
    all_tracks = []
    for album in recent_albums:
        all_tracks.extend(await spotify.get_album_tracks(ctx.sp, album))
    return all_tracks
