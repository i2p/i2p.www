from flask import render_template

from i2p2www import ANONBIB_CFG, ANONBIB_FILE
from i2p2www.anonbib import BibTeX, config

def papers_list():
    config.load(ANONBIB_CFG)
    rbib = BibTeX.parseFile(ANONBIB_FILE)
    rbib = [ b for b in rbib.entries ]
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

    print bib['sections']

    return render_template('papers/list.html', bib=bib)
