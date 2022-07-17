from generator.instruction.instruction import Instruction
import generator.types.track as track
import random


class SearchInstruction(Instruction):

    def __init__(self, search=None, limit=50, choose=10, offset=0):
        self.search = search
        self.choose = choose
        self.limit = limit
        self.offset = offset

    def run(self, songs, sp):
        tracks = sp.search(q=self.search, type='track', limit=self.limit, offset=self.offset)['tracks']
        if self.choose < self.limit:
            tracks = random.sample(tracks, self.choose)
        songs.extend(track.parse_tracks_list(tracks))
        return songs
