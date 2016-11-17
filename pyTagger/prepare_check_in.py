import re
import os
import argparse
import datetime
from functools import partial
from pyTagger.operations.on_mp3 import updateOne
from pyTagger.proxies.id3 import ID3Proxy
from pyTagger.utils import walk, generateUfid


def strip(phrase, x):
    if phrase in x:
        return x.replace(phrase, '')
    return x


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

        self.reader = ID3Proxy(
            self.stripFields.union(self.featuring).union(self.addTags)
        )

        self.regexFeature = re.compile('\((feat|feat\.|featuring|with) (.*)\)')

        self.normalizers = [
            partial(stripBracketedText, re.compile('^(.*)(\[.*\])+(.*)$')),
            partial(strip, ' (Explicit Version)'),
            partial(strip, ' (Explicit)'),
            partial(strip, ' (Explicit Content)'),
            partial(strip, ' (US Version)'),
            partial(strip, ' (US Release)'),
            partial(strip, ' (Album Version)'),
            partial(strip, ' (LP Version)'),
            partial(strip, ' (Deluxe)'),
            partial(strip, ' (Deluxe Edition)'),
            partial(strip, ' (Deluxe Version)'),
            partial(strip, ' (Amazon MP3 Exclusive Version)'),
            partial(strip, ' (Amazon MP3 Exclusive - Deluxe Version)'),
            partial(strip, ' (Original Motion Picture Soundtrack)'),
            partial(strip, ' (Special Edition)'),
            partial(strip, ' (Remastered)')
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
        return self.reader.extractTags(fullPath)

    # -------------------------------------------------------------------------
    # Process
    # -------------------------------------------------------------------------

    def _process(self, fullPath):
        tags = self.getTags(fullPath)
        for k in self.stripFields:
            tags[k] = self.prepareText(tags[k])

        stamp = datetime.date.today()
        ufid = generateUfid()
        preparationTags = {
            'media': 'DIG',
            'ufid': {'DJTagger': ufid},
            'comments': [
                {'lang': 'eng', 'text': '', 'description': ''},
                {'lang': '', 'text': '', 'description': ''}
            ],
            'group': '',
            'subtitle': stamp.isoformat()
        }
        tags.update(preparationTags)
        updateOne(self.reader, fullPath, tags, True)

    def run(self, path):
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

    return p

if __name__ == '__main__':
    parser = buildArgParser()
    args = parser.parse_args()

    pipeline = PrepareCheckIn()
    pipeline.run(args.path)
