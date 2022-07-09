import generator.types.artist as artist
import generator.types.track as track
from datetime import datetime

from generator.util import util


class Album:

    def __init__(self, name, release_date, artists, album_id, uri, url, total_tracks):
        self.name: str = name
        self.release_date: datetime = release_date
        self.artists: list[artist.Artist] = artists
        self.album_id = album_id
        self.uri: str = uri
        self.url: str = url
        self.total_tracks: int = total_tracks
        self._songs = None

    def get_tracks(self, sp):
        if self._songs is not None:
            return self._songs

        results = sp.album_tracks(self.album_id)

        tracks_data = []
        tracks_data.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            tracks_data.extend(results['items'])
        self._songs = track.parse_tracks_list(tracks_data)
        return self._songs

    @classmethod
    def from_json(cls, json_data):
        return Album(
            json_data['name'],
            util.parse_time(json_data['release_date'], json_data['release_date_precision']),
            artist.parse_artists(json_data['artists']),
            json_data['id'],
            json_data['uri'],
            json_data['external_urls']['spotify'],
            json_data['total_tracks']
        )

    def __str__(self):
        return 'Album {0} by {1}'.format(self.name, self.artists)

    def __repr__(self):
        return str(self)


def parse_album_list(album_data):
    albums = []
    for data in album_data:
        albums.append(Album.from_json(data))
    return albums
