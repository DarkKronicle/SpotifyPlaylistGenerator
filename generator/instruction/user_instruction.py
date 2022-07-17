from generator.instruction.instruction import Instruction
import generator.types.track as track
import random

import generator.types.artist as artist_mod


class SavedItems(Instruction):

    def __init__(self, sample=-1, amount=-1, randomize=True, top_down=True, artist=None):
        self.sample = sample
        self.amount = amount
        self.randomize = randomize
        self.top_down = top_down
        self.artist: str = artist

    def run(self, songs, sp):
        tracks = track.parse_tracks_list([t['track'] for t in sp.current_user_saved_tracks()['items']])
        if self.artist is not None:
            tracks = list(filter(lambda t: self.artist.lower() in [a.name.lower() for a in t.artists], tracks))
        if self.sample > 0:
            if self.sample < len(tracks):
                if self.top_down:
                    tracks = tracks[:self.sample]
                else:
                    tracks = tracks[-self.sample:]
        if self.amount < 0:
            songs.extend(tracks)
            return songs
        if self.randomize:
            random.shuffle(tracks)
        if self.amount < len(tracks):
            if self.top_down:
                tracks = tracks[:self.amount]
            else:
                tracks = tracks[-self.amount]
        songs.extend(tracks)
        return songs


class TopTracks(Instruction):

    def __init__(self, amount=20, term='short'):
        self.amount = amount
        self.term = term

    def run(self, songs, sp):
        songs.extend(track.parse_tracks_list(sp.current_user_top_tracks(self.amount, time_range='{0}_term'.format(self.term))['items']))
        return songs


class TopArtists(Instruction):

    def __init__(self, instruction, term='short', limit=10):
        self.instruction = instruction
        self.term = term
        self.limit = limit

    def run(self, songs, sp):
        results = sp.current_user_top_artists(time_range='{0}_term'.format(self.term), limit=self.limit)['items']
        for artist in artist_mod.parse_artists(results):
            self.instruction.set_artist(artist)
            self.instruction.run(songs, sp)
        return songs
