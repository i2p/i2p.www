#!/usr/bin/python2
# Copyright 2003-2008, Nick Mathewson.  See LICENSE for licensing info.

"""metaphone.py -- Pure-python metaphone implementation.

   (This is not guaranteed to match the real metaphone algorithm; I
   haven't tested it thorougly enough.  Let me know if you find bugs.

   Based on the original C++ metaphone implementation.)
"""

TRIPLES = {
    'dge': 'j',
    'dgi': 'j',
    'dgy': 'j',
    'sia': '+x',
    'sio': '+x',
    'tia': '+x',
    'tio': '+x',
    'tch': '',
    'tha': '0',
    'the': '0',
    'thi': '0',
    'tho': '0',
    'thu': '0',
    }

DOUBLES = {
    'ph' : 'f',
    'sh' : 'x'
    }

SINGLETONS = {
    'd': 't',
    'f': 'f',
    'j': 'j',
    'l': 'l',
    'm': 'm',
    'n': 'n',
    'r': 'r',
    'p': 'p',
    'q': 'k',
    'v': 'f',
    'x': 'ks',
    'z': 's',
}

ALLCHARS = "".join(map(chr, range(256)))
NONLCCHARS = "".join([c for c in ALLCHARS if not c.islower()])
def metaphone(s):
    """Return the metaphone equivalent of a provided string"""
    s = s.lower()
    s = s.translate(ALLCHARS, NONLCCHARS)

    if not s: return ""

    # If ae, gn, kn, pn, wr then drop the first letter.
    if s[:2] in ("ae", "gn", "kn", "pn", "wr"):
        s = s[1:]

    # Change "x" to "s"
    if s[0] == 'x':
        s = "s%s" % s[1:]

    # Get rid of "h" in "wh".
    if s[:2] == 'wh':
        s = "w%s" % s[1:]

    # Get rid of s from end.
    if s[-1] == 's':
        s = s[:-1]

    result = []
    prevLtr = ' '
    vowelBefore = 0
    lastChar = len(s)-1
    for idx in range(len(s)):
        curLtr = s[idx]
        # If first char is a vowel, keep it.
        if curLtr in "aeiou":
            if idx == 0:
                result.append(curLtr)
            continue

        # Skip double letters.
        if idx < lastChar:
            if curLtr == s[idx+1]:
                continue

        try:
            r = TRIPLES[s[idx:idx+3]]
            if r == "+x":
                if idx > 1:
                    result.append("x")
                    continue
            else:
                result.append(r)
                continue
        except KeyError:
            pass
        try:
            r = DOUBLES[s[idx:idx+2]]
            result.append(r)
            continue
        except KeyError:
            pass
        try:
            r = SINGLETONS[s[idx]]
            result.append(r)
            continue
        except KeyError:
            pass

        if idx > 0:
            prevLtr = s[idx-1]
            vowelBefore = prevLtr in "aeiou"
        curLtr = s[idx]

        nextLtr2 = ' '
        if idx < lastChar:
            nextLtr = s[idx+1]
            vowelAfter = nextLtr in "aeiou"
            frontvAfter = nextLtr in "eiy"
            if idx+1 < lastChar:
                nextLtr2 = s[idx+2]
        else:
            nextLtr = ' '
            vowelAfter = frontvAfter = 0


        if curLtr == 'b':
            if idx == lastChar and prevLtr == 'm':
                pass
            else:
                result.append(curLtr)
        elif curLtr == 'c':
            # silent 'sci', 'sce, 'scy', 'sci', etc OK.
            if not (prevLtr == 's' and frontvAfter):
                if nextLtr in 'ia':
                    result.append("x")
                elif frontvAfter:
                    result.append("s")
                elif prevLtr == 's' and nextLtr == 'h':
                    result.append('k')
                elif nextLtr == 'h':
                    if idx == 0 and nextLtr2 in "aeiou":
                        result.append('k')
                    else:
                        result.append('x')
                elif prevLtr == 'c':
                    result.append('c')
                else:
                    result.append('k')
        elif curLtr == 'g':
            if (idx < lastChar-1) and nextLtr == 'h':
                pass
            elif s[idx:] == 'gned':
                pass
            elif s[idx:] == 'gn':
                pass
            elif prevLtr == 'd' and frontvAfter:
                pass
            else:
                hard = (prevLtr == 'g')
                if frontvAfter and not hard:
                    result.append('j')
                else:
                    result.append('k')
        elif curLtr == 'h':
            if prevLtr in 'csptg':
                pass
            elif vowelBefore and not vowelAfter:
                pass
            else:
                result.append('h')
        elif curLtr == 'k':
            if prevLtr != 'c': result.append('k')
        elif curLtr in 'wy':
            if vowelAfter:
                result.append(curLtr)

    return "".join(result)

def demo(a):
    print a, "=>", metaphone(a)

if __name__ == '__main__':
    demo("Nick. Mathewson")

    demo("joe schmidt")
    demo("Beethoven")

    demo("Because the world is round")
