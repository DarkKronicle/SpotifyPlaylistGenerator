from generator.util.cache import cache
import tekore as tk
from generator.util import image


def get_id_from_uri(query: str):
    if query.strip().startswith('spotify:') or query.strip().startswith('s:'):
        return query.split(':')[-1]
    return None


@cache()
async def get_track(sp: tk.Spotify, query: str):
    uri = get_id_from_uri(query)
    if uri is not None:
        return await sp.track(uri)
    tracks = await sp.search(query, limit=1)
    if len(tracks) > 0 and len(tracks[0].items) > 0:
        return tracks[0].items[0]
    return None


@cache()
async def get_saved_tracks(sp: tk.Spotify):
    page = await sp.saved_tracks(limit=50)
    all_items = [item async for item in sp.all_items(page)]
    return [t.track for t in all_items]


@cache()
async def get_artist(sp: tk.Spotify, query: str):
    uri = get_id_from_uri(query)
    if uri is not None:
        return await sp.artist(uri)
    return (await sp.search(query, limit=1, types=('artist',)))[0].items[0]


@cache()
async def get_album(sp: tk.Spotify, query: str):
    uri = get_id_from_uri(query)
    if uri is not None:
        return await sp.album(uri)
    return (await sp.search(query, limit=1, types=('album',)))[0].items[0]


@cache()
async def get_playlist(sp: tk.Spotify, query: str):
    uri = get_id_from_uri(query)
    if uri is not None:
        return await sp.playlist(uri)
    return (await sp.search(query, limit=1, types=('playlist',)))[0].items[0]


@cache()
async def get_user_playlists(sp: tk.Spotify):
    playlists = []
    page = await sp.followed_playlists(limit=50)
    async for playlist in sp.all_items(page):
        playlist: tk.model.SimplePlaylist
        playlists.append(playlist)
        get_playlist.set(playlist, sp, playlist.name)
    return playlists


@cache()
async def get_album_tracks(sp: tk.Spotify, album: tk.model.Album):
    page = await sp.album_tracks(album.id, limit=50)
    return [album async for album in sp.all_items(page)]


async def get_artist_songs(sp: tk.Spotify, artist: tk.model.Artist):
    albums = await get_artist_albums(sp, artist)
    tracks = []
    for album in albums:
        tracks.extend(await get_album_tracks(sp, album))
    return tracks


@cache()
async def get_artist_albums(sp: tk.Spotify, artist: tk.model.Artist, limit=-1):
    page = await sp.artist_albums(artist.id, limit=50 if limit <= 0 else limit)
    if limit <= 0:
        return [album async for album in sp.all_items(page)]
    albums = []
    i = 0
    async for album in sp.all_items(page):
        if i >= limit:
            return albums
        albums.append(album)
        i += 1
    return albums


@cache()
async def get_playlist_tracks(sp: tk.Spotify, playlist: tk.model.Playlist):
    page = await sp.playlist_items(playlist.id, limit=100)
    return [t.track async for t in sp.all_items(page)]


async def replace_all_playlist(sp, playlist: str, songs: list[tk.model.Track]):
    if isinstance(playlist, tk.model.Playlist):
        playlist = playlist.id

    await sp.playlist_replace(playlist, [t.uri for t in songs[:min(100, len(songs))]])

    if len(songs) > 100:
        for i in range(1, len(songs) // 100 + 1):
            max_num = min((i + 1) * 100, len(songs))
            await sp.playlist_add(playlist, [t.uri for t in songs[i * 100:max_num]])


async def get_or_create_playlist(sp, name):
    playlists = await get_user_playlists(sp)
    for p in playlists:
        if p.name.lower() == name.lower():
            return p
    return await sp.playlist_create((await sp.current_user()).id, name)


async def generate_cover(sp: tk.Spotify, playlist: tk.model.Playlist, songs: list[tk.model.Track]):
    songs = list(filter(lambda x: x is not None and x.id is not None, songs))
    analysis = await sp.tracks_audio_features([t.id for t in songs])
    base_string = await image.get_playlist_image(songs, analysis)
    # image is a 64 base encoded string
    await sp.playlist_cover_image_upload(playlist.id, base_string)


@cache()
async def get_following_artists(sp: tk.Spotify):
    page = await sp.followed_artists(limit=50)
    return [artist async for artist in sp.all_items(page)]
