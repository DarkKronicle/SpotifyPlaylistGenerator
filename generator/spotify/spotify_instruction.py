import logging

from . import get_user_playlists
from tekore import model

from ..context import Context
from ..parser.instruction_holder import Instructions
from ..parser.script_parser import ScriptParser


async def get_user_instruction_playlists(sp, *, prefix="%"):
    all_playlists: list[model.FullPlaylist] = await get_user_playlists(sp)
    filtered_playlists = []
    for p in all_playlists:
        if p.name.startswith(prefix):
            filtered_playlists.append(p)
    return filtered_playlists


def get_playlist_instructions(playlist: model.Playlist) -> list[Instructions]:
    description = playlist.description.strip().replace("&quot;", '"').replace("&#x27;", "'")
    instructions = []
    for d in description.split("=-="):
        try:
            inst = ScriptParser(d).parse()
            instructions.append(inst)
        except Exception as e:
            logging.exception("Couldn't parse description from {0}".format(playlist.name), e)
            return instructions
    return instructions


async def generate_user_playlist(sp, playlist: model.Playlist):
    ctx = Context(sp, playlist.name, playlist=playlist)
    for i in get_playlist_instructions(playlist):
        await i.run(ctx, True)
