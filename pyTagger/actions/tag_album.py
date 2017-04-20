from __future__ import unicode_literals
from __future__ import print_function
import logging
import os
from collections import *
from configargparse import getArgumentParser
from hew import Normalizer
from pyTagger.operations.ask import *
from pyTagger.operations.name import _safeGet as safeGet
from pyTagger.utils import configurationOptions, defaultConfigFiles
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
    'disc': 0,
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
# Configuration

p = getArgumentParser('tag-album',
                      default_config_files=defaultConfigFiles,
                      parents=[getArgumentParser()],
                      description='settings for editing whole albums')
group = p.add_argument_group('tag-album')
group.add('--tag-album-file', default='albums.json',
          help='a snapshot of the mp3s to edit')
group.add('--tag-album-logging',
          choices=[logging.NOTSET, logging.INFO, logging.WARNING,
                   logging.ERROR],
          default=logging.WARNING, type=int,
          help='how verbose the process should be')


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

    return albums


# -----------------------------------------------------------------------------
# Album Class

class Album(object):
    def __init__(self, tracks=None, status=None):
        options = configurationOptions('tag-album')
        self.log = logging.getLogger(__name__)
        self.log.setLevel(options.tag_album_logging)

        self.tracks = tracks or []
        self.variations = defaultdict(set)
        self.status = status or 'pending'

    def add(self, path, tags):
        self.tracks.append((path, tags))

    def assign(self, field, value):
        self.log.info('{} {} {} {}'.format(self.name, field, '=', value))
        for _, tags in self.tracks:
            tags[field] = value

    def assignToBlank(self, field, value):
        for _, tags in self.tracks:
            if field not in tags or not tags[field]:
                self.log.info('{} {} {} {} {}'.format(
                    self.name, safeGet(tags, 'title'), field, '=', value
                ))
                tags[field] = value

    def assignTotalTrack(self):
        last = max([safeGet(tags, 'track') or 0 for _, tags in self.tracks])
        self.assign('totalTrack', last)

    def evaluate(self):
        self.findVariations()

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

    def findVariations(self):
        self.variations = defaultdict(set)
        for _, tags in self.tracks:
            for field in albumFields:
                self.variations[field].add(safeGet(tags, field) or '')

    @property
    def name(self):
        return self.variations['album'].copy().pop()


# -----------------------------------------------------------------------------
# Process Class

class AlbumTagger(object):
    def __init__(self):
        options = configurationOptions('tag-album')
        self.log = logging.getLogger(__name__)
        self.log.setLevel(options.tag_album_logging)

        self.albums = []
        self.autoFixes = deque()
        self.manualFixes = deque()
        self.skipped = deque()

        self.userQuit = False
        self.userDiscard = False

    def __iter__(self):
        for key in sorted(self.albums):
            yield self.albums[key]

    # -------------------------------------------------------------------------
    # Private

    def _routeAssign(self, album, field, value):
        if len(album.variations[field]) > 1:
            toAll = {
                'A': 'Apply to all tracks',
                'B': 'Apply only to blank tracks'
            }
            a = askMultipleChoice(0, value or u'(blank)', toAll, False)
            if a == 'A':
                album.assign(field, value)
            else:
                album.assignToBlank(field, value)
        else:
            album.assign(field, value)

    def _reportStatus(self):
        self._triage()

        tally = Counter()
        for album in self:
            album.evaluate()
            tally[album.status] += 1

        descr = ['{2}\t{1} {0}'.format(x, tally[x], os.linesep) for x in tally]
        text = 'The state of the albums:' + ''.join(descr)
        wrapped_out(0, text)

    def _triage(self):
        self.autoFixes = deque()
        self.manualFixes = deque()

        def addToAuto(fn, *args):
            self.autoFixes.append((fn, args))

        def addToAsk(album, field, variations):
            self.manualFixes.append((album, field, variations))

        for album in self:
            album.evaluate()

            if album.status == 'complete':
                continue

            for field in sorted(albumFields):
                variations = list(sorted(album.variations[field]))
                if len(variations) == 2 and not variations[0]:
                    addToAuto(album.assign, field, variations[1])
                elif len(variations) == 1 and variations[0]:
                    pass
                elif len(variations) == 1:
                    if field in ['disc', 'totalDisc']:
                        pass
                    elif field == 'totalTrack':
                        addToAuto(album.assignTotalTrack)
                    else:
                        addToAsk(album, field, [])
                else:
                    addToAsk(album, field, variations)

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

    def applyAutoFix(self):
        while self.autoFixes:
            fn, args = self.autoFixes.popleft()
            fn(*args)

        return len(self.autoFixes) == 0

    def askManualFix(self):
        basicOptions = {
            'S': 'Skip',
            'X': 'Save the edits and Exit',
            'Z': 'Discard the edits'
        }

        self.skipped = deque()
        while self.manualFixes and not self.userQuit and not self.userDiscard:
            album, field, variations = self.manualFixes.popleft()
            options = dict(basicOptions)
            for i, v in enumerate(variations):
                options[str(i + 1)] = v or u'(blank)'
            text = '{} - {}'.format(album.name, field)

            try:
                a = askOrEnterMultipleChoice(0, text, options, False)
                if len(a) == 1:
                    try:
                        index = int(a) - 1
                        if field in ['compilation', 'disc', 'totalDisc']:
                            self._routeAssign(album, field, int(a))
                        else:
                            self._routeAssign(album, field, variations[index])
                    except ValueError:
                        if a == 'S':
                            self.skipped.append((album, field, variations))
                        elif a == 'X':
                            self.userQuit = True
                        elif a == 'Z':
                            self.userDiscard = True
                        else:
                            self._routeAssign(album, field, a)
                else:
                    self._routeAssign(album, field, a)

            except KeyboardInterrupt:
                self.userDiscard = True

        return len(self.manualFixes) == 0 and len(self.skipped) == 0

    def conduct(self):
        result = self.applyAutoFix() and self.askManualFix()
        self._reportStatus()
        return result

    def proceed(self):
        self._triage()

        text = 'There are {} auto-fixes and {} fixes that require input. ' \
               'Proceed?'.format(len(self.autoFixes), len(self.manualFixes))
        a = askMultipleChoice(0, text, {
            'Y': 'Yes',
            'N': 'No'
        })

        return a == 'Y'

if __name__ == '__main__':
    from pyTagger.utils import loadJson

    logging.basicConfig()

    options = configurationOptions('tag-album')
    fileName = options.tag_album_file
    snapshot = loadJson(fileName)

    instance = AlbumTagger.createFromSnapshot(snapshot)
    if instance.proceed():
        instance.conduct()
        if not instance.userDiscard:
            instance.save(fileName)
