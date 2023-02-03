import random

import generator
from . import *
import generator.spotify as spotify
import tekore as tk

from ..context import Context


@modifier('clear_duplicates', aliases=['no_dupes'])
async def clear_duplicates(ctx: Context, songs: list[tk.model.Track], active: bool):
    """
    Clears duplicates

    active (bool) - Whether it is active
    """
    if not active:
        return songs
    uris = []
    new_songs = []
    for track in songs:
        if track.uri not in uris:
            uris.append(track.uri)
            new_songs.append(track)
    if generator.verbose:
        generator.logger.info('Removed {0} duplicates'.format(len(songs) - len(new_songs)))
    return new_songs


@modifier('trim', sort=3)
async def trim(ctx: Context, songs, amount: int = 50, rand: bool = False):
    if len(songs) < amount:
        return songs
    if rand:
        return random.sample(songs, amount)
    return songs[:amount]


@modifier('upload', sort=5, aliases=['up'])
async def upload(ctx: Context, songs, name: str = None):
    """
    Upload to Spotify under a specific name. This clears out the playlist and replaces ALL tracks.

    name (string) - Name of the playlist. It will be created if it does not exist.
    """
    if generator.prevent_uploading:
        if not generator.silent:
            generator.logger.info('Uploading songs for ' + name + ' was skipped because prevent_uploading is on')
        return songs
    playlist = await spotify.get_or_create_playlist(ctx.sp, name)
    await spotify.replace_all_playlist(ctx.sp, playlist, songs)
    if generator.verbose:
        generator.logger.info('Uploaded {0} songs to {1} (id {2})'.format(len(songs), playlist.name, playlist.id))
    return songs


@modifier('remove_artists', aliases=['rem_art'])
async def remove_artist(ctx: Context, songs, artist: list[str]):
    """
    Remove artists

    artist (list) - List of artists
    """
    artists = await generator.instruction.parse_var(ctx, list[tk.model.Artist], artist)
    new_songs = []
    for song in songs:
        if all(
                [a.name != art.name for art in artists for a in song.artists]
        ):
            new_songs.append(song)
    if generator.verbose:
        generator.logger.info('Removed {0} songs from artists {1}'.format(len(songs) - len(new_songs), [a.name for a in artists]))
    return new_songs


@modifier('remove_from_playlist', aliases=['rem_play'])
async def remove_from_playlist(ctx: Context, songs, playlist: str):
    """
    Remove songs from playlist

    playlist (str) - Playlist
    """
    playlist = await generator.instruction.parse_var(ctx, tk.model.Playlist, playlist)
    tracks = await spotify.get_playlist_tracks(ctx.sp, playlist)
    new_songs = []
    for song in songs:
        if all(
                [s.name != song.name for s in tracks]
        ):
            new_songs.append(song)
    if generator.verbose:
        generator.logger.info('Removed {0} songs from playlist {1} (id {2})'.format(len(songs) - len(new_songs), playlist.name, playlist.id))
    return new_songs


@modifier('region', aliases=['reg'])
async def allowed_region(ctx: Context, songs, region: str = 'US'):
    """
    Filters tracks to a specific region. This is useful if you only want songs that can play where you are.

    region (string) - Region code to filter for
    """
    new_songs = []
    # Here is a list of all the available markets
    """AD, AE, AG, AL, AM, AO, AR, AT, AU, AZ, BA, BB, BD, BE, BF, BG, BH, BI, BJ, BN, BO, BR, BS, BT, BW, BY, BZ, 
    CA, CD, CG, CH, CI, CL, CM, CO, CR, CV, CW, CY, CZ, DE, DJ, DK, DM, DO, DZ, EC, EE, EG, ES, FI, FJ, FM, FR, GA, 
    GB, GD, GE, GH, GM, GN, GQ, GR, GT, GW, GY, HK, HN, HR, HT, HU, ID, IE, IL, IN, IQ, IS, IT, JM, JO, JP, KE, KG, 
    KH, KI, KM, KN, KR, KW, KZ, LA, LB, LC, LI, LK, LR, LS, LT, LU, LV, LY, MA, MC, MD, ME, MG, MH, MK, ML, MN, MO, 
    MR, MT, MU, MV, MW, MX, MY, MZ, NA, NE, NG, NI, NL, NO, NP, NR, NZ, OM, PA, PE, PG, PH, PK, PL, PS, PT, PW, PY, 
    QA, RO, RS, RW, SA, SB, SC, SE, SG, SI, SK, SL, SM, SN, SR, ST, SV, SZ, TD, TG, TH, TJ, TL, TN, TO, TR, TT, TV, 
    TW, TZ, UA, UG, US, UY, UZ, VC, VE, VN, VU, WS, XK, ZA, ZM, ZW """
    for track in songs:
        if not track.available_markets:
            new_songs.append(track)
            continue
        if region in track.available_markets:
            new_songs.append(track)
    if generator.verbose:
        generator.logger.info('Removed {0} songs that are not allowed in region {1}'.format(len(songs) - len(new_songs), region))
    return new_songs


@modifier('explicit')
async def explicit_filter(ctx: Context, songs, explicit: bool = False):
    new_songs = []
    for track in songs:
        if track.explicit == explicit:
            new_songs.append(track)

    if generator.verbose:
        generator.logger.info(
            "Removed {0} songs that didn't match filter explicit = {1}".format(len(songs) - len(new_songs), explicit))
    return new_songs

