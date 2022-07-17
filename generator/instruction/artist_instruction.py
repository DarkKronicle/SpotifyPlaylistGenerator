import random
from . import *


@instruction('artist_tracks')
def artist_tracks(sp, artist: tk.model.Artist = None, fetch: int = 50, select: int = 50) -> list[tk.model.Track]:
    tracks = spotify.get_artist_songs(sp, artist)
    if len(tracks) > fetch:
        tracks = tracks[:fetch]
    if fetch == select:
        return tracks
    tracks = random.sample(tracks, select)
    return tracks


@instruction('artist_top')
def artist_top(sp: tk.Spotify, artist: tk.model.Artist = None, amount: int = 10) -> list[tk.model.Track]:
    return sp.artist_top_tracks(artist, amount=amount)


@instruction('related_artists')
def related_artists(sp: tk.Spotify, artist: tk.model.Artist = None, instruction: Instruction = None, amount: int = 20) -> list[tk.model.Track]:
    related = sp.artist_related_artists(artist.id)
    if len(related) > amount:
        related = related[:amount]
    songs = []
    for artist in related:
        kwargs = instruction[1]
        kwargs['artist'] = artist
        songs.extend(instruction[0].run(sp, **kwargs))
    return songs
