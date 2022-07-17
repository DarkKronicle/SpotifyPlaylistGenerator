import generator.types.track as track
import generator.types.album as album
import generator.util.cache as cache


class Artist:

    def __init__(self, name, artist_id, uri, url):
        self.name: str = name
        self.artist_id: str = artist_id
        self.uri: str = uri
        self.url: str = url
        self._albums = None

    def get_albums(self, sp):
        if self._albums is not None:
            return self._albums
        albums_data = []
        results = sp.artist_albums(self.artist_id, album_type='album')
        albums_data.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            albums_data.extend(results['items'])
        unique = set()  # skip duplicate albums
        albums_list = []
        for al in albums_data:
            name = al['name'].lower()
            if name not in unique:
                unique.add(name)
                albums_list.append(al)
        self._albums = album.parse_album_list(albums_list)
        return self._albums

    def get_tracks(self, sp):
        songs = []
        for al in self.get_albums(sp):
            songs.extend(al.get_tracks(sp))
        return songs

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def get_top_tracks(self, sp, limit=10):
        return track.parse_tracks_list(sp.artist_top_tracks(self.uri)['tracks'][:limit])

    @classmethod
    def from_json(cls, json_data):
        return Artist(
            json_data['name'],
            json_data['id'],
            json_data['uri'],
            json_data['external_urls']['spotify']
        )


def parse_artists(artist_list) -> list[Artist]:
    artists = []
    for artist in artist_list:
        artists.append(Artist.from_json(artist))
    return artists


@cache.cache()
def get_artist(name, sp) -> Artist:
    results = sp.search(q='artist:' + name, type='artist')
    items = results['artists']['items']
    if len(items) > 0:
        return Artist.from_json(items[0])
    else:
        return None
