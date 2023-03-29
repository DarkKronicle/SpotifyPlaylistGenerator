import generator.util
from . import modifier
from generator import instruction
from generator import sort
import tekore as tk
import numpy as np


@modifier('similar', sort=-1)
async def similar_sort(sp, songs, tracks: dict, **kwargs):
    tracks = await instruction.run(sp, tracks)
    top_analysis = await sp.tracks_audio_features([t.id for t in tracks])

    analysis = list(await sp.tracks_audio_features([t.id for t in songs]))

    # Sort main one
    if len(tracks) < 50:
        pairs = sort.traveling([(tracks[i], top_analysis[i]) for i in range(len(top_analysis))], return_tuple=True)
    else:
        pairs = [(tracks[i], top_analysis[i]) for i in range(len(top_analysis))]

    tracks, top_analysis = list(zip(*pairs))
    # I have no freaking idea why these *sometimes* get flipped. I am about to break something.
    if isinstance(top_analysis[0], tk.model.FullPlaylistTrack):
        inbetween = top_analysis
        top_analysis = tracks
        tracks = inbetween

    attributes = kwargs.get('attributes', ['energy', 'valence'])
    features = generator.util.get_features(list(top_analysis) + analysis, attributes)
    data = np.array(features)
    return sort.similar.sort_by_similar(songs, data, tracks)

