from collections import namedtuple

TrackMatch = namedtuple('TrackMatch', [
    'status', 'newPath', 'oldPath', 'score', 'newTags', 'oldTags'
])
