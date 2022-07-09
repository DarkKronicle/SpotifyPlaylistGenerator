from generator.instruction.instruction import Instruction
from ..types.artist import Artist
import generator.types.artist as artist_mod
import random


class ArtistInstruction(Instruction):

    def get_artist(self):
        raise NotImplementedError

    def set_artist(self, artist):
        raise NotImplementedError


class AristTracksInstruction(ArtistInstruction):

    def __init__(self, artist: Artist=None, fetch=20, select=20):
        self.artist = artist
        self.fetch = fetch
        self.select = select
        if fetch < select:
            raise AssertionError("Fetch cannot be less than sample!")

    def get_artist(self):
        return self.artist

    def set_artist(self, artist):
        self.artist = artist

    def run(self, songs, sp):
        if isinstance(self.artist, str):
            self.artist = artist_mod.get_artist(self.artist, sp)
        tracks = self.get_artist().get_tracks(sp)
        if len(tracks) > self.fetch:
            tracks = tracks[:self.fetch]
        if self.fetch == self.select:
            songs.extend(tracks)
            return songs
        tracks = random.sample(tracks, self.select)
        print(tracks)
        songs.extend(tracks)
        return songs


class ArtistTopInstruction(ArtistInstruction):

    def __init__(self, artist: Artist=None, amount=10):
        self.artist = artist
        self.amount = amount

    def get_artist(self):
        return self.artist

    def set_artist(self, artist):
        self.artist = artist

    def run(self, songs, sp):
        if isinstance(self.artist, str):
            self.artist = artist_mod.get_artist(self.artist, sp)
        songs.extend(self.get_artist().get_top_tracks(sp, self.amount))
        return songs


class RelatedArtistInstruction(ArtistInstruction):

    def __init__(self, artist: Artist=None, instruction: ArtistInstruction=None, amount=20):
        self.artist = artist
        self.instruction = instruction
        self.amount = amount

    def set_artist(self, artist):
        self.artist = artist

    def get_artist(self):
        return self.artist

    def run(self, songs, sp):
        if isinstance(self.artist, str):
            self.artist = artist_mod.get_artist(self.artist, sp)
        related = artist_mod.parse_artists(sp.artist_related_artists(self.get_artist().uri)['artists'])
        if len(related) > self.amount:
            related = related[:self.amount]
        for artist in related:
            self.instruction.set_artist(artist)
            self.instruction.run(songs, sp)
        return songs
