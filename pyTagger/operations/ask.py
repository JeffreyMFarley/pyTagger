from __future__ import print_function
from __future__ import unicode_literals
import os
import sys
import textwrap
from hew import Normalizer

if sys.version < '3':  # pragma: no cover
    _unicode = unicode
else:  # pragma: no cover
    _unicode = lambda x: x


normalizer = Normalizer()


def get_input():  # pragma: no cover
    if sys.version < '3':
        return raw_input('> ')
    else:
        return input('> ')


def wrapped_out(i, v):
    lead = '{0}. '.format(i) if i else ''
    wrapper = textwrap.TextWrapper(width=80, initial_indent=lead,
                                   subsequent_indent=' ' * len(lead))
    s = '{}'.format(v or u'(blank)')
    s = normalizer.to_ascii(s)
    lines = [wrapper.fill(x) for x in s.splitlines()]
    s = os.linesep.join(lines)
    print(s)


def askMultipleChoice(i, title, choices, clear=True):
    a = None
    while a not in choices:
        if clear:
            os.system('cls' if os.name == 'nt' else 'clear')

        wrapped_out(i, title)
        print('\n')

        for k in sorted(choices):
            wrapped_out(k, choices[k])
        print('\n')

        a = get_input().upper()

    return a


def askOrEnterMultipleChoice(i, title, choices, clear=True):
    a = None
    if clear:
        os.system('cls' if os.name == 'nt' else 'clear')

    wrapped_out(i, title)
    print('\n')

    for k in sorted(choices):
        wrapped_out(k, choices[k])
    print('\n')

    a = get_input()
    if a.upper() in choices.keys():
        return a.upper()

    return _unicode(a)
