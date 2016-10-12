from __future__ import print_function
from __future__ import unicode_literals
import os
import sys
import textwrap


def wrapped_out(i, s):
    lead = '{0}. '.format(i)
    wrapper = textwrap.TextWrapper(width=80, initial_indent=lead,
                                   subsequent_indent=' ' * len(lead))
    s = wrapper.fill(s)
    print(s)


def askMultipleChoice(i, title, choices):
    a = None
    while a not in choices:
        os.system('cls' if os.name == 'nt' else 'clear')

        wrapped_out(i, title)
        print('\n')

        for k in sorted(choices):
            wrapped_out(k, choices[k])
        print('\n')

        if sys.version < '3':
            a = raw_input('> ').upper()
        else:
            a = input('> ').upper()

    return a
