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
