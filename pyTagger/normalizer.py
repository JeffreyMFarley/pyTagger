''' Provides a set of normalizing functions
'''
import re
import sys
import unicodedata
from pymonad.Reader import *
from pymonad.List import *
from pymonad.Maybe import * 

if sys.version >= '3':
    _char = chr
else:
    _char = unichr

#-------------------------------------------------------------------------------
# builders
#-------------------------------------------------------------------------------

def buildRomanizeReplace():
    ''' This table for the `translate` function replaces one character for another 
    '''
    table = dict.fromkeys(c for c in range(sys.maxunicode)
                            if unicodedata.combining(_char(c)))

    # latin extended not handled by decombining
    table[0xd0] = ord('D')      # D bar
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
    table['\xc5'] = 'Aa'  # ring a
    table['\xc6'] = 'Ae'  # ligature
    table['\xde'] = 'Th'  # thorn
    table['\xdf'] = 'ss'  # sharp s
    table['\xe5'] = 'aa'  # ring a
    table['\xe6'] = 'ae'  # ligature
    table['\xfe'] = 'th'  # thorn
    return table

def buildPunctuationReplace():
    table = {0xa6 : '|',
             0xb4 : '\'',
             0xb6 : '*',
             0xd7 : 'x',

            0x2022 : '*',   # bullet
            0x2023 : '*',   
            0x2024 : '.',   
            0x2027 : '*',
            0x2032 : "'",
            0x2035 : "'",
            0x2039 : '<',
            0x203a : '>',
            0x2043 : '-',
            0x2044 : '/',
            0x204e : '*',
            0x2053 : '~',
            0x205f : ' ',
            }
    table.update({c :' ' for c in range(0x2000, 0x200a)})
    table.update({c :'-' for c in range(0x2010, 0x2015)})
    table.update({c :"'" for c in range(0x2018, 0x201b)})
    table.update({c :'"' for c in range(0x201c, 0x201f)})

    return table

def buildPunctuationExpand():
    return {'\xa9' : '(C)',
            '\xab' : '<<',
            '\xbb' : '>>',
            '\xae' : '(R)',
            '\xbc' : '1/4',
            '\xbd' : '1/2',
            '\xbe' : '3/4',
            '\x2025' : '..',
            '\x2026' : '...',
            '\x2033' : "''",
            '\x2034' : "'''",
            '\x2036' : "''",
            '\x2037' : "'''",
            '\x203c' : "!!",
            '\x2047' : "??",
            '\x2048' : "?!",
            '\x2049' : "!?",
            '\x2057' : "''''",
            }

def listAllPunctuation():
    """ Creates the list of all punctuation and symbols"""
    punctCat = ['P', 'S', 'Z']
    punct = [c
             for c in range(sys.maxunicode) 
             if unicodedata.category(_char(c))[0] in punctCat]
    return punct

def windowsFileNameReserved():
    reserved = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    return {ord(c):'_' for c in reserved}

def uriReserved():
    reserved =  ['!', '#', '$', '&', "'", '(', ')', '*', '+', ',', '/', ':', 
                 ';', '=', '?', '@', '[', ']', '%']
    return {ord(c):'%{0:02X}'.format(ord(c)) for c in reserved}

#------------------------------------------------------------------------------
# Generators
#------------------------------------------------------------------------------

def tokenize(s):
    for i, x in enumerate(re.split('(\W+)', s)):
        if i % 2 == 0:
            yield x
        else:
            for c in x:
                if c != ' ':
                    yield c

def expandToken(table, tokens):
    for s in tokens:
        if s in table:
            for x in table[s]:
                yield x
        else:
            yield s

#------------------------------------------------------------------------------
# Monads
#------------------------------------------------------------------------------

@curry
def ignoreToken(table, s):
    return Nothing if s in table else Just(s)

@curry
def replaceToken(table, s):
    return Just(table[s]) if s in table else Just(s)

@curry
def replaceCharacters(table, s):
    b = unicodedata.normalize('NFKD', s)
    s = b.translate(table)
    return Just(s)

@curry
def expandCharacters(table, s):
    expanded = [table[c] if c in table else c for c in s]
    return Just(''.join(expanded))

#-------------------------------------------------------------------------------
# Class
#-------------------------------------------------------------------------------

class Normalizer(object):
    def __init__(self):
        self.tokenReplace = {'&': 'and', '+': 'and'}
        self.tokenIgnore = ['the', 'a', 'an']
        self.tokenExpand = {}
        self.charExpand = {}
        self.charReplace = {}
        self.charIgnore = []

    def to_ascii(self, s):

        cr = buildRomanizeReplace()
        cr.update(buildPunctuationReplace())
        cr.update(self.charReplace)

        ce = buildRomanizeExpand()
        ce.update(buildPunctuationExpand())
        ce.update(self.charExpand)

        ci = {c:None for c in listAllPunctuation() if c > 0x7f}
        ci.update(dict.fromkeys(self.charIgnore))

        parts = []
        for token in tokenize(s):
            part = Just(token) 
            part >>= expandCharacters(ce)
            part >>= replaceCharacters(cr)
            part >>= replaceCharacters(ci)
            parts.append(part)

        joined = ' '. join([x.value for x in parts if x.value])
        return joined

    def to_key(self, s):

        cr = buildRomanizeReplace()
        cr.update(self.charReplace)

        ce = buildRomanizeExpand()
        ce.update(self.charExpand)

        ci = {c:None for c in listAllPunctuation()}
        ci.update(dict.fromkeys(self.charIgnore))

        parts = []
        for token in expandToken(self.tokenExpand, tokenize(s)):
            part = Just(token) 
            part >>= replaceToken(self.tokenReplace)
            part >>= ignoreToken(self.tokenIgnore)
            part >>= expandCharacters(ce)
            part >>= replaceCharacters(cr)
            part >>= replaceCharacters(ci)
            parts.append(part)

        joined = ''. join([x.value.lower() for x in parts if x.value])
        return joined

    def for_windows_file(self, s):
        result = replaceCharacters(windowsFileNameReserved(), s)
        return result.value

    def for_query_string(self, s):
        pass

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------

if __name__ == '__main__':
    n = Normalizer()
    n.charExpand = {'a': 'aa', 'i' : 'ii', 'e': 'ee', 'o' : 'oo'}
    n.tokenExpand = {'FREEX' : ['Free-executing', '$cript']}

    s = '\xdeis is intended to be used as a helper class. & not a FREEX!'
    print(n.to_ascii(s))
    print(n.to_key(s))
    print(n.for_windows_file('is * a filename?'))
