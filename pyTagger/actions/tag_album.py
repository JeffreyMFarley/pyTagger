from __future__ import unicode_literals
from __future__ import print_function
import logging
import pyTagger.operations.ask as ask
import os
from collections import Counter, defaultdict, deque
from configargparse import getArgumentParser
from hew import Normalizer
from pyTagger.operations.name import _safeGet as safeGet
from pyTagger.utils import configurationOptions, defaultConfigFiles
from pyTagger.utils import loadJson, saveJsonIncrementalDict


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
                      ignore_unknown_config_file_keys=True,
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
        self.log.info('%s %s = %s' % (self.name, field, value))
        for _, tags in self.tracks:
            tags[field] = value

    def assignToBlank(self, field, value):
        for _, tags in self.tracks:
            if field not in tags or not tags[field]:
                self.log.info('%s %s %s = %s' % (
                    self.name, safeGet(tags, 'title'), field, value
                ))
                tags[field] = value

    def assignTotalTrack(self):
        last = max([safeGet(tags, 'track') or 1 for _, tags in self.tracks])
        self.assign('totalTrack', last)

    def findVariations(self):
        self.variations = defaultdict(set)
        for _, tags in self.tracks:
            for field in albumFields:
                self.variations[field].add(safeGet(tags, field) or '')

    @property
    def name(self):
        if len(self.variations['album']) == 0:
            return u'Unknown'
        return self.variations['album'].copy().pop()

    @property
    def nameAndDisc(self):
        name = self.variations['album'].copy().pop()
        if len(self.variations['disc']) == 0:
            disc = ''
        else:
            disc = self.variations['disc'].copy().pop()
        return '{} **{}**'.format(name, disc)


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
            a = ask.askMultipleChoice(0, value, toAll, False)
            if a == 'A':
                album.assign(field, value)
            else:
                album.assignToBlank(field, value)
        else:
            album.assign(field, value)

    def _triage(self):
        self.autoFixes = deque()
        self.manualFixes = deque()

        def addToAuto(fn, *args):
            self.autoFixes.append((fn, args))

        def addToAsk(album, field, variations):
            self.manualFixes.append((album, field, variations))

        for album in self:
            album.findVariations()

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

    def rebuild(self):
        snapshot = {
            fullPath: row
            for album in self
            for fullPath, row in album.tracks
        }
        self.albums = _buildAlbums(snapshot)

    def save(self, fileName):
        output = saveJsonIncrementalDict(fileName)

        _ = next(output)

        for album in self:
            for fullPath, row in album.tracks:
                pair = (fullPath.replace('\\', '\\\\'), row)
                output.send(pair)

        output.close()

    # -------------------------------------------------------------------------
    # Public Methods

    def applyAutoFix(self):
        while self.autoFixes:
            fn, args = self.autoFixes.popleft()
            fn(*args)

        return len(self.autoFixes) == 0

    def askAlbumName(self):
        albums = [album for album in self]
        options = {
            str(i + 1): album.nameAndDisc for i, album in enumerate(albums)
        }
        options['X'] = 'Return to menu'
        try:
            a = ask.askMultipleChoice(0, 'Select an album to change', options)
            if a == 'X':
                return
            else:
                index = int(a) - 1
                album = albums[index]
                b = ask.askOrEnterMultipleChoice(0, album.name, options, False)
                try:
                    index = int(b) - 1
                    other = albums[index]
                    album.assign('album', other.name)
                except ValueError:
                    album.assign('album', a)
        except KeyboardInterrupt:
            self.userDiscard = True

    def askManualFix(self):
        basicOptions = {
            'I': 'Ignore',
            'X': 'Save the edits and Exit',
            'Z': 'Discard the edits'
        }

        while self.manualFixes and not self.bail():
            album, field, variations = self.manualFixes.popleft()
            options = dict(basicOptions)
            for i, v in enumerate(variations):
                options[str(i + 1)] = v
            text = '{} - {}'.format(album.name, field)

            try:
                a = ask.askOrEnterMultipleChoice(0, text, options)
                if a in options.keys():
                    try:
                        index = int(a) - 1
                        if field in ['compilation', 'disc', 'totalDisc']:
                            self._routeAssign(album, field, int(a))
                        else:
                            self._routeAssign(album, field, variations[index])
                    except ValueError:
                        if a == 'I':
                            pass
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

        return len(self.manualFixes) == 0

    def bail(self):
        return self.userQuit or self.userDiscard

    def conduct(self, args):
        menu = {
            '1': 'Apply Auto Fixes',
            '2': 'Answer questions',
            '3': 'Update Album Names',
            'S': 'Save current edits',
            'X': 'Save current edits and exit',
            'Z': 'Discard current edits and exit'
        }

        self._triage()
        while not self.bail():
            options = dict(menu)
            options['1'] = 'Apply {} auto-fixes'.format(len(self.autoFixes))
            options['2'] = 'Answer {} questions'.format(len(self.manualFixes))

            try:
                a = ask.askMultipleChoice(0, 'Enter a choice', options)
                if a == '1':
                    self.applyAutoFix()
                    self._triage()
                elif a == '2':
                    self.askManualFix()
                    self._triage()
                elif a == '3':
                    self.askAlbumName()
                    self.rebuild()
                    self._triage()
                elif a == 'S':
                    self.save(args.tag_album_file)
                elif a == 'X':
                    self.userQuit = True
                elif a == 'Z':
                    self.userDiscard = True
            except KeyboardInterrupt:
                self.userDiscard = True

# -----------------------------------------------------------------------------
# Action Main

_success = "Success"
_notFinished = "Not Complete"


def process(args):
    result = _notFinished

    fileName = args.tag_album_file
    snapshot = loadJson(fileName)

    instance = AlbumTagger.createFromSnapshot(snapshot)
    instance.conduct(args)
    if not instance.userDiscard:
        instance.save(fileName)
        result = _success

    return result
