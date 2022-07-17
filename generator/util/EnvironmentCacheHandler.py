from spotipy import CacheHandler

import json


class EnvironmentCacheHandler(CacheHandler):

    def __init__(self, token_data):
        self.saved_token = json.loads(token_data)

    def get_cached_token(self):
        return self.saved_token

    def save_token_to_cache(self, token_info):
        self.saved_token = token_info
