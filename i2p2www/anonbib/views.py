from flask import render_template

from i2p2www import ANONBIB_CFG, ANONBIB_FILE
from i2p2www.anonbib import BibTeX, config

def papers_list(tag=None, choice=None):
    config.load(ANONBIB_CFG)
    rbib = BibTeX.parseFile(ANONBIB_FILE)
    if tag:
        rbib = [ b for b in rbib.entries if tag in b.get('www_tags', '').split() ]
    else:
        rbib = rbib.entries

    if choice == 'topic':
        rbib = BibTeX.sortEntriesBy(rbib, 'www_section', 'ZZZZZZZZZZZZZZ')
        rbib = BibTeX.splitSortedEntriesBy(rbib, 'www_section')
        if rbib[-1][0].startswith("<span class='bad'>"):
            rbib[-1] = ("Miscellaneous", rbib[-1][1])

        rbib = [ (s, BibTeX.sortEntriesByDate(ents))
                 for s, ents in rbib
                 ]
    elif choice == 'author':
        rbib, url_map = BibTeX.splitEntriesByAuthor(rbib)
    else:
        rbib = BibTeX.sortEntriesByDate(rbib)
        rbib = BibTeX.splitSortedEntriesBy(rbib, 'year')

    bib = {}
    bib['title'] = 'Papers on I2P'
    bib['short_title'] = 'I2P Papers'
    bib['otherbibs'] = ''
    bib['choices'] = ''
    bib['sectiontypes'] = 'Dates'
    bib['field'] = 'date'

    sections = []
    for section, entries in rbib:
        s = {}
        s['name'] = section
        s['slug'] = section
        s['entries'] = entries
        sections.append(s)
    bib['sections'] = sections

    return render_template('papers/list.html', bib=bib)

def papers_bibtex(tag=None):
    config.load(ANONBIB_CFG)
    rbib = BibTeX.parseFile(ANONBIB_FILE)
    if tag:
        rbib = [ b for b in rbib.entries if tag in b.get('www_tags', '').split() ]
    else:
        rbib = rbib.entries
    entries = [ (ent.key, ent) for ent in rbib ]
    entries.sort()
    entries = [ ent[1] for ent in entries ]

    bib = {}
    bib['title'] = 'Papers on I2P'
    bib['entries'] = rbib

    return render_template('papers/bibtex.html', bib=bib)
