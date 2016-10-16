import os
import argparse
import itertools
import logging
import shutil
from hew import Normalizer
from pyTagger.models import Snapshot
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import walk

winFileReserved = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '.']
winFileTable = {ord(c): u'_' for c in winFileReserved}

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------


def RemoveBadFileNameChars(s):
    return s.translate(winFileTable)


def Limit(s, maxChars):
    return s[:maxChars]

# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class Rename(object):
    def __init__(self, destDir):
        self.normalizer = Normalizer()
        self.log = logging.getLogger(__name__)
        self.destDir = destDir if destDir else os.getcwd()
        if self.destDir[-1] != os.path.sep:
            self.destDir += os.path.sep

    def _buildReader(self):
        fields = list(itertools.chain(Snapshot.basic, Snapshot.distribution))
        fields.append('compilation')
        return ID3Proxy(fields)

    # -------------------------------------------------------------------------
    # Path Methods
    # -------------------------------------------------------------------------

    def buildPath(self, tags, ext=None):
        safeGet = lambda x: tags[x] if x in tags else None
        pipeline = lambda x, n: Limit(RemoveBadFileNameChars(x).strip(' _'), n)

        album = safeGet('album')
        if not album:
            raise ValueError('Album Name must be provided')

        if safeGet('compilation'):
            artist = u'Compilations'
        else:
            artist = safeGet('albumArtist') or safeGet('artist')
            if not artist:
                raise ValueError('Artist must be provided')

        title = safeGet('title')
        if not title:
            raise ValueError('Title must be provided')

        jointedPath = [pipeline(artist, 40), pipeline(album, 40)]

        totalDisc = safeGet('totalDisc') or 1
        if totalDisc > 1:
            fileName = u'{0:02d}-'.format(safeGet('disc') or 0)
        else:
            fileName = u''

        fileName += u'{0:02d} {1}'.format(safeGet('track') or 0,
                                          pipeline(title, 100))
        fileName = u'{0}.{1}'.format(Limit(fileName, 36),
                                     u'mp3' if not ext else ext)

        jointedPath.append(fileName)
        return jointedPath

    def needsMove(self, current, proposed):
        if current == proposed:
            return False

        if os.path.exists(proposed):
            raise ValueError(proposed + ' already exists. Avoiding collision')

        return True

    # -------------------------------------------------------------------------
    # Main Methods
    # -------------------------------------------------------------------------

    def run(self, directory):
        log = logging.getLogger('eyed3')
        log.setLevel(logging.ERROR)

        reader = self._buildReader()

        for fullPath in walk(directory):
            try:
                asciified = self.normalizer.to_ascii(fullPath)
                self.log.info("Reading '%s'", asciified)
                tags = reader.extractTags(fullPath)
                relativePath = self.buildPath(tags, fullPath[-3:])
                proposed = os.path.join(self.destDir, *relativePath)
                if self.needsMove(fullPath, proposed):
                    newPath = os.path.join(self.destDir,
                                           relativePath[0],
                                           relativePath[1], '')
                    if not os.path.exists(newPath):
                        os.makedirs(newPath)
                    self.log.info("Moving to '%s'", proposed)
                    shutil.move(fullPath, proposed)
                else:
                    self.log.info('Same name... Skipping')

            except ValueError as ve:
                self.log.error("%s", ve)
# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def buildArgParser():
    description = 'Rename MP3 files'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('sourceDir',  nargs='?', metavar='sourceDir',
                   default=os.getcwd(),
                   help='the path to scan')
    p.add_argument('destDir',  nargs='?', metavar='destDir',
                   default=None,
                   help='the directory where the files will be moved to')

    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()

    pipeline = Rename(args.destDir)
    pipeline.log.setLevel(logging.INFO)
    pipeline.run(args.sourceDir)
