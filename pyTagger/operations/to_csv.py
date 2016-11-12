from __future__ import unicode_literals
import io
from pyTagger.models import Snapshot

import sys
if sys.version < '3':  # pragma: no cover
    _unicode = unicode
else:  # pragma: no cover
    _unicode = lambda x: x

# yield from is only available <= Python 3.3
SUBFIELD_SEP = '\u2027'


def _encapsulate(field):
    try:
        if not field:
            return ''
        needDoubleQuotes = [',', '"', '\r', '\n']
        addDoubleQuotes = any([x in field for x in needDoubleQuotes])
        if addDoubleQuotes:
            return '"' + field.replace('"', '""') + '"'
        return field
    except (TypeError, AttributeError):
        return str(field)


def flattenOne(row):
    for k, v in row.items():
        if k in ['comments', 'lyrics']:
            for x in v:
                k0 = '{0}{1}{2}{1}{3}'.format(k, SUBFIELD_SEP,
                                              x['lang'], x['description'])
                yield (k0, x['text'])
        elif k == 'ufid':
            for owner, ufid in v.items():
                k0 = 'ufid{0}{1}'.format(SUBFIELD_SEP, owner)
                yield (k0, ufid)
        else:
            yield (k, v)


def flattenSnapshot(snapshot):
    for _, row in snapshot.items():
        for k, v in flattenOne(row):
            yield (k, v)


def listFlattenedColumns(snapshot):
    header = set(k for k, _ in flattenSnapshot(snapshot))

    # Build the ordered set with the extra columns at the end
    known = Snapshot.orderedAllColumns()
    unknown = header - set(known)

    columns = [c for c in known if c in header]
    for c in sorted(unknown):
        columns.append(c)

    return columns


def writeCsv(snapshot, outFileName, excelFormat=True):
    columns = listFlattenedColumns(snapshot)
    columns.append('fullPath')

    # not using csv.DictWriter since the Python 2.x version has a hard time
    # supporting unicode
    with io.open(outFileName, 'w', encoding='utf_16_le', newline='') as f:
        sep = '\t' if excelFormat else ','

        # write BOM
        f.write('\ufeff')

        # write the header row
        a = sep.join([_encapsulate(col) for col in columns])
        f.writelines([a, '\n'])

        # write the rows
        for k in sorted(snapshot):
            row = snapshot[k]
            row['fullPath'] = k

            flattened = dict(flattenOne(row))

            a = sep.join([_encapsulate(flattened[col])
                          if col in flattened else ''
                          for col in columns])
            f.writelines([a, '\n'])
