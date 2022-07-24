from . import instruction, Instruction
import random
import generator.spotify as spotify
import generator
import tekore as tk


@instruction('saved_tracks')
def saved_tracks(sp: tk.Spotify, sample: int = -1, amount: int = -1, artist: tk.model.Artist = None) -> list[tk.model.Track]:
    """
    Saved tracks

    amount (int) - Amount to get. If -1 it does all
    sample (int) - Random sample to get. If -1 it does all
    artist (string) - Filter artist. This is not required.
    """
    tracks = spotify.get_saved_tracks(sp)
    if artist:
        tracks = list(filter(lambda t: artist.name.lower() in [a.name.lower() for a in t.artists], tracks))
    if 0 < amount < len(tracks):
        tracks = tracks[:amount]
    if 0 < sample < amount:
        tracks = random.sample(tracks, sample)
    if generator.verbose:
        generator.logger.info('Fetched {0} songs saved songs'.format(len(tracks)))
    return tracks


@instruction('top_tracks')
def top_tracks(sp: tk.Spotify, amount: int = 20, term: str = 'short') -> list[tk.model.Track]:
    """
    Gets users top tracks

    amount (int) - Amount of tracks to get
    term [short/medium/long] - Time frame
    """
    top = sp.current_user_top_tracks(limit=amount, time_range='{0}_term'.format(term)).items
    if generator.verbose:
        generator.logger.info('Fetched {0} top tracks in {1} term'.format(len(top), term))
    return top


def top_artists(sp: tk.Spotify, instruction: Instruction = None, term: str = 'short', limit: int = 10) -> list[tk.model.Track]:
    """
    Gets a users top artists

    instruction (dict) - Instruction to run for each artist
    limit - Amount of artists to get
    term [short/medium/long] - Time frame
    """
    results = sp.current_user_top_artists(time_range='{0}_term'.format(term), limit=limit).items
    songs = []
    for artist in results:
        kwargs = instruction[1]
        kwargs['artist'] = artist
        songs.extend(instruction[0].run(sp, **kwargs))
    if generator.verbose:
        generator.logger.info('Fetched {0} top artists and then {1} songs'.format(len(results), len(songs)))
    return songs
