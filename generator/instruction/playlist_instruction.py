from . import *
import random
import generator.spotify as spotify


@instruction('playlist_tracks')
def playlist_songs(sp: tk.Spotify, name: tk.model.Playlist, amount: int = 50, sample: int = -1) -> list[tk.model.Track]:
    tracks = spotify.get_playlist_tracks(sp, name)
    if len(tracks) > amount:
        tracks = tracks[:amount]
    if 0 < sample < len(tracks):
        tracks = random.sample(tracks, sample)
    return tracks
