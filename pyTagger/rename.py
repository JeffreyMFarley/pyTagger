
from __future__ import print_function
import os
import sys
import argparse
import itertools
import logging
if sys.version < '3':
    import codecs
    _input = lambda fileName: codecs.open(fileName, 'r', encoding='utf-8')
else:
    _input = lambda fileName: open(fileName, 'r', encoding='utf-8')
from pyTagger.mp3_snapshot import Formatter, Mp3Snapshot

winFileReserved = ['\\', '/', ':', '*', '?', '"', '<', '>', '|', '.']
winFileTable = {ord(c):u'_' for c in winFileReserved}

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

class Rename():
    def __init__(self, destDir):
        self.destDir = destDir if destDir else os.getcwd()
        if not os.path.exists(self.destDir):
            os.makedirs(self.destDir)

    def _buildFormatter(self):
        fields = list(itertools.chain(Formatter.basic, Formatter.distribution))
        fields.append('compilation')
        return Formatter(fields)

    # -------------------------------------------------------------------------
    # Path Methods
    # -------------------------------------------------------------------------

    def buildPath(self, tags, ext=None):
        safeGet = lambda x: tags[x] if x in tags else None 
        pipeline = lambda x, n: RemoveBadFileNameChars(Limit(x.strip(), n))

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

        fileName += u'{0:02d} - {1}'.format(safeGet('track') or 0, 
                                            pipeline(title, 100))
        fileName = u'{0}.{1}'.format(Limit(fileName, 36),
                                     u'mp3' if not ext else ext)
                
        jointedPath.append(fileName)
        return jointedPath

    # -------------------------------------------------------------------------
    # Main Methods
    # -------------------------------------------------------------------------

    def run(self, directory):
        log = logging.getLogger('eyed3')
        log.setLevel(logging.ERROR)

        reader = Mp3Snapshot()
        formatter = self._buildFormatter()

        for currentDir, subdirs, files in os.walk(unicode(directory)):
            # Get the absolute path of the currentDir parameter
            currentDir = os.path.abspath(currentDir)

            # Traverse through all files
            for fileName in files:
                fullPath = os.path.join(currentDir, fileName)

                # Check if the file has an extension of typical music files
                if fullPath[-3:].lower() in ['mp3']:
                    print("Extracting", formatter.normalizeToAscii(fullPath))
                    tags = reader.extractTags(fullPath, formatter)
                    relativePath = self.buildPath(tags, fullPath[-3:])
                    print(relativePath)

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
    pipeline.run(args.sourceDir)
