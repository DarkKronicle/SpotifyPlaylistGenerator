import generator.instruction as instruction
import generator.modifier as modifier


class Playlist:

    def __init__(self, raw_data: dict):
        self.raw_data = raw_data

    def get_songs(self, sp):
        songs = []
        data = dict(self.raw_data)
        data.pop('name')
        data.pop('daily')
        for i in data.pop('instructions'):
            songs.extend(instruction.run(sp, i))
        # Run modifiers like clear duplicates and what not
        songs = modifier.run_modifiers(songs, data)
        return songs

    def __getitem__(self, item):
        return self.raw_data[item]

    def get(self, target, default):
        return self.raw_data.get(target, default)
