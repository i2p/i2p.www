#!/usr/bin/python
# Copyright 2003-2008, Nick Mathewson.  See LICENSE for licensing info.

"""Generate indices by author, topic, date, and BibTeX key."""

import sys
import re
import os
import json

assert sys.version_info[:3] >= (2,2,0)
os.umask(022)

import BibTeX
import config

def getTemplate(name):
    f = open(name)
    template = f.read()
    f.close()
    template_s, template_e = template.split("%(entries)s")
    return template_s, template_e

def pathLength(s):
    n = 0
    while s:
        parent, leaf = os.path.split(s)
        if leaf != '' and leaf != '.':
            n += 1
        s = parent
    return n

def writeBody(f, sections, section_urls, cache_path, base_url):
    '''f: an open file
       sections: list of (sectionname, [list of BibTeXEntry])
       section_urls: map from sectionname to external url'''
    for s, entries in sections:
        u = section_urls.get(s)
        sDisp = re.sub(r'\s+', ' ', s.strip())
        sDisp = sDisp.replace(" ", "&nbsp;")
        if u:
            print >>f, ('<li><h3><a name="%s"></a><a href="%s">%s</a></h3>'%(
                (BibTeX.url_untranslate(s), u, sDisp)))
        else:
            print >>f, ('<li><h3><a name="%s">%s</a></h3>'%(
                BibTeX.url_untranslate(s),sDisp))
        print >>f, "<ul class='expand'>"
        for e in entries:
            print >>f, e.to_html(cache_path=cache_path, base_url=base_url)
        print >>f, "</ul></li>"

def writeHTML(f, sections, sectionType, fieldName, choices,
              tag, config, cache_url_path, section_urls={}):
    """sections: list of (sectionname, [list of BibTeXEntry])'''
       sectionType: str
       fieldName: str
       choices: list of (choice, url)"""

    title = config.TAG_TITLES[tag]
    short_title = config.TAG_SHORT_TITLES[tag]
    #
    secStr = []
    for s, _ in sections:
        hts = re.sub(r'\s+', ' ', s.strip())
        hts = s.replace(" ", "&nbsp;")
        secStr.append("<p class='l2'><a href='#%s'>%s</a></p>\n"%
                      ((BibTeX.url_untranslate(s),hts)))
    secStr = "".join(secStr)

    #
    tagListStr = []
    st = config.TAG_SHORT_TITLES.keys()
    st.sort()
    root = "../"*pathLength(config.TAG_DIRECTORIES[tag])
    if root == "": root = "."
    for t in st:
        name = config.TAG_SHORT_TITLES[t]
        if t == tag:
            tagListStr.append(name)
        else:
            url = BibTeX.smartJoin(root, config.TAG_DIRECTORIES[t], "date.html")
            tagListStr.append("<a href='%s'>%s</a>"%(url, name))
    tagListStr = "&nbsp;|&nbsp;".join(tagListStr)

    #
    choiceStr = []
    for choice, url in choices:
        if url:
            choiceStr.append("<a href='%s'>%s</a>"%(url, choice))
        else:
            choiceStr.append(choice)

    choiceStr = ("&nbsp;|&nbsp;".join(choiceStr))

    fields = { 'command_line' :  "",
               'sectiontypes' :  sectionType,
               'choices' : choiceStr,
               'field': fieldName,
               'sections' : secStr,
               'otherbibs' : tagListStr,
               'title': title,
               'short_title': short_title,
               "root" : root,
         }

    header, footer = getTemplate(config.TEMPLATE_FILE)
    print >>f, header%fields
    writeBody(f, sections, section_urls, cache_path=cache_url_path,
              base_url=root)
    print >>f, footer%fields

def jsonDumper(obj):
    if isinstance(obj, BibTeX.BibTeXEntry):
        e = obj.entries.copy()
        e['key'] = obj.key
        return e
    else:
        raise TypeError("Do not know how to serialize %s"%(obj.__class,))

def writePageSet(config, bib, tag):
    if tag:
        bib_entries = [ b for b in bib.entries
                          if tag in b.get('www_tags', "").split() ]
    else:
        bib_entries = bib.entries[:]

    if not bib_entries:
        print >>sys.stderr, "No entries with tag %r; skipping"%tag
        return

    tagdir = config.TAG_DIRECTORIES[tag]
    outdir = os.path.join(config.OUTPUT_DIR, tagdir)
    cache_url_path = BibTeX.smartJoin("../"*pathLength(tagdir),
                                      config.CACHE_DIR)
    if not os.path.exists(outdir):
        os.makedirs(outdir, 0755)
    ##### Sorted views:

    ## By topic.

    entries = BibTeX.sortEntriesBy(bib_entries, "www_section", "ZZZZZZZZZZZZZZ")
    entries = BibTeX.splitSortedEntriesBy(entries, "www_section")
    if entries[-1][0].startswith("<span class='bad'>"):
        entries[-1] = ("Miscellaneous", entries[-1][1])

    entries = [ (s, BibTeX.sortEntriesByDate(ents))
                for s, ents in entries
                ]

    f = open(os.path.join(outdir,"topic.html"), 'w')
    writeHTML(f, entries, "Topics", "topic",
              (("By topic", None),
               ("By date", "./date.html"),
               ("By author", "./author.html")
               ),
              tag=tag, config=config,
              cache_url_path=cache_url_path)
    f.close()

    ## By date.

    entries = BibTeX.sortEntriesByDate(bib_entries)
    entries = BibTeX.splitSortedEntriesBy(entries, 'year')
    for idx in -1, -2:
        if entries[idx][0].startswith("<span class='bad'>"):
            entries[idx] = ("Unknown", entries[idx][1])
        elif entries[idx][0].startswith("forthcoming"):
            entries[idx] = ("Forthcoming", entries[idx][1])
    sections = [ ent[0] for ent in entries ]

    first_year = int(entries[0][1][0]['year'])
    try:
        last_year = int(entries[-1][1][0].get('year'))
    except ValueError:
        last_year = int(entries[-2][1][0].get('year'))

    years = map(str, range(first_year, last_year+1))
    if entries[-1][0] == 'Unknown':
        years.append("Unknown")

    f = open(os.path.join(outdir,"date.html"), 'w')
    writeHTML(f, entries, "Years", "date",
              (("By topic", "./topic.html"),
               ("By date", None),
               ("By author", "./author.html")
               ),
              tag=tag, config=config,
              cache_url_path=cache_url_path)
    f.close()

    ## By author
    entries, url_map = BibTeX.splitEntriesByAuthor(bib_entries)

    f = open(os.path.join(outdir,"author.html"), 'w')
    writeHTML(f, entries, "Authors", "author",
              (("By topic", "./topic.html"),
               ("By date", "./date.html"),
               ("By author", None),
              ),
              tag=tag, config=config,
              cache_url_path=cache_url_path,
              section_urls=url_map)
    f.close()

    ## The big BibTeX file

    entries = bib_entries[:]
    entries = [ (ent.key, ent) for ent in entries ]
    entries.sort()
    entries = [ ent[1] for ent in entries ]

    ## Finding the root directory is done by writeHTML(), but
    ## the BibTeX file doesn't use that, so repeat the code here
    root = "../"*pathLength(config.TAG_DIRECTORIES[tag])
    if root == "": root = "."

    header,footer = getTemplate(config.BIBTEX_TEMPLATE_FILE)
    f = open(os.path.join(outdir,"bibtex.html"), 'w')
    print >>f, header % { 'command_line' : "",
                          'title': config.TAG_TITLES[tag],
                          'root': root }
    for ent in entries:
        print >>f, (
            ("<tr><td class='bibtex'><a name='%s'>%s</a>"
            "<pre class='bibtex'>%s</pre></td></tr>")
            %(BibTeX.url_untranslate(ent.key), ent.key, ent.format(90,8,1)))
    print >>f, footer
    f.close()

    f = open(os.path.join(outdir,"bibtex.json"), 'w')
    json.dump(entries, f, default=jsonDumper)
    f.close()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        print "Loading from %s"%sys.argv[1]
    else:
        print >>sys.stderr, "Expected a single configuration file as an argument"
        sys.exit(1)
    config.load(sys.argv[1])

    bib = BibTeX.parseFile(config.MASTER_BIB)

    for tag in config.TAG_DIRECTORIES.keys():
        writePageSet(config, bib, tag)
