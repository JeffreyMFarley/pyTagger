from __future__ import unicode_literals
import binascii
import hashlib
import logging
import eyed3
from configargparse import getArgumentParser
from hew import Normalizer
from pyTagger.utils import configurationOptions, defaultConfigFiles

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
# Classes
# -----------------------------------------------------------------------------


class ID3Proxy(object):
    _projection = {
        'album': lambda x: x.tag.album,
        'albumArtist': lambda x: x.tag.album_artist,
        'artist': lambda x: x.tag.artist,
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
        'id': lambda x: _extractTaggerId(x),
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
        'ufid': lambda x: _extractFileIds(x),
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
        chunk_size = 1024
        offset = (track.tag.header.tag_size
                  if track.tag and track.tag.header
                  else 0)
        shaAccum = hashlib.sha1()
        try:
            with open(mp3FileName, "rb") as f:
                f.seek(offset)
                byte = f.read(chunk_size)
                while byte:
                    shaAccum.update(byte)
                    byte = f.read(chunk_size)
        except IOError:
            self.log.error("Cannot Hash '%s'", self.normalize(mp3FileName))
            return ''
        return binascii.b2a_base64(shaAccum.digest()).strip()

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
