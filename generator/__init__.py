from .util import *
from . import instruction
from . import modifier
from . import spotify
from . import config
from . import sort
import tekore as tk
import logging


scopes = tk.scope.read + tk.scope.write


logger = logging.getLogger('generator')


prevent_uploading = False
list_songs = False
verbose = False
silent = False


async def setup(sp):
    # We want user playlists to have priority in search
    await generator.spotify.get_user_playlists(sp)


def get_default_token(manager):
    tk.client_id_var = manager['client_id']
    tk.client_secret_var = manager['client_secret']
    tk.redirect_uri_var = manager['redirect_uri']
    tk.user_refresh_var = manager['saved_token']

    return tk.request_client_token(tk.client_id_var, tk.client_secret_var)
