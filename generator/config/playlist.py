import generator.instruction as instruction
import generator.modifier as modifier
from tqdm import tqdm
import generator


class Playlist:

    def __init__(self, raw_data: dict, name, *, log=True):
        self.raw_data = raw_data
        self.name = name
        self.log = log

    def get_songs(self, sp):
        songs = []
        data = dict(self.raw_data)
        if generator.verbose or not self.log:
            for pos, i in enumerate(data['instructions']):
                if self.log:
                    generator.logger.info('Running instruction {0}/{1} {2}'.format(pos + 1, len(data['instructions']), i['type']))
                songs.extend(instruction.run(sp, i))
        else:
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
