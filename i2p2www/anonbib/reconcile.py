#!/usr/bin/python2
# Copyright 2003-2008, Nick Mathewson.  See LICENSE for licensing info.

"""Code to determine which entries are new and which are old.

   To scan a new file, run "python reconcile.py anonbib.cfg new-file.bib".  This
   will generate a new bibtex file called 'tmp.bib', with all the new entries
   cleaned up a little, and all the duplicate entries commented out.
"""

import sys
import re

assert sys.version_info[:3] >= (2,2,0)

import BibTeX
import config
import metaphone

_MPCACHE = {}
def soundsLike(s1, s2):
    c = _MPCACHE
    s1 = clean(s1)
    s2 = clean(s2)
    try:
        m1 = c[s1]
    except KeyError:
        m1 = c[s1] = metaphone.metaphone(s1)
    try:
        m2 = c[s2]
    except KeyError:
        m2 = c[s2] = metaphone.metaphone(s2)

    return m1 == m2

def mphone(s):
    c = _MPCACHE
    s = clean(s)
    try:
        return c[s]
    except:
        m = c[s] = metaphone.metaphone(s)
        return m

def clean(s):
    s = re.sub(r'\s+', ' ', s)
    s = s.strip()
    return s

class MasterBibTeX(BibTeX.BibTeX):
    def __init__(self):
        BibTeX.BibTeX.__init__(self)

    def buildIndex(self):
        self.byTitle = {}
        for ent in self.entries:
            for t in self._titleForms(ent['title']):
                self.byTitle.setdefault(t, []).append(ent)

    def _titleForms(self, title):
        title = title.lower()
        title = re.sub(r'\b(an|a|the|of)\b', "", title)
        title = clean(title)
        res = [ mphone(title) ]
        if ':' in title:
            for t in title.split(":"):
                res.append(mphone(t.strip()))
        #print "%r\n   => %s" % (title,res)
        return res

    def _titlesAlike(self, t1, t2):
        t1 = clean(t1)
        t2 = clean(t2)
        if t1 == t2:
            return 2
        tf1 = self._titleForms(t1)
        tf2 = self._titleForms(t2)
        for t in tf1:
            if t in tf2: return 1
        return 0

    def _authorsAlike(self, a1, a2):
        if not soundsLike(" ".join(a1.last)," ".join(a2.last)):
            return 0

        if (a1.first == a2.first and a1.von == a2.von
            and a1.jr == a2.jr):
            return 2


        if soundsLike(" ".join(a1.first), " ".join(a2.first)):
            return 1

        if not a1.first or not a2.first:
            return 1

        if self._initialize(a1.first) == self._initialize(a2.first):
            return 1

        return 0

    def _initialize(self, name):
        name = " ".join(name).lower()
        name = re.sub(r'([a-z])[a-z\.]*', r'\1', name)
        name = clean(name)
        return name

    def _authorListsAlike(self, a1, a2):
        if len(a1) != len(a2):
            return 0
        a1 = [ (a.last, a) for a in a1 ]
        a2 = [ (a.last, a) for a in a2 ]
        a1.sort()
        a2.sort()
        if len(a1) != len(a2):
            return 0
        r = 2
        for (_, a1), (_, a2) in zip(a1,a2):
            x = self._authorsAlike(a1,a2)
            if not x:
                return 0
            elif x == 1:
                r = 1
        return r

    def _entryDatesAlike(self, e1, e2):
        try:
            if clean(e1['year']) == clean(e2['year']):
                return 2
            else:
                return 0
        except KeyError:
            return 1

    def includes(self, ent, all=0):
        title = ent['title']
        candidates = []
        for form in self._titleForms(title):
            try:
                candidates.extend(self.byTitle[form])
            except KeyError:
                pass
        goodness = []
        for knownEnt in candidates:
            match = (self._entryDatesAlike(ent, knownEnt) *
                     self._titlesAlike(ent['title'], knownEnt['title']) *
                     self._authorListsAlike(ent.parsedAuthor,
                                            knownEnt.parsedAuthor) )
            if match:
                goodness.append((match, knownEnt))
        goodness.sort()
        if all:
            return goodness
        if goodness:
            return goodness[-1]
        else:
            return None, None

    def demo(self):
        for e in self.entries:
            matches = self.includes(e, 1)
            m2 = []
            mids = []
            for g,m in matches:
                if id(m) not in mids:
                    mids.append(id(m))
                    m2.append((g,m))
            matches = m2

            if not matches:
                print "No match for %s"%e.key
            if matches[-1][1] is e:
                print "%s matches for %s: OK."%(len(matches), e.key)
            else:
                print "%s matches for %s: %s is best!" %(len(matches), e.key,
                                                         matches[-1][1].key)
            if len(matches) > 1:
                for g, m in matches:
                    print "%%%% goodness", g
                    print m


def noteToURL(note):
    " returns tp, url "
    note = note.replace("\n", " ")
    m = re.match(r'\s*(?:\\newline\s*)*\s*\\url{(.*)}\s*(?:\\newline\s*)*',
                 note)
    if not m:
        return None
    url = m.group(1)
    for suffix, tp in ((".html", "html"),
                       (".ps", "ps"),
                       (".ps.gz", "ps_gz"),
                       (".pdf", "pdf"),
                       (".txt", "txt")):
        if url.endswith(suffix):
            return tp,url
    return "???", url

all_ok = 1
def emit(f,ent):
    global all_ok

    errs = ent._check()
    if master.byKey.has_key(ent.key.strip().lower()):
        errs.append("ERROR: Key collision with master file")

    if errs:
        all_ok = 0

    note = ent.get("note")
    if ent.getURL() and not note:
        ent['note'] = "\url{%s}"%ent.getURL()
    elif note:
        m = re.match(r'\\url{(.*)}', note)
        if m:
            url = m.group(0)
            tp = None
            if url.endswith(".txt"):
                tp = "txt"
            elif url.endswith(".ps.gz"):
                tp = "ps_gz"
            elif url.endswith(".ps"):
                tp = "ps_gz"
            elif url.endswith(".pdf"):
                tp = "pdf"
            elif url.endswith(".html"):
                tp = "html"
            if tp:
                ent['www_%s_url'%tp] = url

    if errs:
        all_ok = 0
    for e in errs:
        print >>f, "%%%%", e

    print >>f, ent.format(77, 4, v=1, invStrings=invStrings)

def emitKnown(f, ent, matches):
    print >>f, "%% Candidates are:", ", ".join([e.key for g,e in matches])
    print >>f, "%%"
    print >>f, "%"+(ent.format(77,4,1,invStrings).replace("\n", "\n%"))

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "reconcile.py expects 2 arguments"
        sys.exit(1)

    config.load(sys.argv[1])

    print "========= Scanning master =========="
    master = MasterBibTeX()
    master = BibTeX.parseFile(config.MASTER_BIB, result=master)
    master.buildIndex()

    print "========= Scanning new file ========"
    try:
        fn = sys.argv[2]
        input = BibTeX.parseFile(fn)
    except BibTeX.ParseError, e:
        print "Error parsing %s: %s"%(fn,e)
        sys.exit(1)

    f = open('tmp.bib', 'w')
    keys = input.newStrings.keys()
    keys.sort()
    for k in keys:
        v = input.newStrings[k]
        print >>f, "@string{%s = {%s}}"%(k,v)

    invStrings = input.invStrings

    for e in input.entries:
        if not (e.get('title') and e.get('author')):
            print >>f, "%%\n%%%% Not enough information to search for a match: need title and author.\n%%"
            emit(f, e)
            continue

        matches = master.includes(e, all=1)
        if not matches:
            print >>f, "%%\n%%%% This entry is probably new: No match found.\n%%"
            emit(f, e)
        else:
            print >>f, "%%"
            print >>f, "%%%% Possible match found for this entry; max goodness",\
                  matches[-1][0], "\n%%"
            emitKnown(f, e, matches)

    if not all_ok:
        print >>f, "\n\n\nErrors remain; not finished.\n"

    f.close()
