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
"""Possible locations for the configuration file"""

rootParser = getArgumentParser(
    default_config_files=defaultConfigFiles,
    args_for_setting_config_path=['--config'],
    args_for_writing_out_config_file=['--save-config']
)


def configurationOptions(name):
    """Gets the set of known arguments from a specific parser

    Args:
       name (str):  The name of the parser to get options from

    Returns:
        An object with the options as attributes
    """
    p = getArgumentParser(name)
    options, _ = p.parse_known_args()
    return options

# -----------------------------------------------------------------------------


def toAbsolute(path):
    """Determines the absolute path from a relative path

    Args:
        path (str): A path relative to ``setup.py``

    Returns:
        The absolute path
    """
    # where is _this_ script?
    thisScriptDir = os.path.dirname(__file__)

    # get the expected paths
    return os.path.join(thisScriptDir, path)


def loadJson(fileName):
    """Provides an application-wide standard for loading JSON files

    The application standard uses UTF-8 and no newline translation

    Args:
        fileName (str): The absolute path to a JSON file

    Returns:
        A fully-loaded, deserialized version of the JSON file
    """
    with io.open(fileName, 'r', encoding='utf-8', newline='') as f:
        return json.load(f)


def saveJson(fileName, o):
    """Provides an application-wide standard for saving JSON files

    Args:
        fileName (str): The absolute path to where the JSON file should be
        written

        o (object):     The object that will be written out

    These steps are used for writing the JSON in the application's standard:
      1. Convert the *entire* object to a JSON string
      2. Ensure the string is Unicode
      3. Write out to the filename using UTF-8 encoding

    """
    with io.open(fileName, 'w', encoding='utf-8', newline='') as f:
        f.write(_unicode(json.dumps(o, ensure_ascii=False)))


def saveJsonIncrementalArray(fileName):
    """Provides a way to write an array to a JSON file, one item at a time

    The JSON file is written using the same standards as :func:`saveJson`

    Args:
        fileName (str): The absolute path to where the JSON file should be
        written

    Yields:
        int: The current number of rows processed

    **Example Usage:**

    .. code-block:: python

       output = saveJsonIncrementalArray(fileName)

       counted = next(output)

       for row in someArray:
           counted = output.send(row)

       output.close()

    """
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
    """Provides a way to write a dictionary to a JSON file, one item at a time

    The JSON file is written using the same standards as :func:`saveJson`

    Args:
        fileName (str): The absolute path to where the JSON file should be
        written

        compact (bool): ``True`` if the resulting JSON should be written as
        densely as possible

    Yields:
        int: The current number of rows processed

    **Example Usage:**

    .. code-block:: python

       output = saveJsonIncrementalDict(fileName)

       counted = next(output)

       for key, value in someDict.items():
           pair = (key, value)
           counted = output.send(pair)

       output.close()

    """
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
    """Generate a unique identifer

    Returns:
        str: A 24 character string that should be unique across time and space
    """
    ufid = uuid.uuid4()
    return binascii.b2a_base64(ufid.bytes).strip()


# -----------------------------------------------------------------------------
# Functional FTW

def fmap(fns, x):
    """A version of the Haskell `functor` concept

    Args:
        fns (list[functions]): A list of functions to apply.

        x (object): The object that will be passed to all functions

    Returns:
        The value of ``x`` after calling the last function

    All the functions should have the same signature: ``def foo(x) -> x``
    """
    for fn in fns:
        x = fn(x)
    return x
