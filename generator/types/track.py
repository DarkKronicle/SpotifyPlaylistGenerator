from ..types import artist
from ..types.album import Album
from pprint import pprint
import generator.util.cache as cache


class Track:

    def __init__(self, name, popularity, artists, track_id, uri, url, album):
        self.name: str = name
        self.popularity: int = popularity
        self.artists: list[artist.Artist] = artists
        self.track_id: str = track_id
        self.uri: str = uri
        self.url: str = url
        self.album: Album = album

    @classmethod
    def from_json(cls, json_data):
        album = json_data.get('album', None)
        if album is not None:
            album = Album.from_json(album)
        return Track(
            json_data['name'],
            json_data.get('popularity', -1),
            artist.parse_artists(json_data['artists']),
            json_data['id'],
            json_data['uri'],
            json_data['external_urls']['spotify'],
            album,
        )

    def __str__(self):
        return "'{0}' by {1}".format(self.name, self.artists)

    def __repr__(self):
        return str(self)


def parse_tracks_list(tracks_data):
    tracks = []
    for track in tracks_data:
        tracks.append(Track.from_json(track))
    return tracks


@cache.cache(maxsize=1000)
def get_track(name, sp):
    result = sp.search(name, type='track', limit=1)
    return Track.from_json(result['tracks']['items'][0])
