import json
import logging
import traceback
from typing import Optional, Union

import toml
from tqdm import tqdm

from . import get_user_playlists
from tekore import model
import tekore as tk

from .. import instruction, modifier
from ..context import Context


async def get_user_instruction_playlists(sp, *, prefix="%"):
    all_playlists: list[model.FullPlaylist] = await get_user_playlists(sp)
    filtered_playlists = []
    for p in all_playlists:
        if p.name.startswith(prefix):
            filtered_playlists.append(p)
    return filtered_playlists


async def get_playlist_dict(sp: tk.Spotify, playlist: model.Playlist) -> Optional[dict]:
    description = playlist.description.strip().replace("&quot;", '"')
    if description.startswith('{'):
        try:
            return json.loads(description)
        except:
            return None
    try:
        return toml.loads(description)
    except:
        return None


async def generate_user_playlist(sp, playlist: model.Playlist, data: dict):
    pbar = tqdm(data['instructions'])
    songs = []
    ctx = Context(sp, playlist=playlist)
    for i in pbar:
        try:
            pbar.set_description(playlist.name + ': ' + i['type'])
            songs.extend(await instruction.run(ctx, i))
        except:
            traceback.print_exc()
            logging.error('Could not run instruction ' + str(i))
    songs = await modifier.run_modifiers(ctx, songs, data)
