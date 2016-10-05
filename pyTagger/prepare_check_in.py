import re
import os
import argparse
import logging
import datetime
import uuid
import binascii
from pymonad.Reader import curry
from pyTagger import UpdateFromSnapshot, Mp3Snapshot
from pyTagger.utils import walk
from pyTagger.mp3_snapshot import Formatter


@curry
def strip(phrase, x):
    if phrase in x:
        return x.replace(phrase, '')
    return x


@curry
def stripBracketedText(regex, s):
    if '[' in s:
        while '[' in s:
            m = regex.match(s)
            if not m:  # no closing bracket, strip to end
                openBracket = s.index('[')
                s = s[:openBracket]
            else:
                s = m.group(1).strip() + m.group(3).strip()
    return s


class PrepareCheckIn(object):
    """description of class"""

    def __init__(self):
        self.stripFields = {'title', 'album'}
        self.featuring = {'artist'}
        self.addTags = {'media', 'ufid', 'comments', 'group', 'subtitle'}

        self.reader = Mp3Snapshot()
        self.readerFormatter = Formatter(self.stripFields
                                         .union(self.featuring))

        self.updater = UpdateFromSnapshot()
        self.updater.formatter = Formatter(self.stripFields
                                           .union(self.featuring)
                                           .union(self.addTags))
        self.updater.upgrade = True

        self.regexFeature = re.compile('\((feat|feat\.|featuring|with) (.*)\)')

        self.normalizers = [
            stripBracketedText(re.compile('^(.*)(\[.*\])+(.*)$')),
            strip(' (Explicit Version)'),
            strip(' (Explicit)'),
            strip(' (Explicit Content)'),
            strip(' (US Version)'),
            strip(' (US Release)'),
            strip(' (Album Version)'),
            strip(' (LP Version)'),
            strip(' (Deluxe)'),
            strip(' (Deluxe Edition)'),
            strip(' (Deluxe Version)'),
            strip(' (Amazon MP3 Exclusive Version)'),
            strip(' (Amazon MP3 Exclusive - Deluxe Version)'),
            strip(' (Original Motion Picture Soundtrack)'),
            strip(' (Special Edition)')
        ]

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def prepareText(self, s):
        for fn in self.normalizers:
            s = fn(s)
        return s

    def extractArtist(self, s):
        m = self.regexFeature.match(s)
        if m:
            replace = ' ({0} {1})'.replace(m.group(1), m.group(2))
            s = s.replace(replace, '')
            return s, m.group(2)
        else:
            return s, None

    def getTags(self, fullPath):
        return self.reader.extractTags(fullPath, self.readerFormatter)

    # -------------------------------------------------------------------------
    # Process
    # -------------------------------------------------------------------------

    def _process(self, fullPath):
        tags = self.getTags(fullPath)
        for k in self.stripFields:
            tags[k] = self.prepareText(tags[k])

        stamp = datetime.date.today()
        ufid = uuid.uuid4()
        asString = binascii.b2a_base64(ufid.bytes).strip()
        preparationTags = {
            'media': 'DIG',
            'ufid': {'DJTagger': asString},
            'comments': [
                {'lang': 'eng', 'text': '', 'description': ''},
                {'lang': '', 'text': '', 'description': ''}
            ],
            'group': '',
            'subtitle': stamp.isoformat()
        }
        tags.update(preparationTags)
        self.updater._updateOne(fullPath, tags)

    def run(self, path, supressWarnings=True):
        if supressWarnings:
            log = logging.getLogger('eyed3')
            log.setLevel(logging.ERROR)

        for fullPath in walk(path):
            self._process(fullPath)

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

# debugging
#sys.argv = [sys.argv[0], r'C:\Users\Jeff\Music\Amazon MP3']


def buildArgParser():
    description = 'Update basic fields in a directory'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('path',  nargs='?', metavar='path',
                   default=os.getcwd(),
                   help='the directory to process')
    p.add_argument('--suppress', action='store_true', dest='supressWarnings',
                   help='supress eyed3 warnings')

    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()

    pipeline = PrepareCheckIn()
    pipeline.run(args.path, args.supressWarnings)
