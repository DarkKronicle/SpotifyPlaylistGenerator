import generator.instruction as instruction
import generator.modifier as modifier
from tqdm import tqdm


class Playlist:

    def __init__(self, raw_data: dict, name):
        self.raw_data = raw_data
        self.name = name

    def get_songs(self, sp):
        songs = []
        data = dict(self.raw_data)
        pbar = tqdm(data['instructions'])
        for i in pbar:
            pbar.set_description(self.name + ': ' + i['type'])
            songs.extend(instruction.run(sp, i))
        # Run modifiers like clear duplicates and what not
        songs = modifier.run_modifiers(sp, songs, data)
        return songs

    def __getitem__(self, item):
        return self.raw_data[item]

    def get(self, target, default):
        return self.raw_data.get(target, default)
