from __future__ import unicode_literals
import io
import json
import sys
from pyTagger.utils import walk
if sys.version < '3':  # pragma: no cover
    _unicode = unicode
else:  # pragma: no cover
    _unicode = lambda x: x


def buildSnapshot(scanPath, outFileName, id3Reader, compact=False):
    try:
        fout = io.open(outFileName, 'w', encoding='utf-8')
        fout.writelines('{')
        sep = ''
        indent = None if compact else 2

        for fullPath in walk(scanPath):
            row = id3Reader.extractTags(fullPath)
            if row:
                fout.writelines([sep, '"',
                                 fullPath.replace('\\', '\\\\'),
                                 '":'])
                fout.write(_unicode(json.dumps(
                    row, ensure_ascii=False, indent=indent
                )))
                sep = ','

    finally:
        fout.writelines('}')
        fout.close()
