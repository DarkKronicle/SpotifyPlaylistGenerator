import toml

from generator.config.playlist import Playlist
import os


class ConfigManager:

    def __init__(self):
        self.config = self.load_file('config.toml')

    def load_file(self, file):
        try:
            with open(str(file), 'r', encoding='utf-8') as f:
                return toml.load(f)
        except:
            return dict()

    def load_playlist(self, file):
        data = self.load_file(file)
        return data, Playlist.from_dict(data)

    def __getitem__(self, item: str):
        if item.upper() in os.environ:
            return os.environ[item.upper()]
        return self.config.get(item)
