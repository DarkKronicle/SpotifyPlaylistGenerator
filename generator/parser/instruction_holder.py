import json
import logging
import traceback
from pathlib import Path
from typing import Union

import toml
from tqdm import tqdm

from generator import instruction, modifier
from generator.context import Context


class Instructions:

    def __init__(self, instructions: list, modifiers: dict):
        self.instructions = instructions
        self.modifiers = modifiers

    async def run(self, ctx: Context, show_bar=False, **kwargs):
        songs = []
        if show_bar:
            pbar = tqdm(self.instructions)
        else:
            pbar = self.instructions
        for i in pbar:
            try:
                if show_bar:
                    pbar.set_description(ctx.name + ': ' + i['type'])
                songs.extend(await instruction.run(ctx, i, **kwargs))
            except:
                traceback.print_exc()
                logging.error('Could not run instruction ' + str(i))
        return await modifier.run_modifiers(ctx, songs, self.modifiers)

    @classmethod
    def from_dict(cls, data: dict):
        return Instructions(data.pop('instructions'), data)

    @classmethod
    def from_file(cls, file: Union[str, Path]):
        with open(str(file), 'r') as f:
            if str(file).endswith('.toml'):
                return Instructions.from_dict(toml.load(f))
            if str(file).endswith('.json'):
                return Instructions.from_dict(json.load(f))
        return None

    def __str__(self):
        s = "Modifiers: \n"
        for k, v in self.modifiers.items():
            s += "- " + str(k) + " - " + str(v) + "\n"
        s += "Instructions: \n"
        for i in self.instructions:
            s += "- " + str(i) + "\n"
        return s
