import generator.types.playlist as playlist
import generator.types.track as track
from generator.instruction.instruction import Instruction
import random


class PlaylistInstruction(Instruction):

    def __init__(self, name, amount=50, sample=-1):
        self.name = name
        self.amount = amount
        self.sample = sample

    def run(self, songs, sp):
        p = playlist.get_playlist(sp, self.name)
        response = sp.playlist_items(p.playlist_id, limit=self.amount, additional_types=['track'])['items']
        tracks = track.parse_tracks_list([r['track'] for r in response])
        if len(tracks) > self.amount:
            tracks = tracks[:self.amount]
        if 0 < self.sample < len(tracks):
            tracks = random.sample(tracks, self.sample)
        songs.extend(tracks)
        return songs
