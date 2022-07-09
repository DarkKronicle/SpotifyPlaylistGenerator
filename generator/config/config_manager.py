import toml

from generator.config.playlist import Playlist


class ConfigManager:

    def __init__(self):
        self.config = self.load_file('config.toml')

    def load_file(self, file):
        with open(str(file)) as f:
            return toml.load(f)

    def load_playlist(self, file):
        return Playlist.from_dict(self.load_file(file))

    def __getitem__(self, item):
        return self.config.get(item)
