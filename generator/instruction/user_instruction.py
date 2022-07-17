from . import *
import random
import generator.spotify as spotify


@instruction('saved_tracks')
def saved_tracks(sp: tk.Spotify, sample: int = -1, amount: int = -1, randomize: bool = True, top_down: bool = True, artist: tk.model.Artist = None) -> list[tk.model.Track]:
    tracks = spotify.get_saved_tracks(sp)
    if artist is not None:
        tracks = list(filter(lambda t: artist.name.lower() in [a.name.lower() for a in t.artists], tracks))
    if sample > 0:
        if sample < len(tracks):
            if top_down:
                tracks = tracks[:sample]
            else:
                tracks = tracks[-sample:]
    if amount < 0:
        return tracks
    if randomize:
        random.shuffle(tracks)
    if amount < len(tracks):
        if top_down:
            tracks = tracks[:amount]
        else:
            tracks = tracks[-amount]
    return tracks


@instruction('top_tracks')
def top_tracks(sp: tk.Spotify, amount: int = 20, term: str = 'short') -> list[tk.model.Track]:
    return sp.current_user_top_tracks(limit=amount, time_range='{0}_term'.format(term)).items


def top_artists(sp: tk.Spotify, instruction: Instruction = None, term: str = 'short', limit: int = 10) -> list[tk.model.Track]:
    results = sp.current_user_top_artists(time_range='{0}_term'.format(term), limit=limit).items
    songs = []
    for artist in results:
        kwargs = instruction[1]
        kwargs['artist'] = artist
        songs.extend(instruction[0].run(sp, **kwargs))
    return songs
