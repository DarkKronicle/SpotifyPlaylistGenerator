from typing import Optional

import tekore

from generator import spotify


class Context:

    def __init__(
            self,
            sp: tekore.Spotify,
            name: str,
            *,
            playlist: Optional[tekore.model.Playlist] = None,
            tracks = None
    ):
        self.sp = sp
        self.name = name
        self.playlist = playlist
        self.tracks = tracks

    async def get_track(self, val: str):
        return await spotify.get_track(self.sp, val)

    async def get_album(self, val: str):
        return await spotify.get_album(self.sp, val)

    async def get_artist(self, val: str):
        return await spotify.get_artist(self.sp, val)

    async def get_playlist(self, val: str):
        if val == 'this' and self.playlist is not None:
            return self.playlist
        return await spotify.get_playlist(self.sp, val)

    def with_tracks(self, tracks):
        return Context(self.sp, self.name, playlist=self.playlist, tracks=tracks)


