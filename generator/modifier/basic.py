import generator
from . import *
import generator.spotify as spotify


@modifier('clear_duplicates')
def clear_duplicates(sp, songs, active: bool):
    if not active:
        return songs
    names = []
    new_songs = []
    for track in songs:
        if track.name not in names:
            names.append(track.name)
            new_songs.append(track)
    return new_songs


@modifier('upload', sort=5)
def upload(sp, songs, name: str = None):
    if generator.prevent_uploading:
        generator.logger.info('Uploading songs for ' + name + ' was skipped because prevent_uploading is on')
        return songs
    playlist_id = spotify.get_or_create_playlist(sp, name)
    spotify.replace_all_playlist(sp, playlist_id, songs)
    return songs


@modifier('region')
def allowed_region(sp, songs, region: str = 'US'):
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
    return new_songs
