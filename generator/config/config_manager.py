import toml
import os
import generator.config.playlist as playlist


def load_file(file):
    try:
        with open(str(file), 'r', encoding='utf-8') as f:
            return toml.load(f)
    except:
        return dict()


class ConfigManager:

    def __init__(self):
        self.config = load_file('config.toml')

    def __getitem__(self, item: str):
        if item.lower() in os.environ:
            return os.environ[item.lower()]
        return self.config.get(item)
