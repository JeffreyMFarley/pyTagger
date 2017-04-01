from __future__ import unicode_literals
import binascii
import logging
import eyed3
from configargparse import getArgumentParser
from hew import Normalizer
from pyTagger.models import Snapshot
from pyTagger.operations.hash import hashFile
from pyTagger.utils import configurationOptions, defaultConfigFiles

import sys
if sys.version < '3':  # pragma: no cover
    _unicode = unicode
else:  # pragma: no cover
    _unicode = lambda x: x

# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('id3',
                      default_config_files=defaultConfigFiles,
                      parents=[getArgumentParser()],
                      description='settings for loading MP3 files')
group = p.add_argument_group('id3')
group.add('--id3-logging',
          choices=[logging.NOTSET, logging.INFO, logging.WARNING,
                   logging.ERROR],
          default=logging.WARNING, type=int,
          help='how verbose the id3 client should be')

# -----------------------------------------------------------------------------
# Read Methods
# -----------------------------------------------------------------------------


def _extractDate(date):
    return str(date) if date else ''


def _extractFileIds(track):
    # Python 2.6 does not like dictionary comprehensions
    ids = {}
    for x in track.tag.unique_file_ids:
        ids[x.owner_id] = binascii.b2a_base64(x.uniq_id).strip()
    return ids


def _extractTaggerId(track):
    ufid = ''
    for a0 in track.tag.unique_file_ids:
        if a0.owner_id == 'DJTagger':
            ufid = binascii.b2a_base64(a0.uniq_id).strip()
    return ufid

# -----------------------------------------------------------------------------
# Write Methods
# -----------------------------------------------------------------------------

_useSetAttr = {
    'bpm': 'bpm',
    'playCount': 'play_count',
}

_useSetAttrDate = {
    'encodingDate': 'encoding_date',
    'originalReleaseDate': 'original_release_date',
    'recordingDate': 'recording_date',
    'releaseDate': 'release_date',
    'taggingDate': 'tagging_date'
}

_useSetAttrString = {
    'album': 'album',
    'albumArtist': 'album_artist',
    'artist': 'artist',
    'publisher': 'publisher',
    'title': 'title'
}

_useSetTextFrame = {
    'barcode': 'TSRC',
    'compilation': 'TCMP',
    'composer': 'TCOM',
    'conductor': 'TPE3',
    'genre': 'TCON',
    'group': 'TIT1',
    'key': 'TKEY',
    'language': 'TLAN',
    'media': 'TMED',
    'remixer': 'TPE4',
    'subtitle': 'TIT3'
}


def _writeSimple(track, tags):
    for k, v in tags.items():
        if k in Snapshot.complexTags:
            continue

        assert not isinstance(v, (list, set, dict))
        text = _unicode(v) if v else None

        # pick setting the value based on a strategy
        if k in _useSetAttr and v:
            setattr(track.tag, _useSetAttr[k], v)
        elif k in _useSetAttrString:
            setattr(track.tag, _useSetAttrString[k], text)
        elif k in _useSetAttrDate:
            date = eyed3.core.Date.parse(v) if v else None
            setattr(track.tag, _useSetAttrDate[k], date)
        elif k in _useSetTextFrame:
            track.tag.setTextFrame(_useSetTextFrame[k], text),
        elif k == 'year':
            for dateAttr in _useSetAttrDate.values():
                setattr(track.tag, dateAttr, None)
            date = eyed3.core.Date.parse(v) if v else None
            track.tag.recording_date = date
        elif k == 'disc':
            track.tag.disc_num = (v, track.tag.disc_num[1])
        elif k == 'totalDisc':
            track.tag.disc_num = (track.tag.disc_num[0], v)
        elif k == 'totalTrack':
            track.tag.track_num = (track.tag.track_num[0], v)
        elif k == 'track':  # pragma: no branch
            track.tag.track_num = (v, track.tag.track_num[1])


def _writeCollection(track, tags):
    for k, v in tags.items():
        if k == 'comments':
            for v0 in v:
                l = _unicode(v0['lang'])
                d = _unicode(v0['description'])
                if not v0['text']:
                    track.tag.comments.remove(d, l)
                else:
                    track.tag.comments.set(_unicode(v0['text']), d, l)
        elif k == 'lyrics':
            for v0 in v:
                l = _unicode(v0['lang'])
                d = _unicode(v0['description'])
                if not v0['text']:
                    track.tag.lyrics.remove(d, l)
                else:
                    track.tag.lyrics.set(_unicode(v0['text']), d, l)
        elif k == 'ufid':
            for ufid, value in v.items():
                if not value:
                    track.tag.unique_file_ids.remove(ufid)
                else:
                    toBytes = binascii.a2b_base64(value)
                    # str(ufid) is so Python doesn't try to do ASCII
                    # conversion on the whole string
                    track.tag.unique_file_ids.set(toBytes, str(ufid))


def _update(track, tags):
    _writeSimple(track, tags)
    _writeCollection(track, tags)

# -----------------------------------------------------------------------------
# Compliance Methods
# -----------------------------------------------------------------------------


def _compliance(track, upgrade=False):
    version = track.tag.version
    if version[1] == 2:
        version = (2, 3, 0)

    if upgrade and version[1] < 3:
        version = (2, 3, 0)

    # MJMD tag was in some Jen files
    if 'MJMD' in track.tag.frame_set:
        del track.tag.frame_set['MJMD']

    if version[1] == 3:
        hasMood = track.tag.getTextFrame('TMOO')
        if hasMood:
            track.tag.setTextFrame('TMOO', None)

    return version

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class ID3Proxy(object):
    _projection = {
        'album': lambda x: x.tag.album,
        'albumArtist': lambda x: x.tag.album_artist,
        'artist': lambda x: x.tag.artist,
        'barcode': lambda x:  x.tag.getTextFrame('TSRC'),
        'bitRate':
        lambda x: x.info.bit_rate[1] if x.info is not None else None,
        'bpm': lambda x: x.tag.bpm,
        'comments': lambda x: [{'lang': y.lang,
                                'text': y.text,
                                'description': y.description}
                               for y in x.tag.comments],
        'compilation': lambda x: x.tag.getTextFrame('TCMP'),
        'composer': lambda x: x.tag.getTextFrame('TCOM'),
        'conductor': lambda x: x.tag.getTextFrame('TPE3'),
        'disc': lambda x: x.tag.disc_num[0],
        'encodingDate': lambda x: _extractDate(x.tag.encoding_date),
        'fileHash': lambda x: '',
        'genre': lambda x: x.tag.genre.name if x.tag.genre else '',
        'group': lambda x: x.tag.getTextFrame('TIT1'),
        'id': _extractTaggerId,
        'key': lambda x: x.tag.getTextFrame('TKEY'),
        'language': lambda x: x.tag.getTextFrame('TLAN'),
        'length': lambda x: x.info.time_secs if x.info else '',
        'lyrics': lambda x: [{'lang': y.lang,
                              'text': y.text,
                              'description': y.description}
                             for y in x.tag.lyrics],
        'media': lambda x: x.tag.getTextFrame('TMED'),
        'originalReleaseDate':
        lambda x: _extractDate(x.tag.original_release_date),
        'playCount': lambda x: x.tag.play_count,
        'publisher': lambda x: x.tag.publisher,
        'recordingDate': lambda x: _extractDate(x.tag.recording_date),
        'releaseDate': lambda x: _extractDate(x.tag.release_date),
        'remixer': lambda x: x.tag.getTextFrame('TPE4'),
        'subtitle': lambda x: x.tag.getTextFrame('TIT3'),
        'taggingDate': lambda x: _extractDate(x.tag.tagging_date),
        'title': lambda x: x.tag.title,
        'totalDisc': lambda x: x.tag.disc_num[1],
        'totalTrack': lambda x: x.tag.track_num[1],
        'track': lambda x: x.tag.track_num[0],
        'ufid': _extractFileIds,
        'vbr': lambda x: x.info.bit_rate[0] if x.info is not None else None,
        'version': lambda x: '.'.join([str(y) for y in x.tag.version]),
        'year': lambda x: _extractDate(x.tag.getBestDate()),
    }
    columns = list(_projection.keys())

    def __init__(self, fieldSet=None):
        options = configurationOptions('id3')

        self.fieldSet = self.columns if fieldSet is None else fieldSet
        self.normalize = Normalizer().to_ascii
        self.log = logging.getLogger(__name__)
        self.log.setLevel(options.id3_logging)

        log = logging.getLogger('eyed3')
        log.setLevel(logging.ERROR)

    def _calculateHash(self, track, mp3FileName):
        offset = (track.tag.header.tag_size
                  if track.tag and track.tag.header
                  else 0)
        return hashFile(mp3FileName, offset)

    def extractImages(self, track):
        if track and track.tag and track.tag.images:
            for image in track.tag.images:
                yield image.image_data, image.mime_type.split("/")[1]

    def extractTags(self, mp3FileName):
        track = self.loadID3(mp3FileName)
        if not track:
            return None
        a = self.extractTagsFromTrack(track)
        if 'fileHash' in self.fieldSet:
            a['fileHash'] = self._calculateHash(track, mp3FileName)
        return a

    def extractTagsFromTrack(self, obj):
        if isinstance(obj, eyed3.mp3.Mp3AudioFile) and obj.tag:
            # Python 2.6 does not like dictionary comprehensions
            row = {}
            for k in self.fieldSet:
                row[k] = self._projection[k](obj)
            return row
        return {}

    def loadID3(self, mp3FileName):
        self.log.info("Reading %s", self.normalize(mp3FileName))
        try:
            return eyed3.load(mp3FileName)
        except (IOError, ValueError):
            self.log.error("Cannot load ID3 '%s'", self.normalize(mp3FileName))
            return None

    def saveID3(self, track, tags, upgrade=False):
        self.log.info("Writing %s", self.normalize(track.tag.file_info.name))
        _update(track, tags)
        version = _compliance(track, upgrade)
        track.tag.save(version=version, encoding='utf8')
