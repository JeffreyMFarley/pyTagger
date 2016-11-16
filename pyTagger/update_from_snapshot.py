# -*- coding: utf-8 -*

import sys
import argparse
import logging
import binascii
if sys.version < '3':  # pragma: no cover
    _unicode = unicode
else:  # pragma: no cover
    _unicode = lambda x: x
from hew import Normalizer
from pyTagger.models import Snapshot
from pyTagger.operations.two_tags import difference
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import loadJson

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class UpdateFromSnapshot(object):
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

    def __init__(self):
        self.reader = ID3Proxy()
        self.log = logging.getLogger(__name__)
        self.normalizer = Normalizer()

    def update(self, inFileName, fieldSet=None, upgrade=False):
        self.upgrade = upgrade

        snapshot = loadJson(inFileName)

        if not fieldSet:
            fieldSet = Snapshot.columnsFromSnapshot(snapshot)
        self.reader = ID3Proxy(fieldSet)

        for k, v in snapshot.items():
            k0 = self.normalizer.to_ascii(k)
            self.log.info("Updating '%s'", k0)
            try:
                self.updateOne(k, v)
            except AssertionError as assertEx:
                self.log.error("'%s' Assertion Error %s", k0, assertEx.args)
            except Exception:
                self.log.error("'%s' Error %s", k0, sys.exc_info()[0])

    def updateOne(self, fileName, updates):
        track = self.reader.loadID3(fileName)
        if not track or not track.tag:
            return

        version = self._compliance(track)
        asIs = self.reader.extractTagsFromTrack(track)
        delta = difference(updates, asIs)
        self._writeSimple(track, delta)
        self._writeCollection(track, delta)
        self._saveID3(track, version)

    def _compliance(self, track):
        version = track.tag.version
        if version[1] == 2:
            version = (2, 3, 0)

        if self.upgrade and version[1] < 3:
            version = (2, 3, 0)

        # MJMD tag was in some Jen files
        if 'MJMD' in track.tag.frame_set:
            del track.tag.frame_set['MJMD']

        if version[1] == 3:
            hasMood = track.tag.getTextFrame('TMOO')
            if hasMood:
                track.tag.setTextFrame('TMOO', None)

        return version

    def _saveID3(self, track, version=None):
        if not version:
            track.tag.save()
        else:
            track.tag.save(version=version)

    def _writeSimple(self, track, tags):
        import eyed3

        for k, v in tags.items():
            if k in Snapshot.complexTags:
                continue

            assert not isinstance(v, (list, set, dict))
            text = _unicode(v) if v else None

            # pick setting the value based on a strategy
            if k in self._useSetAttr and v:
                setattr(track.tag, self._useSetAttr[k], v)
            elif k in self._useSetAttrString:
                setattr(track.tag, self._useSetAttrString[k], text)
            elif k in self._useSetAttrDate:
                date = eyed3.core.Date.parse(v) if v else None
                setattr(track.tag, self._useSetAttrDate[k], date)
            elif k in self._useSetTextFrame:
                track.tag.setTextFrame(self._useSetTextFrame[k], text),
            elif k == 'year':
                for dateAttr in self._useSetAttrDate.values():
                    setattr(track.tag, dateAttr, None)
                date = eyed3.core.Date.parse(v) if v else None
                track.tag.recording_date = date
            elif k == 'disc':
                track.tag.disc_num = (v, track.tag.disc_num[1])
            elif k == 'totalDisc':
                track.tag.disc_num = (track.tag.disc_num[0], v)
            elif k == 'totalTrack':
                track.tag.track_num = (track.tag.track_num[0], v)
            elif k == 'track':
                track.tag.track_num = (v, track.tag.track_num[1])

    def _writeCollection(self, track, tags):
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

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def buildArgParser():
    description = 'Update tag values in MP3s from a snapshot'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('infile', metavar='infile', help='the snapshot to process')
    p.add_argument('-b', '--basic', action='store_true', dest='basic',
                   help='Only update: ' + ' '.join(Snapshot.basic))
    p.add_argument('-s', '--songwriting', action='store_true',
                   dest='songwriting',
                   help='Only update: ' + ' '.join(Snapshot.songwriting))
    p.add_argument('-p', '--production', action='store_true',
                   dest='production',
                   help='Only update: ' + ' '.join(Snapshot.production))
    p.add_argument('-d', '--distribution', action='store_true',
                   dest='distribution',
                   help='Only update: ' + ' '.join(Snapshot.distribution))
    p.add_argument('-l', '--library', action='store_true', dest='library',
                   help='Only update: ' + ' '.join(Snapshot.library))
    p.add_argument('-a', '--all', action='store_true', dest='all',
                   help='include all supported fields')
    p.add_argument('--upgrade', action='store_true', dest='upgrade',
                   help='Upgrade the tags to be at least 2.3')

    return p

#sys.argv = ['update_from_snapshot', '--all', '--upgrade',
#            r'c:\Users\Jeff\Music\update.json']

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()
    columns = Snapshot.columnsFromArgs(args)

    pipeline = UpdateFromSnapshot()
    pipeline.log.setLevel(logging.INFO)
    pipeline.update(args.infile, columns, args.upgrade)
