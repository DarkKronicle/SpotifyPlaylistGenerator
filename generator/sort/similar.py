import math


def get_closest(song_pos, input_songs_pca):
    closest_index = 0
    closest_margin = -1
    for i in range(len(input_songs_pca)):
        s_pos = input_songs_pca[i]
        dist = math.sqrt(math.pow(song_pos[0] - s_pos[0], 2) + math.pow(song_pos[1] - s_pos[1], 2))
        if dist < closest_margin or closest_margin < 0:
            closest_index = i
            closest_margin = dist
    return closest_index


def sort_by_similar(songs, data, tracks):

    top_pca = data[:len(tracks)]
    song_pca = data[len(tracks):]

    final = {}

    for i in range(len(songs)):
        closest = get_closest(song_pca[i], top_pca)
        closest_index = final.get(closest, None)
        if closest_index is None:
            final[closest] = []
            closest_index = final.get(closest)
        closest_index.append(songs[i])

    new_songs = []
    for t_index, song_list in final.items():
        new_songs.extend([tracks[t_index], *song_list])
    return new_songs
