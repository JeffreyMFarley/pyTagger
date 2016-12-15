from __future__ import unicode_literals
import binascii
import io
import json
import os
import sys
import uuid
from configargparse import getArgumentParser
from itertools import count

if sys.version < '3':  # pragma: no cover
    _unicode = unicode
else:  # pragma: no cover
    _unicode = lambda x: x

# -----------------------------------------------------------------------------

defaultConfigFiles = ['./config.ini', '~/pyTagger.ini']

rootParser = getArgumentParser(
    default_config_files=defaultConfigFiles,
    args_for_setting_config_path=['--config'],
    args_for_writing_out_config_file=['--save-config']
)


def configurationOptions(name):
    p = getArgumentParser(name)
    options, _ = p.parse_known_args()
    return options

# -----------------------------------------------------------------------------


def toAbsolute(path):
    # where is _this_ script?
    thisScriptDir = os.path.dirname(__file__)

    # get the expected paths
    return os.path.join(thisScriptDir, path)


def loadJson(fileName):
    with io.open(fileName, 'r', encoding='utf-8', newline='') as f:
        return json.load(f)


def saveJson(fileName, o):
    with io.open(fileName, 'w', encoding='utf-8', newline='') as f:
        f.write(_unicode(json.dumps(o, ensure_ascii=False)))


def saveJsonIncrementalArray(fileName):
    sep = '\n'
    with io.open(fileName, 'w', encoding='utf-8', newline='') as f:
        f.write('[')
        try:
            for i in count():  # pragma: no branch
                row = yield i
                f.write(sep)
                f.write(_unicode(json.dumps(row, ensure_ascii=False)))
                sep = ',\n'
        finally:
            f.write('\n]')


def saveJsonIncrementalDict(fileName, compact=False):
    sep = '\n'
    indent = None if compact else 2

    with io.open(fileName, 'w', encoding='utf-8', newline='') as f:
        f.write('{')

        try:
            for i in count():  # pragma: no branch
                key, value = yield i

                f.write(sep)
                f.write('"{0}":\n'.format(key))
                f.write(_unicode(json.dumps(
                    value, ensure_ascii=False, indent=indent
                )))
                sep = ',\n'

        finally:
            f.write('\n}')

# -----------------------------------------------------------------------------


def generateUfid():
    ufid = uuid.uuid4()
    return binascii.b2a_base64(ufid.bytes).strip()


# -----------------------------------------------------------------------------
# Functional FTW

def fmap(fns, x):
    for fn in fns:
        x = fn(x)
    return x
