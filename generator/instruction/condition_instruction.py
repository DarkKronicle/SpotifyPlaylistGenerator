from generator.instruction.instruction import Instruction
import datetime
import random


class ClearDuplicates(Instruction):

    def run(self, songs, sp):
        names = []
        new_songs = []
        for track in songs:
            if track.name not in names:
                names.append(track.name)
                new_songs.append(track)
        return new_songs


class ClearBefore(Instruction):

    def __init__(self, max_date):
        self.max_date = max_date

    def run(self, songs, sp):
        if isinstance(self.max_date, str):
            self.max_date = datetime.datetime.strptime(self.max_date, '%Y-%m-%d')
        new_songs = []
        for track in songs:
            if track.album is None or track.album.release_date is None or track.album.release_date < self.max_date:
                continue
            new_songs.append(track)
        return new_songs


class RandomInstruction(Instruction):

    def __init__(self, instruction: Instruction, select=3):
        self.instruction = instruction
        self.select = select

    def run(self, songs, sp):
        songs = []
        songs = self.instruction.run(songs, sp)
        return random.sample(songs, self.select)
