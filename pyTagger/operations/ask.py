from __future__ import print_function
from __future__ import unicode_literals
import os
import sys
import textwrap
from hew import Normalizer

normalizer = Normalizer()

def get_input():  # pragma: no cover
    if sys.version < '3':
        return raw_input('> ').upper()
    else:
        return input('> ').upper()


def wrapped_out(i, s):
    global normalizer

    lead = '{0}. '.format(i) if i else ''
    wrapper = textwrap.TextWrapper(width=80, initial_indent=lead,
                                   subsequent_indent=' ' * len(lead))
    s = normalizer.to_ascii(s)
    s = wrapper.fill(s)
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

        a = get_input()

    return a
