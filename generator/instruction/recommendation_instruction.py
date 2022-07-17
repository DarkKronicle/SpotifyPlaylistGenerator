from generator.instruction.instruction import Instruction
import generator.types.track as track
import generator.types.artist as artist


class RecommendationInstruction(Instruction):

    def __init__(self, tracks=None, artists=None, genres=None, **kwargs):
        if tracks is None:
            tracks = []
        if artists is None:
            artists = []
        if genres is None:
            genres = []
        self.tracks = tracks
        self.artists = artists
        self.genres = genres
        self.kwargs = kwargs

    def run(self, songs, sp):
        import generator.config.instruction_serializer as instruct
        if all(isinstance(a, str) for a in self.artists):
            self.artists = [artist.get_artist(a, sp) for a in self.artists]
        if isinstance(self.tracks, dict):
            self.tracks = instruct.get_instruction(self.tracks).run([], sp)
        if all(isinstance(t, str) for t in self.tracks):
            self.tracks = [track.get_track(t, sp) for t in self.tracks]
        songs.extend(track.parse_tracks_list(
            sp.recommendations(
                seed_artists=[a.artist_id for a in self.artists],
                seed_genres=self.genres,
                seed_tracks=[t.track_id for t in self.tracks],
                **self.kwargs
            )['tracks']
        ))
        return songs
