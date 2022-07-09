from datetime import datetime
import generator.types.track as track


def parse_time(release_date, release_precision):
    if release_precision == 'day':
        return datetime.strptime(release_date, '%Y-%m-%d')
    if release_precision == 'month':
        return datetime.strptime(release_date, '%Y-%m')
    if release_precision == 'year':
        try:
            return datetime.strptime(release_date, '%Y')
        except Exception:
            print(release_date)
            return None
    return None


def parse_track_list(tracks_data):
    tracks = []
    for data in tracks_data:
        tracks.append(track.Track.from_json(data))
    return tracks
