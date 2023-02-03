import logging
import traceback

import generator.instruction as instruction
import generator.modifier as modifier
from tqdm import tqdm
import generator
from generator.context import Context


class Playlist:

    def __init__(self, raw_data: dict, name, *, log=True):
        self.raw_data = raw_data
        self.name = name
        if generator.silent:
            self.log = False
        else:
            self.log = log

    def create_context(self, sp) -> Context:
        return Context(sp)

    async def get_songs(self, sp):
        songs = []
        data = dict(self.raw_data)
        ctx = self.create_context(sp)
        if generator.verbose or not self.log:
            for pos, i in enumerate(data['instructions']):
                try:
                    if self.log:
                        generator.logger.info(
                            'Running instruction {0}/{1} {2}'.format(pos + 1, len(data['instructions']), i['type'])
                        )
                    songs.extend(await instruction.run(ctx, i))
                except:
                    traceback.print_exc()
                    logging.error('Could not run instruction ' + str(i))
        else:
            pbar = tqdm(data['instructions'])
            for i in pbar:
                try:
                    pbar.set_description(self.name + ': ' + i['type'])
                    songs.extend(await instruction.run(ctx, i))
                except:
                    traceback.print_exc()
                    logging.error('Could not run instruction ' + str(i))
        # Run modifiers like clear duplicates and what not
        songs = await modifier.run_modifiers(ctx, songs, data)
        return songs

    def __getitem__(self, item):
        return self.raw_data[item]

    def get(self, target, default):
        return self.raw_data.get(target, default)

    def __str__(self):
        return '<Playlist ' + self.name + '>'
