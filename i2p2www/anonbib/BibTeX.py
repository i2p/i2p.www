#!/usr/bin/python2
# Copyright 2003-2008, Nick Mathewson.  See LICENSE for licensing info.

"""BibTeX.py -- parse and manipulate BibTeX files and entries.

   Based on perl code by Eddie Kohler; heavily modified.
"""

import cStringIO
import re
import sys
import os

import config

import rank

__all__ = [ 'ParseError', 'BibTeX', 'BibTeXEntry', 'htmlize',
            'ParsedAuthor', 'FileIter', 'Parser', 'parseFile',
            'splitBibTeXEntriesBy', 'sortBibTexEntriesBy', ]

# List: must map from month number to month name.
MONTHS = [ None,
           "January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"]

# Fields that we only care about for making web pages (BibTeX doesn't
# recognize them.)
WWW_FIELDS = [ 'www_section', 'www_important', 'www_remarks',
               'www_abstract_url', 'www_html_url', 'www_pdf_url', 'www_ps_url',
               'www_txt_url', 'www_ps_gz_url', 'www_amazon_url',
	       'www_excerpt_url', 'www_publisher_url',
               'www_cache_section', 'www_tags' ]

def url_untranslate(s):
    """Change a BibTeX key into a string suitable for use in a URL."""
    s = re.sub(r'([%<>`#, &_\';])',
               lambda m: "_%02x"%ord(m.group(1)),
               s)
    s = s.replace("/",":")
    return s

class ParseError(Exception):
    """Raised on invalid BibTeX"""
    pass


def smartJoin(*lst):
    """Equivalent to os.path.join, but handle"." and ".." entries a bit better.
    """
    lst = [ item for item in lst if item != "." ]
    idx = 0
    while idx < len(lst):
        if idx > 0 and lst[idx] == "..":
            del lst[idx]
        else:
            idx += 1
    return os.path.join(*lst)

class BibTeX:
    """A parsed BibTeX file"""
    def __init__(self):
        self.entries = [] # List of BibTeXEntry
        self.byKey = {} # Map from BibTeX key to BibTeX entry.
    def addEntry(self, ent):
        """Add a BibTeX entry to this file."""
        k = ent.key
        if self.byKey.get(ent.key.lower()):
            print >> sys.stderr, "Already have an entry named %s"%k
            return
        self.entries.append(ent)
        self.byKey[ent.key.lower()] = ent
    def resolve(self):
        """Validate all entries in this file, and resolve cross-references"""
        seen = {}
        for ent in self.entries:
            seen.clear()
            while ent.get('crossref'):
                try:
                    cr = self.byKey[ent['crossref'].lower()]
                except KeyError:
                    print "No such crossref: %s"% ent['crossref']
                    break
                if seen.get(cr.key):
                    raise ParseError("Circular crossref at %s" % ent.key)
                seen[cr.key] = 1
                del ent.entries['crossref']

                if cr.entryLine < ent.entryLine:
                    print "Warning: crossref %s used after declaration"%cr.key

                for k in cr.entries.keys():
                    if ent.entries.has_key(k):
                        print "ERROR: %s defined both in %s and in %s"%(
                            k,ent.key,cr.key)
                    else:
                        ent.entries[k] = cr.entries[k]

            ent.resolve()
        newEntries = []
        rk = config.REQUIRE_KEY
        if rk is None:
            # hack: if no key is required, require "title", since every
            # entry will have a title.
            rk = "title"

        for ent in self.entries:
            if ent.type in config.OMIT_ENTRIES or not ent.has_key(rk):
                ent.check()
                del self.byKey[ent.key.lower()]
            else:
                newEntries.append(ent)
        self.entries = newEntries

def buildAuthorTable(entries):
    """Given a list of BibTeXEntry, return a map from parsed author name to
       parsed canonical name.
    """
    authorsByLast = {}
    for e in entries:
        for a in e.parsedAuthor:
            authorsByLast.setdefault(tuple(a.last), []).append(a)
    # map from author to collapsed author.
    result = {}
    for k,v in config.COLLAPSE_AUTHORS.items():
        a = parseAuthor(k)[0]
        c = parseAuthor(v)[0]
        result[c] = c
        result[a] = c

    for e in entries:
        for author in e.parsedAuthor:
            if result.has_key(author):
                continue

            c = author
            for a in authorsByLast[tuple(author.last)]:
                if a is author:
                    continue
                c = c.collapsesTo(a)
            result[author] = c

    if 0:
        for a,c in result.items():
            if a != c:
                print "Collapsing authors: %s => %s" % (a,c)
    if 0:
        print parseAuthor("Franz Kaashoek")[0].collapsesTo(
            parseAuthor("M. Franz Kaashoek")[0])
        print parseAuthor("Paul F. Syverson")[0].collapsesTo(
            parseAuthor("Paul Syverson")[0])
        print parseAuthor("Paul Syverson")[0].collapsesTo(
            parseAuthor("Paul F. Syverson")[0])

    return result

def splitEntriesBy(entries, field):
    """Take a list of BibTeX entries and the name of a bibtex field; return
       a map from vield value to list of entry."""
    result = {}
    for ent in entries:
        key = ent.get(field)
        try:
            result[key].append(ent)
        except:
            result[key] = [ent]
    return result

def splitSortedEntriesBy(entries, field):
    """Take inputs as in splitEntriesBy, where 'entries' is sorted by 'field'.
       Return a list of (field-value, entry-list) tuples, in the order
       given in 'entries'."""
    result = []
    curVal = "alskjdsakldj"
    curList = []
    for ent in entries:
        key = ent.get(field)
        if key == curVal:
            curList.append(ent)
        else:
            curVal = key
            curList = [ent]
            result.append((curVal, curList))
    return result

def sortEntriesBy(entries, field, default):
    """Take inputs as in splitEntriesBy, and return a list of entries sorted
       by the value of 'field'. Entries without 'field' are sorted as if their
       value were 'default'.
       """
    tmp = []
    i = 0
    for ent in entries:
        i += 1
        v = ent.get(field, default)
        if v.startswith("<span class='bad'>"):
            v = default
        tmp.append((txtize(v), i, ent))
    tmp.sort()
    return [ t[2] for t in tmp ]

def splitEntriesByAuthor(entries):
    """Take a list of entries, sort them by author names, and return:
         a sorted list of (authorname-in-html, bibtex-entry-list) tuples,
         a map from authorname-in-html to name-for-url.
       Entries with multiple authors appear once per author.
    """
    collapsedAuthors = buildAuthorTable(entries)
    entries = sortEntriesByDate(entries)
    result = {} # Name in sorting order -> entries
    htmlResult = {} # name in sorting order -> Full name
    url_map = {} # Full name -> Url
    for ent in entries:
        for a in ent.parsedAuthor:
            canonical = collapsedAuthors[a]
            url = canonical.getHomepage()
            sortkey = canonical.getSortingName()
            secname = canonical.getSectionName()
            if url:
                url_map[secname] = url

            htmlResult[sortkey] = secname
            result.setdefault(sortkey, []).append(ent)
    sortnames = result.keys()
    sortnames.sort()
    sections = [ (htmlResult[n], result[n]) for n in sortnames ]
    return sections, url_map

## def sortEntriesByAuthor(entries):
##     tmp = []
##     i = 0
##     for ent in entries:
##         i += 1
##         authors = [ txtize(" ".join(a.von+a.last+a.first+a.jr))
##                     for a in ent.parsedAuthor ]
##         tmp.append((tuple(authors), i, ent))
##     tmp.sort()
##     return [ t[2] for t in tmp ]

def sortEntriesByDate(entries):
    """Sort a list of entries by their publication date."""
    tmp = []
    i = 0
    for ent in entries:
        i += 1
        if (ent.get('month') == "forthcoming" or
            ent.get('year') == "forthcoming"):
            tmp.append((20000*13, i, ent))
            continue
        try:
            monthname = ent.get("month")
            if monthname is not None:
                match = re.match(r"(\w+)--\w+", monthname)
                if match:
                    monthname = match.group(1)
            mon = MONTHS.index(monthname)
        except ValueError:
            print "Unknown month %r in %s"%(ent.get("month"), ent.key)
            mon = 0

        try:
            date = int(ent['year'])*13 + mon
        except KeyError:
            print "ERROR: No year field in %s"%ent.key
            date = 10000*13
        except ValueError:
            date = 10000*13
        tmp.append((date, i, ent))
    tmp.sort()
    return [ t[2] for t in tmp ]


# List of fields that appear when we display the entries as BibTeX.
DISPLAYED_FIELDS = [ 'title', 'author', 'journal', 'booktitle',
'school', 'institution', 'organization', 'volume', 'number', 'year',
'month', 'address', 'location', 'chapter', 'edition', 'pages', 'editor',
'howpublished', 'key', 'publisher', 'type', 'note', 'series' ]

class BibTeXEntry:
    """A single BibTeX entry."""
    def __init__(self, type, key, entries):
        self.type = type  # What kind of entry is it?  (@book,@injournal,etc)
        self.key = key # What key does it have?
        self.entries = entries # Map from key to value.
        self.entryLine = 0 # Defined on this line number
    def get(self, k, v=None):
        return self.entries.get(k,v)
    def has_key(self, k):
        return self.entries.has_key(k)
    def __getitem__(self, k):
        return self.entries[k]
    def __setitem__(self, k, v):
        self.entries[k] = v
    def __str__(self):
        return self.format(70,1)
    def getURL(self):
        """Return the best URL to use for this paper, or None."""
        best = None
        for field in ['www_pdf_url', 'www_ps_gz_url', 'www_ps_url',
                      'www_html_url', 'www_txt_url', ]:
            u = self.get(field)
            if u:
                if not best:
                    best = u
                elif (best.startswith("http://citeseer.nj.nec.com/")
                      and not u.startswith("http://citeseer.nj.nec.com/")):
                    best = u
        return best

    def format(self, width=70, indent=8, v=0, invStrings={}):
        """Format this entry as BibTeX."""
        d = ["@%s{%s,\n" % (self.type, self.key)]
        if v:
            df = DISPLAYED_FIELDS[:]
            for k in self.entries.keys():
                if k not in df:
                    df.append(k)
        else:
            df = DISPLAYED_FIELDS
        for f in df:
            if not self.entries.has_key(f):
                continue
            v = self.entries[f]
            if v.startswith("<span class='bad'>"):
                d.append("%%%%% ERROR: Missing field\n")
                d.append("%% %s = {?????},\n"%f)
                continue
            np = v.translate(ALLCHARS, PRINTINGCHARS)
            if np:
                d.append("%%%%% "+("ERROR: Non-ASCII characters: '%r'\n"%np))
            d.append("  ")
            v = v.replace("&", "&amp;")
            if invStrings.has_key(v):
                s = "%s = %s,\n" %(f, invStrings[v])
            else:
                s = "%s = {%s},\n" % (f, v)
            d.append(_split(s,width,indent))
        d.append("}\n")
        return "".join(d)
    def resolve(self):
        """Handle post-processing for this entry"""
        a = self.get('author')
        if a:
            self.parsedAuthor = parseAuthor(a)
            #print a
            #print "   => ",repr(self.parsedAuthor)
        else:
            self.parsedAuthor = None

    def isImportant(self):
        """Return 1 iff this entry is marked as important"""
        imp = self.get("www_important")
        if imp and imp.strip().lower() not in ("no", "false", "0"):
            return 1
        return 0

    def check(self):
        """Print any errors for this entry, and return true if there were
           none."""
        errs = self._check()
        for e in errs:
            print e
        return not errs

    def _check(self):
        errs = []
        if self.type == 'inproceedings':
            fields = 'booktitle', 'year'
        elif self.type == 'incollection':
            fields = 'booktitle', 'year'
        elif self.type == 'proceedings':
            fields = 'booktitle', 'editor'
        elif self.type == 'article':
            fields = 'journal', 'year'
        elif self.type == 'techreport':
            fields = 'institution',
        elif self.type == 'misc':
            fields = 'howpublished',
        elif self.type in ('mastersthesis', 'phdthesis'):
            fields = ()
        else:
            fields = ()
            errs.append("ERROR: odd type %s"%self.type)
        if self.type != 'proceedings':
            fields += 'title', 'author', 'www_section', 'year'

        for field in fields:
            if self.get(field) is None or \
                   self.get(field).startswith("<span class='bad'>"):
                errs.append("ERROR: %s has no %s field" % (self.key, field))
                self.entries[field] = "<span class='bad'>%s:??</span>"%field

        if self.type == 'inproceedings':
            if self.get("booktitle"):
                if not self['booktitle'].startswith("Proceedings of") and \
                   not self['booktitle'].startswith("{Proceedings of"):
                    errs.append("ERROR: %s's booktitle (%r) doesn't start with 'Proceedings of'" % (self.key, self['booktitle']))

        if self.has_key("pages") and not re.search(r'\d+--\d+', self['pages']):
            errs.append("ERROR: Misformed pages in %s"%self.key)

        if self.type == 'proceedings':
            if self.get('title'):
                errs.append("ERROR: %s is a proceedings: it should have a booktitle, not a title." % self.key)

        for field, value in self.entries.items():
            if value.translate(ALLCHARS, PRINTINGCHARS):
                errs.append("ERROR: %s.%s has non-ASCII characters"%(
                    self.key, field))
            if field.startswith("www_") and field not in WWW_FIELDS:
                errs.append("ERROR: unknown www field %s"% field)
            if value.strip()[-1:] == '.' and \
                field not in ("notes", "www_remarks", "author"):
                errs.append("ERROR: %s.%s has an extraneous period"%(self.key,
                            field))
        return errs

    def biblio_to_html(self):
        """Return the HTML for the citation portion of entry."""
        if self.type in ('inproceedings', 'incollection'):
            booktitle = self['booktitle']
            bookurl = self.get('bookurl')
            if bookurl:
                m = PROCEEDINGS_RE.match(booktitle)
                if m:
                    res = ["In the ", m.group(1),
                           '<a href="%s">'%bookurl, m.group(2), "</a>"]
                else:
                    res = ['In the <a href="%s">%s</a>' % (bookurl,booktitle)]
            else:
                res = ["In the ", booktitle ]

            if self.get("edition"):
                res.append(",")
                res.append(self['edition'])
            if self.get("location"):
                res.append(", ")
                res.append(self['location'])
            elif self.get("address"):
                res.append(", ")
                res.append(self['address'])
            res.append(", %s %s" % (self.get('month',""), self['year']))
            if not self.get('pages'):
                pass
            elif "-" in self['pages']:
                res.append(", pages&nbsp;%s"%self['pages'])
            else:
                res.append(", page&nbsp;%s"%self['pages'])
        elif self.type == 'article':
            res = ["In "]
            if self.get('journalurl'):
                res.append('<a href="%s">%s</a>'%
                           (self['journalurl'],self['journal']))
            else:
                res.append(self['journal'])
            if self.get('volume'):
                res.append(" <b>%s</b>"%self['volume'])
            if self.get('number'):
                res.append("(%s)"%self['number'])
            res.append(", %s %s" % (self.get('month',""), self['year']))
            if not self.get('pages'):
                pass
            elif "-" in self['pages']:
                res.append(", pages&nbsp;%s"%self['pages'])
            else:
                res.append(", page&nbsp;%s"%self['pages'])
        elif self.type == 'techreport':
            res = [ "%s %s %s" % (self['institution'],
                                  self.get('type', 'technical report'),
                                  self.get('number', "")) ]
            if self.get('month') or self.get('year'):
                res.append(", %s %s" % (self.get('month', ''),
                                        self.get('year', '')))
        elif self.type == 'mastersthesis' or self.type == 'phdthesis':
            if self.get('type'):
                res = [self['type']]
            elif self.type == 'mastersthesis':
                res = ["Masters's thesis"]
            else:
                res = ["Ph.D. thesis"]
            if self.get('school'):
                res.append(", %s"%(self['school']))
            if self.get('month') or self.get('year'):
                res.append(", %s %s" % (self.get('month', ''),
                                        self.get('year', '')))
	elif self.type == 'book':
	    res = [self['publisher']]
	    if self.get('year'):
		res.append(" ");
		res.append(self.get('year'));
	#	res.append(", %s"%(self.get('year')))
	    if self.get('series'):
		res.append(",");
		res.append(self['series']);
        elif self.type == 'misc':
            res = [self['howpublished']]
            if self.get('month') or self.get('year'):
                res.append(", %s %s" % (self.get('month', ''),
                                        self.get('year', '')))
            if not self.get('pages'):
                pass
            elif "-" in self['pages']:
                res.append(", pages&nbsp;%s"%self['pages'])
            else:
                res.append(", page&nbsp;%s"%self['pages'])
        else:
            res = ["&lt;Odd type %s&gt;"%self.type]

        res[0:0] = ["<span class='biblio'>"]
        res.append(".</span>")

        bibtexurl = "./bibtex.html#%s"%url_untranslate(self.key)
        res.append((" <span class='availability'>"
                   "(<a href='%s'>BibTeX&nbsp;entry</a>)"
                   "</span>") %bibtexurl)
        return htmlize("".join(res))

    def to_html(self, cache_path="./cache", base_url="."):
        """Return the HTML for this entry."""
        imp = self.isImportant()
        draft = self.get('year') == 'forthcoming'
        if imp:
            res = ["<li><div class='impEntry'><p class='impEntry'>" ]
        elif draft:
            res = ["<li><div class='draftEntry'><p class='draftEntry'>" ]
        else:
            res = ["<li><p class='entry'>"]

        if imp or not draft:
            # Add a picture of the rank
            # Only if year is known or paper important!
            r = rank.get_rank_html(self['title'], self.get('year'),
                                   update=False, base_url=base_url)
            if r is not None:
                res.append(r)

        res.append("<span class='title'><a name='%s'>%s</a></span>"%(
            url_untranslate(self.key),htmlize(self['title'])))

        for cached in 0,1:
            availability = []
            if not cached:
                for which in [ "amazon", "excerpt", "publisher" ]:
                    key = "www_%s_url"%which
                    if self.get(key):
                        url=self[key]
                        url = unTeXescapeURL(url)
                        availability.append('<a href="%s">%s</a>' %(url,which))

            cache_section = self.get('www_cache_section', ".")
            if cache_section not in config.CACHE_SECTIONS:
                if cache_section != ".":
                    print >>sys.stderr, "Unrecognized cache section %s"%(
                        cache_section)
                    cache_section="."

            for key, name, ext in (('www_abstract_url', 'abstract','abstract'),
                                   ('www_html_url', 'HTML', 'html'),
                                   ('www_pdf_url', 'PDF', 'pdf'),
                                   ('www_ps_url', 'PS', 'ps'),
                                   ('www_txt_url', 'TXT', 'txt'),
                                   ('www_ps_gz_url', 'gzipped&nbsp;PS','ps.gz')
                                   ):
                if cached:
                    #XXXX the URL needs to be relative to the absolute
                    #XXXX cache path.
                    url = smartJoin(cache_path,cache_section,
                                    "%s.%s"%(self.key,ext))
                    fname = smartJoin(config.OUTPUT_DIR, config.CACHE_DIR,
                                      cache_section,
                                      "%s.%s"%(self.key,ext))
                    if not os.path.exists(fname): continue
                else:
                    url = self.get(key)
                    if not url: continue
                url = unTeXescapeURL(url)
                url = url.replace('&', '&amp;')
                availability.append('<a href="%s">%s</a>' %(url,name))

            if availability:
                res.append([" ", "&nbsp;"][cached])
                res.append("<span class='availability'>(")
                if cached: res.append("Cached:&nbsp;")
                res.append(",&nbsp;".join(availability))
                res.append(")</span>")

        res.append("<br /><span class='author'>by ")

        #res.append("\n<!-- %r -->\n" % self.parsedAuthor)
        htmlAuthors = [ a.htmlizeWithLink() for a in self.parsedAuthor ]

        if len(htmlAuthors) == 1:
            res.append(htmlAuthors[0])
        elif len(htmlAuthors) == 2:
            res.append(" and ".join(htmlAuthors))
        else:
            res.append(", ".join(htmlAuthors[:-1]))
            res.append(", and ")
            res.append(htmlAuthors[-1])

        if res[-1][-1] != '.':
            res.append(".")
        res.append("</span><br />\n")
        res.append(self.biblio_to_html())
        res.append("<a href='#%s'>&middot;</a>"%url_untranslate(self.key))
        res.append("</p>")

        if self.get('www_remarks'):
            res.append("<p class='remarks'>%s</p>"%htmlize(
                self['www_remarks']))

        if imp or draft:
            res.append("</div>")
        res.append("</li>\n\n")

        return "".join(res)

def unTeXescapeURL(s):
    """Turn a URL as formatted in TeX into a real URL."""
    s = s.replace("\\_", "_")
    s = s.replace("\\-", "")
    s = s.replace("\{}", "")
    s = s.replace("{}", "")
    return s

def TeXescapeURL(s):
    """Escape a URL for use in TeX"""
    s = s.replace("_", "\\_")
    s = s.replace("~", "\{}~")
    return s

RE_LONE_AMP = re.compile(r'&([^a-z0-9])')
RE_LONE_I = re.compile(r'\\i([^a-z0-9])')
RE_ACCENT = re.compile(r'\\([\'`~^"c])([^{]|{.})')
RE_LIGATURE = re.compile(r'\\(AE|ae|OE|oe|AA|aa|O|o|ss)([^a-z0-9])')
ACCENT_MAP = { "'" : 'acute',
               "`" : 'grave',
               "~" : 'tilde',
               "^" : 'circ',
               '"' : 'uml',
               "c" : 'cedil',
               }
UNICODE_MAP = { '&nacute;' : '&#x0144;', }
HTML_LIGATURE_MAP = {
    'AE' : '&AElig;',
    'ae' : '&aelig;',
    'OE' : '&OElig;',
    'oe' : '&oelig;',
    'AA' : '&Aring;',
    'aa' : '&aring;',
    'O'  : '&Oslash;',
    'o'  : '&oslash;',
    'ss' : '&szlig;',
    }
RE_TEX_CMD = re.compile(r"(?:\\[a-zA-Z@]+|\\.)")
RE_PAGE_SPAN = re.compile(r"(\d)--(\d)")
def _unaccent(m):
    accent,char = m.groups()
    if char[0] == '{':
        char = char[1]
    accented = "&%s%s;" % (char, ACCENT_MAP[accent])
    return UNICODE_MAP.get(accented, accented)
def _unlig_html(m):
    return "%s%s"%(HTML_LIGATURE_MAP[m.group(1)],m.group(2))
def htmlize(s):
    """Turn a TeX string into good-looking HTML."""
    s = RE_LONE_AMP.sub(lambda m: "&amp;%s" % m.group(1), s)
    s = RE_LONE_I.sub(lambda m: "i%s" % m.group(1), s)
    s = RE_ACCENT.sub(_unaccent, s)
    s = unTeXescapeURL(s)
    s = RE_LIGATURE.sub(_unlig_html, s);
    s = RE_TEX_CMD.sub("", s)
    s = s.translate(ALLCHARS, "{}")
    s = RE_PAGE_SPAN.sub(lambda m: "%s-%s"%(m.groups()), s)
    s = s.replace("---", "&mdash;");
    s = s.replace("--", "&ndash;");
    return s

def author_url(author):
    """Given an author's name, return a URL for his/her homepage."""
    for pat, url in config.AUTHOR_RE_LIST:
        if pat.search(author):
            return url
    return None

def txtize(s):
    """Turn a TeX string into decnent plaintext."""
    s = RE_LONE_I.sub(lambda m: "i%s" % m.group(1), s)
    s = RE_ACCENT.sub(lambda m: "%s" % m.group(2), s)
    s = RE_LIGATURE.sub(lambda m: "%s%s"%m.groups(), s)
    s = RE_TEX_CMD.sub("", s)
    s = s.translate(ALLCHARS, "{}")
    return s

PROCEEDINGS_RE = re.compile(
                        r'((?:proceedings|workshop record) of(?: the)? )(.*)',
                        re.I)

class ParsedAuthor:
    """The parsed name of an author.

       Eddie deserves credit for this incredibly hairy business.
    """
    def __init__(self, first, von, last, jr):
        self.first = first
        self.von = von
        self.last = last
        self.jr = jr
        self.collapsable = 1

        self.html = htmlize(str(self))
        self.txt = txtize(str(self))

        s = self.html
        for pat in config.NO_COLLAPSE_AUTHORS_RE_LIST:
            if pat.search(s):
                self.collapsable = 0
                break

    def __eq__(self, o):
        return ((self.first == o.first) and
                (self.last  == o.last) and
                (self.von   == o.von) and
                (self.jr    == o.jr))

    def __hash__(self):
        return hash(repr(self))

    def collapsesTo(self, o):
        """Return true iff 'o' could be a more canonical version of this author
        """
        if not self.collapsable or not o.collapsable:
            return self

        if self.last != o.last or self.von != o.von or self.jr != o.jr:
            return self
        if not self.first:
            return o

        if len(self.first) == len(o.first):
            n = []
            for a,b in zip(self.first, o.first):
                if a == b:
                    n.append(a)
                elif len(a) == 2 and a[1] == '.' and a[0] == b[0]:
                    n.append(b)
                elif len(b) == 2 and b[1] == '.' and a[0] == b[0]:
                    n.append(a)
                else:
                    return self
            if n == self.first:
                return self
            elif n == o.first:
                return o
            else:
                return self
        else:
            realname = max([len(n) for n in self.first+o.first])>2
            if not realname:
                return self

            if len(self.first) < len(o.first):
                short = self.first; long = o.first
            else:
                short = o.first; long = self.first

            initials_s = "".join([n[0] for n in short])
            initials_l = "".join([n[0] for n in long])
            idx = initials_l.find(initials_s)
            if idx < 0:
                return self
            n = long[:idx]
            for i in range(idx, idx+len(short)):
                a = long[i]; b = short[i-idx]
                if a == b:
                    n.append(a)
                elif len(a) == 2 and a[1] == '.' and a[0] == b[0]:
                    n.append(b)
                elif len(b) == 2 and b[1] == '.' and a[0] == b[0]:
                    n.append(a)
                else:
                    return self
            n += long[idx+len(short):]

            if n == self.first:
                return self
            elif n == o.first:
                return o
            else:
                return self

    def __repr__(self):
        return "ParsedAuthor(%r,%r,%r,%r)"%(self.first,self.von,
                                            self.last,self.jr)
    def __str__(self):
        a = " ".join(self.first+self.von+self.last)
        if self.jr:
            return "%s, %s" % (a,self.jr)
        return a

    def getHomepage(self):
        s = self.html
        for pat, url in config.AUTHOR_RE_LIST:
            if pat.search(s):
                return url
        return None

    def getSortingName(self):
        """Return a representation of this author's name in von-last-first-jr
           order, unless overridden by ALPH """
        s = self.html
        for pat,v in config.ALPHABETIZE_AUTHOR_AS_RE_LIST:
            if pat.search(s):
                return v

        return txtize(" ".join(self.von+self.last+self.first+self.jr))

    def getSectionName(self):
        """Return a HTML representation of this author's name in
           last, first von, jr order"""
        secname = " ".join(self.last)
        more = self.first+self.von
        if more:
            secname += ", "+" ".join(more)
        if self.jr:
            secname += ", "+" ".join(self.jr)
        secname = htmlize(secname)
        return secname

    def htmlizeWithLink(self):
        a = self.html
        u = self.getHomepage()
        if u:
            return "<a href='%s'>%s</a>"%(u,a)
        else:
            return a

def _split(s,w=79,indent=8):
    r = []
    s = re.sub(r"\s+", " ", s)
    first = 1
    indentation = ""
    while len(s) > w:
        for i in xrange(w-1, 20, -1):
            if s[i] == ' ':
                r.append(indentation+s[:i])
                s = s[i+1:]
                break
        else:
            r.append(indentation+s.strip())
            s = ""
        if first:
            first = 0
            w -= indent
            indentation = " "*indent
    if (s):
        r.append(indentation+s)
    r.append("")
    return "\n".join(r)

class FileIter:
    def __init__(self, fname=None, file=None, it=None, string=None):
        if fname:
            file = open(fname, 'r')
        if string:
            file = cStringIO.StringIO(string)
        if file:
            it = iter(file.xreadlines())
        self.iter = it
        assert self.iter
        self.lineno = 0
        self._next = it.next
    def next(self):
        self.lineno += 1
        return self._next()


def parseAuthor(s):
    try:
        return _parseAuthor(s)
    except:
        print >>sys.stderr, "Internal error while parsing author %r"%s
        raise

def _parseAuthor(s):
    """Take an author string and return a list of ParsedAuthor."""
    items = []

    s = s.strip()
    while s:
        s = s.strip()
        bracelevel = 0
        for i in xrange(len(s)):
            if s[i] == '{':
                bracelevel += 1
            elif s[i] == '}':
                bracelevel -= 1
            elif bracelevel <= 0 and s[i] in " \t\n,":
                break
        if i+1 == len(s):
            items.append(s)
        else:
            items.append(s[0:i])
        if (s[i] == ','):
            items.append(',')
        s = s[i+1:]

    authors = [[]]
    for item in items:
        if item == 'and':
            authors.append([])
        else:
            authors[-1].append(item)

    parsedAuthors = []
    # Split into first, von, last, jr
    for author in authors:
        commas = 0
        fvl = []
        vl = []
        f = []
        v = []
        l = []
        j = []
        cur = fvl
        for item in author:
            if item == ',':
                if commas == 0:
                    vl = fvl
                    fvl = []
                    cur = f
                else:
                    j.extend(f)
                    cur = f = []
                commas += 1
            else:
                cur.append(item)

        if commas == 0:
            split_von(f,v,l,fvl)
        else:
            f_tmp = []
            split_von(f_tmp,v,l,vl)

        parsedAuthors.append(ParsedAuthor(f,v,l,j))

    return parsedAuthors

ALLCHARS = "".join(map(chr,range(256)))
PRINTINGCHARS = "\t\n\r"+"".join(map(chr,range(32, 127)))
LC_CHARS = "abcdefghijklmnopqrstuvwxyz"
SV_DELCHARS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"
               "abcdefghijklmnopqrstuvwxyz"
               "@")
RE_ESCAPED = re.compile(r'\\.')
def split_von(f,v,l,x):
    in_von = 0
    while x:
        tt = t = x[0]
        del x[0]
        if tt[:2] == '{\\':
            tt = tt.translate(ALLCHARS, SV_DELCHARS)
            tt = RE_ESCAPED.sub("", tt)
            tt = tt.translate(ALLCHARS, "{}")
        if tt.translate(ALLCHARS, LC_CHARS) == "":
            v.append(t)
            in_von = 1
        elif in_von and f is not None:
            l.append(t)
            l.extend(x)
            return
        else:
            f.append(t)
    if not in_von:
        l.append(f[-1])
        del f[-1]


class Parser:
    """Parser class: reads BibTeX from a file and returns a BibTeX object."""
    ## Fields
    # strings: maps entry string keys to their values.
    # newStrings: all string definitions not in config.INITIAL_STRINGS
    # invStrings: map from string values to their keys.
    # fileiter: the line iterator we're parsing from.
    # result: the BibTeX object that we're parsing into
    # litStringLine: the line on which we started parsing a literal string;
    #     0 for none.
    # entryLine: the line on which the current entry started; 0 for none.
    #
    # curEntType: the type of the entry we're parsing now. (paper,article,etc)
    def __init__(self, fileiter, initial_strings, result=None):
        self.strings = config.INITIAL_STRINGS.copy()
        self.strings.update(initial_strings)
        self.newStrings = {}
        self.invStrings = {}
        for k,v in config.INITIAL_STRINGS.items():
            self.invStrings[v]=k
        self.fileiter = fileiter
        if result is None:
            result = BibTeX()
        self.result = result
        self.litStringLine = 0
        self.entryLine = 0

    def _parseKey(self, line):
        it = self.fileiter
        line = _advance(it,line)
        m = KEY_RE.match(line)
        if not m:
            raise ParseError("Expected key at line %s"%self.fileiter.lineno)
        key, line = m.groups()
        return key, line

    def _parseValue(self, line):
        it = self.fileiter
        bracelevel = 0
        data = []
        while 1:
            line = _advance(it,line)
            line = line.strip()
            assert line

            # Literal string?
            if line[0] == '"':
                line=line[1:]
                self.litStringLine = it.lineno
                while 1:
                    if bracelevel:
                        m = BRACE_CLOSE_RE.match(line)
                        if m:
                            data.append(m.group(1))
                            data.append('}')
                            line = m.group(2)
                            bracelevel -= 1
                            continue
                    else:
                        m = STRING_CLOSE_RE.match(line)
                        if m:
                            data.append(m.group(1))
                            line = m.group(2)
                            break
                    m = BRACE_OPEN_RE.match(line)
                    if m:
                        data.append(m.group(1))
                        line = m.group(2)
                        bracelevel += 1
                        continue
                    data.append(line)
                    data.append(" ")
                    line = it.next()
                self.litStringLine = 0
            elif line[0] == '{':
                bracelevel += 1
                line = line[1:]
                while bracelevel:
                    m = BRACE_CLOSE_RE.match(line)
                    if m:
                        #print bracelevel, "A", repr(m.group(1))
                        data.append(m.group(1))
                        bracelevel -= 1
                        if bracelevel > 0:
                            #print bracelevel, "- '}'"
                            data.append('}')
                        line = m.group(2)
                        continue
                    m = BRACE_OPEN_RE.match(line)
                    if m:
                        bracelevel += 1
                        #print bracelevel, "B", repr(m.group(1))
                        data.append(m.group(1))
                        line = m.group(2)
                        continue
                    else:
                        #print bracelevel, "C", repr(line)
                        data.append(line)
                        data.append(" ")
                        line = it.next()
            elif line[0] == '#':
                print >>sys.stderr, "Weird concat on line %s"%it.lineno
            elif line[0] in "},":
                if not data:
                    print >>sys.stderr, "No data after field on line %s"%(
                        it.lineno)
            else:
                m = RAW_DATA_RE.match(line)
                if m:
                    s = self.strings.get(m.group(1).lower())
                    if s is not None:
                        data.append(s)
                    else:
                        data.append(m.group(1))
                    line = m.group(2)
                else:
                    raise ParseError("Questionable line at line %s"%it.lineno)

            # Got a string, check for concatenation.
            if line.isspace() or not line:
                data.append(" ")
            line = _advance(it,line)
            line = line.strip()
            assert line
            if line[0] == '#':
                line = line[1:]
            else:
                data = "".join(data)
                data = re.sub(r'\s+', ' ', data)
                data = re.sub(r'^\s+', '', data)
                data = re.sub(r'\s+$', '', data)
                return data, line

    def _parseEntry(self, line): #name, strings, entries
        it = self.fileiter
        self.entryLine = it.lineno
        line = _advance(it,line)

        m = BRACE_BEGIN_RE.match(line)
        if not m:
            raise ParseError("Expected an opening brace at line %s"%it.lineno)
        line = m.group(1)

        proto = { 'string' : 'p',
                  'preamble' : 'v',
                  }.get(self.curEntType, 'kp*')

        v = []
        while 1:
            line = _advance(it,line)

            m = BRACE_END_RE.match(line)
            if m:
                line = m.group(1)
                break
            if not proto:
                raise ParseError("Overlong entry starting on line %s"
                                 % self.entryLine)
            elif proto[0] == 'k':
                key, line = self._parseKey(line)
                v.append(key)
            elif proto[0] == 'v':
                value, line = self._parseValue(line)
                v.append(value)
            elif proto[0] == 'p':
                key, line = self._parseKey(line)
                v.append(key)
                line = _advance(it,line)
                line = line.lstrip()
                if line[0] == '=':
                    line = line[1:]
                value, line = self._parseValue(line)
                v.append(value)
            else:
                assert 0
            line = line.strip()
            if line and line[0] == ',':
                line = line[1:]
            if proto and proto[1:] != '*':
                proto = proto[1:]
        if proto and proto[1:] != '*':
            raise ParseError("Missing arguments to %s on line %s" % (
                             self.curEntType, self.entryLine))

        if self.curEntType == 'string':
            self.strings[v[0]] = v[1]
            self.newStrings[v[0]] = v[1]
            self.invStrings[v[1]] = v[0]
        elif self.curEntType == 'preamble':
            pass
        else:
            key = v[0]
            d = {}
            for i in xrange(1,len(v),2):
                d[v[i].lower()] = v[i+1]
            ent = BibTeXEntry(self.curEntType, key, d)
            ent.entryLine = self.entryLine
            self.result.addEntry(ent)

        return line

    def parse(self):
        try:
            self._parse()
        except StopIteration:
            if self.litStringLine:
                raise ParseError("Unexpected EOF in string (started on %s)" %
                                 self.litStringLine)
            elif self.entryLine:
                raise ParseError("Unexpected EOF at line %s (entry started "
                                 "on %s)" % (self.fileiter.lineno,
                                             self.entryLine))

        self.result.invStrings = self.invStrings
        self.result.newStrings = self.newStrings

        return self.result

    def _parse(self):
        it = self.fileiter
        line = it.next()
        while 1:
            # Skip blank lines.
            while not line or line.isspace() or OUTER_COMMENT_RE.match(line):
                line = it.next()
            # Get the first line of an entry.
            m = ENTRY_BEGIN_RE.match(line)
            if m:
                self.curEntType = m.group(1).lower()
                line = m.group(2)
                line = self._parseEntry(line)
                self.entryLine = 0
            else:
                raise ParseError("Bad input at line %s (expected a new entry.)"
                                 % it.lineno)

def _advance(it,line):
    while not line or line.isspace() or COMMENT_RE.match(line):
        line = it.next()
    return line

# Matches a comment line outside of an entry.
OUTER_COMMENT_RE = re.compile(r'^\s*[\#\%]')
# Matches a comment line inside of an entry.
COMMENT_RE = re.compile(r'^\s*\%')
# Matches the start of an entry. group 1 is the type of the entry.
# group 2 is the rest of the line.
ENTRY_BEGIN_RE = re.compile(r'''^\s*\@([^\s\"\%\'\(\)\,\=\{\}]+)(.*)''')
# Start of an entry.  group 1 is the keyword naming the entry.
BRACE_BEGIN_RE = re.compile(r'\s*\{(.*)')
BRACE_END_RE = re.compile(r'\s*\}(.*)')
KEY_RE = re.compile(r'''\s*([^\"\#\%\'\(\)\,\=\{\}\s]+)(.*)''')

STRING_CLOSE_RE = re.compile(r'^([^\{\}\"]*)\"(.*)')
BRACE_CLOSE_RE = re.compile(r'^([^\{\}]*)\}(.*)')
BRACE_OPEN_RE = re.compile(r'^([^\{\}]*\{)(.*)')
RAW_DATA_RE = re.compile(r'^([^\s\},]+)(.*)')

def parseFile(filename, result=None):
    """Helper function: parse a single BibTeX file"""
    f = FileIter(fname=filename)
    p = Parser(f, {}, result)
    r = p.parse()
    r.resolve()
    for e in r.entries:
        e.check()
    return r

def parseString(string, result=None):
    """Helper function: parse BibTeX from a string"""
    f = FileIter(string=string)
    p = Parser(f, {}, result)
    r = p.parse()
    r.resolve()
    for e in r.entries:
        e.check()
    return r

if __name__ == '__main__':
    if len(sys.argv)>1:
        fname=sys.argv[1]
    else:
        fname="testbib/pdos.bib"

    r = parseFile(fname)

    for e in r.entries:
        if e.type in ("proceedings", "journal"): continue
        print e.to_html()

