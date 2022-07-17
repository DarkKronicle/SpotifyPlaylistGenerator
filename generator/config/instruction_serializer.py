import generator.instruction.condition_instruction as condition
import generator.instruction.user_instruction as user
import generator.instruction.artist_instruction as artist
import generator.instruction.recommendation_instruction as recommendation
import generator.instruction.search_instruction as search
import generator.instruction.playlist_instruction as playlist

instruction_types = {
    'clear_duplicates': condition.ClearDuplicates,
    'clear_before': condition.ClearBefore,
    'user_top_artists': user.TopArtists,
    'user_top_tracks': user.TopTracks,
    'saved_tracks': user.SavedItems,
    'artist_top_tracks': artist.ArtistTopInstruction,
    'related_artists': artist.RelatedArtistInstruction,
    'artist_tracks': artist.AristTracksInstruction,
    'recommendations': recommendation.RecommendationInstruction,
    'random': condition.RandomInstruction,
    'search': search.SearchInstruction,
    'playlist': playlist.PlaylistInstruction,
}


def get_instruction(data: dict):
    type_name: str = data.get('type')
    if type_name is None:
        raise AssertionError('Type for instruction type cannot be none!')
    instruction_type = instruction_types.get(type_name.lower())
    if instruction_type is None:
        raise AssertionError("Instruction type {0} is not a valid instruction!".format(type_name))
    kwargs = dict(data)
    kwargs.pop('type')
    if 'instruction' in kwargs:
        kwargs['instruction'] = get_instruction(kwargs['instruction'])
    return instruction_type(**kwargs)
