from . import *
import random
import generator.spotify as spotify


@instruction('playlist_tracks')
def playlist_songs(sp: tk.Spotify, name: tk.model.Playlist, amount: int = -1, sample: int = -1) -> list[tk.model.Track]:
    """
    Get playlist tracks

    name (string) - Name of playlist
    amount (int) - Amount to get from the playlist. If -1 it is all
    sample (int) - Random sample to get from the playlist. If -1 it is all.
    """
    tracks = spotify.get_playlist_tracks(sp, name)
    if len(tracks) > amount:
        tracks = tracks[:amount]
    if 0 < sample < len(tracks):
        tracks = random.sample(tracks, sample)
    return tracks
