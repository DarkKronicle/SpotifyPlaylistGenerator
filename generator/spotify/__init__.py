from generator.util.cache import cache
import tekore as tk


@cache()
def get_track(sp: tk.Spotify, query: str):
    return sp.search(query, limit=1)[0].items[0]


@cache()
def get_saved_tracks(sp: tk.Spotify):
    return [t.track for t in sp.all_items(sp.saved_tracks(limit=50))]


@cache()
def get_artist(sp: tk.Spotify, query: str):
    return sp.search(query, limit=1, types=('artist',))[0].items[0]


@cache()
def get_album(sp: tk.Spotify, query: str):
    return sp.search(query, limit=1, types=('album',))[0].items[0]


@cache()
def get_playlist(sp: tk.Spotify, query: str):
    return sp.search(query, limit=1, types=('playlist',))[0].items[0]


@cache()
def get_user_playlists(sp: tk.Spotify):
    playlists = []
    for playlist in list(sp.all_items(sp.followed_playlists(limit=50))):
        playlist: tk.model.SimplePlaylist
        playlists.append(playlist)
        get_playlist.set(playlist, sp, playlist.name)
    return playlists


@cache()
def get_album_tracks(sp: tk.Spotify, album: tk.model.Album):
    return list(sp.all_items(sp.album_tracks(album.id, limit=50)))


def get_artist_songs(sp: tk.Spotify, artist: tk.model.Artist):
    albums = get_artist_albums(sp, artist)
    tracks = []
    for album in albums:
        tracks.extend(get_album_tracks(sp, album))
    return tracks


@cache()
def get_artist_albums(sp: tk.Spotify, artist: tk.model.Artist):
    return list(sp.all_items(sp.artist_albums(artist.id, limit=50)))


@cache()
def get_playlist_tracks(sp: tk.Spotify, playlist: tk.model.Playlist):
    return [t.track for t in sp.all_items(sp.playlist_items(playlist.id, limit=100))]
