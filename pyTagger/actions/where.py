from __future__ import unicode_literals
import os
from configargparse import getArgumentParser
from pyTagger.models import COMPARISON, FilterCondition, Snapshot
from pyTagger.operations.name import _safeGet as safeGet
from pyTagger.utils import defaultConfigFiles, loadJson
from pyTagger.utils import saveJsonIncrementalDict


comparisonParse = {
    '=': COMPARISON.EQUAL,
    '!': COMPARISON.NOT,
    '>': COMPARISON.GT,
    '>=': COMPARISON.GTE,
    '<': COMPARISON.LT,
    '<=': COMPARISON.LTE,
    '%': COMPARISON.LIKE
}


# -----------------------------------------------------------------------------
# Configuration

p = getArgumentParser('where',
                      default_config_files=defaultConfigFiles,
                      ignore_unknown_config_file_keys=True,
                      parents=[getArgumentParser()],
                      description='select tags that meet specific criteria')
group = p.add_argument_group('Files')
group.add('infile', help='the input snapshot')
group.add('outfile', help='the output snapshot')
group = p.add_argument_group('Fields')
for field in sorted(Snapshot.orderedAllColumns()):
    group.add('--' + field, help='matches on ' + field, nargs='*',
              metavar=('{' + ', '.join(comparisonParse) + '}', 'value'))


# -----------------------------------------------------------------------------

def _buildCondition(x, args):
    values = getattr(args, x)
    if not values:
        raise StopIteration

    if isinstance(values, str):
        values = [values]

    for v in values:
        pair = _parseComparison(x, v)
        if pair:
            yield FilterCondition(x, *pair)


def _parseComparison(field, s):
    if not s:
        return None

    comparison, value = (COMPARISON.LIKE, s)

    if s[:2] in comparisonParse:
        comparison = comparisonParse[s[:2]]
        value = s[2:]

    elif s[0] in comparisonParse:
        comparison = comparisonParse[s[0]]
        value = s[1:]

    if value == 'null':
        value = None

    if field in Snapshot.integerTags:
        value = int(value)

    return comparison, value


def _testCondition(condition, tags):
    tagValue = safeGet(tags, condition.field)
    if condition.comparison == COMPARISON.NOT:
        return tagValue != condition.value
    elif condition.comparison == COMPARISON.GT:
        return tagValue > condition.value
    elif condition.comparison == COMPARISON.GTE:
        return tagValue >= condition.value
    elif condition.comparison == COMPARISON.LT:
        return tagValue < condition.value
    elif condition.comparison == COMPARISON.LTE:
        return tagValue <= condition.value
    elif condition.comparison == COMPARISON.LIKE:
        return condition.value.lower() in tagValue.lower() if tagValue \
            else False
    else:
        return tagValue == condition.value


def process(args):
    conditions = [
        c
        for x in Snapshot.orderedAllColumns()
        for c in _buildCondition(x, args)
    ]

    if not conditions:
        return 'No conditions specified.  Exiting'

    snapshot = loadJson(args.infile)
    output = saveJsonIncrementalDict(args.outfile)
    next(output)

    included = 0
    excluded = 0

    for fullPath, tags in snapshot.items():
        matches = True
        for c in conditions:
            matches &= _testCondition(c, tags)

        if matches:
            pair = (fullPath.replace('\\', '\\\\'), tags)
            output.send(pair)
            included += 1
        else:
            excluded += 1

    output.close()

    return 'Matched {} files\nSkipped {} files'.format(included, excluded)
