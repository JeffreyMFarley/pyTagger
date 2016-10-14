from collections import namedtuple

TrackMatch = namedtuple('TrackMatch', [
    'status', 'newPath', 'oldPath', 'score', 'newTags', 'oldTags'
])

#------ Snapshot --------------------------------------------------------------


class Snapshot(object):
    basic = ['title', 'track', 'totalTrack', 'artist',
             'albumArtist', 'album', 'length']
    songwriting = ['bpm', 'composer', 'key', 'lyrics', 'language']
    production = ['year', 'releaseDate', 'originalReleaseDate',
                  'recordingDate', 'conductor', 'remixer', 'publisher']
    distribution = ['media', 'disc', 'totalDisc']
    library = ['genre', 'id', 'ufid', 'compilation', 'comments', 'playCount',
               'group', 'subtitle', 'encodingDate', 'taggingDate']
    mp3Info = ['bitRate', 'vbr', 'fileHash', 'version']

    @staticmethod
    def orderedAllColumns():
        # preserve order
        columns = (Snapshot.basic +
                   Snapshot.songwriting +
                   Snapshot.production +
                   Snapshot.distribution +
                   Snapshot.library +
                   Snapshot.mp3Info)

        return columns

    @staticmethod
    def extractColumns(data):
        header = set()

        for v in data.values():
            for j in v.keys():
                if j not in header:
                    header.add(j)

        # Build the ordered set with the extra columns at the end
        known = Snapshot.orderedAllColumns()
        unknown = header - set(known)

        columns = [c for c in known if c in header]
        for c in sorted(unknown):
            columns.append(c)

        return columns
