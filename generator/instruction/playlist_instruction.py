from . import instruction
import random
import generator
import tekore as tk


@instruction('playlist_tracks')
async def playlist_songs(sp: tk.Spotify, name: tk.model.Playlist, amount: int = -1, sample: int = -1) -> list[tk.model.Track]:
    """
    Get playlist tracks

    name (string) - Name of playlist
    amount (int) - Amount to get from the playlist. If -1 it is all
    sample (int) - Random sample to get from the playlist. If -1 it is all.
    """
    tracks = await generator.spotify.get_playlist_tracks(sp, name)
    if len(tracks) > amount:
        tracks = tracks[:amount]
    if 0 < sample < len(tracks):
        tracks = random.sample(tracks, sample)
    if generator.verbose:
        generator.logger.info('Fetched {0} songs from playlist {1}'.format(len(tracks), name.name))
    return tracks
