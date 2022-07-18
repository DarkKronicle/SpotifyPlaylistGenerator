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


def replace_all_playlist(sp, playlist: str, songs: list[tk.model.Track]):
    if isinstance(playlist, tk.model.Playlist):
        playlist = playlist.id

    sp.playlist_replace(playlist, [t.uri for t in songs[:min(100, len(songs))]])

    if len(songs) > 100:
        for i in range(1, len(songs) // 100 + 1):
            max_num = min((i + 1) * 100, len(songs))
            sp.playlist_add(playlist, [t.uri for t in songs[i * 100:max_num]])


def get_or_create_playlist(sp, name):
    playlists = get_user_playlists(sp)
    for p in playlists:
        if p.name.lower() == name.lower():
            return p
    return sp.playlist_create(sp.current_user.id)

