# Copyright 2003-2006, Nick Mathewson.  See LICENSE for licensing info.

import re

_KEYS = [ "ALL_TAGS",
          "ALPHABETIZE_AUTHOR_AS","AUTHOR_URLS","CACHE_DIR","CACHE_SECTIONS",
          "CACHE_UMASK",
          "CITE_CACHE_DIR",
          "COLLAPSE_AUTHORS",
          "DOWNLOAD_CONNECT_TIMEOUT","INITIAL_STRINGS",
          "MASTER_BIB", "NO_COLLAPSE_AUTHORS", "OMIT_ENTRIES",
          "OUTPUT_DIR", "TEMPLATE_FILE", "BIBTEX_TEMPLATE_FILE",
          "REQUIRE_KEY", "TAG_TITLES", "TAG_DIRECTORIES", "TAG_SHORT_TITLES",
          ]

for _k in _KEYS:
    globals()[_k]=None
del _k

def load(cfgFile):
    mod = {}
    execfile(cfgFile, mod)
    for _k in _KEYS:
        try:
            globals()[_k]=mod[_k]
        except KeyError:
            raise KeyError("Configuration option %s is missing"%_k)

    INITIAL_STRINGS.update(_EXTRA_INITIAL_STRINGS)
    AUTHOR_RE_LIST[:] = [
        (re.compile(k, re.I), v,) for k, v in AUTHOR_URLS.items()
        ]

    NO_COLLAPSE_AUTHORS_RE_LIST[:] = [
        re.compile(pat, re.I) for pat in NO_COLLAPSE_AUTHORS
        ]

    ALPHABETIZE_AUTHOR_AS_RE_LIST[:] = [
        (re.compile(k, re.I), v,) for k,v in ALPHABETIZE_AUTHOR_AS.items()
        ]

_EXTRA_INITIAL_STRINGS = {
    # MONTHS
     'jan' : 'January',         'feb' : 'February',
     'mar' : 'March',           'apr' : 'April',
     'may' : 'May',             'jun' : 'June',
     'jul' : 'July',            'aug' : 'August',
     'sep' : 'September',       'oct' : 'October',
     'nov' : 'November',        'dec' : 'December',
}

AUTHOR_RE_LIST = []

NO_COLLAPSE_AUTHORS_RE_LIST = []

ALPHABETIZE_AUTHOR_AS_RE_LIST = []
