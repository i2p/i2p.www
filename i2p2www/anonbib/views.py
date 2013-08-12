from flask import render_template

from i2p2www import ANONBIB_CFG, ANONBIB_FILE
from i2p2www.anonbib import BibTeX, config

def papers_list(tag='', choice='date'):
    config.load(ANONBIB_CFG)
    rbib = BibTeX.parseFile(ANONBIB_FILE)
    if tag:
        rbib = [ b for b in rbib.entries if tag in b.get('www_tags', '').split() ]
    else:
        rbib = rbib.entries

    if choice == 'topic':
        sectionType = 'Topics'
        rbib = BibTeX.sortEntriesBy(rbib, 'www_section', 'ZZZZZZZZZZZZZZ')
        rbib = BibTeX.splitSortedEntriesBy(rbib, 'www_section')
        if rbib[-1][0].startswith("<span class='bad'>"):
            rbib[-1] = ("Miscellaneous", rbib[-1][1])

        rbib = [ (s, BibTeX.sortEntriesByDate(ents))
                 for s, ents in rbib
                 ]
    elif choice == 'author':
        sectionType = 'Authors'
        rbib, url_map = BibTeX.splitEntriesByAuthor(rbib)
    else:
        sectionType = 'Years'
        choice = 'date'
        rbib = BibTeX.sortEntriesByDate(rbib)
        rbib = BibTeX.splitSortedEntriesBy(rbib, 'year')

    bib = {
        'tags':             config.ALL_TAGS,
        'tag_titles':       config.TAG_TITLES,
        'tag_short_titles': config.TAG_SHORT_TITLES,
        'tag':              tag,
        'sectiontypes':     sectionType,
        'field':            choice,
        }

    sections = []
    for section, entries in rbib:
        s = {
            'name':    section,
            'slug':    section,
            'entries': entries,
            }
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

    bib = {
        'title':   'Papers on I2P',
        'entries': rbib,
        }

    return render_template('papers/bibtex.html', bib=bib)
