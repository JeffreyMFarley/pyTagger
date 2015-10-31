''' Provides a set of normalizing functions
'''
import sys
if sys.version < '3':
    import unicodedata
from pymonad.Reader import *

#-------------------------------------------------------------------------------
# builders
#-------------------------------------------------------------------------------

def buildRomanizeReplace():
    ''' This table for the `translate` function replaces one character for another 
    '''
    if sys.version >= '3':
        table = dict.fromkeys(c for c in range(sys.maxunicode)
                                if unicodedata.combining(chr(c)))
    else:
        table = dict.fromkeys(c for c in range(sys.maxunicode)
                                if unicodedata.combining(unichr(c)))

    # latin extended not handled by decombining
    table[0xf0] = ord('d')      # eth
    table[0xd8] = ord('O')      # oe
    table[0xf8] = ord('o')      # oe

    table[0x0110] = ord('D')    # D bar
    table[0x0111] = ord('d')    # d bar

    # polish
    table[0x0141] = ord('L')    # l with stroke
    table[0x0142] = ord('l')    # l with stroke

    # greek
    table[0x3b1] = ord('a')
    table[0x3b4] = ord('d')

    table[0xfeff] = ord(' ')
    return table

def buildRomanizeExpand():
    table = {}
    table['\xdf'] = 'ss'  # sharp s
    table['\xe6'] = 'ae'  # ligature
    table['\xde'] = 'Th'  # thorn
    table['\xfe'] = 'th'  # thorn
    return table

def buildDefaultExpand():
    table = {}
    table['&'] = 'and'
    table['+'] = 'and'
    return table

def buildPunctuation():
    """ Creates the list of punctuation
    """
    punctCat = ['P', 'S', 'Z']
    if sys.version >= '3':
        punct = [c
                 for c in range(sys.maxunicode) 
                 if unicodedata.category(chr(c))[0] in punctCat]
    else:
        punct = [c 
                 for c in range(sys.maxunicode)
                 if unicodedata.category(unichr(c))[0] in punctCat]
    return punct

def buildDefaultIgnore():
    """ Creates the default list of tokens to ignore
    """
    ignore = []
    ignore.append('the')
    ignore.append('a')
    ignore.append('an')
    return ignore

#-------------------------------------------------------------------------------
# string -> string functions
#-------------------------------------------------------------------------------

@curry
def removePunctuation(s):
    return s

@curry
def replace(table, s):
    b = unicodedata.normalize('NFKD', s)
    s = b.translate(table)
    return s

@curry
def expand(table, s):
    s0 = s
    for c in s:
        if c in table:
            s0 = s0.replace(c, table[c])
    return s0

#-------------------------------------------------------------------------------
# Class
#-------------------------------------------------------------------------------

class Normalizer(object):
    def __init__(self):
        pass

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print(len(buildPunctuation()))
#    print('this is intended to be used as a helper class and not a free-executing script')
