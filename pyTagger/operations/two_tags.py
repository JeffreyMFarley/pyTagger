from __future__ import print_function
from __future__ import unicode_literals
import copy
from pyTagger.models import Snapshot


def difference(a, b):
    """Compare two file snapshots and return the difference
    `a` should be considered the source, like the JSON snapshot.
    `b` should be considered the destination, like the file
    """
    result = {}

    # Scope the work
    ka = set(a.keys())
    kb = set(b.keys())
    notb = ka - kb
    kboth = ka & kb

    # copy over the new keys
    for k in notb:
        result[k] = a[k]

    # look for the smaller differences
    for k in kboth:
        if k not in Snapshot.complexTags:
            if a[k] != b[k]:
                result[k] = a[k] if a[k] else None
        elif k in Snapshot.dltTags:
            result[k] = _differenceDLT(a[k], b[k])
        elif k == 'ufid':  # pragma: no branch
            result[k] = difference(a[k], b[k])

        # if there are no members of a collection, remove the collection
        if k in Snapshot.complexTags:
            if not result[k]:
                del result[k]

    return result


def _differenceDLT(a, b):
    """ Compares collections of Description, Language, Text tuples
    """
    result = []

    for a0 in a:
        toTest = list(
            filter(
                lambda x, y=a0: x['lang'] == y['lang']
                and x['description'] == y['description'], b
            )
        )
        if not toTest and a0['text']:
            result.append(a0)
        else:
            for b0 in toTest:
                if a0['text'] != b0['text']:
                    result.append(a0)
                    break

    return result


def union(newer, older):
    """Create a union of two file snapshots

    When both snapshots have the same key, the value in `newer` will be chosen
    """
    c = {}
    if not older:
        c = copy.deepcopy(newer)
        for k in Snapshot.mp3Info:
            if k in c:
                del c[k]

    else:
        keys = set(newer.keys()) | set(older.keys())
        keys = keys - set(Snapshot.mp3Info)
        for k in keys:
            if k in older and k in newer:
                if older[k]:
                    c[k] = older[k]
                else:
                    c[k] = newer[k]
            elif k in older:
                c[k] = older[k]
            else:
                c[k] = newer[k]

    return c
