from . import *


@modifier('clear_duplicates')
def clear_duplicates(songs, active: bool):
    if not active:
        return songs
    names = []
    new_songs = []
    for track in songs:
        if track.name not in names:
            names.append(track.name)
            new_songs.append(track)
    return new_songs
