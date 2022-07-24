from . import *
import random
import generator
import tekore as tk


@instruction('search')
def search(sp: tk.Spotify, search: str, limit: int = 50, sample: int = -1, offset: int = 0) -> list[tk.model.Track]:
    """
    Search for tracks

    search (string) - Query to search for. This can contain any tags Spotify allows for
    limit (int) - Amount to get
    sample (int) - Random amount to get from the search. If -1 it just returns the searched
    """
    paging: tk.model.FullTrackPaging = sp.search(q=search, type='track', limit=limit, offset=offset)[0]
    tracks = paging.items
    if 0 < sample < limit:
        tracks = random.sample(tracks, sample)
    if generator.verbose:
        generator.logger.info('Searched {0} songs with query "{1}"'.format(len(tracks), search))
    return tracks
