from __future__ import unicode_literals
from __future__ import print_function
from collections import *
from hew import Normalizer
from pyTagger.operations.ask import askMultipleChoice
from pyTagger.operations.name import _safeGet as safeGet
from pyTagger.utils import saveJsonIncrementalDict

REQUIRED = 3
PREFERRED = 2
NICE = 1
NOT_REQUIRED = 0

# key: requiredLevel
albumFields = {
    'album': 3,
    'albumArtist': 3,
    'barcode': 1,
    'compilation': 0,
    'genre': 1,
    'media': 1,
    'publisher': 1,
    'recordingDate': 2,
    'subtitle': 0,
    'totalDisc': 0,
    'totalTrack': 1,
    'year': 2
}

# 'comments',

normalizer = Normalizer()


# -----------------------------------------------------------------------------
# Methods

def _albumKey(tags):
    album = safeGet(tags, 'album') or 'Unknown'
    disc = safeGet(tags, 'disc') or 1
    return normalizer.to_key(album + str(disc))


def _buildAlbums(snapshot):
    albums = defaultdict(Album)
    for path, tags in snapshot.items():
        key = _albumKey(tags)
        albums[key].add(path, tags)

    for key, album in albums.items():
        album.evaluate()

    return albums


# -----------------------------------------------------------------------------
# Album Class

class Album(object):
    def __init__(self, tracks=None, variations=None, status=None):
        self.tracks = tracks or []
        self.variations = variations or defaultdict(set)
        self.status = status or 'pending'

    def add(self, path, tags):
        self.tracks.append((path, tags))
        for field in albumFields:
            self.variations[field].add(safeGet(tags, field) or '')

    def evaluate(self):
        # Count the number of non-blank entries for each field
        tally = Counter()
        for field in albumFields:
            s = self.variations[field] - set([u''])
            tally[field] += len(s)

        blanks = sum([
            1
            for k, v in albumFields.items()
            if v > NOT_REQUIRED and tally[k] == 0
        ])
        singles = sum([1 for k in albumFields if tally[k] == 1])
        multiples = sum([1 for k in albumFields if tally[k] > 1])

        if multiples == 0:
            self.status = 'consistent' if blanks > 0 else 'complete'
        else:
            self.status = 'multiples'


# -----------------------------------------------------------------------------
# Process Class

class AlbumTagger(object):
    def __init__(self):
        self.albums = []

    def __iter__(self):
        for album in self.albums.values():
            yield album

    # -------------------------------------------------------------------------
    # Private

    def _tallyStatuses(self):
        tally = Counter()
        for album in self:
            tally[album.status] += 1
        return tally

    # -------------------------------------------------------------------------
    # I/O

    @staticmethod
    def createFromSnapshot(snapshot):
        instance = AlbumTagger()
        instance.albums = _buildAlbums(snapshot)
        return instance

    def save(self, fileName):
        output = saveJsonIncrementalDict(fileName)

        _ = next(output)

        for album in self:
            for pair in album.tracks:
                _ = output.send(pair)

        output.close()

    # -------------------------------------------------------------------------
    # Public Methods

    def proceed(self):
        tally = self._tallyStatuses()
        descr = ['\n\t{1} {0}'.format(x, tally[x]) for x in tally]
        text = 'Would you like to edit this set of albums?{}'.format(
            ''.join(descr)
        )

        a = askMultipleChoice(0, text, {
            'Y': 'Yes',
            'N': 'No'
        }, False)

        return a == 'Y'

    def conduct(self):
        return False
