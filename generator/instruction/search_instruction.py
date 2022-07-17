from . import *
import random


@instruction('search')
def search(sp: tk.Spotify, search: str, limit: int = 50, choose: int = 10, offset: int = 0) -> list[tk.model.Track]:
    paging: tk.model.FullTrackPaging = sp.search(q=search, type='track', limit=limit, offset=offset)[0]
    tracks = paging.items
    if choose < limit:
        tracks = random.sample(tracks, choose)
    return tracks
