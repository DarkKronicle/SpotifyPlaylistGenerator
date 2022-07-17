import generator.util.cache as cache


class Playlist:

    def __init__(self, name, uri, url, playlist_id):
        self.name = name
        self.uri = uri
        self.url = url
        self.playlist_id = playlist_id

    @classmethod
    def from_json(cls, json_data):
        return Playlist(
            json_data['name'],
            json_data['uri'],
            json_data['external_urls']['spotify'],
            json_data['id'],
        )


@cache.cache()
def get_playlist(sp, name):
    result = sp.search(name, type='playlist')
    return Playlist.from_json(result['items'])


def parse_playlist_list(playlist_list):
    return [Playlist.from_json(playlist) for playlist in playlist_list]

